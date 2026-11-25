# STATUS — Espacialização da RAIS
Atualizado em: 2026-11-25

## Objetivo
Espacializar os estabelecimentos da RAIS (2017–2025) de São José dos Campos pelo CEP, usando a base de logradouros com CEP (Geosanja + Correios + CNEFE), e entregar todos os registros (com ou sem ponto) e o saldo anual de vínculos ativos. Corrigir a base do Geosanja é objetivo secundário.

## Estado atual
- **Fluxo 01 a 07 pronto e rodado com dados reais em 25/11/2026 (06 e 07 às 16:17), sem erros e com todas as conferências OK.** Repositório: https://github.com/hiagoesc/espacializacao_rais (branch `main`).
- **Entrega final (`04_entrega/`):** `rais_estab_espacial.gpkg` (uma camada, EPSG:4674, 330.067 registros: 327.383 com ponto e 2.684 `nao_localizavel`, sem geometria), `rais_estab_espacial.xlsx` (uma aba por ano + legenda), `saldo_vinculos_ativos.xlsx` (saldo anual) e `ceps_espacializados.gpkg`.
- **Números:** 99,2% dos registros de todos os anos têm ponto (97,8% em 2017 a 100% em 2024–2025); em 2025, 100% dos estabelecimentos e dos vínculos. Confiança dos pontos (registros): alta 224.050, média 70.963, baixa 32.370. CEPs da RAIS por classe: A 2.960 · B 560 · G 348 · P 274 · D 3 · E 751.
- **Saldo de vínculos ativos (31/12):** 187.441 em 2017 → 228.391 em 2025; total dos anos = 1.786.247, igual à RAIS consolidada. Parcela `nao_localizavel`: 1,15% em 2017, 0,01% em 2025.
- **Aviso conhecido:** o número de estabelecimentos sobe 57,4% de 2022 (27.960) para 2023 (44.020); vem da própria RAIS (os totais batem com a consolidada), os vínculos não têm esse salto.
- **Sobra:** 754 CEPs sem ponto (2.684 registros, 0,8%): 17 dá para localizar à mão (maiores: 12213842, 12214470, 12244001) e 737 não são espacializáveis pelo CEP (vazio, inválido, outro município, geral do município). Registros de CEP de outro município ficam `nao_localizavel` e continuam contados como de São José dos Campos.
- **ViaCEP ainda bloqueando o IP (10054):** 30 CEPs ficaram `nao_consultado` na 04 (maioria CEPs 000 de outros municípios, ex.: 12260000, 12460000, 12270000). A etapa avisa e o cache em `03_processamento/04_localizar_ceps/cache_*.parquet` retoma sozinho.
- **Etapa 04** (`04_localizar_ceps`): endereço por Correios → ViaCEP → BrasilAPI (coordenada da BrasilAPI não é usada); coordenada por CNEFE → Geosanja → Nominatim → bairro/CEPs vizinhos (confiança baixa). Cache em parquet, disjuntor após 3 falhas seguidas, CSV `02_dados_editados/ceps_localizados.csv` aceita endereço manual, `cep_novo` (desmembrado com `|`), `nao_localizavel` e `outra_cidade`. A leitura do CSV tolera o Excel (cp850 e decimal com separador de milhar).
- **Casos manuais de 25/11 aplicados no CSV:** 12214500 (Estrada Jaguari, Buquirinha II), 12225000 (desmembrado em 9 CEPs da Av. Presidente Tancredo Neves), 12200000 (`nao_localizavel`), 12250000 (`outra_cidade`).

## Última sessão (2026-11-25)
- Cache das APIs e disjuntor na 04; filtro de outro município; CEPs 000 como alvo; últimos recursos (`cnefe_bairro`, `cnefe_cep_vizinhos`); CSV tolerante ao Excel.
- Etapa 07 nova (`07_exportar_entregas`); a 06 deixou de gravar `rais_estab_pontos.gpkg`. Ciclo = 04, 05, 06, 07. Detalhes em `docs/decisoes.md` e `docs/handoff/2026-11-25_localizacao_enderecos_e_entrega.md`.

## Pendências
- [ ] Rodar a 04 de novo quando o ViaCEP liberar (resolve os 30 `nao_consultado`), depois `python executar_tudo.py --ciclo`.
- [ ] Localizar à mão os 17 CEPs da aba "CEPs sem ponto" com `pode_espacializar = Sim` (preencher `lat`/`lon` e `fonte_coord = manual` no CSV), depois `--ciclo`.
- [ ] Apagar à mão `04_entrega/rais_estab_pontos.gpkg` (versão antiga, não é mais gerado).
- [ ] Opcional: instalar `xlsxwriter` (o Excel dos registros leva ~100 s com `openpyxl`).
- [ ] Opcional: revisar os CEPs de confiança baixa (aba "Confianca baixa" do `ceps_a_localizar.xlsx`).

## Próxima ação
Nenhuma obrigatória: a entrega está pronta. Quando o ViaCEP liberar, rodar `python executar_tudo.py --de 04` e conferir o log da 04.

## Arquivos-chave
- Base (editável): `02_dados_editados/logradouros_cep.gpkg`
- CEPs localizados pelo endereço (editável): `02_dados_editados/ceps_localizados.csv` (ver `02_dados_editados/LEIAME.md`)
- Lista manual: `03_processamento/06_pontos_e_pendencias/ceps_a_localizar.xlsx`
- Entrega: `04_entrega/rais_estab_espacial.gpkg`, `rais_estab_espacial.xlsx`, `saldo_vinculos_ativos.xlsx`, `ceps_espacializados.gpkg`
- Logs: `03_processamento/logs/`
