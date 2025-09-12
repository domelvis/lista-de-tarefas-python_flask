from flask import Blueprint, request, jsonify
from models import db, Tarefa

routes = Blueprint("routes", __name__)

# -------- LISTAR TAREFAS --------
@routes.route("/tarefas", methods=["GET"])
def listar_tarefas():
    tarefas = Tarefa.query.all()
    resultado = [{
        "id": t.id_tarefa,
        "titulo": t.titulo,
        "descricao": t.descricao,
        "prioridade": t.prioridade,
        "status": t.status,
        "data_criacao": t.data_criacao,
        "data_prazo": t.data_prazo,
        "id_usuario": t.id_usuario,
        "id_categoria": t.id_categoria
    } for t in tarefas]
    return jsonify(resultado)

# -------- CRIAR TAREFA --------
@routes.route("/tarefas", methods=["POST"])
def criar_tarefa():
    data = request.json
    nova = Tarefa(
        titulo=data["titulo"],
        descricao=data.get("descricao", ""),
        prioridade=data.get("prioridade", "Média"),
        status=data.get("status", "Pendente"),
        id_usuario=data.get("id_usuario", 1),
        id_categoria=data.get("id_categoria", 1)
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({"message": "Tarefa criada com sucesso!", "id": nova.id_tarefa})

# -------- ATUALIZAR TAREFA --------
@routes.route("/tarefas/<int:id>", methods=["PUT"])
def atualizar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    data = request.json
    tarefa.titulo = data.get("titulo", tarefa.titulo)
    tarefa.descricao = data.get("descricao", tarefa.descricao)
    tarefa.prioridade = data.get("prioridade", tarefa.prioridade)
    tarefa.status = data.get("status", tarefa.status)
    tarefa.id_categoria = data.get("id_categoria", tarefa.id_categoria)
    db.session.commit()
    return jsonify({"message": "Tarefa atualizada com sucesso!"})

# -------- DELETAR TAREFA --------
@routes.route("/tarefas/<int:id>", methods=["DELETE"])
def deletar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    db.session.delete(tarefa)
    db.session.commit()
    return jsonify({"message": "Tarefa deletada com sucesso!"})
