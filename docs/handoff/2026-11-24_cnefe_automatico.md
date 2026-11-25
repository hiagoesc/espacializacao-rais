# Sessão 2026-11-24 — CNEFE decisivo e automático

- Decisão: refazer a base do zero; o CNEFE grava CEP sem aprovação manual, com processo e confiança em colunas.
- Confirmado pelo Hiago: CNEFE troca o CEP dos Correios quando a mediana passa de 200 m; confiança baixa também é aplicada; classe P (ponto pelos endereços do CNEFE) entra; mantém a regra "editado tem prioridade, senão cria do zero".
- Etapa 03 reescrita, 05 e 06 ajustadas, 07 removida, `config.yaml` (seção `cnefe`, `processamento.cnefe_locais`, ciclo 05–06), README e `decisoes.md` atualizados.
- Não rodado com dados reais (só sintaxe e testes com dados de brinquedo da votação e da classe P).
- 1ª execução: 98,3% dos estabelecimentos / 97,4% dos vínculos espacializáveis em 2025.
- Busca CEP mostrou que CEPs terminados em 000 (12220000 JK "de 6001 ao fim" etc.) são de logradouro: a etapa 02 os põe no trecho errado por não conhecer a numeração.
- Confirmado pelo Hiago: CNEFE corrige também o CEP dos Correios (só com confiança alta/média); etapa 04 localiza pelo endereço tudo o que sobrar (Nominatim já usado no projeto CNPJ); coordenada de API/manual só em último caso.
