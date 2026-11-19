# Fontes de dados

Todos os arquivos brutos ficam em `01_dados_brutos/` (fora do Git) e **não são alterados**. Para atualizar uma fonte, substitua o arquivo mantendo o nome indicado aqui (ou ajuste o `config.yaml`) e rode o fluxo de novo.

## RAIS — Estabelecimentos (PDET/MTE)

- **Pasta:** `01_dados_brutos/RAIS/<ano>/` (2017 a 2025), arquivos como vêm do FTP, já extraídos do `.7z`.
- **Origem:** `ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/<ano>/`
- **Arquivos por ano:**

| Ano | Arquivo | Formato |
|---|---|---|
| 2017 | `ESTB2017.txt` | antigo (`;`) |
| 2018–2021 | `RAIS_ESTAB_PUB.txt` | antigo (`;`) |
| 2022 | `RAIS_ESTAB_PUB.txt.txt` (extensão duplicada no original) | antigo (`;`) |
| 2023–2025 | `RAIS_ESTAB_PUB.COMT` | novo (`,`) |

- **Encoding:** `latin-1`. Colunas lidas por posição (ver cabeçalho do notebook 01).
- **Conferência:** 2025 = 47.223 estabelecimentos e 228.391 vínculos ativos em São José dos Campos.

## Correios — Logradouros de São José dos Campos

- **Arquivo:** `01_dados_brutos/Correios/correios_logradouros_sjc.xlsx`
- **Nome original:** `exportar-logradouros-SP-São José dos Campos-01_10_2026-07_54_39.xlsx` (exportação de 01/10/2026). Renomeado para seguir o padrão (sem espaço e sem acento).
- **Conteúdo:** CEP, logradouro, bairro, situação (5.330 linhas na exportação usada).

## Geosanja — Logradouros

- **Arquivo:** `01_dados_brutos/Geosanja/logradouros.gpkg`, camada `logradouros`.
- **Origem:** tabela de logradouros do banco PostGIS da Prefeitura, exportada para GeoPackage.
- **CRS:** EPSG:31983 (SIRGAS 2000 / UTM 23S). 9.435 feições (MultiLineString).
- **Campos:** `id` (chave), `id_0`, `oms_id`, `nome`, `tipo`, `diploma`, `numero`, `ano`, `loteamento`, `nome_ante`, `shape_leng`.

## CNEFE — Cadastro Nacional de Endereços para Fins Estatísticos (IBGE, Censo 2022)

- **Arquivo:** `01_dados_brutos/CNEFE/3549904_SAO_JOSE_DOS_CAMPOS.csv` (nome original do IBGE).
- **Separador:** `;`. Coordenadas em graus decimais com ponto.
- **CRS assumido:** EPSG:4674 (SIRGAS 2000, graus) — confirmar na documentação do IBGE.
- **Colunas usadas:** `CEP`, `NOM_TIPO_SEGLOGR`, `NOM_TITULO_SEGLOGR`, `NOM_SEGLOGR`, `NUM_ENDERECO`, `DSC_MODIFICADOR`, `LATITUDE`, `LONGITUDE`, `DSC_ESTABELECIMENTO`.

## APIs (etapa 04)

- **ViaCEP** (`https://viacep.com.br/ws/<cep>/json/`): unidade, logradouro, número (`complemento`) e bairro do CEP. Gratuita, sem cadastro.
- **BrasilAPI** (`https://brasilapi.com.br/api/cep/v2/<cep>`): coordenada aproximada (fonte open-cep). Usada só quando o CNEFE falha.
