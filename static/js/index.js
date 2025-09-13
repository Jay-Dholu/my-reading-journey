function openDeleteModal(deleteUrl, bookTitle) {
    const deleteForm = document.getElementById('deleteForm');
    if(deleteForm) {
        deleteForm.action = deleteUrl;
    }
    
    const bookNameElement = document.getElementById('bookNameToDelete');
    if(bookNameElement) {
        bookNameElement.textContent = `"${bookTitle}"`;
    }

    const modal = document.getElementById('deleteModal');
    if(modal) {
        modal.style.display = 'flex';
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if(modal) {
        modal.style.display = 'none';
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target == modal) {
        closeDeleteModal();
    }
}