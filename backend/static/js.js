/**
 * Sistema de Gerenciamento de Tarefas
 * JavaScript moderno com ES6+, tratamento de erros e UX aprimorada
 */

class TaskManager {
    constructor() {
        this.elements = this.initializeElements();
        this.state = {
            tasks: [],
            loading: false,
            currentFilter: 'todas'
        };
        this.init();
    }

    // Inicializar elementos DOM
    initializeElements() {
        return {
            // Formulário
            form: document.getElementById('taskForm'),
            titulo: document.getElementById('titulo'),
            descricao: document.getElementById('descricao'),
            prioridade: document.getElementById('prioridade'),
            status: document.getElementById('status'),
            
            // Containers
            taskContainer: document.getElementById('taskContainer'),
            messagesSection: document.getElementById('messages'),
            emptyState: document.getElementById('emptyState'),
            
            // Filtros
            filtro: document.getElementById('filtro')
        };
    }

    // Inicializar aplicação
    init() {
        this.bindEvents();
        this.loadTasks();
        this.showWelcomeMessage();
    }

    // Vincular eventos
    bindEvents() {
        // Formulário
        this.elements.form?.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Filtros
        this.elements.filtro?.addEventListener('change', (e) => this.handleFilterChange(e));
        
        // Limpar formulário ao resetar
        this.elements.form?.addEventListener('reset', () => {
            setTimeout(() => this.resetForm(), 100);
        });

        // Auto-save draft (opcional)
        this.elements.titulo?.addEventListener('input', this.debounce(() => this.saveDraft(), 1000));
    }

