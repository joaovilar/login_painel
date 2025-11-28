
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do Banco de Dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'sistema_combatentes'),
    'auth_plugin': 'mysql_native_password'
}

# Configurações da Aplicação
SECRET_KEY = os.getenv('SECRET_KEY', 'chave_super_secreta_padrao_mude_em_producao')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

def conectar_mysql():
    """
    Função para conectar ao MySQL
    Retorna a conexão ou None em caso de erro
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Conexão com MySQL estabelecida")
        return conn
    except Error as e:
        print(f"Erro na conexão com MySQL: {e}")
        return None

# Validação opcional 
def validar_configuracao():
    print("🔧 Configurações carregadas:")
    print(f"   DB_HOST: {DB_CONFIG['host']}")
    print(f"   DB_USER: {DB_CONFIG['user']}")
    print(f"   DB_NAME: {DB_CONFIG['database']}")

# Executa a validação ao importar
validar_configuracao()