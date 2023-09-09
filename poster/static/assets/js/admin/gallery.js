
$(document).ready(function() {
    $('body').on('click', 'tr.add-row a', (e) => {
        const count = $('.dynamic-galleryphoto_set').length;
        
        if (!count) {
            return;
        }

        $(`#galleryphoto_set-${count-1} .fr-box`).remove(); // Remove not initialized widget

        const FroalaEditorOptions = JSON.parse(
            $('#id_galleryphoto_set-__prefix__-froala_editor_options').val()
        );

        FroalaEditorOptions['toolbarInline'] = true;
        FroalaEditorOptions['charCounterCount'] = false;

        new FroalaEditor(`#id_galleryphoto_set-${count-1}-caption`, FroalaEditorOptions);
    });
});
