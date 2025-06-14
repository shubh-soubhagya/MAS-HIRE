document.addEventListener('DOMContentLoaded', function() {
    // Element references
    const jdUpload = document.getElementById('jd-upload');
    const jdFile = document.getElementById('jd-file');
    const jdStatus = document.getElementById('jd-status');
    
    const cvUpload = document.getElementById('cv-upload');
    const cvFiles = document.getElementById('cv-files');
    const cvStatus = document.getElementById('cv-status');
    
    const processJdCheckbox = document.getElementById('process-jd');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    const statusSection = document.getElementById('status-section');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const statusMessage = document.getElementById('status-message');
    
    const downloadSection = document.getElementById('download-section');
    const downloadCvAnalysis = document.getElementById('download-cv-analysis');
    const downloadShortlisted = document.getElementById('download-shortlisted');

    let statusInterval;
    let jdUploaded = false;
    let cvUploaded = false;

    // File upload handlers
    setupFileUpload(jdUpload, jdFile, 'job_descriptions', jdStatus, (success) => {
        jdUploaded = success;
        updateAnalyzeButton();
    });

    setupFileUpload(cvUpload, cvFiles, 'cvs', cvStatus, (success) => {
        cvUploaded = success;
        updateAnalyzeButton();
    });

    // Analyze button click handler
    analyzeBtn.addEventListener('click', function() {
        if (!jdUploaded || !cvUploaded) {
            showNotification('Please upload both job descriptions and CV files first', 'error');
            return;
        }

        startAnalysis();
    });

    // Download button handlers
    downloadCvAnalysis.addEventListener('click', () => downloadFile('cv_analysis'));
    downloadShortlisted.addEventListener('click', () => downloadFile('shortlisted'));

    function setupFileUpload(uploadArea, fileInput, endpoint, statusDiv, callback) {
        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (endpoint === 'job_descriptions') {
                if (files.length === 1 && files[0].name.endsWith('.csv')) {
                    fileInput.files = files;
                    handleFileUpload(files, endpoint, statusDiv, callback);
                } else {
                    showStatus(statusDiv, 'Please drop a single CSV file', 'error');
                }
            } else {
                const pdfFiles = Array.from(files).filter(file => file.name.endsWith('.pdf'));
                if (pdfFiles.length > 0) {
                    handleFileUpload(pdfFiles, endpoint, statusDiv, callback);
                } else {
                    showStatus(statusDiv, 'Please drop PDF files only', 'error');
                }
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            handleFileUpload(e.target.files, endpoint, statusDiv, callback);
        });
    }

    function handleFileUpload(files, endpoint, statusDiv, callback) {
        const formData = new FormData();
        
        if (endpoint === 'job_descriptions') {
            formData.append('file', files[0]);
        } else {
            for (let file of files) {
                formData.append('files', file);
            }
        }

        showStatus(statusDiv, 'Uploading...', 'info');

        fetch(`/upload_${endpoint}`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showStatus(statusDiv, data.message, 'success');
                callback(true);
            } else {
                showStatus(statusDiv, data.message, 'error');
                callback(false);
            }
        })
        .catch(error => {
            showStatus(statusDiv, 'Upload failed: ' + error.message, 'error');
            callback(false);
        });
    }

    function showStatus(statusDiv, message, type) {
        statusDiv.textContent = message;
        statusDiv.className = `upload-status ${type}`;
        statusDiv.style.display = 'block';
    }

    function updateAnalyzeButton() {
        analyzeBtn.disabled = !(jdUploaded && cvUploaded);
    }

    function startAnalysis() {
        analyzeBtn.disabled = true;
        statusSection.style.display = 'block';
        statusSection.classList.add('fade-in');
        downloadSection.style.display = 'none';

        const processJd = processJdCheckbox.checked;

        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ process_jd: processJd })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                startStatusPolling();
            } else {
                showNotification('Failed to start processing', 'error');
                analyzeBtn.disabled = false;
            }
        })
        .catch(error => {
            showNotification('Error: ' + error.message, 'error');
            analyzeBtn.disabled = false;
        });
    }

    function startStatusPolling() {
        statusInterval = setInterval(() => {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    updateStatus(data);
                    
                    if (data.stage === 'complete') {
                        clearInterval(statusInterval);
                        showDownloadSection();
                        analyzeBtn.disabled = false;
                        showNotification('Analysis completed successfully!', 'success');
                    } else if (data.stage === 'error') {
                        clearInterval(statusInterval);
                        analyzeBtn.disabled = false;
                        showNotification('Processing failed: ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Status polling error:', error);
                });
        }, 1000);
    }

    function updateStatus(data) {
        progressFill.style.width = data.progress + '%';
        progressText.textContent = data.progress + '%';
        statusMessage.textContent = data.message;
    }

    function showDownloadSection() {
        downloadSection.style.display = 'block';
        downloadSection.classList.add('fade-in');
    }

    function downloadFile(type) {
        window.location.href = `/download/${type}`;
    }

    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        
        if (type === 'success') {
            notification.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
        } else if (type === 'error') {
            notification.style.background = 'linear-gradient(135deg, #f56565 0%, #e53e3e 100%)';
        } else {
            notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        }
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 5000);
    }

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1