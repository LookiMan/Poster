
$(document).ready(function() {
    const galleryType = $('#id_media_gallery_type').val();

    $('body').on('click', 'tr.add-row a', (e) => {
        const count = $(`.dynamic-gallery${galleryType}_set`).length;
        
        if (!count) {
            return;
        }

        $(`#gallery${galleryType}_set-${count-1} .fr-box`).remove(); // Remove not initialized widget

        const FroalaEditorOptions = JSON.parse(
            $(`#id_gallery${galleryType}_set-__prefix__-froala_editor_options`).val()
        );

        FroalaEditorOptions['toolbarInline'] = true;
        FroalaEditorOptions['charCounterCount'] = false;

        new FroalaEditor(`#id_gallery${galleryType}_set-${count-1}-caption`, FroalaEditorOptions);
    });
});
