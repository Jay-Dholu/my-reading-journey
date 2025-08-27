document.addEventListener('DOMContentLoaded', function() {
    initializeFormInputs();
    initializePasswordToggle();
    initializePasswordStrength();
    initializeTabs();
    initializeFormValidation();
});


function initializeFormInputs() {
    const formInputs = document.querySelectorAll('.form-input');
    
    formInputs.forEach(input => {
        const container = input.closest('.form-group');
        const label = container?.querySelector('.form-label');
        
        if (!container || !label) return;
        
        // Function to update container state
        function updateContainerState() {
            const hasValue = input.value.trim() !== '';
            const isFocused = document.activeElement === input;
            
            // Remove all state classes
            container.classList.remove('focused', 'has-value');
            
            // Add appropriate state classes
            if (isFocused) {
                container.classList.add('focused');
            }
            if (hasValue) {
                container.classList.add('has-value');
            }
        }
        
        // Event listeners for proper state management
        input.addEventListener('focus', function() {
            updateContainerState();
        });
        
        input.addEventListener('blur', function() {
            updateContainerState();
        });
        
        input.addEventListener('input', function() {
            updateContainerState();
        });
        
        // Initial state check
        updateContainerState();
        
        // Handle autofill detection
        setTimeout(() => {
            updateContainerState();
        }, 100);
    });
    
    // Additional check for browser autofill
    setTimeout(() => {
        formInputs.forEach(input => {
            if (input.value) {
                const container = input.closest('.input-container');
                if (container) {
                    container.classList.add('has-value');
                }
            }
        });
    }, 500);
}


function initializeTabs() {
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
                
                setTimeout(() => {
                    const tabInputs = targetContent.querySelectorAll('.form-input');
                    tabInputs.forEach(input => {
                        const container = input.closest('.form-group');
                        if (container && input.value.trim() !== '') {
                            container.classList.add('has-value');
                        }
                    });
                }, 10);
            }
        });
    });
}


// Password toggle functionality
function initializePasswordToggle() {
    window.togglePassword = function(button) {
        const input = button.closest('.input-container').querySelector('.form-input');
        const icon = button.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.className = 'bx bx-hide';
        } else {
            input.type = 'password';
            icon.className = 'bx bx-show';
        }
        
        // Maintain focus and cursor position
        const cursorPosition = input.selectionStart;
        input.focus();
        input.setSelectionRange(cursorPosition, cursorPosition);
    };
}


// Password strength indicator
function initializePasswordStrength() {
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
            if (/\d/.test(password)) strength += 1;
            if (/[^a-zA-Z\d]/.test(password)) strength += 1;
            
            const percentage = (strength / 4) * 100;
            strengthBar.style.width = percentage + '%';
            
            // Remove existing strength classes
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
}


// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.auth-form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('.form-input');
        
        inputs.forEach(input => {
            input.addEventListener('blur', validateInput);
            input.addEventListener('input', clearValidation);
        });
        
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateInput({ target: input })) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}


function validateInput(e) {
    const input = e.target;
    const container = input.closest('.form-group');
    let errorDiv = container.querySelector('.error-message');
    
    // Remove existing error styling
    container.classList.remove('error');
    if (errorDiv) {
        errorDiv.remove();
    }
    
    // Validate based on input type and requirements
    let isValid = true;
    let errorMessage = '';
    
    if (input.required && !input.value.trim()) {
        isValid = false;
        errorMessage = 'This field is required';
    } else if (input.type === 'email' && input.value && !isValidEmail(input.value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
    } else if (input.name === 'confirm_password' && input.value) {
        const passwordInput = input.form.querySelector('input[name="password"]');
        if (passwordInput && input.value !== passwordInput.value) {
            isValid = false;
            errorMessage = 'Passwords do not match';
        }
    } else if (input.name === 'userid' && input.value && input.value.length < 2) {
        isValid = false;
        errorMessage = 'User ID must be at least 2 characters';
    } else if (input.name === 'password' && input.value && input.value.length < 8) {
        isValid = false;
        errorMessage = 'Password must be at least 8 characters';
    }
    
    if (!isValid) {
        container.classList.add('error');
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<span>${errorMessage}</span>`;
        container.appendChild(errorDiv);
    }
    
    return isValid;
}


function clearValidation(e) {
    const input = e.target;
    const container = input.closest('.form-group');
    const errorDiv = container.querySelector('.error-message');
    
    container.classList.remove('error');
    if (errorDiv) {
        errorDiv.remove();
    }
}


function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Handle dynamic form switching for login
document.addEventListener('DOMContentLoaded', function() {
    const emailTab = document.querySelector('[data-tab="email"]');
    const userIdTab = document.querySelector('[data-tab="userid"]');
    
    if (emailTab && userIdTab) {
        emailTab.addEventListener('click', function() {
            // Clear userid input when switching to email
            const useridInput = document.querySelector('#userid-tab input[name="userid"]');
            if (useridInput) {
                useridInput.value = '';
                const container = useridInput.closest('.input-container');
                if (container) {
                    container.classList.remove('has-value', 'focused');
                }
            }
        });
        
        userIdTab.addEventListener('click', function() {
            // Clear email input when switching to userid
            const emailInput = document.querySelector('#email-tab input[name="email"]');
            if (emailInput) {
                emailInput.value = '';
                const container = emailInput.closest('.input-container');
                if (container) {
                    container.classList.remove('has-value', 'focused');
                }
            }
        });
    }
});


// Clipboard and paste handling
document.addEventListener('paste', function(e) {
    const input = e.target;
    if (input.classList.contains('form-input')) {
        setTimeout(() => {
            const container = input.closest('.input-container');
            if (container && input.value.trim() !== '') {
                container.classList.add('has-value');
            }
        }, 10);
    }
});


// Handle browser back/forward navigation
window.addEventListener('pageshow', function(e) {
    // Re-initialize form states on page show (including back navigation)
    setTimeout(initializeFormInputs, 100);
});
