function sendMessage() {
    const prompt = document.getElementById('prompt').value;
    if (!prompt) return;
    console.log("Recieved prompt");

    // Display the user's message in the chat
    const messagesDiv = document.getElementById('messages');
    const userMessage = document.createElement('div');
    userMessage.textContent = `You: ${prompt}`;
    userMessage.classList.add("user-message");
    messagesDiv.appendChild(userMessage);

    // Clear the input field after sending the message
    document.getElementById('prompt').value = '';

    // Make an AJAX request to the Flask server
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt: prompt })
    })

    .then(response => response.json())
    .then(data => {
        if (data.error) {
            const errorMessage = document.createElement('div');
            errorMessage.textContent = `Error: ${data.error}`;
            errorMessage.style.textAlign = "center";
            messagesDiv.appendChild(errorMessage);
            console.log("data error occured");
        } else {
            const llmResponse = document.createElement('div');
            llmResponse.textContent = `LLM: ${data.response}`;
            llmResponse.classList.add("llm-reponse");
            messagesDiv.appendChild(llmResponse);
            console.log("Response should now be displayed.")
        }
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

document.getElementById('prompt').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});


function toggleMenu() {
    const menuItems = document.getElementById("menuItems");
    const arrow = document.getElementById("arrow");
    const infoBox = document.getElementById("info");

    if (menuItems.style.display === "block") {
      menuItems.style.display = "none";
      infoBox.style.display = "none"; // Hide info when collapsing
      arrow.innerHTML = "&#9660;"; // Down arrow
    } else {
      menuItems.style.display = "block";
      arrow.innerHTML = "&#9650;"; // Up arrow
    }
  }

  // Display level info when a level is clicked
  function showInfo(event, level) {
    // Prevent click from toggling the menu header
    event.stopPropagation();
    const infoBox = document.getElementById("info");
    const levelInfo = {
      1: "Level 1: Stay alert and move fast!",
      2: "Level 2: Watch out for hidden traps!",
      3: "Level 3: Use your resources wisely.",
      4: "Level 4: Speed is key in this level.",
      5: "Level 5: Time your moves carefully.",
      6: "Level 6: Use power-ups strategically!"
    };

    infoBox.innerText = levelInfo[level];
    infoBox.style.display = "block";
  }

  document.querySelectorAll('.level').forEach(level => {
    level.addEventListener('click', () => {
      document.querySelectorAll('.level').forEach(item => item.classList.remove('selected'));
      level.classList.add('selected');
    });
  });