    // Submissão do formulário
    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.state.loading) return;

        const formData = this.getFormData();
        
        if (!this.validateForm(formData)) {
            return;
        }

        await this.addTask(formData);
    }

    // Obter dados do formulário
    getFormData() {
        return {
            titulo: this.elements.titulo?.value?.trim() || '',
            descricao: this.elements.descricao?.value?.trim() || '',
            prioridade: this.elements.prioridade?.value || 'media',
            status: this.elements.status?.value || 'pendente'
        };
    }

    // Validar formulário
    validateForm(data) {
        const errors = [];

        if (!data.titulo) {
            errors.push('O título é obrigatório');
            this.elements.titulo?.focus();
        }

        if (data.titulo && data.titulo.length > 100) {
            errors.push('O título deve ter no máximo 100 caracteres');
        }

        if (data.descricao && data.descricao.length > 500) {
            errors.push('A descrição deve ter no máximo 500 caracteres');
        }

        if (errors.length > 0) {
            this.showMessage(errors.join('<br>'), 'error');
            return false;
        }

        return true;
    }

    // Adicionar nova tarefa
    async addTask(taskData) {
        this.setLoading(true);
        
        try {
            const response = await fetch('/api/tarefas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    ...taskData,
                    usuario_id: 1, // Temporário - implementar autenticação depois
                    categoria_id: 1 // Temporário - implementar categorias depois
                })
            });

            const result = await this.handleResponse(response);
            
            if (result.success) {
                this.showMessage('✅ Tarefa adicionada com sucesso!', 'success');
                this.resetForm();
                await this.loadTasks();
                this.clearDraft();
            } else {
                throw new Error(result.message || 'Erro ao adicionar tarefa');
            }

        } catch (error) {
            console.error('Erro ao adicionar tarefa:', error);
            this.showMessage(`❌ Erro ao adicionar tarefa: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    // Carregar tarefas
    async loadTasks() {
        this.setLoading(true);
        
        try {
            const response = await fetch('/api/tarefas', {
                headers: { 'Accept': 'application/json' }
            });
            
            const result = await this.handleResponse(response);
            
            if (result.success) {
                this.state.tasks = result.data || [];
                this.renderTasks();
            } else {
                throw new Error(result.message || 'Erro ao carregar tarefas');
            }

        } catch (error) {
            console.error('Erro ao carregar tarefas:', error);
            this.showMessage(`❌ Erro ao carregar tarefas: ${error.message}`, 'error');
            this.showEmptyState('Erro ao carregar tarefas. Tente recarregar a página.');
        } finally {
            this.setLoading(false);
        }
    }

    // Excluir tarefa
    async deleteTask(id) {
        if (!confirm('🗑️ Tem certeza que deseja excluir esta tarefa?\n\nEsta ação não pode ser desfeita.')) {
            return;
        }

        this.setLoading(true);

        try {
            const response = await fetch(`/api/tarefas/${id}`, {
                method: 'DELETE',
                headers: { 'Accept': 'application/json' }
            });

            const result = await this.handleResponse(response);
            
            if (result.success) {
                this.showMessage('🗑️ Tarefa excluída com sucesso!', 'success');
                await this.loadTasks();
            } else {
                throw new Error(result.message || 'Erro ao excluir tarefa');
            }

        } catch (error) {
            console.error('Erro ao excluir tarefa:', error);
            this.showMessage(`❌ Erro ao excluir tarefa: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    // Renderizar tarefas
    renderTasks() {
        if (!this.elements.taskContainer) return;

        const filteredTasks = this.filterTasks();
        
        if (filteredTasks.length === 0) {
            this.showEmptyState();
            return;
        }

        this.hideEmptyState();
        
        this.elements.taskContainer.innerHTML = filteredTasks
            .map(task => this.createTaskHTML(task))
            .join('');
        
        this.bindTaskEvents();
    }

    // Filtrar tarefas
    filterTasks() {
        if (this.state.currentFilter === 'todas') {
            return this.state.tasks;
        }
        
        return this.state.tasks.filter(task => 
            task.status.toLowerCase() === this.state.currentFilter
        );
    }

    // Criar HTML da tarefa
    createTaskHTML(task) {
        const createdDate = new Date(task.data_criacao || Date.now()).toLocaleDateString('pt-BR');
        const priorityIcon = this.getPriorityIcon(task.prioridade);
        const statusIcon = this.getStatusIcon(task.status);

        return `
            <article class="task-item" data-status="${task.status.toLowerCase()}" data-priority="${task.prioridade.toLowerCase()}" data-id="${task.id}">
                <header class="task-header">
                    <h3 class="task-title">${this.escapeHtml(task.titulo)}</h3>
                    <div class="task-actions">
                        <button class="btn-edit" aria-label="Editar tarefa" data-id="${task.id}">✏️</button>
                        <button class="btn-delete" aria-label="Excluir tarefa" data-id="${task.id}">🗑️</button>
                    </div>
                </header>
                
                <div class="task-meta">
                    <span class="task-status status-${task.status.toLowerCase()}">${statusIcon} ${this.capitalizeFirst(task.status)}</span>
                    <span class="task-priority priority-${task.prioridade.toLowerCase()}">${priorityIcon} ${this.capitalizeFirst(task.prioridade)}</span>
                    <time class="task-date" datetime="${task.data_criacao}">Criado em: ${createdDate}</time>
                </div>
                
                ${task.descricao ? `
                <div class="task-description">
                    <p>${this.escapeHtml(task.descricao)}</p>
                </div>
                ` : ''}
            </article>
        `;
    }

    // Vincular eventos das tarefas
    bindTaskEvents() {
        // Botões de excluir
        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const id = btn.getAttribute('data-id');
                this.deleteTask(id);
            });
        });

        // Botões de editar (futuro)
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const id = btn.getAttribute('data-id');
                this.editTask(id);
            });
        });
    }

    // Editar tarefa (placeholder para futuro)
    editTask(id) {
        this.showMessage('🚧 Funcionalidade de edição em desenvolvimento!', 'info');
        // TODO: Implementar edição inline ou modal
    }

    // Manipular mudança de filtro
    handleFilterChange(e) {
        this.state.currentFilter = e.target.value;
        this.renderTasks();
    }

    // Mostrar/ocultar estado vazio
    showEmptyState(message = null) {
        if (!this.elements.emptyState) return;
        
        const defaultMessage = this.state.currentFilter === 'todas' 
            ? '📝 Nenhuma tarefa encontrada. Que tal adicionar uma nova?'
            : `📝 Nenhuma tarefa ${this.state.currentFilter} encontrada.`;
            
        this.elements.emptyState.innerHTML = `<p>${message || defaultMessage}</p>`;
        this.elements.emptyState.style.display = 'block';
        this.elements.taskContainer.style.display = 'none';
    }

    hideEmptyState() {
        if (this.elements.emptyState) {
            this.elements.emptyState.style.display = 'none';
        }
        if (this.elements.taskContainer) {
            this.elements.taskContainer.style.display = 'block';
        }
    }

    // Mostrar mensagem
    showMessage(text, type = 'info', duration = 5000) {
        if (!this.elements.messagesSection) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.innerHTML = text;

        this.elements.messagesSection.appendChild(messageDiv);
        this.elements.messagesSection.classList.add('show');

        setTimeout(() => {
            messageDiv.remove();
            if (this.elements.messagesSection.children.length === 0) {
                this.elements.messagesSection.classList.remove('show');
            }
        }, duration);
    }

    // Resetar formulário
    resetForm() {
        if (this.elements.form) {
            this.elements.form.reset();
        }
        
        // Resetar valores padrão
        if (this.elements.prioridade) this.elements.prioridade.value = 'media';
        if (this.elements.status) this.elements.status.value = 'pendente';
    }

    // Controle de loading
    setLoading(loading) {
        this.state.loading = loading;
        
        const submitBtn = this.elements.form?.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = loading;
            submitBtn.textContent = loading ? '⏳ Salvando...' : '💾 Salvar Tarefa';
        }
    }

    // Manipular resposta da API
    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }

    // Utilitários
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
    }

    getPriorityIcon(priority) {
        const icons = {
            baixa: '🟢',
            media: '🟡', 
            alta: '🔴'
        };
        return icons[priority.toLowerCase()] || '🟡';
    }

    getStatusIcon(status) {
        const icons = {
            pendente: '⏳',
            andamento: '🔄',
            concluida: '✅'
        };
        return icons[status.toLowerCase()] || '⏳';
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Salvar rascunho (localStorage)
    saveDraft() {
        const draft = this.getFormData();
        if (draft.titulo) {
            localStorage.setItem('taskDraft', JSON.stringify(draft));
        }
    }

    // Carregar rascunho
    loadDraft() {
        try {
            const draft = localStorage.getItem('taskDraft');
            if (draft) {
                const data = JSON.parse(draft);
                if (this.elements.titulo) this.elements.titulo.value = data.titulo || '';
                if (this.elements.descricao) this.elements.descricao.value = data.descricao || '';
                if (this.elements.prioridade) this.elements.prioridade.value = data.prioridade || 'media';
                if (this.elements.status) this.elements.status.value = data.status || 'pendente';
            }
        } catch (error) {
            console.warn('Erro ao carregar rascunho:', error);
        }
    }

    // Limpar rascunho
    clearDraft() {
        localStorage.removeItem('taskDraft');
    }

    // Mensagem de boas-vindas
    showWelcomeMessage() {
        setTimeout(() => {
            this.showMessage('🎉 Bem-vindo ao seu gerenciador de tarefas!', 'success', 3000);
        }, 500);
    }
}

// Função global para compatibilidade (se necessário)
function deletarTarefa(id) {
    if (window.taskManager) {
        window.taskManager.deleteTask(id);
    }
}

// Inicializar aplicação quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.taskManager = new TaskManager();
    
    // Carregar rascunho se existir
    window.taskManager.loadDraft();
});

// Salvar rascunho antes de sair da página
window.addEventListener('beforeunload', () => {
    if (window.taskManager) {
        window.taskManager.saveDraft();
    }
});