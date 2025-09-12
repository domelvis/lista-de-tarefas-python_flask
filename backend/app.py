# app.py - Versão modernizada com API REST e melhorias

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from datetime import datetime
from models import db, Usuario, Categoria, Tarefa, Comentario

app = Flask(__name__)
app.secret_key = "sua-chave-secreta-super-segura-2025"

# ========================================
# CONFIGURAÇÃO DO BANCO POSTGRESQL
# ========================================
DB_USER = os.environ.get("DB_USER", "elvis")
DB_PASS = os.environ.get("DB_PASS", "8531")
DB_NAME = os.environ.get("DB_NAME", "northwind")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# ========================================
# INICIALIZAÇÃO DO BANCO E DADOS PADRÃO
# ========================================
def criar_dados_iniciais():
    """Criar usuário e categoria padrão se não existirem"""
    try:
        # Verificar se já existe usuário padrão
        if Usuario.query.count() == 0:
            usuario_padrao = Usuario(
                nome="Usuário Padrão", 
                email="usuario@exemplo.com"
            )
            db.session.add(usuario_padrao)
            print("✅ Usuário padrão criado")
        
        # Verificar se já existe categoria padrão
        if Categoria.query.count() == 0:
            categoria_padrao = Categoria(nome="Geral")
            db.session.add(categoria_padrao)
            print("✅ Categoria padrão criada")
        
        db.session.commit()
        print("🎉 Dados iniciais configurados com sucesso!")
        
    except Exception as erro:
        print(f"❌ Erro ao criar dados iniciais: {erro}")
        db.session.rollback()

with app.app_context():
    db.create_all()
    criar_dados_iniciais()

# ========================================
# FUNÇÃO UTILITÁRIA PARA PADRONIZAR RESPOSTAS JSON
# ========================================
def create_response(success=True, message="", data=None):
    """Criar resposta JSON padronizada"""
    return jsonify({
        "success": success,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    })

def tarefa_to_dict(tarefa):
    """Converter tarefa para dicionário JSON"""
    return {
        "id": tarefa.tarefa_id,
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao or "",
        "prioridade": tarefa.prioridade,
        "status": tarefa.status,
        "data_criacao": tarefa.data_criacao.isoformat() if tarefa.data_criacao else None,
        "usuario_id": tarefa.usuario_id,
        "categoria_id": tarefa.categoria_id
    }

# ========================================
# ROTAS TRADICIONAIS (HTML)
# ========================================
@app.route("/")
def home():
    """Página inicial - renderizar HTML"""
    print("🏠 Usuário acessou a página inicial")
    
    try:
        todas_as_tarefas = Tarefa.query.all()
        print(f"📋 Encontrei {len(todas_as_tarefas)} tarefas no banco")
        
        return render_template("index.html", tarefas=todas_as_tarefas)
        
    except Exception as erro:
        print(f"❌ Erro ao buscar tarefas: {erro}")
        flash("Erro ao carregar tarefas!", "error")
        return render_template("index.html", tarefas=[])

@app.route("/adicionar", methods=["POST"])
def adicionar_tradicional():
    """Rota tradicional para compatibilidade com forms HTML"""
    print("💾 Usuário enviou tarefa via formulário HTML tradicional")
    
    try:
        # Receber dados do formulário
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        prioridade = request.form.get("prioridade", "media")
        status = request.form.get("status", "pendente")
        
        # Validar
        if not titulo:
            flash("Título é obrigatório!", "error")
            return redirect(url_for("home"))
        
        # Buscar dados padrão
        primeiro_usuario = Usuario.query.first()
        primeira_categoria = Categoria.query.first()
        
        if not primeiro_usuario or not primeira_categoria:
            flash("Erro: dados básicos do sistema não encontrados!", "error")
            return redirect(url_for("home"))
        
        # Criar tarefa
        nova_tarefa = Tarefa(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            status=status,
            usuario_id=primeiro_usuario.id_usuario,
            categoria_id=primeira_categoria.id_categoria,
            data_criacao=datetime.now()
        )
        
        db.session.add(nova_tarefa)
        db.session.commit()
        
        flash(f"Tarefa '{titulo}' adicionada com sucesso! 🎉", "success")
        return redirect(url_for("home"))
        
    except Exception as erro:
        db.session.rollback()
        print(f"❌ Erro ao salvar tarefa: {erro}")
        flash(f"Erro ao salvar tarefa: {erro}", "error")
        return redirect(url_for("home"))

