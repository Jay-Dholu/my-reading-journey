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
    setTimeout(() => flash.remove(), 500); // Clean up
  }
}, 3000); // 3 seconds
