document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    htmx.on('htmx:beforeRequest', function(evt) {
        const target = evt.detail.target;
        if (target) {
            target.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"></div></div>';
        }
    });

    htmx.on('htmx:afterRequest', function(evt) {
        if (evt.detail.failed) {
            const el = evt.detail.target;
            if (el) {
                el.innerHTML = '<div class="alert alert-danger">Erro ao carregar dados.</div>';
            }
        }
    });
});
