const ws = new WebSocket("ws://localhost:8000/ws");
let username;

document.getElementById("usernameForm").addEventListener("submit", function (event) {
    event.preventDefault();
    username = document.getElementById("username").value;
    ws.send(username);

    // Show chat container and hide the username form
    document.getElementById("usernameForm").style.display = "none";
    document.getElementById("container").style.display = "flex";
});

document.getElementById("messageForm").addEventListener("submit", function (event) {
    event.preventDefault();
    const message = document.getElementById("messageInput").value;
    ws.send(message);
    document.getElementById("messageInput").value = "";
});

function scrollToBottom(chatbox) {
    chatbox.scrollTop = chatbox.scrollHeight;
}

function updateOnlineUsers(users) {
    const usersList = document.getElementById("online-users");
    usersList.innerHTML = "";  // Clear existing list
    users.forEach(user => {
        const li = document.createElement("li");
        li.textContent = user;
        li.classList.add("user-item");
        usersList.appendChild(li);
    });
}
// Function to render a message (harmful or regular)
function renderMessage(msg, chatbox) {
    console.log("Rendering message:", msg, "msg.data: ", msg.data);
    const messageId = `message-${msg.data.timestamp}`;
    console.log(messageId)

    // Create message container div
    const messageDiv = document.createElement("div");
    messageDiv.id = messageId;
    messageDiv.classList.add("message-item"); // Shared style for all messages

    // Create the username span (unblurred)
    const usernameSpan = document.createElement("strong");
    usernameSpan.textContent = `${msg.data.user}: `;

    console.log(msg.subtype);
    if (msg.subtype === "harmful") {
        const harmfulMessageContentText = splitMessage(msg.data.content, 80); // Adjust maxLength to something reasonable

        // Harmful message content (blurred by default)
        const harmfulMessageContent = document.createElement("span");
        harmfulMessageContent.classList.add("blurred");
        harmfulMessageContent.style.filter = "blur(5px)";
        harmfulMessageContent.style.transition = "filter 0.3s ease";
        harmfulMessageContent.innerHTML = harmfulMessageContentText; // Properly split message

        // Create popup for classification (good/bad)
        const harmfulPopup = createPopup(harmfulMessageContent, messageDiv);

        // Append elements: username (unblurred), harmful message content (blurred), and popup
        messageDiv.appendChild(usernameSpan);
        messageDiv.appendChild(harmfulMessageContent);
        messageDiv.appendChild(harmfulPopup);
    } else {
        // Regular message content (no blur or popup)
        const regularMessageContent = document.createElement("span");
        regularMessageContent.innerHTML = splitMessage(msg.data.content, 80); // Properly split message

        // Append elements: username and regular message content
        messageDiv.appendChild(usernameSpan);
        messageDiv.appendChild(regularMessageContent);
    }

    // Append message div to the chatbox and scroll down
    chatbox.appendChild(messageDiv);
    scrollToBottom(chatbox);
}

// Function to create a classification popup for harmful messages
function createPopup(harmfulMessageContent, messageDiv) {
    const harmfulPopup = document.createElement("div");
    harmfulPopup.classList.add("popup");

    const harmfulPopupText = document.createElement("p");
    harmfulPopupText.textContent = "Is this message good or bad?";
    harmfulPopup.appendChild(harmfulPopupText);

    // Add Good and Bad buttons
    const harmfulGoodBtn = document.createElement("button");
    harmfulGoodBtn.textContent = "✔";
    harmfulGoodBtn.classList.add("good-btn");

    const harmfulBadBtn = document.createElement("button");
    harmfulBadBtn.textContent = "✖";
    harmfulBadBtn.classList.add("bad-btn");

    harmfulPopup.appendChild(harmfulGoodBtn);
    harmfulPopup.appendChild(harmfulBadBtn);

    // Event listeners for classification (Good/Bad)
    harmfulGoodBtn.addEventListener('click', function () {
        harmfulMessageContent.style.filter = 'none';  // Unblur
        harmfulPopup.style.display = 'none';  // Hide popup
        messageDiv.style.backgroundColor = 'lightgreen';  // Mark as good
        messageDiv.classList.add("classified-good");
    });

    harmfulBadBtn.addEventListener('click', function () {
        harmfulMessageContent.style.filter = 'blur(5px)';  // Keep blurred
        harmfulPopup.style.display = 'none';  // Hide popup
        messageDiv.style.backgroundColor = 'lightcoral';  // Mark as bad
        messageDiv.classList.add("classified-bad");
    });

    // Hover event to toggle blur and show popup
    messageDiv.addEventListener('mouseenter', function () {
        if (!messageDiv.classList.contains("classified-good") && !messageDiv.classList.contains("classified-bad")) {
            harmfulMessageContent.style.filter = 'none';  // Temporarily unblur
            harmfulPopup.style.display = 'block';  // Show popup
        }
    });

    messageDiv.addEventListener('mouseleave', function () {
        if (!messageDiv.classList.contains("classified-good") && !messageDiv.classList.contains("classified-bad")) {
            harmfulMessageContent.style.filter = 'blur(5px)';  // Reblur
            harmfulPopup.style.display = 'none';  // Hide popup
        }
    });

    return harmfulPopup;
}

// Function to split long messages into multiple lines
function splitMessage(content, maxLength = 80) {
    console.log("Splitting message:", content);
    const lines = [];
    let currentLine = '';

    // Regular expression to match both words and long sequences without spaces
    const tokens = content.match(/(\S+\s*)/g); // Match non-whitespace sequences followed by optional spaces

    tokens.forEach(token => {
        // Check if adding the token exceeds the maximum line length
        if ((currentLine + token).length <= maxLength) {
            currentLine += token;
        } else {
            // Push the current line if it's full
            lines.push(currentLine.trim());
            // Start a new line with the current token
            currentLine = token;
        }
    });

    // Add the last line if any
    if (currentLine.trim().length > 0) {
        lines.push(currentLine.trim());
    }

    // Join the lines with a <br> tag
    const splitResult = lines.join('<br>');
    console.log("Split message:", splitResult);
    return splitResult;
}


// WebSocket message handler
ws.onmessage = function (event) {
    const message = JSON.parse(event.data);
    const chatbox = document.getElementById("chatbox");

    switch (message.type) {
        case "online_users":
            const onlineUsers = message.data;
            updateOnlineUsers(onlineUsers);
            break;

        case "history":
            const history = message.data;
            history.forEach(msg => {
                renderMessage(msg, chatbox);
            });
            break;

        case "new_user":
            renderMessage(message, chatbox);
            break;


        case "message":
            renderMessage(message, chatbox);
            break;

        default:
            console.log("Unknown message type:", message.type);
            break;
    }
};
