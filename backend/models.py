# models.py - Modelos atualizados e compatíveis com o banco PostgreSQL

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ========================================
# MODELO: USUARIOS
# ========================================
class Usuario(db.Model):
    __tablename__ = "usuarios"
    
    # Campos
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=True)  # Para futuro sistema de login
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    data_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    tarefas = db.relationship(
        "Tarefa",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="Tarefa.usuario_id"
    )
    
    projetos_responsavel = db.relationship(
        "Projeto",
        backref="responsavel",
        lazy=True,
        foreign_keys="Projeto.responsavel_id"
    )
    
    comentarios = db.relationship(
        "Comentario",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    anexos = db.relationship(
        "Anexo",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    # Métodos
    def __repr__(self):
        return f"<Usuario {self.nome} ({self.email})>"
    
    def to_dict(self):
        """Converter para dicionário (útil para JSON)"""
        return {
            'id_usuario': self.id_usuario,
            'nome': self.nome,
            'email': self.email,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'total_tarefas': len(self.tarefas) if self.tarefas else 0
        }

# ========================================
# MODELO: CATEGORIAS
# ========================================
class Categoria(db.Model):
    __tablename__ = "categorias"
    
    # Campos
    id_categoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    cor = db.Column(db.String(7), default="#6366f1")  # Cor hex
    icone = db.Column(db.String(50), default="📁")
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    tarefas = db.relationship(
        "Tarefa",
        backref="categoria",
        lazy=True
        # Não usar cascade aqui - categoria não deve ser deletada se houver tarefas
    )
    
    # Métodos
    def __repr__(self):
        return f"<Categoria {self.nome}>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id_categoria': self.id_categoria,
            'nome': self.nome,
            'descricao': self.descricao,
            'cor': self.cor,
            'icone': self.icone,
            'ativo': self.ativo,
            'total_tarefas': len(self.tarefas) if self.tarefas else 0
        }

# ========================================
# MODELO: PROJETOS
# ========================================
class Projeto(db.Model):
    __tablename__ = "projetos"
    
    # Campos
    id_projeto = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data_inicio = db.Column(db.Date, nullable=True)
    data_fim_prevista = db.Column(db.Date, nullable=True)
    data_fim_real = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="ativo")  # ativo, pausado, concluido, cancelado
    prioridade = db.Column(db.String(10), default="media")  # baixa, media, alta, critica
    progresso = db.Column(db.Integer, default=0)  # 0-100%
    responsavel_id = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=True)
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    data_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relacionamentos
    tarefas = db.relationship(
        "Tarefa",
        backref="projeto",
        lazy=True,
        foreign_keys="Tarefa.projeto_id"
    )
    
    # Métodos
    def __repr__(self):
        return f"<Projeto {self.nome} ({self.status})>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id_projeto': self.id_projeto,
            'nome': self.nome,
            'descricao': self.descricao,
            'status': self.status,
            'prioridade': self.prioridade,
            'progresso': self.progresso,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim_prevista': self.data_fim_prevista.isoformat() if self.data_fim_prevista else None,
            'responsavel_nome': self.responsavel.nome if self.responsavel else None,
            'total_tarefas': len(self.tarefas) if self.tarefas else 0
        }

# ========================================
# MODELO: TAREFAS (Principal)
# ========================================
class Tarefa(db.Model):
    __tablename__ = "tarefas"
    
    # Campos
    tarefa_id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="pendente")  # pendente, andamento, concluida, cancelada
    prioridade = db.Column(db.String(10), default="media")  # baixa, media, alta, critica
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    data_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_conclusao = db.Column(db.DateTime, nullable=True)
    data_vencimento = db.Column(db.Date, nullable=True)
    estimativa_horas = db.Column(db.Numeric(5, 2), nullable=True)
    horas_trabalhadas = db.Column(db.Numeric(5, 2), default=0)
    progresso = db.Column(db.Integer, default=0)  # 0-100%
    
    # Foreign Keys
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id_categoria"), nullable=False)
    projeto_id = db.Column(db.Integer, db.ForeignKey("projetos.id_projeto"), nullable=True)
    tarefa_pai_id = db.Column(db.Integer, db.ForeignKey("tarefas.tarefa_id"), nullable=True)
    
    # Relacionamentos
    comentarios = db.relationship(
        "Comentario",
        backref="tarefa",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="Comentario.tarefa_id"
    )
    
    anexos = db.relationship(
        "Anexo",
        backref="tarefa",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
    # Relacionamento para subtarefas
    subtarefas = db.relationship(
        "Tarefa",
        backref=db.backref("tarefa_pai", remote_side="Tarefa.tarefa_id"),
        lazy=True
    )
    
    # Métodos
    def __repr__(self):
        return f"<Tarefa {self.titulo} ({self.status})>"
    
    def to_dict(self):
        """Converter para dicionário (compatível com API)"""
        return {
            'id': self.tarefa_id,  # Para compatibilidade com JavaScript
            'tarefa_id': self.tarefa_id,  # Para compatibilidade com código existente
            'titulo': self.titulo,
            'descricao': self.descricao or "",
            'status': self.status,
            'prioridade': self.prioridade,
            'progresso': self.progresso,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'estimativa_horas': float(self.estimativa_horas) if self.estimativa_horas else None,
            'horas_trabalhadas': float(self.horas_trabalhadas) if self.horas_trabalhadas else 0,
            'usuario_id': self.usuario_id,
            'categoria_id': self.categoria_id,
            'projeto_id': self.projeto_id,
            'usuario_nome': self.usuario.nome if self.usuario else None,
            'categoria_nome': self.categoria.nome if self.categoria else None,
            'projeto_nome': self.projeto.nome if self.projeto else None,
            'total_comentarios': len(self.comentarios) if self.comentarios else 0,
            'total_anexos': len(self.anexos) if self.anexos else 0
        }
    
    @property
    def is_vencida(self):
        """Verificar se a tarefa está vencida"""
        if self.data_vencimento and self.status not in ['concluida', 'cancelada']:
            return datetime.now().date() > self.data_vencimento
        return False
    
    @property
    def dias_para_vencimento(self):
        """Calcular dias para vencimento"""
        if self.data_vencimento:
            delta = self.data_vencimento - datetime.now().date()
            return delta.days
        return None

# ========================================
# MODELO: COMENTARIOS
# ========================================
class Comentario(db.Model):
    __tablename__ = "comentarios"
    
    # Campos
    id_comentario = db.Column(db.Integer, primary_key=True)
    comentario = db.Column(db.Text, nullable=False)  # Campo correto conforme BD
    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    data_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    tipo = db.Column(db.String(20), default="comentario")  # comentario, nota, log, alteracao
    privado = db.Column(db.Boolean, default=False)
    
    # Foreign Keys
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey("tarefas.tarefa_id"), nullable=False)
    comentario_pai_id = db.Column(db.Integer, db.ForeignKey("comentarios.id_comentario"), nullable=True)
    
    # Relacionamento para respostas
    respostas = db.relationship(
        "Comentario",
        backref=db.backref("comentario_pai", remote_side="Comentario.id_comentario"),
        lazy=True
    )
    
    # Métodos
    def __repr__(self):
        return f"<Comentario {self.id_comentario} - Tarefa {self.tarefa_id}>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id_comentario': self.id_comentario,
            'comentario': self.comentario,
            'tipo': self.tipo,
            'privado': self.privado,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'usuario_nome': self.usuario.nome if self.usuario else None,
            'tarefa_id': self.tarefa_id,
            'comentario_pai_id': self.comentario_pai_id,
            'total_respostas': len(self.respostas) if self.respostas else 0
        }

