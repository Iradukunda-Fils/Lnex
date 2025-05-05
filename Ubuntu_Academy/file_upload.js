(function() {
    const fileInput = document.getElementById('fileInput');
    const uploadProgressBar = document.getElementById('uploadProgressBar');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadButton = document.getElementById('uploadButton');
    const descriptionInput = document.getElementById('descriptionInput'); // Add description input.
  
    uploadButton.addEventListener('click', () => {
      const file = fileInput.files[0];
      if (!file) {
        uploadStatus.textContent = 'Please select a file.';
        return;
      }
      uploadFile(file, '/upload/');
    });
  
    function uploadFile(file, uploadUrl) {
      const xhr = new XMLHttpRequest();
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', descriptionInput.value); // Add description to form data.
  
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          uploadProgressBar.value = percentComplete;
        }
      });
  
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          uploadStatus.textContent = 'Upload successful!';
          const response = JSON.parse(xhr.responseText);
          console.log("Uploaded file ID:", response.id); // Access the id of the uploaded file.
        } else {
          uploadStatus.textContent = `Upload failed: ${xhr.status} ${xhr.statusText}`;
        }
      };
  
      xhr.onerror = () => {
        uploadStatus.textContent = 'An error occurred during upload.';
      };
  
      xhr.open('POST', uploadUrl);
      xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
      xhr.send(formData);
    }
  
    function getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }
  })();