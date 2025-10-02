document.addEventListener("DOMContentLoaded", function() {
    const changePhotoToggle = document.getElementById('change-photo-toggle');
    const photoUploadForm = document.getElementById('photo-upload-form');

    if (changePhotoToggle && photoUploadForm) {
        changePhotoToggle.addEventListener('click', function() {
            photoUploadForm.classList.toggle('active'); // Добавляем/удаляем класс active
        });
    }
});
