document.addEventListener('DOMContentLoaded', () => {
    const fileInputWrappers = document.querySelectorAll('.file-input-wrapper');

    fileInputWrappers.forEach(wrapper => {
        const fileInput = wrapper.querySelector('input[type="file"]');
        const fileName = wrapper.querySelector('.file-name');

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

        fileInput.addEventListener('change', updateFileName);
        updateFileName();
    });
});