# ========================================
# MODELO: ANEXOS
# ========================================
class Anexo(db.Model):
    __tablename__ = "anexos"
    
    # Campos
    id_anexo = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    nome_original = db.Column(db.String(255), nullable=False)
    tipo_mime = db.Column(db.String(100), nullable=True)
    tamanho_bytes = db.Column(db.BigInteger, nullable=True)
    caminho_arquivo = db.Column(db.Text, nullable=False)
    data_upload = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    ativo = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    tarefa_id = db.Column(db.Integer, db.ForeignKey("tarefas.tarefa_id"), nullable=False)
    
    # Métodos
    def __repr__(self):
        return f"<Anexo {self.nome_original}>"
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id_anexo': self.id_anexo,
            'nome_arquivo': self.nome_arquivo,
            'nome_original': self.nome_original,
            'tipo_mime': self.tipo_mime,
            'tamanho_bytes': self.tamanho_bytes,
            'tamanho_legivel': self.tamanho_legivel,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None,
            'usuario_nome': self.usuario.nome if self.usuario else None,
            'tarefa_id': self.tarefa_id,
            'ativo': self.ativo
        }
    
    @property
    def tamanho_legivel(self):
        """Converter bytes para formato legível"""
        if not self.tamanho_bytes:
            return "0 B"
        
        for unidade in ['B', 'KB', 'MB', 'GB']:
            if self.tamanho_bytes < 1024.0:
                return f"{self.tamanho_bytes:.1f} {unidade}"
            self.tamanho_bytes /= 1024.0
        return f"{self.tamanho_bytes:.1f} TB"

# ========================================
# FUNÇÕES UTILITÁRIAS
# ========================================

def init_db(app):
    """Inicializar banco de dados com a aplicação Flask"""
    db.init_app(app)
    
    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()
        print("✅ Tabelas verificadas/criadas no banco de dados")

def criar_dados_exemplo():
    """Criar dados de exemplo se não existirem"""
    try:
        # Verificar se já existem dados
        if Usuario.query.count() > 0:
            print("📊 Dados já existem no banco")
            return
        
        # Criar usuário exemplo
        usuario = Usuario(
            nome="Usuário Teste",
            email="teste@exemplo.com"
        )
        db.session.add(usuario)
        
        # Criar categoria exemplo
        categoria = Categoria(
            nome="Exemplo",
            descricao="Categoria de exemplo"
        )
        db.session.add(categoria)
        
        db.session.commit()
        print("✅ Dados de exemplo criados")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao criar dados de exemplo: {e}")

def get_estatisticas():
    """Obter estatísticas gerais do sistema"""
    try:
        return {
            'total_usuarios': Usuario.query.count(),
            'total_categorias': Categoria.query.count(),
            'total_projetos': Projeto.query.count(),
            'total_tarefas': Tarefa.query.count(),
            'tarefas_pendentes': Tarefa.query.filter_by(status='pendente').count(),
            'tarefas_andamento': Tarefa.query.filter_by(status='andamento').count(),
            'tarefas_concluidas': Tarefa.query.filter_by(status='concluida').count(),
            'total_comentarios': Comentario.query.count(),
            'total_anexos': Anexo.query.count()
        }
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        return {}

# ========================================
# VALIDAÇÕES PERSONALIZADAS
# ========================================

def validar_email(email):
    """Validar formato do email"""
    import re
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.match(pattern, email) is not None

def validar_prioridade(prioridade):
    """Validar se prioridade é válida"""
    return prioridade.lower() in ['baixa', 'media', 'alta', 'critica']

def validar_status_tarefa(status):
    """Validar se status da tarefa é válido"""
    return status.lower() in ['pendente', 'andamento', 'concluida', 'cancelada']

def validar_status_projeto(status):
    """Validar se status do projeto é válido"""
    return status.lower() in ['ativo', 'pausado', 'concluido', 'cancelado']