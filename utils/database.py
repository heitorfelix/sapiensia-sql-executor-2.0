import pyodbc
from pyodbc import ProgrammingError


class QueryError(Exception):
    pass

class Conexao:

    def __init__(self, server, database = 'master', user = None, password = None):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        
    def test_azure_connection(self):
        if self.user != '' and self.password != '':
            conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={self.server};DATABASE={self.database};UID={self.user};PWD={self.password};"
            )
            
        elif self.user == '' and self.password == '':
            conn_str = 'DRIVER={SQL Server Native Client 11.0};SERVER='+self.server+';DATABASE='+self.database+';Trusted_Connection=yes;'

        else:
            raise NameError("Missing crendentials")
        try:
            with pyodbc.connect(conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT @@SERVERNAME")
                cursor.fetchone()
                
            self.conn_str = conn_str
            print('Conexão estabelecida')
            return True
        
        except pyodbc.Error as e:
            print('Conexão não funcionou')
            return False

    def list_databases(self):

        query = """select [name] 
        from sys.databases
        where name not in ('master','tempdb','model','msdb')
        order by [name]"""

        try:
            with pyodbc.connect(self.conn_str) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                results = [result[0] for result in results]
                
            return results 
        
        except Exception as e:
            print(str(e))
    
    def execute_ddl(self, database, query):

        # Estabelecer a conexão com o banco
        conn_str = self.conn_str.replace(self.database, database)
        conn = pyodbc.connect(conn_str)
        
        # Executar a consulta para obter o nome do banco
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")

        # Obter o nome do banco
        db_name = cursor.fetchone()[0]
        
        try:
            # Executar a consulta principal
            cursor.execute(query)
            cursor.commit()

            # Obter o resultado da consulta
            result = 'Executado com sucesso'
           
        except ProgrammingError as e:
            result = str(e)
            
        # Fechar a conexão com o banco
        conn.close()

        # Retornar o nome do banco e o resultado da consulta
        return db_name, result
    
    

    def execute_query(self, database, query):

        # Estabelecer a conexão com o banco
        conn_str = self.conn_str.replace(self.database, database)
        conn = pyodbc.connect(conn_str)
        
        # Executar a consulta para obter o nome do banco
        cursor = conn.cursor()
        cursor.execute("SELECT DB_NAME()")

        # Obter o nome do banco
        db_name = cursor.fetchone()[0]
        
        try:
            # Executar a consulta principal
            cursor.execute(query)
            
            # Obter as colunas do resultado
            self.columns = [column[0] for column in cursor.description]
            
            # Obter as linhas do resultado
            rows = cursor.fetchall()

            # Montar a lista de tuplas com o nome do banco e o resultado
            result = [(db_name,) + tuple(row) for row in rows]

        except ProgrammingError as e:
            result = "Error: " + str(e)
            
        # Fechar a conexão com o banco
        conn.close()
        return result
