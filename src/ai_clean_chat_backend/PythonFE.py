import tkinter as tk
from tkinter import messagebox
import asyncio
import websockets
import threading
import json

class ChatApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("WebSocket Chat")
        self.username = None
        self.ws = None

        # Username input screen
        self.username_frame = tk.Frame(root)
        self.username_frame.pack(pady=20)

        self.header_label = tk.Label(self.username_frame, text="WebSocket Chat", font=("Arial", 24))
        self.header_label.pack(pady=10)

        self.username_label = tk.Label(self.username_frame, text="Enter your username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.username_frame, width=30)
        self.username_entry.pack(pady=5)

        self.join_button = tk.Button(self.username_frame, text="Join Chat", command=self.join_chat)
        self.join_button.pack(pady=10)

        # Chat window
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Online users list
        self.users_frame = tk.Frame(self.chat_frame)
        self.users_frame.pack(side="left", padx=10, fill="y")

        self.users_label = tk.Label(self.users_frame, text="Online Users", font=("Arial", 14))
        self.users_label.pack()

        self.users_listbox = tk.Listbox(self.users_frame, width=20, height=15)
        self.users_listbox.pack(pady=5)

        # Chat area
        self.chat_area_frame = tk.Frame(self.chat_frame)
        self.chat_area_frame.pack(side="right", fill="both", expand=True)

        self.chatbox = tk.Text(self.chat_area_frame, state="disabled", wrap="word", height=15)
        self.chatbox.pack(pady=5, fill="both", expand=True)

        self.message_entry = tk.Entry(self.chat_area_frame, width=50)
        self.message_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        self.send_button = tk.Button(self.chat_area_frame, text="Send", command=self.send_message)
        self.send_button.pack(side="right", padx=5, pady=5)

        # Initially hide the chat window
        self.chat_frame.pack_forget()

    def join_chat(self):
        self.username = self.username_entry.get().strip()
        if self.username:
            # Show chat window and hide username input
            self.username_frame.pack_forget()
            self.chat_frame.pack(pady=10, padx=10, fill="both", expand=True)

            # Start WebSocket connection
            threading.Thread(target=self.start_websocket, daemon=True).start()
        else:
            messagebox.showerror("Error", "Username cannot be empty!")

    async def websocket_handler(self):
        async with websockets.connect("ws://localhost:8000/ws") as ws:
            self.ws = ws
            # Send username to server
            await self.ws.send(self.username)
            while True:
                try:
                    message = await self.ws.recv()
                    print("Received message:", message)
                    self.handle_message(message)
                except websockets.ConnectionClosed:
                    break

    def start_websocket(self):
        asyncio.run(self.websocket_handler())

    def send_message(self):
        message = self.message_entry.get()
        if message and self.ws:
            asyncio.run(self.ws.send(message))
            self.message_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Message cannot be empty!")

    def handle_message(self, message):
        data = json.loads(message)
        message_type = data.get("type")
        content = data.get("data")

        if message_type == "online_users":
            self.update_online_users(content)
        elif message_type == "message":
            self.render_message(content)
        elif message_type == "history":
            for msg in content:
                msg_content = msg.get("data")
                self.render_message(msg_content)
        else:
            print("Unknown message type:", message_type)

    def update_online_users(self, users):
        self.users_listbox.delete(0, tk.END)
        for user in users:
            self.users_listbox.insert(tk.END, user)

    def render_message(self, msg):
        self.chatbox.config(state="normal")
        self.chatbox.insert("end", f"{msg['user']}: {msg['content']}\n")
        self.chatbox.config(state="disabled")
        self.chatbox.see("end")


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApplication(root)
    root.mainloop()
