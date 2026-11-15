document.addEventListener('DOMContentLoaded', () => {
    const authForms = document.querySelectorAll('form');
    authForms.forEach((form) => {
        form.addEventListener('submit', function () {
            const btn = form.querySelector("button[type='submit']");
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = 'Please Wait...';
            }
        });
    });
});
