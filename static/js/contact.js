// static/js/contact.js
document.addEventListener('DOMContentLoaded', function () {

    const form         = document.getElementById('invContactForm');
    const feedback     = document.getElementById('invFormFeedback');
    const telefoneInput = document.getElementById('invTelefone');
    const submitBtn    = form ? form.querySelector('button[type="submit"]') : null;

    // ── Máscara de telefone ────────────────────────────────
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function () {
            let val = this.value.replace(/\D/g, '');
            if (val.length > 11) val = val.slice(0, 11);
            if (val.length > 7)      val = val.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
            else if (val.length > 2) val = val.replace(/^(\d{2})(\d+)$/,          '($1) $2');
            this.value = val;
        });
    }

    // ── Helpers de UI ──────────────────────────────────────
    function showFeedback(tipo, texto) {
        feedback.className = 'inv-form-feedback ' + tipo;
        feedback.textContent = texto;
        feedback.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function setLoading(loading) {
        if (!submitBtn) return;
        submitBtn.disabled = loading;
        submitBtn.textContent = loading ? 'Enviando…' : 'Enviar mensagem';
    }

    // ── Envio real via fetch → /api/contato ───────────────
    if (form) {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();

            // Limpa feedback anterior
            feedback.className = 'inv-form-feedback';
            feedback.textContent = '';

            // Captura todos os campos (incluindo empresa e serviço)
            const nome      = document.getElementById('invNome').value.trim();
            const empresa   = document.getElementById('invEmpresa')?.value.trim() || '';
            const email     = document.getElementById('invEmail').value.trim();
            const telefone  = document.getElementById('invTelefone').value.trim();
            const interesse = document.getElementById('invServico')?.value.trim() || 'Consultoria';
            const mensagem  = document.getElementById('invMensagem').value.trim();
            const newsletter = document.getElementById('invNewsletter')?.checked || false;

            // ── Validação client-side ─────────────────────
            if (!nome || !email || !telefone || !mensagem) {
                showFeedback('error', '⚠️ Por favor, preencha todos os campos obrigatórios (Nome, Telefone, E-mail e Mensagem).');
                return;
            }
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showFeedback('error', '⚠️ Por favor, insira um e-mail válido.');
                return;
            }
            if (mensagem.length < 20) {
                showFeedback('error', '⚠️ A mensagem deve ter pelo menos 20 caracteres.');
                return;
            }

            // ── Envio para o backend ──────────────────────
            setLoading(true);

            try {
                const response = await fetch('/api/contato', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nome, empresa, email, telefone, interesse, mensagem, newsletter })
                });

                const data = await response.json();

                if (response.ok) {
                    showFeedback('success', '✓ Mensagem enviada com sucesso! Entraremos em contato em até 24 horas úteis.');
                    form.reset();
                } else {
                    // Erro de validação ou regra de negócio retornado pelo backend
                    const erroMsg = data.erro || 'Erro ao enviar. Tente novamente.';
                    showFeedback('error', '⚠️ ' + erroMsg);
                }

            } catch (err) {
                // Falha de rede ou servidor indisponível
                console.error('[contact.js] Erro de rede:', err);
                showFeedback('error', '⚠️ Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.');
            } finally {
                setLoading(false);
            }
        });
    }

});
