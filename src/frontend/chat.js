const ws = new WebSocket("ws://localhost:8000/ws");
let username;

document.getElementById("usernameForm").addEventListener("submit", function(event) {
    event.preventDefault();
    username = document.getElementById("username").value;
    ws.send(username);

    // Show chat container and hide the username form
    document.getElementById("usernameForm").style.display = "none";
    document.getElementById("container").style.display = "flex";
});

ws.onmessage = function(event) {
    const message = event.data;
    const chatbox = document.getElementById("chatbox");

    if (message.startsWith("ONLINE_USERS:")) {
        const onlineUsers = JSON.parse(message.split("ONLINE_USERS:")[1]);
        updateOnlineUsers(onlineUsers);
    } else if (message.startsWith("HISTORY:")) {
        const history = JSON.parse(message.split("HISTORY:")[1]);
        history.forEach(msg => {
            chatbox.innerHTML += `<div><strong>${msg.user}</strong>: ${msg.content} (${msg.timestamp})</div>`;
        });
        scrollToBottom(chatbox); // Scroll to the end after loading history
    } else {
        chatbox.innerHTML += `<div>${message}</div>`;
        scrollToBottom(chatbox); // Scroll to the end when a new message is added
    }
};

document.getElementById("messageForm").addEventListener("submit", function(event) {
    event.preventDefault();
    const message = document.getElementById("messageInput").value;
    ws.send(message);
    document.getElementById("messageInput").value = "";
});

// Scroll chatbox to the bottom
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
