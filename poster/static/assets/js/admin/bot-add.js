$(document).ready(function() {
    $('#id_bot_type').change((e) => {
        const map = {
            'discord': 'webhook',
            'telegram': 'token',
        }
        const field = $(e.currentTarget).val();
        const group = map[field];

        if (!group) {
            console.error(`Unknown group from field ${field}`);
            return;
        }

        $('.form-group.field-token').hide();
        $('.form-group.field-webhook').hide();
        $(`.form-group.field-${group}`).show();
    });

    $('#id_bot_type').change();
});
