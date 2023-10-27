# BackupSQLServer

`BackupSQLServer` é uma classe Python que permite realizar backups de bancos de dados SQL Server e monitorar o progresso do backup em tempo real.


## Funcionalidades

- **Backup do Banco de Dados:**

  ```python
  backup.iniciar_backup_e_monitoramento()
  ```

  Inicia o backup do banco de dados e monitora o progresso em tempo real.

- **Configuração Personalizada:**

  Personalize o caminho de backup, prefixo de arquivo e opções de compressão conforme necessário.

- **Autenticação:**

  Suporta autenticação do Windows ou autenticação SQL com nome de usuário e senha.

- **Monitoramento em Tempo Real:**

  Monitora o progresso do backup em tempo real e exibe a porcentagem concluída.

## Exemplo de Uso

```python
import classeBackup

servidor = 'SeuServidor'
banco_de_dados = 'SeuBancoDeDados'
autenticacao_windows = True # Ou False se estiver usando autenticação SQL
usuario = '' if autenticacao_windows else 'seu_usuario' # Usuario Autenticação do SQL Server
senha = '' if autenticacao_windows else 'sua_senha' # Senha Autenticação do SQL Server

backup = classeBackup.BackupSQLServer(servidor, banco_de_dados, autenticacao_windows, usuario, senha)
backup.iniciar_backup_e_monitoramento()
```

*Lembre-se de substituir `'SeuServidor'`, `'SeuBancoDeDados'`, `'SeuUsuario'`, `'SuaSenha'` pelos valores apropriados.*
