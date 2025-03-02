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
            console.log("Data error occurred");
        } else {
            const llmResponse = document.createElement('div');
            llmResponse.textContent = `LLM: ${data.message}`;  // FIXED: Use "data.message"
            llmResponse.classList.add("llm-response");
            messagesDiv.appendChild(llmResponse);
            console.log("Response should now be displayed.");
        }
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    })
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
      1: "Tips for Level 1: ",
      2: "Tips for Level 2: ",
      3: "Tips for Level 3: ",
      4: "Tips for Level 4: ",
      5: "Tips for Level 5: ",
      6: "Tips for Level 6: "
    };

    infoBox.innerText = levelInfo[level];
    infoBox.style.display = "block";
    fetch('/set_level', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ level: level })
    })
    .then(response => response.json())
    .then(data => {
        // Optionally handle the server response if needed
        console.log('Level set:', data);
        // Reload the page with the new level
        window.location.reload();
    })
    .catch(error => {
        console.error('Error setting level:', error);
    });
  }

  document.querySelectorAll('.level').forEach(level => {
    level.addEventListener('click', () => {
      document.querySelectorAll('.level').forEach(item => item.classList.remove('selected'));
      level.classList.add('selected');
    });
  });

  document.addEventListener("DOMContentLoaded", function () {
    const messagesDiv = document.getElementById('messages');
    
    // Use the global variable set in the HTML
    if (window.initialMessage && window.initialMessage.content) {
        const llmResponse = document.createElement('div');
        llmResponse.textContent = `LLM: ${window.initialMessage.content}`;
        llmResponse.classList.add("llm-response");
        messagesDiv.appendChild(llmResponse);
    }
  });


function showData(event, level) {
  const container = document.querySelector('.empty-space');
  container.innerHTML = '<div class="loading">Loading data...</div>';
  fetch('/get_data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ level: level })
  }).then(response => response.json()) 
  .then(responseData => {
    container.innerHTML = ''; 
    
    if (!responseData.data || responseData.data.length === 0) {
        container.innerHTML = '<div class="no-data">No data found</div>';
        return;
    }
    const dataList = document.createElement('div');
    dataList.className = 'data-list';
    
    responseData.data.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'data-item';
        
        const idEl = document.createElement('strong');
        idEl.textContent = `ID: ${item.id}`;
        
        const textEl = document.createElement('p');
        textEl.textContent = item.text;
        
        itemDiv.appendChild(idEl);
        itemDiv.appendChild(textEl);
        dataList.appendChild(itemDiv);
    });
    
    container.appendChild(dataList);
})
.catch(error => {
  console.error('Error:', error);
  container.innerHTML = `<div class="error">Error: ${error.message}</div>`;
});
}
