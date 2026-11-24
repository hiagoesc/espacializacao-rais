# Espacialização da RAIS — São José dos Campos

Pipeline reprodutível para **espacializar os estabelecimentos da RAIS (2017–2025)** de São José dos Campos usando o **CEP** como chave: o CEP dos Correios é transferido para a malha de logradouros do Geosanja, e cada registro da RAIS recebe o ponto do seu CEP.

Segue o **padrão de projetos** (`docs/manual_padrao_projetos.md`).

## Fluxo

| Nº | Notebook | O que faz | Lê | Grava |
|---|---|---|---|---|
| 01 | `01_consolidar_rais` | Lê os 9 arquivos nacionais da RAIS, filtra o município e padroniza | `01_dados_brutos/rais` | `03_processamento/01_…` |
| 02 | `02_parear_cep_logradouro` | Pareia CEP (Correios) × segmento (Geosanja) em cascata: exato → iniciais → fuzzy | Correios, Geosanja | `03_processamento/02_…` |
| 03 | `03_base_logradouros_cep` | Cria a **base oficial editável** de logradouros com CEP (só se ainda não existir) | Geosanja + 02 | **`02_dados_editados/logradouros_cep.gpkg`** |
| 04 | `04_grandes_usuarios` | Localiza CEPs de grande usuário (sufixo ≥ 900) via ViaCEP + CNEFE | 01 + CNEFE + internet | **`02_dados_editados/grande_usuario_ceps.csv`** |
| 05 | `05_classificar_rais_cep` | Classifica cada CEP da RAIS (A, B, C, D, E, G) e gera as linhas/pontos por CEP | 01, 02, base, CSV 04 | `03_processamento/05_…` |
| 06 | `06_pontos_e_pendencias` | Camada de pontos da RAIS (A, B, G) + Excel de CEPs a localizar | 05, base | **`04_entrega/`** + `03_processamento/06_…` |
| 07 | `07_auditar_cep_cnefe` | Audita os CEPs da base e sugere CEP por trecho (classes C e D) pelo CNEFE | base, CNEFE, 02, 05 | `03_processamento/07_…` |

Exploratório (fora do fluxo): `scripts/exploratorio/diagnostico_bases_correios_geosanja.ipynb`.

### Classes de CEP (etapa 05)

| Classe | Significado | Tem ponto? |
|---|---|---|
| A | CEP em 1 logradouro, até 1 km | sim (boa precisão) |
| B | CEP em vários logradouros ou mais de 1 km | sim (aproximado) |
| G | grande usuário localizado (etapa 04) | sim |
| C | CEP só como candidato em trecho ambíguo | não — verificar |
| D | CEP dos Correios fora da base (órfão) | não — verificar |
| E | CEP fora dos Correios (inválido, outra cidade, sufixo 000…) | não |

## Como rodar

1. Criar o ambiente: `conda env create -f environment.yml` (ou `pip install -r requirements.txt`) e ativar.
2. Colocar os dados brutos em `01_dados_brutos/` (ver `docs/fontes.md`).
3. Rodar tudo: `python executar_tudo.py` (ou abrir os notebooks de `scripts/` em ordem).

Opções: `--de 05`, `--ate 04`, `--ciclo`, `--listar`. Logs em `03_processamento/logs/`; notebooks executados em `03_processamento/notebooks_executados/`.

## Ciclo de correção manual

A base `02_dados_editados/logradouros_cep.gpkg` é a **base oficial** da Prefeitura e é corrigida à mão (QGIS):

1. Ver as pendências: `03_processamento/06_pontos_e_pendencias/ceps_a_localizar.xlsx` e `03_processamento/07_auditar_cep_cnefe/auditoria_cnefe.*`.
2. Corrigir a coluna `cep` da base (vários CEPs separados por `|`), marcar `cep_origem = manual` e `cep_conferido = Sim`.
3. Rodar `python executar_tudo.py --ciclo` (etapas 05, 06 e 07).

A etapa 03 **nunca** sobrescreve a base editada. A etapa 04 faz backup do CSV em `02_dados_editados/_backup/` antes de regravar.

## Entrega

`04_entrega/rais_estab_pontos.gpkg` (camada `rais_pontos`: um ponto por registro da RAIS com classe A, B ou G, todos os anos) e `04_entrega/ceps_espacializados.gpkg` (linhas e pontos por CEP).

## Documentação

- `docs/fontes.md` — origem e formato de cada dado bruto
- `docs/decisoes.md` — decisões de método
- `docs/handoff/STATUS.md` — estado atual do projeto
