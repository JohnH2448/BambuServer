const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadBtn = document.getElementById('uploadBtn');
const status = document.getElementById('status');

let selectedFile = null;

// Click to select file
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    handleFile(e.target.files[0]);
});

// Drag and drop events
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFile(e.dataTransfer.files[0]);
});

function handleFile(file) {
    if (!file) return;
    
    selectedFile = file;
    fileName.textContent = `${file.name}: (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    fileInfo.style.display = 'block';
    uploadBtn.style.display = 'inline-block';
    status.style.display = 'none';
}

// Upload file
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading...';
    status.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            showStatus('File uploaded successfully!', 'success');
            // Reset form
            selectedFile = null;
            fileInput.value = '';
            fileInfo.style.display = 'none';
            uploadBtn.style.display = 'none';
        } else {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
    } catch (error) {
        showStatus(`${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload File';
    }
});

function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
}
