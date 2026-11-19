# Decisões de método

Registro das regras adotadas, com data e motivo. Parâmetros numéricos ficam no `config.yaml` (`parametros`).

## 2026-11 — Base e consolidação

- **RAIS 2023–2025 = arquivo `.COMT`:** é o único que bate com o total nacional do Sumário Executivo (2023 = 11.768.420; 2024 = 13.186.059). O `Parcial` não tem administração pública; o `Legado` de 2023 não bate.
- **Linhas duplicadas da RAIS não são removidas:** não há identificador do estabelecimento; linhas iguais são, provavelmente, estabelecimentos diferentes.
- **CEP inválido não descarta a linha:** é sinalizado (`cep_valido`, `cep_prefixo_fora_12`) e classificado como E.

## 2026-11 — Pareamento CEP × logradouro (etapa 02)

- **Cascata:** tipo+nome+bairro → tipo+nome (CEP único) → nome+bairro → iniciais → fuzzy. Cada nível só trabalha o que sobrou.
- **Fuzzy:** `limiar_fuzzy` = 90; abaixo de `limiar_fuzzy_sem_bairro` = 93 só vale com bairro compatível; nomes com menos de 6 caracteres fora do fuzzy (falsos positivos).
- **Bairro x loteamento:** compatível com similaridade ≥ 85 ou igualdade após retirar palavras genéricas (VILA, JARDIM...).

## 2026-11 — Base oficial de logradouros (etapa 03)

- A base de logradouros com CEP é **a base oficial da Prefeitura**, usada também em outros projetos. Fica em `02_dados_editados` e é **editada à mão**; o pipeline nunca a sobrescreve.
- Vários CEPs no mesmo segmento ficam **na mesma coluna `cep`**, separados por `|`, para o editor deixar só o correto.
- Sugestões de CEP vão só na observação (`obs_cep`); o CEP não é preenchido sozinho.

## 2026-11 — Classificação da RAIS (etapa 05)

- Espacialização **por CEP** (não por linha): linhas dissolvidas + ponto no meio da linha (`line_interpolate_point` a 50%; se o CEP tiver partes soltas, centroide puxado para a linha mais próxima).
- **Classe A:** 1 logradouro e até 1.000 m. **Classe B:** mais de 1 logradouro ou mais de 1.000 m.
- **Ano de referência** dos rankings: o mais recente da RAIS.

## 2026-11 — Grandes usuários (etapa 04)

- CEP com sufixo ≥ 900 e prefixo 12 = grande usuário; entram os que têm vínculos em algum ano (soma 2017–2025 > 0).
- Coordenada: CNEFE primeiro (CEP+número > rua+número > CEP > rua com número mais próximo); BrasilAPI só como último recurso (coordenada aproximada, aceita só dentro da área do município).
- **CEP substituído:** consulta pelo CEP novo, ponto gravado no CEP antigo (o da RAIS). Confirmados no Busca CEP: 12237970→12238972, 12237971→12238971, 12237974→12238973, 12211970→12212970.
- Selecionados direto da RAIS (e não do diagnóstico da etapa 05) para eliminar a dependência circular entre 04 e 05.

## 2026-11 — Auditoria pelo CNEFE (etapa 07)

- **Local** = coordenada distinta do CNEFE por CEP (um prédio conta 1 voto).
- Ligação ponto → segmento mais próximo da base até **100 m**; ponto "na linha" até **60 m**.
- CEP associado **suspeito** se a mediana da distância dos seus locais aos seus segmentos passar de **200 m**.
- Sugestão exige **≥ 3 locais** e **participação ≥ 60 %**. Trechos ambíguos votam só entre os candidatos; CEPs órfãos votam **por segmento** (uma rua com vários CEPs recebe um por trecho).
- Escopo: **base inteira** (não só os CEPs da RAIS), porque a base é oficial e serve a outros projetos; os vínculos da RAIS só ordenam as listas.
- Nada é gravado na base: as sugestões ficam em `03_processamento/07_auditar_cep_cnefe` para revisão no QGIS.
