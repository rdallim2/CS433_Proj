function sendMessage() {
    const prompt = document.getElementById('prompt').value;
    if (!prompt) return;
    console.log("Recieved prompt");

    // Display user message
    const messagesDiv = document.getElementById('messages');
    const userMessage = document.createElement('div');
    userMessage.textContent = `You: ${prompt}`;
    userMessage.classList.add("user-message");
    messagesDiv.appendChild(userMessage);

    // Clear input field
    document.getElementById('prompt').value = '';

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
            llmResponse.innerHTML = `LLM: ${data.message}`;
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

  function showInfo(event, level) {
    return new Promise((resolve, reject) => {
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
          console.log('Level set:', data);
          const messagesDiv = document.getElementById('messages');
          messagesDiv.innerHTML = `<div class="llm-response">LLM: ${data.message.content}</div>`;
          resolve();
      })
      .catch(error => {
          console.error('Error setting level:', error);
      });
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
    if (window.initialMessage && window.initialMessage.content) {
        const llmResponse = document.createElement('div');
        llmResponse.innerHTML = `LLM: ${window.initialMessage.content}`;
        llmResponse.classList.add("llm-response");
        messagesDiv.appendChild(llmResponse);
    }
  });



function showData(event, level) {
  const container = document.querySelector('.data-items');
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

        const editButton = document.createElement('button');
        editButton.textContent = 'Edit';
        const editContainer = document.createElement('div');
        editContainer.style.display = 'none';
        const editInput = document.createElement('input');
        editInput.type = 'text';
        editInput.value = item.text;
        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save';

        saveButton.addEventListener('click', () => {
          const updatedText = editInput.value;
          
          fetch('/update_data', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: item.id, text: updatedText })
          })
          .then(response => response.json())
          .then(data => {
            if (data.message === "Update successful") {
              textEl.textContent = updatedText;
              editContainer.style.display = 'none';
            } else {
              alert("Failed to update data: " + (data.error || "Unknown error"));
            }
          })
          .catch(error => {
            console.error('Error:', error);
            alert("Error updating data");
          });
        });
        editButton.addEventListener('click', () => {
          if (editContainer.style.display === 'none') {
            editInput.value = textEl.textContent;
            editContainer.style.display = 'block';
          } else {
            editContainer.style.display = 'none';
          }
        });

        editContainer.appendChild(editInput);
        editContainer.appendChild(saveButton);
        
        itemDiv.appendChild(idEl);
        itemDiv.appendChild(textEl);
        dataList.appendChild(itemDiv);
        itemDiv.appendChild(editButton);
        itemDiv.appendChild(editContainer);
    });
    
    container.appendChild(dataList);
})
.catch(error => {
  console.error('Error:', error);
  container.innerHTML = `<div class="error">Error: ${error.message}</div>`;
});
}

function handleLevelClick(event, level) {
  document.querySelectorAll('.level').forEach(item => item.classList.remove('selected'));
  event.target.classList.add('selected');
  showInfo(event, level)
    .then(() => {
      console.log(`showInfo for level ${level} completed, now executing showData`);
      return showData(event, level);
    })
    .catch(error => console.error('Error in sequence:', error));
}

document.addEventListener("DOMContentLoaded", function () {
    const quizModal = document.getElementById("quizModal");
    const submitQuiz = document.getElementById("submitQuiz");

    function showQuiz() {
        quizModal.style.display = "block";
    }

    submitQuiz.addEventListener("click", function () {
        const answers = {};
        document.querySelectorAll(".quiz-question").forEach((questionDiv, index) => {
            const selectedOption = questionDiv.querySelector("input[name='quizOption" + index + "']:checked");
            answers[`Question ${index + 1}`] = selectedOption ? selectedOption.value : "No answer";
        });

        // Send answers to be saved
        fetch("/save_quiz_answers", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ answers: answers })
        })
        .then(response => response.json())
        .then(data => console.log("Quiz answers saved:", data))
        .catch(error => console.error("Error saving quiz answers:", error));

        quizModal.style.display = "none"; // Hide quiz modal
        startGame();
    });

    function startGame() {
        console.log("Game Starting...");

    }

    // Show quiz at the start of the game
    showQuiz();

    // Show quiz at the end of the game as well
    document.addEventListener("gameCompleted", function () {
        quizModal.querySelector("h2").textContent = "Quick Quiz Before You Finish";
        quizModal.style.display = "block";
    });
});


