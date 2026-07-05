// static/js/contact.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('invContactForm');
    const feedback = document.getElementById('invFormFeedback');
    const telefoneInput = document.getElementById('invTelefone');

    if (telefoneInput) {
        telefoneInput.addEventListener('input', function() {
            let val = this.value.replace(/\D/g, '');
            if (val.length > 11) val = val.slice(0, 11);
            if (val.length > 7) val = val.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
            else if (val.length > 2) val = val.replace(/^(\d{2})(\d+)$/, '($1) $2');
            this.value = val;
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            feedback.className = 'inv-form-feedback';
            feedback.textContent = '';

            const nome = document.getElementById('invNome').value.trim();
            const email = document.getElementById('invEmail').value.trim();
            const telefone = document.getElementById('invTelefone').value.trim();
            const mensagem = document.getElementById('invMensagem').value.trim();

            if (!nome || !email || !telefone || !mensagem) {
                feedback.className = 'inv-form-feedback error';
                feedback.textContent = '⚠️ Por favor, preencha todos os campos obrigatórios (Nome, Telefone, E-mail e Mensagem).';
                feedback.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                feedback.className = 'inv-form-feedback error';
                feedback.textContent = '⚠️ Por favor, insira um e-mail válido.';
                feedback.scrollIntoView({ behavior: 'smooth', block: 'center' });
                return;
            }
            // Simula envio
            feedback.className = 'inv-form-feedback success';
            feedback.textContent = '✓ Mensagem enviada com sucesso! Entraremos em contato em até 24 horas úteis.';
            form.reset();
            feedback.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });
    }
});