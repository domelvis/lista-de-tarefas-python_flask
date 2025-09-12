-- SCRIPT PARA CORRIGIR PERMISSÕES DO POSTGRESQL
-- Execute este script no pgAdmin como ADMINISTRADOR

-- 1. CONECTAR COMO SUPERUSUÁRIO (postgres)
-- Abra o pgAdmin e conecte com usuário 'postgres'

-- 2. VERIFICAR SE O USUÁRIO 'elvis' EXISTE
SELECT usename FROM pg_user WHERE usename = 'elvis';

-- 3. SE NÃO EXISTIR, CRIAR O USUÁRIO
-- (Descomente se necessário)
-- CREATE USER elvis WITH PASSWORD '8531';

-- 4. DAR PERMISSÕES COMPLETAS AO USUÁRIO 'elvis' NO BANCO 'northwind'
GRANT ALL PRIVILEGES ON DATABASE northwind TO elvis;

-- 5. CONECTAR AO BANCO 'northwind' ESPECIFICAMENTE
\c northwind;

-- 6. DAR PERMISSÕES NO SCHEMA PUBLIC
GRANT ALL PRIVILEGES ON SCHEMA public TO elvis;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO elvis;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO elvis;

-- 7. PERMITIR CRIAÇÃO DE TABELAS FUTURAS
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO elvis;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO elvis;

-- 8. VERIFICAR AS PERMISSÕES
SELECT 
    schemaname,
    tablename,
    tableowner,
    hasinsert,
    hasselect,
    hasupdate,
    hasdelete
FROM pg_tables 
WHERE schemaname = 'public';

-- 9. MOSTRAR RESULTADO
SELECT 'Permissões corrigidas para usuário elvis! ✅' as resultado;