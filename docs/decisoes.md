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
- Coordenada: CNEFE primeiro (CEP+número > rua+número > CEP > rua com número mais próximo); coordenada da BrasilAPI **não é usada** (decisão de 2026-11-25: pouco confiável); a BrasilAPI serve só para o endereço.
- **CEP substituído:** consulta pelo CEP novo, ponto gravado no CEP antigo (o da RAIS). Confirmados no Busca CEP: 12237970→12238972, 12237971→12238971, 12237974→12238973, 12211970→12212970.
- Selecionados direto da RAIS (e não do diagnóstico da etapa 05) para eliminar a dependência circular entre 04 e 05.

## 2026-11 — Auditoria pelo CNEFE (etapa 07) — substituída em 2026-11-24, ver abaixo

- **Local** = coordenada distinta do CNEFE por CEP (um prédio conta 1 voto).
- Ligação ponto → segmento mais próximo da base até **100 m**; ponto "na linha" até **60 m**.
- CEP associado **suspeito** se a mediana da distância dos seus locais aos seus segmentos passar de **200 m**.
- Sugestão exige **≥ 3 locais** e **participação ≥ 60 %**. Trechos ambíguos votam só entre os candidatos; CEPs órfãos votam **por segmento** (uma rua com vários CEPs recebe um por trecho).
- Escopo: **base inteira** (não só os CEPs da RAIS), porque a base é oficial e serve a outros projetos; os vínculos da RAIS só ordenam as listas.
- Nada é gravado na base: as sugestões ficam em `03_processamento/07_auditar_cep_cnefe` para revisão no QGIS.

## 2026-11-24 — CNEFE decisivo e automático (etapa 03; etapa 07 removida)

- **Objetivo:** reduzir a edição manual ao mínimo. A base é refeita do zero; o CNEFE grava o CEP **sem aprovação manual**, com processo e confiança documentados em colunas.
- **Correios primeiro:** segmento `pareado` na etapa 02 fica com o CEP dos Correios (`cep_origem = correios_geosanja:<método>`; confiança alta no nome exato, média em iniciais/fuzzy).
- **Suspeito é trocado:** CEP pareado com ≥ 3 locais no CNEFE e mediana da distância aos seus segmentos > 200 m é retirado desses segmentos, que vão para a votação (`cnefe_motivo = cep_suspeito:...`). Com menos de 3 locais o CEP dos Correios fica.
- **Votação do CNEFE** em `multi_cep`, `ambiguo`, `sem_cep`, `sem_nome` e nos liberados por suspeita. Só votam CEPs que existem nos Correios. Vencedor = mais locais (desempate: mais endereços, menor distância média). Confiança: alta (≥ 3 locais e ≥ 60 %), média (≥ 50 % sem empate), **baixa também é gravada**.
- **Filtro de nome na ligação ponto → segmento:** nome compatível a até 60 m > sem nome a até 60 m > nome compatível a até 100 m > sem nome a até 100 m. Compatível = `token_sort_ratio` ≥ 85 ou um nome contido no outro (menor com ≥ 2 palavras). Evita voto de esquina na rua transversal.
- **Sem nome:** o nome vem do CNEFE (o mais frequente entre os locais do vencedor); original em `nome_geosanja`.
- **`multi_cep` sem pontos** mantém os CEPs dos Correios (confiança baixa); `ambiguo`/`sem_cep`/`sem_nome` sem pontos ficam vazios.
- **Classe P (etapa 05):** CEP da RAIS sem trecho na base (C, D ou E ausente dos Correios) com endereços no CNEFE ganha ponto no centro (mediana) dos endereços, puxado para o segmento mais próximo a até 100 m. Confiança pela quantidade e dispersão dos pontos (alta: ≥ 3 locais e dispersão ≤ 200 m; média: ≥ 2 e ≤ 1.000 m).
- ~~Pareados não são revotados~~ (mudado no mesmo dia, ver abaixo).
- **Regra do editado mantida:** a base em `02_dados_editados` só é criada se não existir; as edições manuais seguem tendo prioridade.

## 2026-11-24 (tarde) — CNEFE corrige os Correios e localização pelo endereço

