// ========================================
// SISTEMA DE TAREFAS - ELVIS
// ========================================

console.log('📝 Sistema de Tarefas carregado!');

// ========================================
// FILTRAR TAREFAS
// ========================================
function filtrarTarefas() {
    const filtro = document.getElementById('filtro').value;
    const tarefas = document.querySelectorAll('.task-item');
    let contador = 0;
    
    console.log(`🔍 Filtrando por: ${filtro}`);
    
    tarefas.forEach(tarefa => {
        if (filtro === 'todas' || tarefa.dataset.status === filtro) {
            tarefa.style.display = 'block';
            contador++;
        } else {
            tarefa.style.display = 'none';
        }
    });
    
    console.log(`📋 Mostrando ${contador} tarefas`);
    
    // Mostrar mensagem se não houver tarefas
    mostrarMensagemVazia(contador);
}

// ========================================
// MOSTRAR MENSAGEM QUANDO VAZIO
// ========================================
function mostrarMensagemVazia(contador) {
    const container = document.getElementById('taskContainer');
    let mensagemVazia = document.getElementById('mensagem-filtro-vazio');
    
    if (contador === 0 && !mensagemVazia) {
        const filtro = document.getElementById('filtro').value;
        const mensagens = {
            'pendente': 'Nenhuma tarefa pendente! 🎉',
            'andamento': 'Nenhuma tarefa em andamento.',
            'concluida': 'Nenhuma tarefa concluída ainda.'
        };
        
        mensagemVazia = document.createElement('div');
        mensagemVazia.id = 'mensagem-filtro-vazio';
        mensagemVazia.className = 'empty-state';
        mensagemVazia.innerHTML = `
            <div class="empty-state-icon">🔍</div>
            <h3>${mensagens[filtro] || 'Nenhuma tarefa encontrada'}</h3>
            <p>Tente alterar o filtro ou criar uma nova tarefa.</p>
        `;
        
        container.appendChild(mensagemVazia);
    } else if (contador > 0 && mensagemVazia) {
        mensagemVazia.remove();
    }
}

// ========================================
// EDITAR TAREFA - MODAL (Função principal)
// ========================================
function editarTarefa(id, titulo, descricao, prioridade, status) {
    console.log(`✏️ Editando tarefa ID: ${id}`);
    
    // Preencher campos do modal
    document.getElementById('edit-titulo').value = titulo;
    document.getElementById('edit-descricao').value = descricao || '';
    document.getElementById('edit-prioridade').value = prioridade;
    document.getElementById('edit-status').value = status;
    
    // Configurar ação do formulário
    document.getElementById('editForm').action = '/editar/' + id;
    
    // Mostrar modal
    document.getElementById('editModal').style.display = 'block';
    
    // Focar no primeiro campo
    setTimeout(() => {
        document.getElementById('edit-titulo').focus();
    }, 100);
}

// ========================================
// FECHAR MODAL
// ========================================
function fecharModal() {
    console.log('❌ Fechando modal de edição');
    document.getElementById('editModal').style.display = 'none';
}

// ========================================
// EVENTOS DO MODAL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('editModal');
    
    // Fechar modal clicando fora
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            fecharModal();
        }
    });
    
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            fecharModal();
        }
    });
});

// ========================================
// GERENCIAR ALERTAS
// ========================================
function gerenciarAlertas() {
    const alertas = document.querySelectorAll('.alert');
    
    if (alertas.length > 0) {
        console.log(`📢 ${alertas.length} alerta(s) encontrado(s)`);
        
        // Fechar automaticamente após 5 segundos
        setTimeout(() => {
            alertas.forEach(alerta => {
                if (alerta.style.display !== 'none') {
                    alerta.style.opacity = '0';
                    setTimeout(() => {
                        alerta.style.display = 'none';
                    }, 300);
                }
            });
        }, 5000);
    }
}

