const drawer = document.getElementById("customerDrawer");

const overlay = document.getElementById("drawerOverlay");

const closeBtn = document.getElementById("closeDrawer");

function openDrawer() {

    const drawer = document.getElementById("customerDrawer");
    const overlay = document.getElementById("drawerOverlay");

    // Close mobile navbar
    const nav = document.getElementById("navLinks");

    if (nav) {
        nav.classList.remove("active");
    }

    drawer.classList.add("open");
    overlay.classList.add("active");

    document.body.style.overflow = "hidden";
}
function closeDrawer() {

    const drawer = document.getElementById("customerDrawer");
    const overlay = document.getElementById("drawerOverlay");

    drawer.classList.remove("open");
    overlay.classList.remove("active");

    document.body.style.overflow = "";
}

if(closeBtn){

    closeBtn.addEventListener("click",closeDrawer);

}

if(overlay){

    overlay.addEventListener("click",closeDrawer);

}

window.openCustomerDrawer=openDrawer;