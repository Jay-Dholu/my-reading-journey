// Password strength indicator for the sign-up page
document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('input[name="password"]');
    const strengthBar = document.querySelector('.strength-fill');
    const strengthText = document.querySelector('.strength-text');

    if (passwordInput && strengthBar && strengthText) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            let text = 'Password strength';
            
            if (password.length >= 8) strength += 1;
            if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 1;
            if (/\d]/.test(password)) strength += 1;
            if (/[^a-zA-Z\d]/.test(password)) strength += 1;
            
            const percentage = (strength / 4) * 100;
            strengthBar.style.width = percentage + '%';
            
            strengthBar.classList.remove('weak', 'medium', 'strong');

            if (strength === 0) {
                text = 'Password strength';
            } else if (strength <= 2) {
                strengthBar.classList.add('weak');
                text = 'Weak';
            } else if (strength === 3) {
                strengthBar.classList.add('medium');
                text = 'Medium';
            } else {
                strengthBar.classList.add('strong');
                text = 'Strong';
            }
            
            strengthText.textContent = text;
        });
    }
});
