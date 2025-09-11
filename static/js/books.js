document.addEventListener('DOMContentLoaded', function () {
    initializeFormInputs();
    initializeFileUpload();
    initializeStarRating();
    initializeDateInputs();
});

function initializeFormInputs() {
    // Floating label animation
    document.querySelectorAll('.form-control').forEach(input => {
        // More robust check for a value on page load
        if (input.value && input.value.trim() !== '') {
            input.closest('.input-group').classList.add('has-value');
        }

        input.addEventListener('focus', function () {
            this.closest('.input-group').classList.add('focused');
        });

        input.addEventListener('blur', function () {
            this.closest('.input-group').classList.remove('focused');
            if (this.value && this.value.trim() !== '') {
                this.closest('.input-group').classList.add('has-value');
            } else {
                this.closest('.input-group').classList.remove('has-value');
            }
        });

        input.addEventListener('input', function () {
            if (this.value && this.value.trim() !== '') {
                this.closest('.input-group').classList.add('has-value');
            } else {
                this.closest('.input-group').classList.remove('has-value');
            }
        });
    });
}

function initializeFileUpload() {
    const fileUploadArea = document.querySelector('.file-upload-area');
    if (!fileUploadArea) return; // Stop if this element isn't on the page

    const uploadZone = fileUploadArea.querySelector('#uploadZone');
    const fileInput = fileUploadArea.querySelector('.file-input');
    const imagePreview = fileUploadArea.querySelector('#imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeImageBtn = document.querySelector('.remove-image');

    if (uploadZone) {
        uploadZone.addEventListener('click', () => fileInput.click());
    }

    if (uploadZone) {
        uploadZone.addEventListener('dragover', function (e) {
            e.preventDefault();
            this.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', function (e) {
            e.preventDefault();
            this.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', function (e) {
            e.preventDefault();
            this.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', removeImage);
    }

    function handleFileSelect(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                previewImg.src = e.target.result;
                uploadZone.style.display = 'none';
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }

    function removeImage() {
        if (uploadZone) uploadZone.style.display = 'block';
        if (imagePreview) imagePreview.style.display = 'none';
        if (fileInput) fileInput.value = '';
    }
}


function initializeStarRating() {
    const ratingContainer = document.querySelector('.rating-container');
    if (!ratingContainer) return;

    const stars = ratingContainer.querySelectorAll('.star');
    const hiddenInput = document.getElementById('ratingValueInput');
    const ratingText = ratingContainer.querySelector('.rating-text');
    const ratingValueDisplay = ratingContainer.querySelector('.rating-value');
    const ratingValueEdit = ratingContainer.querySelector('.rating-value-edit');

    const ratingTexts = {
        0: 'No rating',
        1: 'Poor',
        2: 'Fair',
        3: 'Good',
        4: 'Very Good',
        5: 'Excellent'
    };

    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            const newRating = index + 1;
            updateRating(newRating);
        });
    });

    ratingValueDisplay.addEventListener('click', () => {
        ratingValueDisplay.style.display = 'none';
        ratingValueEdit.style.display = 'inline-block';
        ratingValueEdit.value = hiddenInput.value;
        ratingValueEdit.focus();
    });

    ratingValueEdit.addEventListener('blur', () => {
        saveAndCloseEdit();
    });
    ratingValueEdit.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            saveAndCloseEdit();
        }
    });

    function saveAndCloseEdit() {
        let newRating = parseFloat(ratingValueEdit.value);
        if (isNaN(newRating)) newRating = 0;
        if (newRating < 0) newRating = 0;
        if (newRating > 5) newRating = 5;

        updateRating(newRating);

        ratingValueEdit.style.display = 'none';
        ratingValueDisplay.style.display = 'inline-block';
    }

    function updateRating(newRating) {
        hiddenInput.value = newRating.toFixed(1);
        updateRatingDisplay(newRating);
    }

    function updateRatingDisplay(rating) {
        ratingValueDisplay.textContent = rating.toFixed(1);
        ratingText.textContent = ratingTexts[Math.round(rating)] || ratingTexts[0];

        stars.forEach((star, index) => {
            const starFill = star.querySelector('.bxs-star');
            const turn = index + 1;

            if (turn <= rating) {
                starFill.style.width = '100%';
            } else if (turn > rating && turn - 1 < rating) {
                const decimalPart = (rating - (turn - 1)) * 100;
                starFill.style.width = `${decimalPart}%`;
            } else {
                starFill.style.width = '0%';
            }
        });
    }

    updateRating(parseFloat(hiddenInput.value));
}


function initializeDateInputs() {
    const dateInputs = document.querySelectorAll('.date-input');

    dateInputs.forEach(input => {
        if (!input.value) {
            input.type = 'text';
        }

        input.addEventListener('focus', () => {
            input.type = 'date';
        });

        input.addEventListener('blur', () => {
            if (!input.value) {
                input.type = 'text';
            }
        });
    });
}
