/**
 * Backup Management System - JavaScript Helpers
 */

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alert banners after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

/**
 * Toggle Add Record form visibility on records page
 */
function toggleAddForm() {
    const card = document.getElementById('addRecordCard');
    if (card) {
        if (card.style.display === 'none' || card.style.display === '') {
            card.style.display = 'block';
            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            const nameInput = document.getElementById('name');
            if (nameInput) nameInput.focus();
        } else {
            card.style.display = 'none';
        }
    }
}

/**
 * Display selected filename in upload zone
 */
function updateFileName(input) {
    const displayDiv = document.getElementById('fileSelectedName');
    if (displayDiv && input.files && input.files[0]) {
        const file = input.files[0];
        displayDiv.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    }
}
