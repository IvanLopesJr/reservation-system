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
        if (target && !target.closest('[data-no-shimmer]')) {
            target.style.minHeight = target.offsetHeight + 'px';
            target.innerHTML =
                '<div class="p-4"><div class="shimmer shimmer-card"></div><div class="shimmer shimmer-line"></div><div class="shimmer shimmer-line short"></div><div class="shimmer shimmer-line"></div></div>';
        }
    });

    htmx.on('htmx:afterRequest', function(evt) {
        if (evt.detail.failed) {
            const el = evt.detail.target;
            if (el) {
                el.innerHTML = '<div class="alert alert-danger m-3">Erro ao carregar dados.</div>';
                setTimeout(function() {
                    const alert = el.querySelector('.alert');
                    if (alert) bootstrap.Alert.getOrCreateInstance(alert).close();
                }, 5000);
            }
        }
    });

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
        new bootstrap.Tooltip(el);
    });
});