@app.route("/excluir/<int:tarefa_id>")
def excluir_tradicional(tarefa_id):
    """Rota tradicional para excluir tarefa"""
    print(f"🗑️ Excluindo tarefa ID: {tarefa_id} (rota tradicional)")
    
    try:
        tarefa = Tarefa.query.filter_by(tarefa_id=tarefa_id).first()
        
        if not tarefa:
            flash("Tarefa não encontrada!", "error")
            return redirect(url_for("home"))
        
        titulo = tarefa.titulo
        db.session.delete(tarefa)
        db.session.commit()
        
        flash(f"Tarefa '{titulo}' foi excluída! 🗑️", "success")
        return redirect(url_for("home"))
        
    except Exception as erro:
        db.session.rollback()
        print(f"❌ Erro ao excluir: {erro}")
        flash(f"Erro ao excluir tarefa: {erro}", "error")
        return redirect(url_for("home"))

# ========================================
# API REST MODERNA (JSON)
# ========================================
@app.route("/api/tarefas", methods=["GET"])
def api_listar_tarefas():
    """API: Listar todas as tarefas (JSON)"""
    print("🔗 API: Buscando tarefas...")
    
    try:
        tarefas = Tarefa.query.order_by(Tarefa.data_criacao.desc()).all()
        tarefas_json = [tarefa_to_dict(tarefa) for tarefa in tarefas]
        
        print(f"📋 API: Retornando {len(tarefas_json)} tarefas")
        return create_response(
            success=True,
            message=f"Encontradas {len(tarefas_json)} tarefas",
            data=tarefas_json
        )
        
    except Exception as erro:
        print(f"❌ API Erro ao buscar tarefas: {erro}")
        return create_response(
            success=False,
            message=f"Erro ao buscar tarefas: {str(erro)}"
        ), 500

@app.route("/api/tarefas", methods=["POST"])
def api_adicionar_tarefa():
    """API: Adicionar nova tarefa (JSON)"""
    print("💾 API: Adicionando nova tarefa...")
    
    try:
        # Verificar Content-Type
        if not request.is_json:
            return create_response(
                success=False,
                message="Content-Type deve ser application/json"
            ), 400
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        titulo = data.get("titulo", "").strip()
        if not titulo:
            return create_response(
                success=False,
                message="Título é obrigatório"
            ), 400
        
        if len(titulo) > 100:
            return create_response(
                success=False,
                message="Título deve ter no máximo 100 caracteres"
            ), 400
        
        # Dados opcionais com valores padrão
        descricao = data.get("descricao", "").strip()
        prioridade = data.get("prioridade", "media").lower()
        status = data.get("status", "pendente").lower()
        
        # Validar valores permitidos
        prioridades_validas = ["baixa", "media", "alta"]
        status_validos = ["pendente", "andamento", "concluida"]
        
        if prioridade not in prioridades_validas:
            return create_response(
                success=False,
                message=f"Prioridade deve ser: {', '.join(prioridades_validas)}"
            ), 400
        
        if status not in status_validos:
            return create_response(
                success=False,
                message=f"Status deve ser: {', '.join(status_validos)}"
            ), 400
        
        # Buscar usuário e categoria padrão
        primeiro_usuario = Usuario.query.first()
        primeira_categoria = Categoria.query.first()
        
        if not primeiro_usuario or not primeira_categoria:
            return create_response(
                success=False,
                message="Dados básicos do sistema não configurados"
            ), 500
        
        # Criar nova tarefa
        nova_tarefa = Tarefa(
            titulo=titulo,
            descricao=descricao if len(descricao) <= 500 else descricao[:500],
            prioridade=prioridade,
            status=status,
            usuario_id=primeiro_usuario.id_usuario,
            categoria_id=primeira_categoria.id_categoria,
            data_criacao=datetime.now()
        )
        
        db.session.add(nova_tarefa)
        db.session.commit()
        
        print(f"✅ API: Tarefa '{titulo}' criada com ID {nova_tarefa.tarefa_id}")
        
        return create_response(
            success=True,
            message=f"Tarefa '{titulo}' adicionada com sucesso!",
            data=tarefa_to_dict(nova_tarefa)
        ), 201
        
    except Exception as erro:
        db.session.rollback()
        print(f"❌ API Erro ao criar tarefa: {erro}")
        return create_response(
            success=False,
            message=f"Erro interno do servidor: {str(erro)}"
        ), 500

