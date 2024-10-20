function displayFileName(event) {
    const fileInput = event.target;
    const fileNameDisplay = document.getElementById('file-name');
    const fileName = fileInput.files[0]?.name || 'No file chosen';
    fileNameDisplay.textContent = fileName;
  }


  function showMessage(event) {
    event.preventDefault(); // Prevent default form submission

    const fileInput = document.getElementById("file-upload");
    if (!fileInput.files.length) {
      // Show modal if no file is selected
      document.getElementById("modal").classList.remove("hidden");
      return false; // Prevent showing the message
    }

    // Show message if a file is selected
    const messageDiv = document.getElementById("message");
    messageDiv.classList.remove("hidden"); // Show the message container
    document.getElementById("modal").classList.add("hidden"); // Hide the modal if a file is selected

    return true; // Allow form submission
  }

  function closeModal() {
    document.getElementById("modal").classList.add("hidden");
  }
  //salam ilyas