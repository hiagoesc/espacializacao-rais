"""Arquivos editados à mão (02_dados_editados): existência, prioridade sobre o bruto e backup.

Regra do padrão:
1. existe a versão editada? -> usa ela;
2. não existe? -> o notebook indicado em 'gerado_por' cria a versão inicial (uma vez só);
3. antes de regravar um editado, faz cópia datada em 02_dados_editados/_backup.
"""
import io
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("fontes")


def existe_editado(cfg, chave: str) -> bool:
    """True se o arquivo editado 'editados.<chave>' já existe."""
    return cfg.caminho("editados." + chave).exists()


def caminho_editado(cfg, chave: str, obrigatorio: bool = True):
    """Caminho do arquivo editado. Se não existir e for obrigatório, para com a instrução de qual notebook rodar."""
    caminho = cfg.caminho("editados." + chave)
    if caminho.exists():
        log.info("Usando a versão editada: %s", caminho.name)
        return caminho
    gerador = cfg._buscar("editados." + chave).get("gerado_por", "?")
    if obrigatorio:
        raise FileNotFoundError(f"{caminho} não existe. Rode antes o notebook {gerador} (ele cria a versão inicial).")
    log.warning("Arquivo editado %s ainda não existe (é criado pelo notebook %s).", caminho.name, gerador)
    return None


def backup(cfg, caminho) -> Path:
    """Copia um arquivo para 02_dados_editados/_backup com data e hora no nome. Devolve o caminho da cópia."""
    caminho = Path(caminho)
    destino = cfg.pasta("backup") / f"{caminho.stem}_{datetime.now():%Y%m%d_%H%M%S}{caminho.suffix}"
    shutil.copy2(caminho, destino)
    log.info("Backup criado: %s", destino.name)
    return destino


def ler_csv_editado(caminho, sep=";"):
    """Lê um CSV editado à mão (tudo como texto), aceitando o que o Excel grava.

    O Excel pode salvar em UTF-8, em ANSI (cp1252) ou em 'CSV (MS-DOS)' (cp850). Tenta UTF-8 primeiro; se não for,
    escolhe entre cp1252 e cp850 a leitura que tem mais letras acentuadas do português (ã, é, ç...).
    """
    bruto = Path(caminho).read_bytes()
    try:
        texto = bruto.decode("utf-8-sig")
    except UnicodeDecodeError:
        letras = "áàâãäéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ"
        candidatos = {enc: bruto.decode(enc, errors="replace") for enc in ("cp1252", "cp850")}
        codificacao = max(candidatos, key=lambda enc: sum(candidatos[enc].count(c) for c in letras))
        log.warning("%s não está em UTF-8 (salvo pelo Excel?): lido como %s. Na próxima gravação volta para UTF-8.",
                    Path(caminho).name, codificacao)
        texto = candidatos[codificacao]
    return pd.read_csv(io.StringIO(texto), sep=sep, dtype=str, keep_default_na=False)


def _coordenada(texto):
    """Um texto -> número (ou NaN). Ver ler_coordenada."""
    t = str(texto).strip().replace(" ", "")
    if not t:
        return np.nan
    if re.fullmatch(r"-?\d+[.,]\d+", t):                       # formato normal: -23.220157 ou -23,220157
        return float(t.replace(",", "."))
    digitos = re.sub(r"\D", "", t)                              # Excel pt-BR trata o ponto como milhar: -23.220.157 ou -23220157
    if len(digitos) < 3:
        return np.nan
    return (-1 if t.startswith("-") else 1) * float(digitos[:2] + "." + digitos[2:])   # parte inteira de lat/lon daqui tem 2 dígitos


def ler_coordenada(serie):
    """Converte uma coluna de lat/lon em texto para número, mesmo se o Excel estragou o decimal.

    Aceita '-23.220157', '-23,220157' e '-23.220.157' / '-23220157' (decimal tomado como separador de milhar).
    Texto vazio ou sem dígitos vira NaN.
    """
    return serie.map(_coordenada).astype(float)
