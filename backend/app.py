# app.py - Sistema Completo de Lista de Tarefas com CRUD

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
        if Usuario.query.count() == 0:
            usuario_padrao = Usuario(
                nome="Usuário Padrão", 
                email="usuario@exemplo.com"
            )
            db.session.add(usuario_padrao)
            print("✅ Usuário padrão criado")
        
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
# FUNÇÕES UTILITÁRIAS
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

def validar_dados_tarefa(titulo, prioridade, status):
    """Validar dados da tarefa"""
    erros = []
    
    if not titulo or len(titulo.strip()) < 3:
        erros.append("Título deve ter pelo menos 3 caracteres")
    
    if len(titulo) > 100:
        erros.append("Título deve ter no máximo 100 caracteres")
    
    prioridades_validas = ["baixa", "media", "alta"]
    if prioridade not in prioridades_validas:
        erros.append(f"Prioridade deve ser: {', '.join(prioridades_validas)}")
    
    status_validos = ["pendente", "andamento", "concluida"]
    if status not in status_validos:
        erros.append(f"Status deve ser: {', '.join(status_validos)}")
    
    return erros

# ========================================
# ROTAS PRINCIPAIS (HTML)
# ========================================
@app.route("/")
def home():
    """Página inicial - renderizar HTML"""
    print("🏠 Usuário acessou a página inicial")
    
    try:
        todas_as_tarefas = Tarefa.query.order_by(Tarefa.data_criacao.desc()).all()
        print(f"📋 Encontrei {len(todas_as_tarefas)} tarefas no banco")
        
        return render_template("index.html", tarefas=todas_as_tarefas)
        
    except Exception as erro:
        print(f"❌ Erro ao buscar tarefas: {erro}")
        flash("Erro ao carregar tarefas!", "error")
        return render_template("index.html", tarefas=[])

@app.route("/adicionar", methods=["POST"])
def adicionar_tarefa():
    """Adicionar nova tarefa"""
    print("💾 Usuário enviou nova tarefa")
    
    try:
        # Receber dados do formulário
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        prioridade = request.form.get("prioridade", "media").lower()
        status = request.form.get("status", "pendente").lower()
        
        # Validar dados
        erros = validar_dados_tarefa(titulo, prioridade, status)
        if erros:
            for erro in erros:
                flash(erro, "error")
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
            descricao=descricao if len(descricao) <= 500 else descricao[:500],
            prioridade=prioridade,
            status=status,
            usuario_id=primeiro_usuario.id_usuario,
            categoria_id=primeira_categoria.id_categoria,
            data_criacao=datetime.now(),
            data_atualizacao=datetime.now()
        )
        
        db.session.add(nova_tarefa)
        db.session.commit()
        
        print(f"✅ Tarefa '{titulo}' criada com ID {nova_tarefa.tarefa_id}")
        flash(f"Tarefa '{titulo}' adicionada com sucesso!", "success")
        return redirect(url_for("home"))
        
    except Exception as erro:
        db.session.rollback()
        print(f"❌ Erro ao salvar tarefa: {erro}")
        flash(f"Erro ao salvar tarefa: {str(erro)}", "error")
        return redirect(url_for("home"))