@app.route("/api/tarefas/<int:tarefa_id>", methods=["DELETE"])
def api_excluir_tarefa(tarefa_id):
    """API: Excluir tarefa por ID (JSON)"""
    print(f"🗑️ API: Excluindo tarefa ID {tarefa_id}...")
    
    try:
        tarefa = Tarefa.query.filter_by(tarefa_id=tarefa_id).first()
        
        if not tarefa:
            return create_response(
                success=False,
                message="Tarefa não encontrada"
            ), 404
        
        titulo = tarefa.titulo
        db.session.delete(tarefa)
        db.session.commit()
        
        print(f"✅ API: Tarefa '{titulo}' excluída")
        
        return create_response(
            success=True,
            message=f"Tarefa '{titulo}' excluída com sucesso!"
        )
        
    except Exception as erro:
        db.session.rollback()
        print(f"❌ API Erro ao excluir tarefa: {erro}")
        return create_response(
            success=False,
            message=f"Erro ao excluir tarefa: {str(erro)}"
        ), 500

@app.route("/api/tarefas/<int:tarefa_id>", methods=["GET"])
def api_obter_tarefa(tarefa_id):
    """API: Obter tarefa específica por ID"""
    print(f"🔍 API: Buscando tarefa ID {tarefa_id}...")
    
    try:
        tarefa = Tarefa.query.filter_by(tarefa_id=tarefa_id).first()
        
        if not tarefa:
            return create_response(
                success=False,
                message="Tarefa não encontrada"
            ), 404
        
        return create_response(
            success=True,
            message="Tarefa encontrada",
            data=tarefa_to_dict(tarefa)
        )
        
    except Exception as erro:
        print(f"❌ API Erro ao buscar tarefa: {erro}")
        return create_response(
            success=False,
            message=f"Erro ao buscar tarefa: {str(erro)}"
        ), 500

# ========================================
# ROTAS DE DEPURAÇÃO E UTILITÁRIOS
# ========================================
@app.route("/debug")
def debug():
    """Rota para debugar dados do banco"""
    try:
        usuarios = Usuario.query.all()
        categorias = Categoria.query.all()
        tarefas = Tarefa.query.all()
        
        resultado = "<h1>🔍 Debug - Dados no Banco</h1>"
        resultado += f"<p><strong>Banco:</strong> {DB_NAME} | <strong>Host:</strong> {DB_HOST}:{DB_PORT}</p>"
        
        resultado += f"<h2>👥 Usuários ({len(usuarios)})</h2><ul>"
        for u in usuarios:
            resultado += f"<li>ID: {u.id_usuario} - {u.nome} ({u.email})</li>"
        resultado += "</ul>"
        
        resultado += f"<h2>📁 Categorias ({len(categorias)})</h2><ul>"
        for c in categorias:
            resultado += f"<li>ID: {c.id_categoria} - {c.nome}</li>"
        resultado += "</ul>"
        
        resultado += f"<h2>📝 Tarefas ({len(tarefas)})</h2><ul>"
        for t in tarefas:
            resultado += f"<li>ID: {t.tarefa_id} - {t.titulo} ({t.status}) - {t.data_criacao}</li>"
        resultado += "</ul>"
        
        resultado += "<br><hr>"
        resultado += "<h3>🔗 Links Úteis:</h3><ul>"
        resultado += '<li><a href="/">← Voltar para Home</a></li>'
        resultado += '<li><a href="/api/tarefas">API: Listar Tarefas (JSON)</a></li>'
        resultado += "</ul>"
        
        return resultado
        
    except Exception as erro:
        return f"<h1>❌ Erro no Debug</h1><p>{erro}</p><a href='/'>← Voltar</a>"

@app.route("/api/status")
def api_status():
    """API: Status da aplicação"""
    try:
        total_tarefas = Tarefa.query.count()
        total_usuarios = Usuario.query.count()
        total_categorias = Categoria.query.count()
        
        return create_response(
            success=True,
            message="Sistema funcionando normalmente",
            data={
                "database": "PostgreSQL",
                "database_name": DB_NAME,
                "total_tarefas": total_tarefas,
                "total_usuarios": total_usuarios,
                "total_categorias": total_categorias,
                "server_time": datetime.now().isoformat()
            }
        )
    except Exception as erro:
        return create_response(
            success=False,
            message=f"Erro no sistema: {str(erro)}"
        ), 500

# ========================================
# TRATAMENTO DE ERROS HTTP
# ========================================
@app.errorhandler(404)
def page_not_found(e):
    """Página não encontrada"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Erro interno do servidor"""
    db.session.rollback()
    return create_response(
        success=False,
        message="Erro interno do servidor"
    ), 500

# ========================================
# INICIAR APLICAÇÃO
# ========================================
if __name__ == "__main__":
    print("🚀 Iniciando aplicação Flask...")
    print(f"📊 Home: http://localhost:5000/")
    print(f"🔍 Debug: http://localhost:5000/debug")
    print(f"📡 API Status: http://localhost:5000/api/status")
    print(f"📋 API Tarefas: http://localhost:5000/api/tarefas")
    print("=" * 50)
    
    app.run(debug=True, port=5000, host='0.0.0.0')