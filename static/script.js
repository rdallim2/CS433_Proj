function sendMessage() {
    const prompt = document.getElementById('prompt').value;
    if (!prompt) return;
    console.log("Recieved prompt");

    // Display the user's message in the chat
    const messagesDiv = document.getElementById('messages');
    const userMessage = document.createElement('div');
    userMessage.textContent = `You: ${prompt}`;
    userMessage.style.textAlign = "left"; // Align user's message to the left
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
            llmResponse.style.textAlign = "right"; 
            messagesDiv.appendChild(llmResponse);
            console.log("Response should now be displayed.")
        }
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
