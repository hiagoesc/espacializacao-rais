# STATUS — Espacialização da RAIS
Atualizado em: 2026-11-19

## Objetivo
Espacializar os estabelecimentos da RAIS (2017–2025) de São José dos Campos pelo CEP, usando a base oficial de logradouros com CEP (Geosanja + Correios), corrigida em ciclos manuais.

## Estado atual
- Projeto no padrão de projetos (pastas 01–04, `scripts/`, `config.yaml`, `src/`, `executar_tudo.py`). Dados migrados e **fluxo completo 01–07 rodado na estrutura nova em 19/11/2026, sem erros (308 s)**.
- Etapa 05 reproduz os números da estrutura antiga (ano de referência 2025): A 2626 CEPs, B 254, C 53, D 676, E 56, G 68. Espacializável (A+B+G) = 86,2% dos estabelecimentos e 85,6% dos vínculos.
- Etapa 04: 94 CEPs de grande usuário com vínculos; 85 com coordenada (99,7% dos vínculos); 9 sem coordenada (393 vínculos; maior: 12245972, 178). 27 coordenadas aproximadas para conferir.
- Etapa 07 (CNEFE) rodada com dados reais: 97% dos locais do CNEFE a até 100 m de um segmento (CRS 4674 confirmado na prática).
  - Auditoria de 3641 CEPs da base: ok 3140 | suspeito 88 | atenção 52 | poucos pontos 114 | sem pontos 247.
  - Classe C: 380 trechos ambíguos → sugerido 72 | votação fraca 23 | sem pontos 285 (avenidas/rodovias longas continuam manuais).
  - Classe D: 1684 órfãos → trecho sugerido 681 | sem pontos no CNEFE 763 | votação fraca 118. Órfãos com vínculos na RAIS: 537, 360 com trecho sugerido.
  - 1868 segmentos para revisar no QGIS (preencher 1181 | conferir 687).
- Maiores suspeitos (por vínculos): 12224300 (Dutra), 12242000 e 12242840 (Av. São João), 12227000 (Faria Lima), 12247000, 12244000, 12220000 (JK), 12245010, 12237540, 12229380. Hipótese (não verificada no mapa): (a) via dos pontos = via da base, distância 200 m–1 km → CEP aplicado só a parte da avenida; (b) via dos pontos "Sem nome", 4–7 km → CEP em segmento errado/sem nome.
- Nenhuma sugestão da etapa 07 foi aplicada à base ainda.
- Repositório publicado (público): https://github.com/hiagoesc/espacializacao-rais (branch `main`, 28 arquivos, só código e docs). Atualizar com `git add .`, `git status`, `git commit -m ...`, `git push`.

## Pendências
- [ ] Revisar `sugestoes_segmentos` e `auditoria_segmentos` no QGIS (começar por `status_sugestao = sugerido` e `acao = preencher`; suspeitos com mais vínculos).
- [ ] Copiar os CEPs aceitos para a base `02_dados_editados/logradouros_cep.gpkg` (`cep_origem = manual`, `cep_conferido = Sim`) e rodar `python executar_tudo.py --ciclo`.
- [ ] Rodovia Presidente Dutra: 33 trechos ambíguos com 9 CEPs por faixa de km; sem pontos no CNEFE → manual (opção: referência por km).
- [ ] 9 CEPs de grande usuário sem coordenada: preencher lat/lon (`fonte_coord = manual`) ou `cep_novo` no CSV.
- [ ] Opcional: etapa 04 faz backup do CSV a cada execução enquanto houver CEPs não encontrados.

## Próxima ação
Revisão manual das sugestões da etapa 07 no QGIS e novo ciclo (`--ciclo`).

## Arquivos-chave
- Base oficial (editada): `02_dados_editados/logradouros_cep.gpkg`
- Grandes usuários (editável): `02_dados_editados/grande_usuario_ceps.csv`
- Entrega: `04_entrega/rais_estab_pontos.gpkg`, `04_entrega/ceps_espacializados.gpkg`
- Pendências: `03_processamento/06_pontos_e_pendencias/ceps_a_localizar.xlsx`, `03_processamento/07_auditar_cep_cnefe/auditoria_cnefe.xlsx` e `.gpkg`
- Logs: `03_processamento/logs/`
