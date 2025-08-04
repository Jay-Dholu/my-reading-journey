document.addEventListener('DOMContentLoaded', () => {
  const themeToggleMobile = document.getElementById('theme-toggle-mobile');
  const themeToggleDesktop = document.getElementById('theme-toggle');
  const menuBtn = document.getElementById('menu-btn');
  const navLinks = document.getElementById('nav-links');
  const root = document.documentElement;

  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

  const applyTheme = (mode) => {
    const icon = mode === 'dark' ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    root.classList.toggle('dark', mode === 'dark');
    if (themeToggleMobile) themeToggleMobile.innerHTML = icon;
    if (themeToggleDesktop) themeToggleDesktop.innerHTML = icon;
  };

  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    applyTheme(prefersDark ? 'dark' : 'light');
  }

  const toggleTheme = () => {
    const newTheme = root.classList.contains('dark') ? 'light' : 'dark';
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  };

  // Theme toggle buttons
  if (themeToggleMobile) {
    themeToggleMobile.addEventListener('click', toggleTheme);
  }

  if (themeToggleDesktop) {
    themeToggleDesktop.addEventListener('click', toggleTheme);
  }

  // Menu button toggle
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('show');
    });
  }
});

setTimeout(() => {
  const flash = document.querySelector('.flash-message');
  if (flash) {
    flash.classList.add('fade-out');
    setTimeout(() => flash.remove(), 500);
  }
}, 4000); // 4 seconds

function filterBooks() {
    const search = document.getElementById("searchBar").value.toLowerCase();
    const cards = document.querySelectorAll(".book-card");

    cards.forEach(card => {
        const title = card.dataset.title;
        const author = card.dataset.author;
        card.style.display = (title.includes(search) || author.includes(search)) ? "block" : "none";
    });
}

function sortBooks() {
    const value = document.getElementById("sortBy").value;
    const grid = document.getElementById("bookGrid");
    const cards = Array.from(grid.querySelectorAll(".book-card"));

    let [field, direction] = value.split("-");

    cards.sort((a, b) => {
        let valA = a.dataset[field];
        let valB = b.dataset[field];

        if (field === 'date') {
            return direction === 'asc' ? new Date(valA) - new Date(valB) : new Date(valB) - new Date(valA);
        }

        return direction === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
    });

    grid.innerHTML = "";
    cards.forEach(card => grid.appendChild(card));

    // Optional: Store in sessionStorage
    sessionStorage.setItem("lastSort", value);
}

// Optional: Restore last sort
window.onload = function () {
    const lastSort = sessionStorage.getItem("lastSort");
    if (lastSort) {
        document.getElementById("sortBy").value = lastSort;
        sortBooks();
    }
};