- **CNEFE vota em todos os segmentos**, inclusive os pareados pelos Correios (o CEP dos Correios veio só pelo nome; o CNEFE tem a posição). Vencedor igual → `confirmado_cnefe`, confiança alta. Diferente com confiança alta ou média → troca (`correios_divergente:<cep dos correios>`). Diferente com confiança baixa → mantém (`correios_divergente_fraco:<cep do cnefe>`). Motivo: a JK 12220000 (“de 6001 ao fim”) tinha ido para os trechos da Vila Industrial; a etapa 02 não conhece faixas de numeração.
- **CEPs terminados em 000 não são genéricos** (Busca CEP: 12220000, 12229000, 12238000, 12234000 são de logradouro). Não há regra especial para eles.
- **Etapa 04 virou `04_localizar_ceps`**: localiza pelo endereço todo CEP da RAIS de grande usuário (com ou sem vínculos) e todo CEP sem trecho na base e sem pontos no CNEFE. Endereço: Correios → ViaCEP → BrasilAPI. Coordenada: CNEFE (CEP+número, rua+número, CEP, rua número mais próximo, rua) → Geosanja pelo nome → **Nominatim** (só aceita rua devolvida com nome compatível) → manual (coordenada da BrasilAPI descartada). Grande usuário com pontos no CNEFE pelo CEP não consulta API. **Cache em parquet** de cada API em `03_processamento/04_localizar_ceps/cache_*.parquet` (gravado a cada consulta; falha de rede não entra) e **disjuntor**: após 3 falhas seguidas o serviço é desligado na execução, a etapa avisa que não consultou tudo e a próxima execução retoma do cache (2026-11-25, após bloqueio do ViaCEP). **CEPs terminados em 000 também são alvo da 04** (muitos são CEPs reais de avenidas). Dois últimos recursos, sempre com confiança baixa e só se as APIs responderam: `cnefe_bairro` (centro dos endereços do CNEFE no mesmo loteamento do bairro) e `cnefe_cep_vizinhos` (CEPs com os mesmos 6 primeiros dígitos; não vale para sufixo 000). **CEP de outro município** (cidade devolvida pelo ViaCEP/BrasilAPI diferente de São José dos Campos; o prefixo `12` cobre o Vale todo) vira `fonte_coord = outra_cidade`: não é localizado e sai da lista manual (2026-11-25). **O CSV da 04 aceita informação manual** (2026-11-25): endereço (`fonte_endereco = manual`), `cep_novo` com vários CEPs `|` = CEP desmembrado (ponto = centro dos endereços do CNEFE dos CEPs novos; confiança média até `cnefe.dispersao_media_m`, baixa acima) e `fonte_coord = nao_localizavel`/`outra_cidade`. Leitura tolerante ao Excel (`fontes.ler_csv_editado` e `fontes.ler_coordenada`, 2026-11-25): o Excel pt-BR salvou o CSV em cp850 e trocou o decimal por separador de milhar. Casos de 25/11: 12214500 (Estrada Jaguari, Buquirinha II), 12225000 (desmembrado em 9 CEPs da Av. Presidente Tancredo Neves), 12200000 (genérico de SJC) e 12250000 (genérico de Monteiro Lobato, desativado). **CEP geral 000 com pontos no CNEFE** (ex.: 12249000, distrito de São Francisco Xavier) entra na classe P, com confiança baixa se os pontos forem espalhados.
- **Ruas homônimas:** fica a parte cujo loteamento é compatível com o bairro do endereço; sem bairro compatível, só se os pontos estiverem concentrados (≤ 1.000 m).
- **Faixa de numeração** (`de 6001/6002 ao fim`, `até 999/1000`): vira número de referência (início ou meio da faixa) para o passo "rua, número mais próximo". Faixas em km (rodovias) não geram número.
- **Classe G** passa a ser "localizado pelo endereço" (não só grande usuário). Ordem na etapa 05: A/B → P → G.
- O CSV `grande_usuario_ceps.csv` foi substituído por `ceps_localizados.csv`; linhas `manual` do antigo são trazidas na primeira execução. Ciclo = 04, 05, 06.

## 2026-11-25 — Entrega final (etapa 07)
- **Nova etapa `07_exportar_entregas`** (padrão da entrega de CNPJs): `rais_estab_espacial.gpkg` (uma camada, EPSG:4674), `rais_estab_espacial.xlsx` (uma aba por ano + legenda) e `saldo_vinculos_ativos.xlsx`. A 06 deixou de gravar `rais_estab_pontos.gpkg` (só confere os pontos e copia `ceps_espacializados.gpkg`). Ciclo = 04, 05, 06, 07.
- **Todos os registros da RAIS são mantidos.** Sem ponto = sem geometria e sem `lat`/`lon`, com `situacao_espacial = nao_localizavel`. Só há dois valores de `situacao_espacial`: o CEP de outro município pode ter sido cadastrado errado e o registro consta para São José dos Campos, então não ganha rótulo próprio (o motivo técnico fica em `motivo_cep`).
- **Colunas:** todas as da RAIS (menos `parametros.pontos.colunas_excluir`) + `linha_rais`, `situacao_espacial`, `classe_cep`, `motivo_cep`, `processo_cep`, `confianca_cep`, `ponto_metodo`, `n_partes`, `lat`, `lon`. `confianca_cep` fica nas duas entregas.
- **Saldo só anual** (a RAIS de estabelecimentos não traz admissões/desligamentos por mês): saldo do ano = soma de `qtd_vinc_ativos` (vínculos ativos em 31/12) de **todos** os registros; variação = saldo menos o do ano anterior. A etapa confere o total contra a RAIS consolidada (etapa 01) e que espacializado + nao_localizavel = total, ano a ano.

