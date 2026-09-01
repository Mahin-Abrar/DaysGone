document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.draft-form').forEach(form => {
        const formType = form.dataset.formType;
        const statusEl = form.querySelector('.draft-status');
        let timeout;

        form.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const formData = new FormData(form);
                formData.append('form_type', formType);
                const csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;

                fetch('/drafts/save/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrf },
                    body: formData,
                }).then(r => r.json()).then(() => {
                    if (statusEl) {
                        statusEl.textContent = 'Draft saved ✓';
                        setTimeout(() => { statusEl.textContent = ''; }, 2000);
                    }
                });
            }, 2000);
        });
    });
});
