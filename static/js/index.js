function openDeleteModal(deleteUrl, bookTitle) {
    document.getElementById('bookNameToDelete').textContent = `"${bookTitle}"`;
    document.getElementById('confirmDeleteLink').href = deleteUrl;
    document.getElementById('deleteModal').style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('deleteModal');
    if (event.target == modal) {
        closeDeleteModal();
    }
}
