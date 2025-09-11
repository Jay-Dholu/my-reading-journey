document.addEventListener('DOMContentLoaded', function () {
    initializeTheme();
    initializeMobileMenu();
    initializeFlashMessages();
    initializeScrollEffects();
    initializeBookSearch();
    initializeAnimations();
    initializeUploadModal();
    initializeDeleteAccountModal();
});


// Theme Management
function initializeTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Initial theme
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    setTheme(initialTheme);

    // Theme toggle event listener
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fa fa-sun' : 'fa fa-moon';
        }
    }
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}


// Mobile Menu
function initializeMobileMenu() {
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const mobileNav = document.getElementById('mobile-nav');

    if (mobileToggle && mobileNav) {
        mobileToggle.addEventListener('click', function (event) {
            event.stopPropagation();
            mobileNav.classList.toggle('show');
            mobileToggle.classList.toggle('active');
        });
    }
}


// Flash Messages
function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            dismissFlashMessage(message);
        }, 5000); // Auto-dismiss after 5 seconds
    });
}

function dismissFlashMessage(message) {
    // Add a fade-out animation
    message.style.opacity = '0';
    message.style.transform = 'translateX(20px)';
    setTimeout(() => {
        if (message.parentNode) {
            message.remove();
        }
    }, 300); // Remove after animation
}


// Scroll Effects for Navbar
function initializeScrollEffects() {
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
            if (currentScrollTop > lastScrollTop && currentScrollTop > navbar.offsetHeight) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
            }
            lastScrollTop = currentScrollTop <= 0 ? 0 : currentScrollTop;
        }, { passive: true });
    }
}


// Book Search and Sorting
function initializeBookSearch() {
    const searchBar = document.getElementById('searchBar');
    if (searchBar) {
        searchBar.addEventListener('input', filterBooks);
    }
    const sortSelect = document.getElementById('sortBy');
    if (sortSelect) {
        sortSelect.addEventListener('change', sortBooks);
    }
}

function filterBooks() {
    const searchTerm = document.getElementById('searchBar').value.toLowerCase().trim();
    const bookCards = document.querySelectorAll('.book-card');
    const noResults = document.getElementById('noResults');
    let visibleCount = 0;

    bookCards.forEach(card => {
        const title = card.getAttribute('data-title') || '';
        const author = card.getAttribute('data-author') || '';
        const isMatch = title.includes(searchTerm) || author.includes(searchTerm);
        if (isMatch) {
            card.style.display = 'block';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

function sortBooks() {
    const sortValue = document.getElementById('sortBy').value;
    if (!sortValue) return;

    const bookGrid = document.getElementById('bookGrid');
    if (!bookGrid) return;

    const bookCards = Array.from(bookGrid.querySelectorAll('.book-card'));
    const [field, direction] = sortValue.split('-');

    bookCards.sort((a, b) => {
        const valueA = a.getAttribute(`data-${field}`) || '';
        const valueB = b.getAttribute(`data-${field}`) || '';

        const comparison = valueA.localeCompare(valueB, undefined, { numeric: true });
        return direction === 'desc' ? -comparison : comparison;
    });

    bookCards.forEach(card => bookGrid.appendChild(card));
}


// Fade-in Animations on Scroll
function initializeAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.book-card, .stat-card, .empty-state').forEach(el => {
        el.classList.add('fade-in-init');
        observer.observe(el);
    });
}


function initializeUploadModal() {
    const uploadModal = document.getElementById('uploadModal');
    const uploadForm = document.getElementById('uploadForm');
    const uploadSubmitBtn = document.getElementById('uploadSubmitBtn');
    const uploadArea = uploadModal.querySelector('.upload-area');
    const fileInput = uploadModal.querySelector('.file-input');
    const uploadText = uploadModal.querySelector('.upload-text');

    if (uploadModal && uploadForm && uploadSubmitBtn && uploadArea && fileInput && uploadText) {

        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                uploadText.textContent = fileInput.files[0].name;
            } else {
                uploadText.textContent = 'Choose your JSON file';
            }
        });

        // This is the core logic that makes the button work
        uploadSubmitBtn.addEventListener('click', () => {
            if (fileInput.files.length > 0) {
                uploadForm.submit();
            } else {
                alert("Please select a JSON file to upload.");
            }
        });
    }
}


function initializeDeleteAccountModal() {
    const deleteModal = document.getElementById('deleteAccountModal');
    if (!deleteModal) return;

    const confirmInput = deleteModal.querySelector('#confirmUserId');
    const confirmBtn = deleteModal.querySelector('#confirmDeleteBtn');
    const deleteForm = deleteModal.querySelector('#deleteAccountForm');
    const correctUserId = "{{ current_user.userid }}"; // This will be rendered by Jinja in the template

    confirmInput.addEventListener('input', () => {
        // Enable the button only if the input matches the user's User ID
        if (confirmInput.value === correctUserId) {
            confirmBtn.disabled = false;
        } else {
            confirmBtn.disabled = true;
        }
    });

    confirmBtn.addEventListener('click', () => {
        // When the confirmation button is clicked, submit the form
        deleteForm.submit();
    });
}


// calculate current age to render on 'developer' page
const birthDate = new Date('2005-02-09');
const currentAge = new Date().getFullYear() - birthDate.getFullYear();
document.querySelector('.age').innerText = currentAge;
