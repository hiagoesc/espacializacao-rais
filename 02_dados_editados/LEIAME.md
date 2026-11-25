# 02_dados_editados

Arquivos **corrigidos à mão**. O pipeline nunca os sobrescreve (só cria a versão inicial e faz backup em `_backup/`). Fora do Git.

- `logradouros_cep.gpkg` — base oficial de logradouros com CEP (camada `logradouros_cep`). Edite a coluna `cep`.
- `ceps_localizados.csv` — CEPs localizados pelo endereço na etapa 04 (grandes usuários e CEPs sem trecho). Você pode escrever nele: `lat`/`lon` + `fonte_coord = manual` (coordenada achada por você); `logradouro`/`bairro` + `fonte_endereco = manual` (endereço que as APIs não acharam; a etapa 04 localiza por ele); `cep_novo` com 1 CEP (troca) ou vários separados por `|` (CEP desmembrado); `fonte_coord = nao_localizavel` ou `outra_cidade` (CEP sem como localizar, com o motivo em `obs`). Para refazer um CEP que já tem coordenada, apague `lat` e `lon`. Pode editar no Excel: as etapas 04, 05 e 06 aceitam a codificação que ele grava (UTF-8, ANSI ou MS-DOS) e consertam o decimal que ele estraga (`-23.220.157` vira `-23.220157`); a próxima gravação da etapa 04 volta para UTF-8.
- `logradouros_cep.gpkg` é criado automaticamente pela etapa 03 (Correios + CNEFE) se não existir.
