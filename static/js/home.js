document.addEventListener("DOMContentLoaded", () => {

    const slides = document.querySelectorAll(".hero-slide");
    const dots = document.querySelectorAll(".hero-dot");

    const prevButton = document.getElementById("heroPrev");
    const nextButton = document.getElementById("heroNext");

    let currentSlide = 0;
    let autoSlide;


    function showSlide(index) {

        if (index >= slides.length) {
            currentSlide = 0;
        } else if (index < 0) {
            currentSlide = slides.length - 1;
        } else {
            currentSlide = index;
        }

        slides.forEach((slide, i) => {
            slide.classList.toggle(
                "active",
                i === currentSlide
            );
        });

        dots.forEach((dot, i) => {
            dot.classList.toggle(
                "active",
                i === currentSlide
            );
        });
    }


    function nextSlide() {
        showSlide(currentSlide + 1);
    }


    function previousSlide() {
        showSlide(currentSlide - 1);
    }


    function startAutoSlide() {

        clearInterval(autoSlide);

        autoSlide = setInterval(() => {
            nextSlide();
        }, 6000);
    }


    nextButton.addEventListener("click", () => {

        nextSlide();
        startAutoSlide();

    });


    prevButton.addEventListener("click", () => {

        previousSlide();
        startAutoSlide();

    });


    dots.forEach((dot, index) => {

        dot.addEventListener("click", () => {

            showSlide(index);
            startAutoSlide();

        });

    });


    showSlide(0);
    startAutoSlide();

});