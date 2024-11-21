// Define the autoScroll function
function autoScroll() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

function sendMessage() {
    let messageInput = document.getElementById('message-input');
    let message = messageInput.value;

    // Display the user message and auto-scroll
    displayMessage('user', message);
    autoScroll();

    // Get the selected function from the dropdown menu
    let functionSelect = document.getElementById('function-select');
    let selectedFunction = functionSelect.value;

    // Send an AJAX request to the Flask API endpoint based on the selected function
    let xhr = new XMLHttpRequest();
    let url;

    switch (selectedFunction) {
        case 'search':
            url = '/search';
            break;
        case 'kbanswer':
            url = '/kbanswer';
            break;
        case 'answer':
            url = '/answer';
            break;
        default:
            url = '/answer';
    }

    xhr.open('POST', url);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function () {
        if (xhr.status === 200) {
            let response = JSON.parse(xhr.responseText);
            // Display the assistant message and auto-scroll
            displayMessage('assistant', response.message);
            autoScroll();
        }
    };
    xhr.send(JSON.stringify({ message: message }));

    // Clear the input field
    messageInput.value = '';
}

function displayMessage(sender, message) {
    let chatContainer = document.getElementById('chat-container');
    let messageDiv = document.createElement('div');

    if (sender === 'assistant') {
        messageDiv.classList.add('assistant-message');

        // Create a span for the Chatbot text
        let chatbotSpan = document.createElement('span');
        chatbotSpan.innerHTML = "<b>Chatbot:</b> ";
        messageDiv.appendChild(chatbotSpan);

        // Append the message to the Chatbot span
        messageDiv.innerHTML += message;
    } else {
        messageDiv.classList.add('user-message');

        let userSpan = document.createElement('span');
        userSpan.innerHTML = "<b>User:</b> ";
        messageDiv.appendChild(userSpan);

        // Append the message to the span
        messageDiv.innerHTML += message;
    }

    // Create a timestamp element
    let timestamp = document.createElement('span');
    timestamp.classList.add('timestamp');
    let currentTime = new Date().toLocaleTimeString();
    timestamp.innerText = " [" + currentTime + "]";
    messageDiv.appendChild(timestamp);

    chatContainer.appendChild(messageDiv);

    // Auto-scroll after appending a new message
    autoScroll();
}

function clearChat() {
    document.getElementById('chat-container').replaceChildren();
}

// Handle button click event
let sendButton = document.getElementById('send-btn');
sendButton.addEventListener('click', sendMessage);

// Handle clear button event
let clearButton = document.getElementById('clear-btn');
clearButton.addEventListener('click', clearChat);
