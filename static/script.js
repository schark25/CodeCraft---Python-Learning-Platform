function sendMessage() {
    const input = document.getElementById('chat-input');
    const chatContent = document.querySelector('.chat-content');
    const message = input.value.trim();
    input.value = '';

    if (message) {
        const userMessageDiv = document.createElement('div');
        userMessageDiv.innerHTML = `<strong class="user-message">User:</strong> ${message}`;
        userMessageDiv.className = 'user-message';
        chatContent.appendChild(userMessageDiv);

        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache' // Disabling cache to ensure fresh responses
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            if (!data.response || data.response === "") {
                throw new Error("Empty response from server"); // Handling empty or undefined responses
            }
            const responseDiv = document.createElement('div');
            responseDiv.innerHTML = `<strong>CodeCraft:</strong>`;
            data.response.split('\n').forEach(paragraph => {
                const responseParagraph = document.createElement('p');
                responseParagraph.textContent = paragraph;
                responseDiv.appendChild(responseParagraph);
            });
            chatContent.appendChild(responseDiv);
            chatContent.scrollTop = chatContent.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            const errorMessage = document.createElement('p');
            errorMessage.textContent = "Failed to fetch response or invalid response received.";
            chatContent.appendChild(errorMessage);
        });
    }
}   



var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
    mode: "python",
    theme: "default",
    lineNumbers: true
});

function runCode() {
    var code = editor.getValue();
    console.log("Sending code to run:", code);
    fetch('/run_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: code }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Server error:", data.error);
            throw new Error(data.error); // Properly handle server errors
        }
        console.log("Execution result:", data.result);
        document.getElementById('output').textContent = data.result || "No output returned.";
    })
    .catch(error => {
        console.error('Client or network error:', error);
        document.getElementById('output').textContent = "Error executing code.";
    });
}


// Function to send the code to the chatbot
function sendCodeToChatbot() {
    const chatContent = document.querySelector('.chat-content');
    const code = editor.getValue();

    if (code) {
        // Display the code being sent to the chatbot
        const userCodeDiv = document.createElement('div');
        userCodeDiv.innerHTML = `<strong class="user-message">User:</strong> ${code}`;
        userCodeDiv.className = 'user-message';
        chatContent.appendChild(userCodeDiv);

        fetch('/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: code }),
        })
        .then(response => response.json())
        .then(data => {
            const responseDiv = document.createElement('div');
            responseDiv.innerHTML = `<strong>CodeCraft:</strong>`;

            // Add response from the chatbot
            const paragraphs = data.response.split('\n');
            paragraphs.forEach(paragraph => {
                const responseParagraph = document.createElement('p');
                responseParagraph.textContent = paragraph;
                responseDiv.appendChild(responseParagraph);
            });

            chatContent.appendChild(responseDiv);
            chatContent.scrollTop = chatContent.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            const errorMessage = document.createElement('p');
            errorMessage.textContent = "Failed to fetch response from chatbot.";
            chatContent.appendChild(errorMessage);
        });
    }
}

// This script listens for keypresses on the entire document
document.addEventListener('keypress', function (e) {
    
    if (e.key === 'Enter' || e.keyCode === 13) {
        // Find the active or focused element
        var activeElement = document.activeElement;

        // Check if the active element is a button or an input field of type text
        if (activeElement.tagName.toLowerCase() === 'button') {
            activeElement.click(); // Click the active button
        } else if (activeElement.tagName.toLowerCase() === 'input' && activeElement.type === 'text') {
            // Find the next button to click
            var closestButton = activeElement.parentNode.querySelector('button');
            if (closestButton) {
                closestButton.click(); // Click the closest button
            }
        }
    }
});