@app.route("/editar/<int:tarefa_id>", methods=["POST"])
def editar_tarefa(tarefa_id):
    """Editar tarefa existente"""
    print(f"✏️ Editando tarefa ID: {tarefa_id}")
    
    try:
        # Buscar a tarefa no banco
        tarefa = Tarefa.query.filter_by(tarefa_id=tarefa_id).first()
        
        if not tarefa:
            flash("Tarefa não encontrada!", "error")
            return redirect(url_for("home"))
        
        # Receber dados do formulário
        titulo = request.form.get("titulo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        prioridade = request.form.get("prioridade", "media").lower()
        status = request.form.get("status", "pendente").lower()
        
        # Validar dados
        erros = validar_dados_tarefa(titulo, prioridade, status)
        if erros:
            for erro in erros:
                flash(erro, "error")
            return redirect(url_for("home"))
        
        # Atualizar os dados da tarefa
        titulo_antigo = tarefa.titulo
        tarefa.titulo = titulo
        tarefa.descricao = descricao if len(descricao) <= 500 else descricao[:500]
        tarefa.prioridade = prioridade
        tarefa.status = status
        tarefa.data_atualizacao = datetime.now()
        
        # Salvar no banco
        db.session.commit()
        
        print(f"✅ Tarefa '{titulo_antigo}' atualizada para '{titulo}'")
        flash(f"Tarefa '{titulo}' foi atualizada com sucesso!", "success")
        
        return redirect(url_for("home"))
        
    except Exception as erro:
        db.session.rollback()
        print(f"❌ Erro ao editar tarefa: {erro}")
        flash(f"Erro ao editar tarefa: {str(erro)}", "error")
        return redirect(url_for("home"))

@app.route("/excluir/<int:tarefa_id>")
def excluir_tarefa(tarefa_id):
    """Excluir tarefa"""
    print(f"🗑️ Excluindo tarefa ID: {tarefa_id}")
    
    try:
        tarefa = Tarefa.query.filter_by(tarefa_id=tarefa_id).first()
        
        if not tarefa:
            flash("Tarefa não encontrada!", "error")
            return redirect(url_for("home"))
        
        titulo = tarefa.titulo
        db.session.delete(tarefa)
        db.session.commit()
        
        print(f"✅ Tarefa '{titulo}' excluída")
        flash(f"Tarefa '{titulo}' foi excluída!", "success")
        return redirect(url_for("home"))
        
    except Exception as erro:
        db.session.rollback()
        print(f"❌ Erro ao excluir: {erro}")
        flash(f"Erro ao excluir tarefa: {str(erro)}", "error")
        return redirect(url_for("home"))

# ========================================
# API REST (JSON)
# ========================================
@app.route("/api/tarefas", methods=["GET"])
def api_listar_tarefas():
    """API: Listar todas as tarefas"""
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
    """API: Adicionar nova tarefa"""
    print("💾 API: Adicionando nova tarefa...")
    
    try:
        if not request.is_json:
            return create_response(
                success=False,
                message="Content-Type deve ser application/json"
            ), 400
        
        data = request.get_json()
        
        titulo = data.get("titulo", "").strip()
        descricao = data.get("descricao", "").strip()
        prioridade = data.get("prioridade", "media").lower()
        status = data.get("status", "pendente").lower()
        
        # Validar dados
        erros = validar_dados_tarefa(titulo, prioridade, status)
        if erros:
            return create_response(
                success=False,
                message="; ".join(erros)
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
            data_criacao=datetime.now(),
            data_atualizacao=datetime.now()
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

@app.route("/api/tarefas/<int:tarefa_id>", methods=["GET"])
def api_obter_tarefa(tarefa_id):
    """API: Obter tarefa específica por ID"""
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
        return create_response(
            success=False,
            message=f"Erro ao buscar tarefa: {str(erro)}"
        ), 500

@app.route("/api/tarefas/<int:tarefa_id>", methods=["PUT"])
def api_editar_tarefa(tarefa_id):
    """API: Editar tarefa"""
    try:
        if not request.is_json:
            return create_response(
                success=False,
                message="Content-Type deve ser application/json"
            ), 400
        
        tarefa = Tarefa.query.filter_by(tarefa_id=tarefa_id).first()
        if not tarefa:
            return create_response(
                success=False,
                message="Tarefa não encontrada"
            ), 404
        
        data = request.get_json()
        
        titulo = data.get("titulo", tarefa.titulo).strip()
        descricao = data.get("descricao", tarefa.descricao or "").strip()
        prioridade = data.get("prioridade", tarefa.prioridade).lower()
        status = data.get("status", tarefa.status).lower()
        
        # Validar dados
        erros = validar_dados_tarefa(titulo, prioridade, status)
        if erros:
            return create_response(
                success=False,
                message="; ".join(erros)
            ), 400
        
        # Atualizar tarefa
        tarefa.titulo = titulo
        tarefa.descricao = descricao if len(descricao) <= 500 else descricao[:500]
        tarefa.prioridade = prioridade
        tarefa.status = status
        tarefa.data_atualizacao = datetime.now()
        
        db.session.commit()
        
        return create_response(
            success=True,
            message=f"Tarefa '{titulo}' atualizada com sucesso!",
            data=tarefa_to_dict(tarefa)
        )
        
    except Exception as erro:
        db.session.rollback()
        return create_response(
            success=False,
            message=f"Erro ao editar tarefa: {str(erro)}"
        ), 500

@app.route("/api/tarefas/<int:tarefa_id>", methods=["DELETE"])
def api_excluir_tarefa(tarefa_id):
    """API: Excluir tarefa"""
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
        
        return create_response(
            success=True,
            message=f"Tarefa '{titulo}' excluída com sucesso!"
        )
        
    except Exception as erro:
        db.session.rollback()
        return create_response(
            success=False,
            message=f"Erro ao excluir tarefa: {str(erro)}"
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
            resultado += f"<li>ID: {t.tarefa_id} - {t.titulo} ({t.status}) - {t.prioridade} - {t.data_criacao}</li>"
        resultado += "</ul>"
        
        resultado += "<br><hr>"
        resultado += "<h3>🔗 Links Úteis:</h3><ul>"
        resultado += '<li><a href="/">← Voltar para Home</a></li>'
        resultado += '<li><a href="/api/tarefas">API: Listar Tarefas (JSON)</a></li>'
        resultado += '<li><a href="/api/status">API: Status do Sistema</a></li>'
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
        
        # Estatísticas por status
        stats_status = {
            'pendente': Tarefa.query.filter_by(status='pendente').count(),
            'andamento': Tarefa.query.filter_by(status='andamento').count(),
            'concluida': Tarefa.query.filter_by(status='concluida').count()
        }
        
        # Estatísticas por prioridade
        stats_prioridade = {
            'baixa': Tarefa.query.filter_by(prioridade='baixa').count(),
            'media': Tarefa.query.filter_by(prioridade='media').count(),
            'alta': Tarefa.query.filter_by(prioridade='alta').count()
        }
        
        return create_response(
            success=True,
            message="Sistema funcionando normalmente",
            data={
                "database": "PostgreSQL",
                "database_name": DB_NAME,
                "total_tarefas": total_tarefas,
                "total_usuarios": total_usuarios,
                "total_categorias": total_categorias,
                "estatisticas_status": stats_status,
                "estatisticas_prioridade": stats_prioridade,
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