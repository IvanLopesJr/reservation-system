document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('form[novalidate]:not(.js-skip-validation)').forEach(function(form) {
        form.querySelectorAll('.form-control, .form-select').forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid') || this.classList.contains('is-valid')) {
                    validateField(this);
                }
            });
        });
    });

    function validateField(input) {
        if (!input.hasAttribute('required') && !input.value.trim()) {
            input.classList.remove('is-valid', 'is-invalid');
            return;
        }

        if (input.hasAttribute('required') && !input.value.trim()) {
            setInvalid(input, 'Campo obrigatório.');
            return;
        }

        if (input.type === 'email' && input.value.trim()) {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!re.test(input.value.trim())) {
                setInvalid(input, 'E-mail inválido.');
                return;
            }
        }

        if (input.type === 'password' && input.value.trim().length < 6) {
            setInvalid(input, 'Mínimo 6 caracteres.');
            return;
        }

        setValid(input);
    }

    function setValid(input) {
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        const feedback = input.parentElement.querySelector('.feedback-invalid');
        if (feedback) feedback.remove();
        let validFeedback = input.parentElement.querySelector('.feedback-valid');
        if (!validFeedback) {
            validFeedback = document.createElement('div');
            validFeedback.className = 'feedback-valid';
            validFeedback.textContent = 'OK';
            input.parentElement.appendChild(validFeedback);
        }
    }

    function setInvalid(input, msg) {
        input.classList.remove('is-valid');
        input.classList.add('is-invalid');
        const oldFeedback = input.parentElement.querySelector('.feedback-valid');
        if (oldFeedback) oldFeedback.remove();
        let feedback = input.parentElement.querySelector('.feedback-invalid');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'feedback-invalid';
            input.parentElement.appendChild(feedback);
        }
        feedback.textContent = msg;
    }
});
