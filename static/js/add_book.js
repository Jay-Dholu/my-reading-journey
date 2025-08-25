document.addEventListener('DOMContentLoaded', function() {
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

        input.addEventListener('focus', function() {
            this.closest('.input-group').classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.closest('.input-group').classList.remove('focused');
            if (this.value && this.value.trim() !== '') {
                this.closest('.input-group').classList.add('has-value');
            } else {
                this.closest('.input-group').classList.remove('has-value');
            }
        });

        input.addEventListener('input', function() {
            if (this.value && this.value.trim() !== '') {
                this.closest('.input-group').classList.add('has-value');
            } else {
                this.closest('.input-group').classList.remove('has-value');
            }
        });
    });
}

function initializeFileUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.querySelector('.file-input');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const removeImageBtn = document.querySelector('.remove-image');

    // Click to upload
    if(uploadZone) {
      uploadZone.addEventListener('click', () => fileInput.click());
    }

    // Drag and drop
    if(uploadZone) {
      uploadZone.addEventListener('dragover', function(e) {
          e.preventDefault();
          this.classList.add('dragover');
      });

      uploadZone.addEventListener('dragleave', function(e) {
          e.preventDefault();
          this.classList.remove('dragover');
      });

      uploadZone.addEventListener('drop', function(e) {
          e.preventDefault();
          this.classList.remove('dragover');
          
          const files = e.dataTransfer.files;
          if (files.length > 0) {
              fileInput.files = files;
              handleFileSelect(files[0]);
          }
      });
    }

    // File input change
    if(fileInput) {
      fileInput.addEventListener('change', function(e) {
          if (e.target.files.length > 0) {
              handleFileSelect(e.target.files[0]);
          }
      });
    }

    // Remove image button
    if(removeImageBtn) {
      removeImageBtn.addEventListener('click', removeImage);
    }

    function handleFileSelect(file) {
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                uploadZone.style.display = 'none';
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }

    function removeImage() {
        if(uploadZone) uploadZone.style.display = 'block';
        if(imagePreview) imagePreview.style.display = 'none';
        if(fileInput) fileInput.value = '';
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

    // --- Event Listeners ---

    // Handle star clicks
    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            const newRating = index + 1;
            updateRating(newRating);
        });
    });

    // Handle clicking the number to edit it
    ratingValueDisplay.addEventListener('click', () => {
        ratingValueDisplay.style.display = 'none';
        ratingValueEdit.style.display = 'inline-block';
        ratingValueEdit.value = hiddenInput.value;
        ratingValueEdit.focus();
    });

    // Handle saving the edited number
    ratingValueEdit.addEventListener('blur', () => { // When clicking away
        saveAndCloseEdit();
    });
    ratingValueEdit.addEventListener('keydown', (e) => { // When pressing Enter
        if (e.key === 'Enter') {
            saveAndCloseEdit();
        }
    });

    // --- Helper Functions ---

    function saveAndCloseEdit() {
        let newRating = parseFloat(ratingValueEdit.value);
        // Validate and clamp the value between 0 and 5
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
        // Update the number "0.0"
        ratingValueDisplay.textContent = rating.toFixed(1);
        
        // Update the text "Good", "Excellent", etc.
        ratingText.textContent = ratingTexts[Math.round(rating)] || ratingTexts[0];

        // Update the stars to show partial fills
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

    // Initialize the display on page load
    updateRating(parseFloat(hiddenInput.value));
}


function initializeDateInputs() {
    const dateInputs = document.querySelectorAll('.date-input');

    dateInputs.forEach(input => {
        // Hide the native date placeholder on page load
        input.type = 'text';

        input.addEventListener('focus', () => {
            // Switch to date type when user clicks in
            input.type = 'date';
        });

        input.addEventListener('blur', () => {
            // If the input is empty, switch back to text
            if (!input.value) {
                input.type = 'text';
            }
        });
    });
}