// ========================================
// MELHORAR FORMULÁRIO
// ========================================
function configurarFormulario() {
    const form = document.querySelector('form[action="/adicionar"]');
    const tituloInput = document.getElementById('titulo');
    const descricaoInput = document.getElementById('descricao');
    
    if (form) {
        // Resetar valores padrão após limpar
        form.addEventListener('reset', function() {
            setTimeout(() => {
                document.getElementById('prioridade').value = 'media';
                document.getElementById('status').value = 'pendente';
                console.log('🔄 Formulário resetado');
            }, 100);
        });
        
        // Contador de caracteres para título
        if (tituloInput) {
            const maxTitulo = tituloInput.getAttribute('maxlength') || 100;
            
            tituloInput.addEventListener('input', function() {
                const atual = this.value.length;
                console.log(`📝 Título: ${atual}/${maxTitulo} caracteres`);
                
                // Mudar cor quando próximo do limite
                if (atual > maxTitulo * 0.8) {
                    this.style.borderColor = '#f59e0b';
                } else {
                    this.style.borderColor = '#e5e7eb';
                }
            });
        }
        
        // Contador de caracteres para descrição
        if (descricaoInput) {
            const maxDescricao = descricaoInput.getAttribute('maxlength') || 500;
            
            // Criar elemento contador
            const contador = document.createElement('small');
            contador.style.color = '#6b7280';
            contador.style.fontSize = '12px';
            contador.style.marginTop = '5px';
            contador.style.display = 'block';
            
            descricaoInput.parentNode.appendChild(contador);
            
            descricaoInput.addEventListener('input', function() {
                const atual = this.value.length;
                contador.textContent = `${atual}/${maxDescricao} caracteres`;
                
                // Mudar cor quando próximo do limite
                if (atual > maxDescricao * 0.8) {
                    this.style.borderColor = '#f59e0b';
                    contador.style.color = '#f59e0b';
                } else {
                    this.style.borderColor = '#e5e7eb';
                    contador.style.color = '#6b7280';
                }
            });
            
            // Mostrar contador inicial
            contador.textContent = `0/${maxDescricao} caracteres`;
        }
        
        // Validação do formulário
        form.addEventListener('submit', function(e) {
            const titulo = tituloInput.value.trim();
            
            if (!titulo) {
                e.preventDefault();
                alert('⚠️ O título da tarefa é obrigatório!');
                tituloInput.focus();
                return false;
            }
            
            if (titulo.length < 3) {
                e.preventDefault();
                alert('⚠️ O título deve ter pelo menos 3 caracteres!');
                tituloInput.focus();
                return false;
            }
            
            console.log('✅ Formulário válido, enviando...');
        });
    }
}

