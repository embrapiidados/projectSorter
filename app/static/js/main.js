/**
 * Script principal para o sistema de categorização de projetos
 */

// Esconder alertas após alguns segundos
document.addEventListener('DOMContentLoaded', function() {
    // Auto-fechar alertas após 5 segundos
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            // Criar um objeto bootstrap para o alerta
            const bsAlert = new bootstrap.Alert(alert);
            // Fechar o alerta
            bsAlert.close();
        });
    }, 5000);
    
    // Adicionar classes ativas para links de navegação
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath && currentLocation.includes(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });
});

// Função para confirmar exclusão
function confirmDelete(message) {
    return confirm(message || 'Tem certeza que deseja excluir este item?');
}

// Função para mostrar/esconder um elemento
function toggleElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        if (element.style.display === 'none') {
            element.style.display = 'block';
        } else {
            element.style.display = 'none';
        }
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

// Função de busca para tabelas
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const filter = input.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) { // Começar do 1 para pular o cabeçalho
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;
            
            for (let j = 0; j < cells.length; j++) {
                const cellText = cells[j].textContent || cells[j].innerText;
                
                if (cellText.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
            
            row.style.display = found ? '' : 'none';
        }
    });
}