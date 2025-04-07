/**
 * Script principal para o sistema de categorização de projetos
 */

// Inicialização do documento
document.addEventListener('DOMContentLoaded', function() {
    // Auto-fechar alertas após 4 segundos
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            // Criar um objeto bootstrap para o alerta
            const bsAlert = new bootstrap.Alert(alert);
            // Aplicar fade-out
            alert.style.opacity = 0;
            // Após transição, fechar o alerta
            setTimeout(() => {
                bsAlert.close();
            }, 400);
        });
    }, 4000);
    
    // Adicionar classes ativas para links de navegação
    markActiveNavLink();
    
    // Inicializar tooltips se existirem
    initTooltips();
    
    // Aplicar efeitos de hover em cards onde aplicável
    initCardHoverEffects();
});

// Marca link ativo na navegação
function markActiveNavLink() {
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentLocation.includes(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });
}

// Inicializa tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Inicializa efeitos de hover em cards
function initCardHoverEffects() {
    const hoverCards = document.querySelectorAll('.hover-card');
    hoverCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover-effect');
        });
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover-effect');
        });
    });
}

// Função para confirmar exclusão
function confirmDelete(message) {
    return confirm(message || 'Tem certeza que deseja excluir este item?');
}

// Função para mostrar/esconder um elemento
function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = element.style.display === 'none' ? 'block' : 'none';
    }
}

// Validação de formulários
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    // Adicionar classe 'was-validated' para mostrar validação
    form.classList.add('was-validated');
    
    // Verificar se o formulário é válido
    return form.checkValidity();
}

// Função para copiar texto para a área de transferência
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Mostrar notificação de cópia
    showNotification('Copiado para a área de transferência!');
}

// Mostrar uma notificação flutuante
function showNotification(message, type = 'success', duration = 3000) {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="${type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Adicionar ao corpo da página
    document.body.appendChild(notification);
    
    // Mostrar com animação
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remover após o tempo especificado
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, duration);
}

// Função de busca para tabelas
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const filter = input.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        let noResults = true;
        
        for (let i = 1; i < rows.length; i++) { // Começar do 1 para pular o cabeçalho
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;
            
            for (let j = 0; j < cells.length; j++) {
                const cellText = cells[j].textContent || cells[j].innerText;
                
                if (cellText.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    noResults = false;
                    break;
                }
            }
            
            row.style.display = found ? '' : 'none';
        }
        
        // Mostrar mensagem se não houver resultados
        const noResultsMsg = document.getElementById('noResultsMessage');
        if (noResultsMsg) {
            noResultsMsg.style.display = noResults ? 'block' : 'none';
        }
    });
}