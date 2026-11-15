function toggleMenu() {
    const nav = document.getElementById('navLinks');
    if (nav) {
        nav.classList.toggle('active');
    }
}

function toggleSearch() {
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');

    if (searchForm) {
        searchForm.classList.toggle('active');
        if (searchForm.classList.contains('active') && searchInput) {
            searchInput.focus();
        }
    }
}
