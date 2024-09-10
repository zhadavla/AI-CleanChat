const ws = new WebSocket("ws://localhost:6789");

ws.onopen = () => {
    console.log("Connected to the WebSocket server");
    ws.send(username);
};

ws.onmessage = (event) => {
    const chatbox = document.getElementById("chatbox");
    const chatList = document.getElementById("chat-list");
    const message = event.data;

    if (message.startsWith("NEW_USER:")) {
        const newUser = message.split(":")[1];
        const userItem = document.createElement("div");
        userItem.textContent = newUser;
        userItem.classList.add("user-item");
        userItem.onclick = () => {
            // Handle user click to start chat
            console.log(`Start chat with ${newUser}`);
        };
        chatList.appendChild(userItem);
    } else {
        const messageDiv = document.createElement("div");
        messageDiv.textContent = message;
        chatbox.appendChild(messageDiv);
    }
};

let username = prompt("Enter your username:");

function sendMessage() {
    const input = document.getElementById("message");
    const message = `${username}: ${input.value}`;
    ws.send(message);
    input.value = "";
}

document.getElementById("message").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        sendMessage();
    }
});

