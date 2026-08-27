document.addEventListener('DOMContentLoaded', () => {
    const fileInputWrappers = document.querySelectorAll('.file-input-wrapper');

    fileInputWrappers.forEach(wrapper => {
        const fileInput = wrapper.querySelector('input[type="file"]');
        const fileName = wrapper.querySelector('.file-name');
        const imagePreview = wrapper.querySelector('.file-input-preview');

        if (!fileInput || !fileName) {
            return;
        }

        const emptyText = fileName.dataset.emptyText || 'Ningún archivo seleccionado';

        const updateFileName = () => {
            const selectedFiles = fileInput.files;

            if (!selectedFiles || selectedFiles.length === 0) {
                fileName.textContent = emptyText;
                return;
            }

            fileName.textContent = selectedFiles.length === 1
                ? selectedFiles[0].name
                : `${selectedFiles.length} archivos seleccionados`;
        };

        const updateImagePreview = () => {
            const [selectedFile] = fileInput.files || [];

            if (!imagePreview || !selectedFile || !selectedFile.type.startsWith('image/')) {
                return;
            }

            const objectUrl = URL.createObjectURL(selectedFile);
            imagePreview.src = objectUrl;
            imagePreview.hidden = false;

            const releaseObjectUrl = () => URL.revokeObjectURL(objectUrl);
            imagePreview.addEventListener('load', releaseObjectUrl, { once: true });
            imagePreview.addEventListener('error', releaseObjectUrl, { once: true });
        };

        fileInput.addEventListener('change', () => {
            updateFileName();
            updateImagePreview();
        });

        updateFileName();
    });
});
