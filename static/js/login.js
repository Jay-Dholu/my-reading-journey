const tabButtons = document.querySelectorAll('.login-tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        // Switch active tab button
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        // Show correct tab content
        const tabToShow = button.getAttribute('data-tab');
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.classList.contains(tabToShow)) {
                content.classList.add('active');
            }
        });
    });
});
