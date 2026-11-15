document.addEventListener('DOMContentLoaded', () => {
    const stars = document.querySelectorAll('.rating-stars span');
    const ratingInput = document.getElementById('rating-input');

    if (stars.length && ratingInput) {
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                ratingInput.value = index + 1;

                stars.forEach((s, i) => {
                    if (i <= index) {
                        s.classList.add('active-star');
                    } else {
                        s.classList.remove('active-star');
                    }
                });
            });
        });
    }
});
