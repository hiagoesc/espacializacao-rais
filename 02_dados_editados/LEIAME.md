# 02_dados_editados

Arquivos **corrigidos à mão**. O pipeline nunca os sobrescreve (só cria a versão inicial e faz backup em `_backup/`). Fora do Git.

- `logradouros_cep.gpkg` — base oficial de logradouros com CEP (camada `logradouros_cep`). Edite a coluna `cep`.
- `grande_usuario_ceps.csv` — CEPs de grande usuário com coordenada. Edite `lat`, `lon`, `fonte_coord`, `cep_novo`.
