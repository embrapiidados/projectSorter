/**
 * AI Suggestions Handler - Versão Modernizada
 * Este script gerencia a funcionalidade de sugestões da IA para a página de categorização.
 */

// Função para inicializar sugestões da IA com animações e efeitos modernos
function initAiSuggestions() {
    console.log("Inicializando módulo de sugestões da IA...");
    
    // Atualizar mensagem do overlay de carregamento se estiver ativo
    if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
        aiLoading.updateMessage(
            "Processando sugestões da IA...",
            "Analisando o projeto e gerando recomendações inteligentes"
        );
    }
    
    // Variável para armazenar as sugestões da IA
    let aiSuggestions = null;
    
    // Utilizar a variável global definida no template
    try {
        // Verificar se a variável global aiSuggestionData existe
        if (typeof aiSuggestionData !== 'undefined') {
            aiSuggestions = aiSuggestionData;
            console.log("Dados da IA carregados:", aiSuggestions);
            
            // Atualizar mensagem do overlay
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                aiLoading.updateMessage(
                    "Aplicando sugestões...",
                    "Preparando a interface com as recomendações da IA"
                );
            }
            
            // Exibir informações da sugestão com animação
            displayAiSuggestions(aiSuggestions);
            
            // Aplicar automaticamente as sugestões aos campos do formulário
            applyAllAiSuggestions(aiSuggestions);
        } else {
            console.log("Nenhuma sugestão da IA disponível");
            
            // Esconder o overlay de carregamento se estiver ativo
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                aiLoading.completeProgress();
            }
        }
    } catch (error) {
        console.error("Erro ao processar dados da IA:", error);
        
        // Esconder o overlay de carregamento em caso de erro
        if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
            aiLoading.completeProgress();
        }
    }
    
    /**
     * Função para exibir as informações da sugestão da IA com efeitos visuais
     * @param {Object} data - Dados de sugestão da IA
     */
    function displayAiSuggestions(data) {
        if (!data) {
            console.error("Dados da IA inválidos");
            return;
        }
        
        aiSuggestions = data;
        
        // Mostrar a seção de sugestões com animação
        $('#aiSuggestionSection').fadeIn(300);
        
        // Atualizar badge de confiança com classes modernas
        if (data.confianca) {
            let confidenceClass = 'accent-badge-info';
            let borderColor = '#17a2b8'; // cor padrão info
            
            if (data.confianca === 'ALTA') {
                confidenceClass = 'accent-badge-success';
                borderColor = '#198754'; // cor verde para alta confiança
            } else if (data.confianca === 'BAIXA') {
                confidenceClass = 'accent-badge-warning';
                borderColor = '#ffc107'; // cor amarela para baixa confiança
            }
            
            // Aplicar classes com animação
            $('#aiConfidenceBadge')
                .hide()
                .removeClass('accent-badge-info accent-badge-success accent-badge-warning')
                .addClass(confidenceClass)
                .css('border-color', borderColor)
                .find('span').text(data.confianca)
                .end()
                .fadeIn(400);
        }
        
        // Atualizar justificativa
        if (data.justificativa) {
            $('#aiJustificationText').text(data.justificativa);
        }
        
        // Atualizar categorias sugeridas
        updateAiCategories(data);
    }
    
    /**
     * Função para atualizar as categorias sugeridas pela IA
     * @param {Object} data - Dados de sugestão da IA
     */
    function updateAiCategories(data) {
        // Atualizar macroarea
        const macroarea = data._aia_n1_macroarea || data.microarea || '';
        $('#aiMacroarea').text(macroarea || '-');
        
        // Atualizar segmento
        const segmento = data._aia_n2_segmento || data.segmento || '';
        $('#aiSegmento').text(segmento || '-');
        
        // Atualizar domínios afeitos como balões
        const dominioAfeito = data._aia_n3_dominio_afeito || data.dominio || '';
        updateCategoryBubbles('aiDominioAfeito', dominioAfeito);
        
        // Atualizar domínios afeitos outros como balões
        const dominioOutro = data._aia_n3_dominio_outro || data.dominio_outro || '';
        
        // Verificar se há domínios outros para exibir ou ocultar a seção
        if (dominioOutro && dominioOutro !== 'N/A' && dominioOutro !== '-') {
            $('#aiDominioOutroContainer').show();
            updateCategoryBubbles('aiDominioOutro', dominioOutro);
        } else {
            $('#aiDominioOutroContainer').hide();
        }
    }
    
    /**
     * Função para criar balões de categorias a partir de uma string separada por ponto-e-vírgula
     * @param {string} containerId - ID do container onde os balões serão adicionados
     * @param {string} categoriesString - String com categorias separadas por ponto-e-vírgula
     */
    function updateCategoryBubbles(containerId, categoriesString) {
        const container = $(`#${containerId}`);
        container.empty();
        
        // Verificar se há categorias para exibir
        if (!categoriesString || categoriesString === 'N/A' || categoriesString === '-') {
            container.append('<span class="no-categories">Nenhuma categoria</span>');
            return;
        }
        
        // Dividir a string em categorias individuais
        let categories = [];
        if (typeof categoriesString === 'string' && categoriesString.includes(';')) {
            categories = categoriesString.split(';').map(cat => cat.trim()).filter(cat => cat);
        } else if (Array.isArray(categoriesString)) {
            categories = categoriesString.filter(cat => cat);
        } else {
            categories = [categoriesString];
        }
        
        // Criar um balão para cada categoria
        categories.forEach(category => {
            const bubble = $('<span>')
                .addClass('category-bubble')
                .text(category);
            container.append(bubble);
        });
    }
    
    /**
     * Função para aplicar todas as sugestões da IA aos campos do formulário
     * @param {Object} data - Dados de sugestão da IA
     */
    function applyAllAiSuggestions(data) {
        if (!data) {
            console.error("Não há sugestões da IA para aplicar");
            
            // Esconder o overlay de carregamento se estiver ativo
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                aiLoading.completeProgress();
            }
            
            return;
        }
        
        // Verificar se já existem valores nos campos
        const currentMicroarea = $('#microarea').val();
        const currentSegmento = $('#segmento').val();
        const currentDominio = $('#dominio').val();
        const currentDominioOutros = $('#dominio_outros').val();
        
        console.log("Valores atuais nos campos:", {
            microarea: currentMicroarea,
            segmento: currentSegmento,
            dominio: currentDominio,
            dominio_outros: currentDominioOutros
        });
        
        // Se já existem valores nos campos, não aplicar as sugestões da IA
        if (currentMicroarea || currentSegmento || 
            (currentDominio && currentDominio.length > 0) || 
            (currentDominioOutros && currentDominioOutros.length > 0)) {
            console.log("Campos já preenchidos, não aplicando sugestões da IA");
            
            // Esconder o overlay de carregamento se estiver ativo
            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                aiLoading.completeProgress();
            }
            
            return;
        }
        
        // Indicar que estamos aplicando sugestões da IA (para não marcar como modificado pelo usuário)
        window.applyingAiSuggestions = true;
        
        // Mapear campos da API para campos da UI
        const microarea = data._aia_n1_macroarea || data.microarea || '';
        const segmento = data._aia_n2_segmento || data.segmento || '';
        const dominio = data._aia_n3_dominio_afeito || data.dominio || '';
        const dominio_outros = data._aia_n3_dominio_outro || data.dominio_outro || '';
        
        console.log("Aplicando sugestões da IA:", {
            microarea, segmento, dominio, dominio_outros
        });
        
        // Aplicar as sugestões com um delay inicial para garantir que a página está completamente carregada
        setTimeout(() => {
            console.log("Iniciando aplicação das sugestões após delay inicial");
            
            // Aplicar microárea com highlight visual temporário
            if (microarea) {
                $('#microarea').val(microarea);
                highlightField('#microarea');
                console.log("Microárea definida para:", microarea);
                
                // Forçar o evento change para garantir que os listeners sejam acionados
                $('#microarea').trigger('change');
                
                // Chamar a função global filtrarSegmentos diretamente
                if (typeof window.filtrarSegmentos === 'function') {
                    console.log("Chamando filtrarSegmentos diretamente");
                    window.filtrarSegmentos();
                    console.log("Segmentos filtrados após definir microárea");
                    
                    // Aguardar um pouco para garantir que os segmentos foram atualizados
                    setTimeout(() => {
                        // Aplicar segmento e atualizar domínios
                        if (segmento) {
                            $('#segmento').val(segmento);
                            highlightField('#segmento');
                            console.log("Segmento definido para:", segmento);
                            
                            // Forçar o evento change para garantir que os listeners sejam acionados
                            $('#segmento').trigger('change');
                            
                            // Chamar a função global atualizarDominios diretamente
                            if (typeof window.atualizarDominios === 'function') {
                                console.log("Chamando atualizarDominios diretamente");
                                window.atualizarDominios();
                                console.log("Domínios atualizados após definir segmento");
                                
                                // Aguardar um pouco para garantir que os domínios foram atualizados
                                setTimeout(() => {
                                    // Aplicar domínios
                                    if (dominio) {
                                        let dominioValues = [];
                                        if (typeof dominio === 'string' && dominio.includes(';')) {
                                            dominioValues = dominio.split(';').map(d => d.trim());
                                        } else if (Array.isArray(dominio)) {
                                            dominioValues = dominio;
                                        } else {
                                            dominioValues = [dominio];
                                        }
                                        
                                        console.log("Definindo domínios:", dominioValues);
                                        $('#dominio').val(dominioValues);
                                        // Atualizar o select2 para refletir as mudanças
                                        if ($('#dominio').hasClass('searchable-select')) {
                                            $('#dominio').trigger('change');
                                        } else {
                                            // Forçar o evento change para garantir que os listeners sejam acionados
                                            $('#dominio').trigger('change');
                                        }
                                        highlightField('#dominio');
                                    }
                                    
                                    // Aplicar domínios outros com verificação de disponibilidade e retry melhorado
                                    if (dominio_outros) {
                                        // Tratar valores N/A ou vazios
                                        if (dominio_outros === 'N/A' || dominio_outros === '') {
                                            console.log("Domínios afeitos outros está vazio ou marcado como N/A. Definindo como vazio no formulário.");
                                            // Limpar o campo de domínios outros
                                            $('#dominio_outros').val([]);
                                            
                                            // Atualizar o select2 para refletir as mudanças
                                            if ($('#dominio_outros').hasClass('searchable-select')) {
                                                $('#dominio_outros').trigger('change');
                                            } else {
                                                // Forçar o evento change para garantir que os listeners sejam acionados
                                                $('#dominio_outros').trigger('change');
                                            }
                                            
                                            // Adicionar um atributo de dados para indicar que foi definido como N/A
                                            $('#dominio_outros').attr('data-na', 'true');
                                            
                                            // Restaurar a flag após aplicar as sugestões
                                            window.applyingAiSuggestions = false;
                                
                                // Esconder o overlay de carregamento se estiver ativo
                                if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                                    aiLoading.completeProgress();
                                }
                                            
                                            // Esconder o overlay de carregamento se estiver ativo
                                            if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                                                aiLoading.completeProgress();
                                            }
                                        } else {
                                            let dominioOutrosValues = [];
                                            if (typeof dominio_outros === 'string' && dominio_outros.includes(';')) {
                                                dominioOutrosValues = dominio_outros.split(';').map(d => d.trim());
                                            } else if (Array.isArray(dominio_outros)) {
                                                dominioOutrosValues = dominio_outros;
                                            } else {
                                                dominioOutrosValues = [dominio_outros];
                                            }
                                        
                                            console.log("Preparando para definir domínios afeitos outros:", dominioOutrosValues);
                                        
                                            // Função melhorada para verificar se as opções estão disponíveis no select
                                            function checkOptionsAvailable(values, selectElement) {
                                        // Obter todas as opções disponíveis no select
                                        const options = Array.from(selectElement.options).map(opt => opt.value);
                                        console.log("Opções disponíveis no select:", options);
                                        
                                        // Normalizar as opções para comparação (remover espaços, converter para minúsculas)
                                        const normalizedOptions = options.map(opt => opt.trim().toLowerCase());
                                        console.log("Opções normalizadas:", normalizedOptions);
                                        
                                        // Verificar cada valor
                                        const missingValues = [];
                                        const matchedValues = [];
                                        
                                        values.forEach(val => {
                                            // Normalizar o valor para comparação
                                            const normalizedVal = val.trim().toLowerCase();
                                            
                                            // Verificar se o valor está nas opções (comparação mais flexível)
                                            let found = false;
                                            let matchedOption = null;
                                            
                                            for (let i = 0; i < normalizedOptions.length; i++) {
                                                const opt = normalizedOptions[i];
                                                // Verificar correspondência exata, inclusão parcial ou similaridade
                                                if (opt === normalizedVal || 
                                                    opt.includes(normalizedVal) || 
                                                    normalizedVal.includes(opt)) {
                                                    found = true;
                                                    matchedOption = options[i];
                                                    break;
                                                }
                                            }
                                            
                                            if (found && matchedOption) {
                                                matchedValues.push(matchedOption); // Usar o valor exato da opção
                                                console.log(`Valor "${val}" corresponde à opção "${matchedOption}"`);
                                            } else {
                                                missingValues.push(val);
                                            }
                                        });
                                        
                                        // Logar valores que não foram encontrados
                                        if (missingValues.length > 0) {
                                            console.warn("Valores não encontrados nas opções:", missingValues);
                                        }
                                        
                                        // Retornar os valores que foram encontrados
                                        return {
                                            allFound: missingValues.length === 0,
                                            matchedValues: matchedValues
                                        };
                                    }
                                    
                                    // Função melhorada para aplicar os valores com retry
                                    function applyDominioOutrosWithRetry(values, maxRetries = 8, currentRetry = 0, delay = 1000) {
                                        console.log(`Tentativa ${currentRetry + 1} de aplicar domínios afeitos outros:`, values);
                                        
                                        // Verificar se o select tem alguma opção
                                        const selectElement = document.getElementById('dominio_outros');
                                        
                                        if (!selectElement) {
                                            console.error("Elemento select 'dominio_outros' não encontrado!");
                                            return;
                                        }
                                        
                                        if (selectElement.options.length === 0) {
                                            console.log("Select não tem opções ainda. Aguardando...");
                                            if (currentRetry < maxRetries) {
                                                setTimeout(() => {
                                                    applyDominioOutrosWithRetry(values, maxRetries, currentRetry + 1, delay);
                                                }, delay);
                                            } else {
                                                console.error("Número máximo de tentativas atingido. O select não tem opções.");
                                            }
                                            return;
                                        }
                                        
                                        // Verificar se as opções estão disponíveis
                                        const checkResult = checkOptionsAvailable(values, selectElement);
                                        const optionsAvailable = checkResult.allFound;
                                        const matchedValues = checkResult.matchedValues;
                                        
                                        // Se encontramos pelo menos algumas opções, aplicá-las
                                        if (matchedValues.length > 0) {
                                            console.log("Aplicando valores encontrados:", matchedValues);
                                            
                                            // Aplicar os valores
                                            $('#dominio_outros').val(matchedValues);
                                            
                                            // Atualizar o select2 para refletir as mudanças
                                            if ($('#dominio_outros').hasClass('searchable-select')) {
                                                $('#dominio_outros').trigger('change');
                                            }
                                            
                                            highlightField('#dominio_outros');
                                            
                                                // Verificar se a seleção foi aplicada corretamente
                                                const selectedValues = $('#dominio_outros').val();
                                                if (!selectedValues || selectedValues.length === 0) {
                                                    console.log("Seleção não aplicada corretamente. Tentando novamente...");
                                                    if (currentRetry < maxRetries) {
                                                        setTimeout(() => {
                                                            applyDominioOutrosWithRetry(values, maxRetries, currentRetry + 1, delay);
                                                        }, delay);
                                                    } else {
                                                        console.error("Número máximo de tentativas atingido. Não foi possível aplicar os domínios afeitos outros.");
                                                        // Restaurar a flag mesmo se falhar
                                                        window.applyingAiSuggestions = false;
                                                    
                                                    // Esconder o overlay de carregamento se estiver ativo
                                                    if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                                                        aiLoading.completeProgress();
                                                    }
                                                        
                                                        // Esconder o overlay de carregamento se estiver ativo
                                                        if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                                                            aiLoading.completeProgress();
                                                        }
                                                    }
                                                } else {
                                                    console.log("Domínios afeitos outros aplicados com sucesso:", selectedValues);
                                                    
                                                    // Restaurar a flag após aplicar as sugestões
                                                    window.applyingAiSuggestions = false;
                                                }
                                            } else if (!optionsAvailable) {
                                            // Se não encontramos nenhuma opção e ainda temos tentativas
                                            console.log("Nenhuma opção correspondente encontrada. Aguardando...");
                                            if (currentRetry < maxRetries) {
                                                setTimeout(() => {
                                                    applyDominioOutrosWithRetry(values, maxRetries, currentRetry + 1, delay);
                                                }, delay);
                                            } else {
                                                // Na última tentativa, tentar aplicar os valores originais
                                                console.log("Última tentativa: aplicando valores originais mesmo sem correspondência");
                                                $('#dominio_outros').val(values);
                                                
                                                if ($('#dominio_outros').hasClass('searchable-select')) {
                                                    $('#dominio_outros').trigger('change');
                                                }
                                                
                                                    highlightField('#dominio_outros');
                                                    console.log("Tentativa final de aplicação concluída");
                                                    
                                                    // Restaurar a flag mesmo após a última tentativa
                                                    window.applyingAiSuggestions = false;
                                                }
                                            }
                                        }
                                        
                                            // Aplicar diretamente os valores no select
                                            function applyDominioOutrosDirectly(values) {
                                                console.log("Tentando aplicar diretamente os valores:", values);
                                                
                                                // Verificar se o select tem opções
                                                const selectElement = document.getElementById('dominio_outros');
                                                if (!selectElement || selectElement.options.length === 0) {
                                                    console.log("Select não tem opções ainda, tentando aplicar mesmo assim");
                                                }
                                                
                                                // Aplicar os valores diretamente
                                                $('#dominio_outros').val(values);
                                                
                                                // Atualizar o select2 para refletir as mudanças
                                                if ($('#dominio_outros').hasClass('searchable-select')) {
                                                    $('#dominio_outros').trigger('change');
                                                } else {
                                                    // Forçar o evento change para garantir que os listeners sejam acionados
                                                    $('#dominio_outros').trigger('change');
                                                }
                                                
                                                highlightField('#dominio_outros');
                                                
                                                // Verificar se a seleção foi aplicada corretamente
                                                const selectedValues = $('#dominio_outros').val();
                                                console.log("Valores selecionados após aplicação direta:", selectedValues);
                                                
                                                // Restaurar a flag após aplicar as sugestões
                                                window.applyingAiSuggestions = false;
                                                
                                                // Esconder o overlay de carregamento se estiver ativo
                                                if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
                                                    aiLoading.completeProgress();
                                                }
                                            }
                                            
                                            // Iniciar o processo de aplicação com um delay maior para garantir que o select esteja preenchido
                                            setTimeout(() => {
                                                // Tentar aplicar diretamente primeiro
                                                applyDominioOutrosDirectly(dominioOutrosValues);
                                                
                                                // Se não funcionar, tentar com o retry
                                                setTimeout(() => {
                                                    // Verificar se a aplicação direta funcionou
                                                    const selectedValues = $('#dominio_outros').val();
                                                    if (!selectedValues || selectedValues.length === 0) {
                                                        console.log("Aplicação direta falhou, tentando com retry");
                                                        applyDominioOutrosWithRetry(dominioOutrosValues);
                                                    }
                                                }, 1000);
                                            }, 3000); // Aumentado para 3000ms para dar mais tempo para o select ser preenchido
                                        }
                                    }
                                    
                                    // Se não houver domínios afeitos ou domínios afeitos outros, restaurar a flag
                                    if (!dominio && (!dominio_outros || dominio_outros === 'N/A' || dominio_outros === '')) {
                                        window.applyingAiSuggestions = false;
                                    }
                                }, 2000); // Aumentado para 2000ms
                            } else {
                                console.error("Função atualizarDominios não encontrada");
                                window.applyingAiSuggestions = false;
                            }
                        }
                    }, 2000); // Aumentado para 2000ms
                } else {
                    console.error("Função filtrarSegmentos não encontrada");
                    window.applyingAiSuggestions = false;
                }
            } else {
                console.log("Nenhuma microárea para aplicar");
                window.applyingAiSuggestions = false;
            }
        }, 1000); // Delay inicial de 1000ms
    }
    
    /**
     * Função auxiliar para destacar visualmente um campo que foi preenchido pela IA
     * @param {string} selector - Seletor do campo
     */
    function highlightField(selector) {
        // Removido o destaque visual a pedido do usuário
        console.log("Campo preenchido pela IA:", selector);
    }
    
    // Inicializar o botão de justificativa com efeito de transição suave
    $('#showJustificationBtn').on('click', function() {
        console.log("Botão de justificativa clicado");
        
        // Animação suave para mostrar/ocultar
        $('#justificationBox').slideToggle({
            duration: 300,
            easing: 'swing'
        });
        
        // Toggle da classe active preservando o botão
        $(this).toggleClass('active');
        
        // Alternar texto e ícone sem perder a forma do botão
        if ($(this).hasClass('active')) {
            $(this).find('i').removeClass('fa-info-circle').addClass('fa-times-circle');
            $(this).find('span').text('Ocultar Classificação');
        } else {
            $(this).find('i').removeClass('fa-times-circle').addClass('fa-info-circle');
            $(this).find('span').text('Ver Classificação');
        }
    });
}

// Initialize when document is ready
$(document).ready(function() {
    // Check if we're on the categorize page
    if ($('#aiSuggestionSection').length > 0) {
        initAiSuggestions();
    } else {
        // Se não estamos na página de categorização, garantir que o overlay seja escondido
        if (typeof aiLoading !== 'undefined' && localStorage.getItem('aiLoadingActive') === 'true') {
            console.log('Não estamos na página de categorização, escondendo o overlay de carregamento');
            aiLoading.completeProgress();
        }
    }
    
    // Adicionar funcionalidade de toggle para os cabeçalhos colapsáveis
    $('.collapse-icon').parent().on('click', function() {
        $(this).find('i').toggleClass('fa-chevron-up fa-chevron-down');
    });
});
