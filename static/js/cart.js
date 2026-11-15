function openReviews() {
    const drawer = document.getElementById('reviewDrawer');
    const overlay = document.getElementById('reviewOverlay');

    if (drawer) {
        drawer.classList.add('active');
    }

    if (overlay) {
        overlay.classList.add('active');
    }
}


function closeReviews() {
    const drawer = document.getElementById('reviewDrawer');
    const overlay = document.getElementById('reviewOverlay');

    if (drawer) {
        drawer.classList.remove('active');
    }

    if (overlay) {
        overlay.classList.remove('active');
    }
}


function placeOrder() {

    const button = event.currentTarget;

    const loggedIn =
        button.dataset.loggedIn === "true";

    if (!loggedIn) {

        document
            .getElementById("loginPopup")
            .classList.add("active");

        return;
    }

    window.location.href = "/checkout";
}


function closeLoginPopup() {

    document
        .getElementById("loginPopup")
        .classList.remove("active");

}