document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabs = document.querySelectorAll('.auth-tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');

            const targetTab = tab.getAttribute('data-tab');
            const targetContent = document.getElementById(targetTab + '-tab');
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    const loginForm = document.querySelector('#email-tab form');
    const userIdForm = document.querySelector('#userid-tab form');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            if (!validateLoginInputs()) {
                e.preventDefault();
            }
        });
    }
    if (userIdForm) {
        userIdForm.addEventListener('submit', function(e) {
            if (!validateLoginInputs()) {
                e.preventDefault();
            }
        });
    }
});


function validateLoginInputs() {
    const activeForm = document.querySelector('.tab-content.active form');
    if (!activeForm) return false;
    
    let hasError = false;
    const inputs = activeForm.querySelectorAll('.form-input');
    
    inputs.forEach(input => {
        const parentGroup = input.closest('.form-group');
        if (input.value.trim() === '') {
            parentGroup.classList.add('error');
            hasError = true;
        } else {
            parentGroup.classList.remove('error');
        }
    });

    return !hasError;
}