// ========================================
// ANIMAÇÕES E MELHORIAS VISUAIS
// ========================================
function adicionarAnimacoes() {
    // Animação ao carregar as tarefas
    const tarefas = document.querySelectorAll('.task-item');
    tarefas.forEach((tarefa, index) => {
        tarefa.style.opacity = '0';
        tarefa.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            tarefa.style.transition = 'all 0.5s ease';
            tarefa.style.opacity = '1';
            tarefa.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Animação nos botões
    const botoes = document.querySelectorAll('.btn, .btn-icon');
    botoes.forEach(botao => {
        botao.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        botao.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// ========================================
// ESTATÍSTICAS DINÂMICAS
// ========================================
function atualizarEstatisticas() {
    const tarefas = document.querySelectorAll('.task-item');
    const stats = {
        total: tarefas.length,
        pendente: 0,
        andamento: 0,
        concluida: 0
    };
    
    tarefas.forEach(tarefa => {
        const status = tarefa.dataset.status;
        if (stats.hasOwnProperty(status)) {
            stats[status]++;
        }
    });
    
    // Atualizar elementos de estatística se existirem
    const statElements = {
        total: document.querySelector('.stat-item:nth-child(1) .stat-number'),
        pendente: document.querySelector('.stat-item:nth-child(2) .stat-number'),
        andamento: document.querySelector('.stat-item:nth-child(3) .stat-number'),
        concluida: document.querySelector('.stat-item:nth-child(4) .stat-number')
    };
    
    Object.keys(statElements).forEach(key => {
        if (statElements[key]) {
            statElements[key].textContent = stats[key];
        }
    });
    
    console.log('📊 Estatísticas:', stats);
}

// ========================================
// BUSCA RÁPIDA
// ========================================
function adicionarBuscaRapida() {
    const header = document.querySelector('.tasks-header');
    if (!header || document.getElementById('busca-rapida')) return;
    
    const buscaContainer = document.createElement('div');
    buscaContainer.innerHTML = `
        <input type="text" 
               id="busca-rapida" 
               placeholder="🔍 Buscar tarefas..." 
               style="padding: 8px 12px; border: 2px solid #e5e7eb; border-radius: 6px; margin-left: 10px;">
    `;
    
    header.appendChild(buscaContainer);
    
    const inputBusca = document.getElementById('busca-rapida');
    inputBusca.addEventListener('input', function() {
        const termo = this.value.toLowerCase();
        const tarefas = document.querySelectorAll('.task-item');
        
        tarefas.forEach(tarefa => {
            const titulo = tarefa.querySelector('.task-title').textContent.toLowerCase();
            const descricao = tarefa.querySelector('.task-description p');
            const textoDescricao = descricao ? descricao.textContent.toLowerCase() : '';
            
            if (titulo.includes(termo) || textoDescricao.includes(termo)) {
                tarefa.style.display = 'block';
            } else {
                tarefa.style.display = 'none';
            }
        });
        
        console.log(`🔍 Buscando por: "${termo}"`);
    });
}

// ========================================
// CONFIRMAÇÕES MELHORADAS
// ========================================
function melhorarConfirmacoes() {
    const botoesExcluir = document.querySelectorAll('.btn-delete');
    
    botoesExcluir.forEach(botao => {
        botao.addEventListener('click', function(e) {
            const titulo = this.closest('.task-item').querySelector('.task-title').textContent;
            
            const confirmacao = confirm(
                `🗑️ EXCLUIR TAREFA\n\n` +
                `Título: "${titulo}"\n\n` +
                `Esta ação não pode ser desfeita.\n` +
                `Deseja continuar?`
            );
            
            if (!confirmacao) {
                e.preventDefault();
                console.log('❌ Exclusão cancelada pelo usuário');
            } else {
                console.log(`🗑️ Excluindo tarefa: "${titulo}"`);
            }
        });
    });
}

// ========================================
// SALVAR PREFERÊNCIAS NO SESSIONSTORAGE
// ========================================
function salvarPreferencias() {
    const filtro = document.getElementById('filtro');
    
    // Carregar filtro salvo
    const filtroSalvo = sessionStorage.getItem('filtro-tarefas');
    if (filtroSalvo && filtro) {
        filtro.value = filtroSalvo;
        filtrarTarefas();
    }
    
    // Salvar quando mudar
    if (filtro) {
        filtro.addEventListener('change', function() {
            sessionStorage.setItem('filtro-tarefas', this.value);
            console.log(`💾 Filtro salvo: ${this.value}`);
        });
    }
}

// ========================================
// INICIALIZAÇÃO PRINCIPAL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando sistema de tarefas...');
    
    try {
        // Executar todas as funções de inicialização
        gerenciarAlertas();
        configurarFormulario();
        atualizarEstatisticas();
        adicionarAnimacoes();
        adicionarBuscaRapida();
        melhorarConfirmacoes();
        salvarPreferencias();
        
        console.log('✅ Sistema inicializado com sucesso!');
        
        // Mostrar informações do sistema no console
        console.log(`
        📋 SISTEMA DE TAREFAS - ELVIS
        =============================
        ✅ Criar tarefas
        ✅ Editar tarefas  
        ✅ Excluir tarefas
        ✅ Filtrar tarefas
        ✅ Buscar tarefas
        ✅ Estatísticas dinâmicas
        ✅ Animações suaves
        ✅ Design responsivo
        
        Desenvolvido com ❤️ por Elvis
        `);
        
    } catch (error) {
        console.error('❌ Erro na inicialização:', error);
    }
});

// ========================================
// DETECTAR MUDANÇAS NO SISTEMA
// ========================================
window.addEventListener('beforeunload', function() {
    console.log('👋 Saindo do sistema de tarefas...');
});

// ========================================
// FUNÇÕES GLOBAIS EXPOSTAS
// ========================================
window.sistemaTA 

// ========================================
// MODO DEBUG
// ========================================
if (window.location.search.includes('debug=true')) {
    console.log('🔧 MODO DEBUG ATIVADO');
    
    // Adicionar botão de debug
    const debugBtn = document.createElement('button');
    debugBtn.textContent = '🔧 Debug';
    debugBtn.style.position = 'fixed';
    debugBtn.style.bottom = '20px';
    debugBtn.style.right = '20px';
    debugBtn.style.zIndex = '9999';
    debugBtn.style.padding = '10px';
    debugBtn.style.background = '#ef4444';
    debugBtn.style.color = 'white';
    debugBtn.style.border = 'none';
    debugBtn.style.borderRadius = '5px';
    debugBtn.style.cursor = 'pointer';
    
    debugBtn.addEventListener('click', function() {
        console.table({
            'Tarefas totais': document.querySelectorAll('.task-item').length,
            'Tarefas visíveis': document.querySelectorAll('.task-item[style*="block"], .task-item:not([style])').length,
            'Filtro atual': document.getElementById('filtro').value,
            'Modal aberto': document.getElementById('editModal').style.display === 'block'
        });
    });
    
    document.body.appendChild(debugBtn);
}
