"""Bloco padrão de validação de tabelas (nulos, duplicados, perda de registros)."""
import logging

log = logging.getLogger("validacao")


def validar_tabela(nome, df, chave=None, obrigatorias=None, linhas_entrada=None):
    """Registra no log: linhas, perda vs. entrada, nulos/vazios nas colunas obrigatórias e duplicados na chave."""
    log.info("Validando %s...", nome)
    log.info("  linhas: %d", len(df))
    if linhas_entrada is not None:
        perda = linhas_entrada - len(df)
        log.info("  perda vs. entrada: %d (%.2f%%)", perda, (perda / linhas_entrada * 100) if linhas_entrada else 0.0)
    for col in (obrigatorias or []):
        vazios = int((df[col].isna() | (df[col].astype(str).str.strip() == "")).sum())
        (log.info if vazios == 0 else log.warning)("  '%s': %d nulos/vazios", col, vazios)
    if chave:
        dup = int(df.duplicated(chave).sum())
        (log.info if dup == 0 else log.warning)("  duplicados na chave %s: %d", chave, dup)
    log.info("Validação de %s concluída!", nome)
