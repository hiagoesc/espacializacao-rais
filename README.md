# Espacialização da RAIS — São José dos Campos

Pipeline reprodutível para **espacializar os estabelecimentos da RAIS (2017–2025)** de São José dos Campos usando o **CEP** como chave: o CEP dos Correios é transferido para a malha de logradouros do Geosanja, o CNEFE completa e corrige o que o nome não resolve, e cada registro da RAIS recebe o ponto do seu CEP.

Segue o **padrão de projetos** (`docs/manual_padrao_projetos.md`).

## Fluxo

| Nº | Notebook | O que faz | Lê | Grava |
|---|---|---|---|---|
| 01 | `01_consolidar_rais` | Lê os 9 arquivos nacionais da RAIS, filtra o município e padroniza | `01_dados_brutos/rais` | `03_processamento/01_…` |
| 02 | `02_parear_cep_logradouro` | Pareia CEP (Correios) × segmento (Geosanja) em cascata: exato → iniciais → fuzzy | Correios, Geosanja | `03_processamento/02_…` |
| 03 | `03_base_logradouros_cep` | Monta a base de logradouros com CEP **sem revisão manual**: Correios × Geosanja + CNEFE (troca CEP suspeito, resolve multi_cep, ambíguo, sem CEP e sem nome) | Geosanja, 02, CNEFE | **`02_dados_editados/logradouros_cep.gpkg`** (só se não existir) + `03_processamento/03_…` |
| 04 | `04_localizar_ceps` | Localiza pelo **endereço** os CEPs que sobraram (grandes usuários e CEPs sem trecho nem pontos do CNEFE): endereço por Correios/ViaCEP/BrasilAPI (com cache em parquet) → CNEFE → Geosanja → Nominatim → bairro/CEPs vizinhos (baixa confiança) | 01, 02, 03, CNEFE + internet | **`02_dados_editados/ceps_localizados.csv`** |
| 05 | `05_classificar_rais_cep` | Classifica cada CEP da RAIS (A, B, G, P, C, D, E), com processo e confiança, e gera as linhas/pontos por CEP | 01, 02, base, CSV 04, locais do CNEFE (03) | `03_processamento/05_…` |
| 06 | `06_pontos_e_pendencias` | Confere os pontos da RAIS (A, B, G, P) e gera o Excel com **exatamente** os CEPs da RAIS sem ponto | 05, base | `04_entrega/ceps_espacializados.gpkg` + `03_processamento/06_…` |
| 07 | `07_exportar_entregas` | **Entregas finais:** todos os registros da RAIS (GeoPackage e Excel; sem ponto = sem geometria) e o saldo anual de vínculos ativos | 05 (classificada e pontos), 01 | **`04_entrega/`** |

Exploratório (fora do fluxo): `scripts/exploratorio/diagnostico_bases_correios_geosanja.ipynb`.

### Processo de cada CEP

| Coluna | Valores |
|---|---|
| `cep_origem` (base, por segmento) | `correios_geosanja:<método>` · `cnefe_segmento` · `correios_geosanja:multi_cep_sem_cnefe` · `manual` |
| `processo` (por CEP da RAIS) | `correios_geosanja` · `cnefe_segmento` · `manual` (vários: `a\|b`) · `cnefe_pontos_cep` · `localizacao_endereco` |
| `cep_confianca` / `confianca` | `alta` · `media` · `baixa` · `manual` |

A base também guarda `cep_correios` (o que os Correios deram), `cnefe_motivo` (por que o CNEFE agiu, inclusive `cep_suspeito:<cep> (mediana N m)`), `cnefe_votos`, `cnefe_n_locais`, `cnefe_participacao`, `cep_entre_candidatos`, `nome_origem` e `nome_geosanja`.

### Classes de CEP (etapa 05)

| Classe | Significado | Tem ponto? |
|---|---|---|
| A | CEP em 1 logradouro, até 1 km | sim |
| B | CEP em vários logradouros ou mais de 1 km | sim (aproximado) |
| G | localizado pelo endereço na etapa 04 (`confianca` e fonte no CSV) | sim |
| P | sem trecho na base, mas com endereços no CNEFE (centro dos pontos, puxado para o segmento mais próximo) | sim |
| C | CEP só como candidato em trecho ambíguo, sem pontos no CNEFE e não localizado na etapa 04 | não — localizar à mão |
| D | CEP dos Correios fora da base, sem pontos no CNEFE e não localizado na etapa 04 | não — localizar à mão |
| E | CEP fora dos Correios que nem a etapa 04 localizou (inválido, outra cidade, sufixo 000, endereço desconhecido…) | não |

## Como rodar

1. Criar o ambiente: `conda env create -f environment.yml` (ou `pip install -r requirements.txt`) e ativar.
2. Colocar os dados brutos em `01_dados_brutos/` (ver `docs/fontes.md`).
3. Rodar tudo: `python executar_tudo.py` (ou abrir os notebooks de `scripts/` em ordem).

Opções: `--de 05`, `--ate 04`, `--ciclo`, `--listar`. Logs em `03_processamento/logs/`; notebooks executados em `03_processamento/notebooks_executados/`.

## Correção manual (o que sobrar)

1. Abrir `03_processamento/06_pontos_e_pendencias/ceps_a_localizar.xlsx`, aba **CEPs sem ponto** (coluna `acao`).
2. Corrigir a coluna `cep` da base `02_dados_editados/logradouros_cep.gpkg` no QGIS (vários CEPs separados por `|`), com `cep_origem = manual` e `cep_conferido = Sim`; ou preencher `lat`/`lon` com `fonte_coord = manual` em `02_dados_editados/ceps_localizados.csv`.
3. Rodar `python executar_tudo.py --ciclo` (etapas 04, 05, 06 e 07).

A etapa 03 **nunca** sobrescreve a base editada: se ela existir, a versão automática vai para `03_processamento/03_base_logradouros_cep/logradouros_cep_automatico.gpkg`. Para refazer a base do zero, apague a base editada e rode `python executar_tudo.py --de 03`. A etapa 04 faz backup do CSV em `02_dados_editados/_backup/` antes de regravar.

## Entrega

`04_entrega/` (dados internos da Prefeitura, fora do Git):

- `rais_estab_espacial.gpkg` (camada `rais_estab_espacial`, EPSG:4674): **todos** os registros da RAIS (todos os anos) com as colunas originais da RAIS e `situacao_espacial` (`espacializado` ou `nao_localizavel`), `classe_cep`, `motivo_cep`, `processo_cep`, `confianca_cep`, `ponto_metodo`, `n_partes`, `lat` e `lon`. Registros sem ponto ficam **sem geometria** (e sem `lat`/`lon`). CEP de outro município **não** tem rótulo próprio: o registro consta como de São José dos Campos e fica `nao_localizavel`.
- `rais_estab_espacial.xlsx`: as mesmas linhas e colunas, sem geometria, **uma aba por ano** + aba `legenda`.
- `saldo_vinculos_ativos.xlsx`: **saldo anual** de vínculos ativos (soma de `qtd_vinc_ativos` de todos os registros, com ou sem ponto), variação em relação ao ano anterior, parcela `espacializado` × `nao_localizavel` (aba `por_ano`) e saldo por confiança do ponto (aba `por_ano_confianca`).
- `ceps_espacializados.gpkg`: linhas e pontos por CEP.

O `rais_estab_pontos.gpkg` das versões anteriores não é mais gerado (pode ser apagado).

## Documentação

- `docs/fontes.md` — origem e formato de cada dado bruto
- `docs/decisoes.md` — decisões de método
- `docs/handoff/STATUS.md` — estado atual do projeto
