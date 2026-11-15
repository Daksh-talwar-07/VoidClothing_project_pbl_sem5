document.addEventListener('DOMContentLoaded', () => {
    const flash = document.querySelector('.flash-box');
    if (flash) {
        setTimeout(() => {
            flash.style.display = 'none';
        }, 3000);
    }

    document.querySelectorAll('form').forEach((form) => {
        form.addEventListener('submit', function () {
            const btn = form.querySelector("button[type='submit']");
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = 'Please Wait...';
            }
        });
    });
});
