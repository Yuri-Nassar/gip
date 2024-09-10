$(document).ready(function() {
    $('#id_ticker_type').change(function() {
        var url = ajaxUrl  // URL to the view that handles the AJAX request
        var tickerTypeId = $(this).val();  // get the selected ticker type
        $.ajax({
            url: url,
            method: 'GET',
            data: {
                'ticker_type': tickerTypeId
            },
            success: function(data) {
                var $tickerCodeSelect = $("#id_ticker_code");
                $tickerCodeSelect.empty();  // Clear the existing options
                $tickerCodeSelect.append('<option value="">Selecione o Ticker</option>');  // Add a default option
                $.each(data, function(index, item) {
                    $tickerCodeSelect.append('<option value="' + item.id + '">' + item.ticker + '</option>');
                });
            }
        });
    });
});

$(document).ready(function() {
    $('#id_cnpj').each(function() {
        this.required = false;
    });
});

$(document).ready(function() {
    // Função para verificar se o modal foi criado e exibi-lo
    function checkAndShowModal() {
        const form = document.querySelector('form');
        if (form.id === 'ticker_form_delete') {
            id = 'messageModal';
            // const successModal = document.getElementById(id);
        } else {
            id = 'successModal';
            // const successModal = document.getElementById(id); 
        }
        const successModal = document.getElementById(id);
        
        if (successModal) {
            console.log('successModal detectado. Exibindo o modal.');

            // Exibe o modal
            // $('#successModal').modal('show');
            $('#'+id).modal('show');

            // Espera 2 segundos, fecha o modal e redireciona
            setTimeout(function() {
                // if ($('#successModal').length) {
                if ($('#'+id).length) {
                    console.log('fechando o modal');

                    // $('#successModal').modal('hide');
                    $('#'+id).modal('hide');

                    // Define a URL de redirecionamento com base no ID do formulário
                    // const form = document.querySelector('form');
                    let redirectUrl;
                    if (['ticker_form_update', 'ticker_form_new','ticker_form_delete'].includes(form.id)) {
                        redirectUrl = "portfolio/tickers";
                    } else if (['transaction_form_update', 'transaction_form_new'].includes(form.id)) {
                        redirectUrl = "ticker_list";
                    } else if (['dividend_form_update', 'dividend_form_new'].includes(form.id)) {
                        redirectUrl = "ticker_list";
                    } else {
                        redirectUrl = "portfolio"; // URL padrão caso o ID não corresponda
                    }

                    // Constrói a URL absoluta
                    const baseUrl = window.location.origin;
                    const absoluteUrl = new URL(redirectUrl, baseUrl);
                    console.log('Redirecionando para: ' + absoluteUrl);

                    // Faz o redirecionamento
                    window.location.href = absoluteUrl;
                } else {
                    console.log('Modal não encontrado');
                }
            }, 2000); // 2000 milissegundos = 2 segundos
        }
    }

    // Cria um MutationObserver para monitorar mudanças no DOM
    const observer = new MutationObserver(function(mutationsList, observer) {
        for (let mutation of mutationsList) {
            if (mutation.type === 'childList') {
                // Verifica se algum novo nó foi adicionado (como o modal)
                checkAndShowModal();
            }
        }
    });

    // Inicia a observação do body por mudanças no DOM
    observer.observe(document.body, {
        childList: true,  // Observa adição/remoção de elementos
        subtree: true     // Observa mudanças em todos os nós descendentes
    });

    // Verifica inicialmente se o modal já está presente (caso tenha sido renderizado antes do observer)
    checkAndShowModal();
});

$(document).ready(function() {
    // Ao clicar em qualquer botão com data-toggle="modal", o modal é acionado
    $('[data-toggle="modal"]').on('click', function(event) {
        event.preventDefault();  // Impede comportamento padrão
        var targetModal = $(this).data('target');
        $(targetModal).modal('show');
        console.log("Mostrando modal: " + targetModal);
    });

    // Quando o botão de cancelar for clicado, o modal é fechado corretamente
    $('.modal .btn-secondary').on('click', function() {
        $(this).closest('.modal').modal('hide');
        console.log("Cancelando modal.");
    });

    $('.modal .btn-danger').on('click', function() {
        $(this).closest('.modal').modal('hide');
        console.log("Fechando modal para deletar.");

        // const successModalDelete = document.getElementById('messageModal');
        // if (successModalDelete) {
        //     console.log('successModalDelete detectado. Exibindo o modal.');
        //     $('#messageModal').modal('show');
        // }else{
        //     console.log('successModalDelete não detectado. Não exibindo o modal.');
        // }
    });
    
    // $('.modal .btn-danger').on('click', function() {
    //     // $(this).closest('.modal').modal('hide');
    //     console.log("Mostrando modal de DELETADO.");
    //     $('#messageModal').modal('show');
    //     setTimeout(function() {
            
    //         // Constrói a URL absoluta
    //         const baseUrl = window.location.origin;
    //         const absoluteUrl = new URL('ticker_list', baseUrl);
    //         console.log('Redirecionando para: ' + absoluteUrl);
    //         console.log("Fechando modal de DELETADO.");
    //         $('#messageModal').modal('hide');

    //         // Faz o redirecionamento
    //         window.location.href = absoluteUrl;
            
    //     }, 2000);

    // });
    // Após o envio do formulário de deletar, exibe o modal de sucesso ou erro
    // var deleteForm = $('form.delete-form');  // Certifique-se de que o formulário de deleção tem essa classe
    // deleteForm.on('submit', function(event) {
    //     event.preventDefault();  // Impede o envio tradicional do formulário
        

    //     var form = $(this);
    //     var actionUrl = form.attr('action');
    //     var formData = form.serialize();

    //     $.ajax({
    //         url: actionUrl,
    //         type: 'POST',
    //         data: formData,
    //         success: function(response) {
    //             if (response.success) {
    //                 $('#messageModal').modal('show');  // Exibe o modal de sucesso
    //                 // Constrói a URL absoluta
    //                 const baseUrl = window.location.origin;
    //                 const absoluteUrl = new URL(response.redirect_url, baseUrl);
    //                 // const absoluteUrl = new URL( baseUrl);
    //                 console.log('Redirecionando para: ' + absoluteUrl);
    //                 setTimeout(function() {
    //                     // window.location.href = absoluteUrl;  // Redireciona após o tempo
    //                 }, 2000);
    //             }// else {
    //                 // Exibe um modal de erro ou feedback
    //             //     $('#messageModal .modal-body').html(response.error_message);
    //             //     $('#messageModal').modal('show');
    //             // }
    //         },
    //         // error: function() {
    //         //     $('#messageModal .modal-body').html('Erro ao tentar deletar o item.');
    //         //     $('#messageModal').modal('show');
    //         // }
    //     });
    // });
});
