import classeBackup

servidor = 'SeuServidor'
banco_de_dados = 'SeuBancoDeDados'
autenticacao_windows = True
usuario = '' if autenticacao_windows else 'seu_usuario'
senha = '' if autenticacao_windows else 'sua_senha'

backup = classeBackup.BackupSQLServer(servidor, banco_de_dados, autenticacao_windows, usuario, senha)
backup.iniciar_backup_e_monitoramento()
