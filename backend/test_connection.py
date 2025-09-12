import os
import psycopg2
from sqlalchemy import create_engine, text

print("🔍 Testando conexão com PostgreSQL...")
print("=" * 50)

# Suas configurações (mesmas do app.py)
DB_USER = os.environ.get("DB_USER", "elvis")
DB_PASS = os.environ.get("DB_PASS", "8531")
DB_NAME = os.environ.get("DB_NAME", "northwind")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

print(f"📊 Configurações:")
print(f"   Usuário: {DB_USER}")
print(f"   Senha: {'*' * len(DB_PASS)}")
print(f"   Banco: {DB_NAME}")
print(f"   Host: {DB_HOST}")
print(f"   Porta: {DB_PORT}")
print()

# Teste 1: Conexão básica com psycopg2
print("🧪 Teste 1: Conexão básica com psycopg2")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    print("✅ Conexão psycopg2: SUCESSO!")
    conn.close()
except Exception as e:
    print(f"❌ Conexão psycopg2: FALHOU - {e}")
    print()
    print("🔧 Possíveis soluções:")
    print("   1. Verifique se o PostgreSQL está rodando")
    print("   2. Confirme usuário e senha")
    print("   3. Verifique se o banco 'northwind' existe")
    print("   4. Teste no pgAdmin primeiro")
    exit(1)

print()

# Teste 2: Conexão com SQLAlchemy
print("🧪 Teste 2: Conexão com SQLAlchemy")
try:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ SQLAlchemy: SUCESSO!")
        print(f"   PostgreSQL: {version}")
        
except Exception as e:
    print(f"❌ SQLAlchemy: FALHOU - {e}")
    exit(1)

print()

# Teste 3: Verificar se as tabelas existem
print("🧪 Teste 3: Verificando tabelas existentes")
try:
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tabelas = [row[0] for row in result]
        
        if tabelas:
            print(f"✅ Encontrei {len(tabelas)} tabelas:")
            for tabela in tabelas:
                print(f"   - {tabela}")
        else:
            print("⚠️  Nenhuma tabela encontrada no banco")
            print("   Você precisa executar o script de criação das tabelas")
            
except Exception as e:
    print(f"❌ Erro ao listar tabelas: {e}")

print()

# Teste 4: Verificar tabelas específicas do projeto
print("🧪 Teste 4: Verificando tabelas do projeto")
tabelas_necessarias = ['usuarios', 'categorias', 'tarefas', 'comentarios']

for tabela in tabelas_necessarias:
    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
            count = result.fetchone()[0]
            print(f"   ✅ {tabela}: {count} registros")
    except Exception as e:
        print(f"   ❌ {tabela}: NÃO EXISTE - {e}")

print()
print("🎯 RESULTADO:")
print("   Se todos os testes passaram, o Flask deveria funcionar!")
print("   Se algum falhou, resolva primeiro antes de rodar o Flask.")
print()
print("📝 Para rodar o Flask: python app.py")