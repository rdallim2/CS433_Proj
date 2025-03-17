function sendMessage() {
    const user_input = document.getElementById('prompt').value;
    if (!user_input.trim()) return;

    const userMessages = document.getElementById('messages')
    const userMessage = document.createElement('div')
    userMessage.classList.add("user-message");
    userMessage.innerHTML = `You: ${prompt}`; 
    userMessages.appendChild(userMessage);

    document.getElementById('prompt').value = "";
    fetch('/ask', {
        "method": "POST", 
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify({prompt: prompt})
    })

    .then(response => response.json())
    .then(data => {
        const llmMessage = document.createElement('div');
        llmMessage.innerHTML = `LLM: ${data.message}`;
        llmMessage.classList.add("llm-response"); 
        userMessages.appendChild(llmMessage);

        // Check if the game is complete or if end quiz should be triggered
        if (data.success && (data.game_complete || data.trigger_end_quiz)) {
            console.log("Game completed! Triggering end quiz...");
            // Dispatch a custom event to trigger the quiz modal
            document.dispatchEvent(new Event("gameCompleted"));
        }
    })
}

document.getElementById('prompt').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});


function showInfo(event, level) {
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
    return fetch('/set_level', {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify({ level: level })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Level set:', data);
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = `<div class="llm-response">LLM: ${data.message.content}</div>`;
        return data; // Return data to allow further chaining
    })
    .catch(error => {
        console.error('Error setting level:', error);
        throw error; // Rethrow the error to be caught in the promise chain
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
    const container = document.querySelector(".data-items");
    container.innerHTML = '<div class="loading">Loading data...</div>';
    return fetch('/get_data', {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify({level: level})
    })
    .then(response => response.json())
    .then(responseData => {
        container.innerHTML = "";
        const dataDiv = document.createElement('div');
        dataDiv.className = "data-div";

        responseData.data.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = "data-item";
            
            const itemText = document.createElement('p');
            itemText.textContent = item.text;

            const editButton = document.createElement('button');
            editButton.textContent = "Edit Text";

            const editContainer = document.createElement('div');
            editContainer.style.display = "none";

            const editInput = document.createElement('input');
            editInput.type = "text";
            editInput.value = item.text;
            
            const saveButton = document.createElement('button');
            saveButton.textContent = "Save Text";

            saveButton.addEventListener("click", () => {
                const updatedText = editInput.value;
                fetch('/update_data', {
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"},
                    "body": JSON.stringify({ id: item.id, text: updatedText })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message === "Update successful") {
                        itemText.textContent = updatedText;
                        editContainer.style.display = "none";
                    }
                });
            });
            editButton.addEventListener("click", () => {
                if (editContainer.style.display === "none") {
                    editInput.value = itemText.textContent;
                    editContainer.style.display = 'block';
                }
            });
            editContainer.appendChild(editInput);
            editContainer.appendChild(saveButton);

            itemDiv.appendChild(itemText);
            dataDiv.appendChild(itemDiv);
            itemDiv.appendChild(editButton);
            itemDiv.appendChild(editContainer);
        });
        container.appendChild(dataDiv);
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