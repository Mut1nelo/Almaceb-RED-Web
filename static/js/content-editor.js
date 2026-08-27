document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.querySelector('.content-file-input');
    const preview = document.querySelector('.content-image-preview');
    const placeholder = document.querySelector('.content-upload-placeholder');

    if (!fileInput || !preview || !placeholder) return;

    fileInput.addEventListener('change', () => {
        const [file] = fileInput.files || [];
        if (!file) return;

        const objectUrl = URL.createObjectURL(file);
        preview.src = objectUrl;
        preview.hidden = false;
        placeholder.hidden = true;
        preview.addEventListener('load', () => URL.revokeObjectURL(objectUrl), { once: true });
    });
});
