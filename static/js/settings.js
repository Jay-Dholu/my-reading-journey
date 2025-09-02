document.addEventListener('DOMContentLoaded', function() {
    // --- Section Navigation ---
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.section');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));

            item.classList.add('active');
            const sectionId = item.dataset.section;
            document.getElementById(sectionId).classList.add('active');
        });
    });

    // --- Theme Toggle ---
    // Connects the settings page button to the global theme toggle function in script.js
    const settingsThemeToggle = document.getElementById('theme-toggle-settings');
    if (settingsThemeToggle) {
        settingsThemeToggle.addEventListener('click', window.toggleTheme);
    }
    
    // --- Delete Account Modal Logic (from your original code) ---
    const deleteModal = document.getElementById('deleteAccountModal');
    if (deleteModal) {
        const confirmInput = deleteModal.querySelector('#confirmUserId');
        const confirmBtn = deleteModal.querySelector('#confirmDeleteBtn');
        const deleteForm = deleteModal.querySelector('#deleteAccountForm');
        const correctUserId = "{{ current_user.userid }}";

        if(confirmInput && confirmBtn && deleteForm) {
            confirmInput.addEventListener('input', () => {
                confirmBtn.disabled = confirmInput.value !== correctUserId;
            });

            confirmBtn.addEventListener('click', () => {
                deleteForm.submit();
            });
        }
    }
});
