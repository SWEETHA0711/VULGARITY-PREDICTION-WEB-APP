const socket = io();

const registerBtn = document.getElementById('register-btn');
const phoneNumberInput = document.getElementById('phone-number');
const chatForm = document.getElementById('chat-form');
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const recipientInput = document.getElementById('recipient-input');


// Register user with their phone number
registerBtn.addEventListener('click', () => {
    const phoneNumber = phoneNumberInput.value.trim();
    if (phoneNumber) {
        socket.emit('register', phoneNumber);
        alert(`Registered as ${phoneNumber}`);
    }
});

// Listen for form submission to send chat message
chatForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const msg = messageInput.value;
    const recipient = recipientInput.value;

    if (msg && recipient) {
        // Show the message on the sender's side immediately
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', 'sender'); // Class for sender messages
        messageElement.innerText = `${phoneNumberInput.value}: ${msg}`; // Display sender's name
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message

        socket.emit('chatMessage', { to: recipient, msg });
        messageInput.value = ''; // Clear the input field
        recipientInput.value = ''; // Clear the recipient field
        messageInput.focus();
    }
});

// Listen for chatMessage events from the server (for non-vulgar messages)
socket.on('chatMessage', ({ from, msg }) => {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'receiver'); // Class for receiver messages
    messageElement.innerText = `${from}: ${msg}`;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
});

// Listen for vulgarMessageAlert events from the server
socket.on('vulgarMessageAlert', ({ from, msg, prediction }) => {
    const messageElement = document.createElement('div');
    messageElement.classList.add('vulgar-alert');

  
    // Create alert message asking whether to show or hide the vulgar message
    messageElement.innerHTML = `
        <div><strong>${from}</strong> attempted to send a potentially vulgar message!</div>
        <div><strong>Toxicity:</strong> ${prediction.toxicity}%</div>
        <div><strong>Severe Toxicity:</strong> ${prediction.severe_toxicity}%</div>
        <div><strong>Obscene:</strong> ${prediction.obscene}%</div>
        <div><strong>Threat:</strong> ${prediction.threat}%</div>
        <div><strong>Insult:</strong> ${prediction.insult}%</div>
        <div><strong>Identity Hate:</strong> ${prediction.identity_hate}%</div>
        <button class="show-message-btn">Show Message</button>
        <button class="hide-message-btn">Hide Message</button>
    `;

    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message

    // Show/Hide buttons functionality
    const showBtn = messageElement.querySelector('.show-message-btn');
    const hideBtn = messageElement.querySelector('.hide-message-btn');

    showBtn.addEventListener('click', () => {
        const vulgarMessageElement = document.createElement('div');
        vulgarMessageElement.classList.add('message', 'receiver'); // Class for receiver messages
        vulgarMessageElement.innerText = `${from}: ${msg}`;
        chatBox.appendChild(vulgarMessageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
        messageElement.remove(); // Remove the alert
    });

    hideBtn.addEventListener('click', () => {
        messageElement.remove(); // Remove the alert without showing the message
    });
});
