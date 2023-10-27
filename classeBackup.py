import pyodbc
import os
import datetime
import zipfile
import threading
import subprocess
import time

class BackupSQLServer:
    def __init__(self, servidor, banco_de_dados, autenticacao_windows, usuario=None, senha=None,
                 caminho_backup='C:\\BACKUP\\', prefixo_arquivo_backup='backup_teste',
                 compressao=True):
        self.servidor = servidor
        self.banco_de_dados = banco_de_dados
        self.autenticacao_windows = autenticacao_windows
        self.usuario = usuario
        self.senha = senha
        self.caminho_backup = caminho_backup
        self.prefixo_arquivo_backup = prefixo_arquivo_backup
        self.compressao = compressao
        self.backup_em_andamento = False
        self.tamanho_total_do_banco_de_dados = 0
        self.thread_monitoramento = None

    def _obter_nome_arquivo_backup(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{self.prefixo_arquivo_backup}{timestamp}.bak'

    def _obter_tamanho_arquivo(self, caminho_arquivo):
        return os.path.getsize(caminho_arquivo)

    def _iniciar_monitoramento_eventos(self):
        caminho_log_eventos = 'C:\\Caminho\\Para\\Seu\\Log\\backup_progress.xel'
        comando_eventos = f'sqlcmd -S {self.servidor} -d {self.banco_de_dados} -Q "CREATE EVENT SESSION BackupProgress ON SERVER ADD EVENT sqlserver.backup_restore_progress_reported (ACTION(sqlserver.database_id, sqlserver.session_id, sqlserver.sql_text)) ADD TARGET package0.event_file (SET filename=N\'{caminho_log_eventos}\')"'
        subprocess.run(comando_eventos, shell=True)

    def _monitorar_progresso_backup(self):
        caminho_arquivo_backup = os.path.join(self.caminho_backup, self._obter_nome_arquivo_backup())

        while self.backup_em_andamento:
            tamanho_atual = self._obter_tamanho_arquivo(caminho_arquivo_backup)
            porcentagem_progresso = (tamanho_atual / self.tamanho_total_do_banco_de_dados) * 100
            print(f'Progresso do backup: {porcentagem_progresso:.2f}%')
            time.sleep(1)  # Aguarda 1 segundo antes de verificar novamente

    def _executar_comando_backup(self, nome_arquivo_backup):
        if self.autenticacao_windows:
            conn = pyodbc.connect(
                f'DRIVER={{SQL Server}};SERVER={self.servidor};DATABASE={self.banco_de_dados};Trusted_Connection=yes')
        else:
            conn = pyodbc.connect(
                f'DRIVER={{SQL Server}};SERVER={self.servidor};DATABASE={self.banco_de_dados};UID={self.usuario};PWD={self.senha}')

        cursor = conn.cursor()
        try:
            # Verificar se há transações pendentes e, se houver, fazer um commit para encerrá-las
            cursor.execute("IF @@TRANCOUNT > 0 COMMIT")

            # Executar o comando de backup
            cursor.execute(
                f'BACKUP DATABASE {self.banco_de_dados} TO DISK=\'{os.path.join(self.caminho_backup, nome_arquivo_backup)}\'')
            conn.commit()
            print(f'BACKUP DATABASE {self.banco_de_dados} TO DISK=\'{os.path.join(self.caminho_backup, nome_arquivo_backup)}\'')
            print(f'Backup do banco de dados {self.banco_de_dados} realizado com sucesso.')
            self.backup_em_andamento = True
        except Exception as e:
            print(f'Ocorreu um erro durante o backup: {str(e)}')
            self.backup_em_andamento = False
        finally:
            cursor.close()
            conn.close()

    def _compactar_backup(self, nome_arquivo_backup):
        # Nome do arquivo ZIP
        arquivo_zip = f'{os.path.join(self.caminho_backup, nome_arquivo_backup)}.zip'

        # Criar um arquivo ZIP e adicionar o arquivo de backup a ele
        with zipfile.ZipFile(arquivo_zip, 'w') as zipf:
            zipf.write(os.path.join(self.caminho_backup, f"{nome_arquivo_backup}.zip"), os.path.basename(nome_arquivo_backup))

        print(f'Backup compactado em {arquivo_zip}')

    def _calcular_tamanho_total_banco_de_dados(self):
        conn = pyodbc.connect(
            f'DRIVER={{SQL Server}};SERVER={self.servidor};DATABASE={self.banco_de_dados};Trusted_Connection=yes')
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"SELECT SUM(size * 8 / 1024) AS TamanhoTotalMB FROM sys.master_files WHERE database_id = DB_ID('{self.banco_de_dados}')")
            resultado = cursor.fetchone()
            if resultado and resultado.TamanhoTotalMB:
                return resultado.TamanhoTotalMB
            else:
                raise Exception("Não foi possível obter o tamanho total do banco de dados.")
        except Exception as e:
            print(f"Erro ao calcular o tamanho total do banco de dados: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def salvar_arquivo_no_caminho(self, arquivo, caminho):
        # Verifica se o caminho existe, se não existir, cria a pasta
        if not os.path.exists(caminho):
            os.makedirs(caminho)

        # Obtém o caminho completo para o arquivo no diretório especificado
        caminho_completo = os.path.join(caminho, arquivo)

        # Salva o arquivo no caminho completo
        with open(caminho_completo, 'w') as f:
            f.write("Conteúdo do arquivo")

        print(f'Arquivo {arquivo} salvo em {caminho_completo}')

    def iniciar_backup_e_monitoramento(self):
        # Configurar o monitoramento de eventos em uma thread separada
        if self.autenticacao_windows:
            self._iniciar_monitoramento_eventos()
            self.tamanho_total_do_banco_de_dados = self._calcular_tamanho_total_banco_de_dados()
            self.backup_em_andamento = True
            self.thread_monitoramento = threading.Thread(target=self._monitorar_progresso_backup)
            self.thread_monitoramento.start()

        nome_arquivo_backup = self._obter_nome_arquivo_backup()
        self._executar_comando_backup(nome_arquivo_backup)

        # Compactar o backup em um arquivo ZIP
        if self.compressao and self.backup_em_andamento:
            self._compactar_backup(nome_arquivo_backup)

        # Salvar o arquivo de backup no caminho especificado
        caminho_do_arquivo = 'C:\\MinhaPasta'
        self.salvar_arquivo_no_caminho(nome_arquivo_backup, caminho_do_arquivo)
