import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, colorchooser
from tkinter.scrolledtext import ScrolledText
from playsound import playsound  # type: ignore # Install via pip install playsound
import time

# Server Configuration
HOST = '127.0.0.1'
PORT = 12345


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Application")

        # Initialize variables
        self.username = ""
        self.running = True

        # Username prompt
        self.username = simpledialog.askstring("Username", "Enter your username:")
        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty!")
            self.root.destroy()
            return

        # Connect to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((HOST, PORT))
            self.client_socket.send(f"USERNAME:{self.username}".encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.root.destroy()
            return

        # Create the chat window layout
        self.create_widgets()

        # Start threads for receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.close_connection)

    def create_widgets(self):
        """Set up the GUI layout."""
        # Chat display area
        self.chat_area = ScrolledText(self.root, wrap=tk.WORD, state='disabled', font=("Arial", 12))
        self.chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Entry area for typing messages
        self.message_entry = ttk.Entry(self.root, font=("Arial", 16))
        self.message_entry.pack(padx=10, pady=10, ipady=8, fill=tk.X, side=tk.LEFT, expand=True)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<KeyPress>", self.start_typing)

        # Send button
        self.send_button = ttk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack(padx=5, pady=5, side=tk.RIGHT)

        # Emoji button
        self.emoji_button = ttk.Button(self.root, text="😀", command=self.insert_emoji)
        self.emoji_button.pack(padx=5, pady=5, side=tk.LEFT)

        # Background change button
        self.background_button = ttk.Button(self.root, text="Change Background", command=self.change_background)
        self.background_button.pack(padx=5, pady=5, side=tk.RIGHT)

    def send_message(self, event=None):
        """Send a message to the server."""
        message = self.message_entry.get().strip()
        if message:
            try:
                if message.startswith("/pm"):
                    # Private message format
                    self.client_socket.send(message.encode('utf-8'))
                else:
                    timestamp = time.strftime("[%H:%M:%S]")
                    self.client_socket.send(f"{timestamp} {self.username}: {message}".encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to send message: {e}")
                self.close_connection()

    def start_typing(self, event=None):
        """Notify the server that the user is typing."""
        try:
            self.client_socket.send("TYPING".encode('utf-8'))
        except:
            pass

    def insert_emoji(self):
        """Insert a selected emoji into the message entry."""
        emojis = ["😀", "😂", "😍", "👍", "🙏", "🎉", "❤️", "🌟"]
        selected_emoji = simpledialog.askstring("Emoji Picker", "Enter an emoji:\n" + " ".join(emojis))
        if selected_emoji and selected_emoji.strip() in emojis:
            self.message_entry.insert(tk.END, selected_emoji.strip())

    def change_background(self):
        """Change the background color of the chat area."""
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.chat_area.configure(bg=color)

    def receive_messages(self):
        """Receive messages from the server."""
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message)
                    playsound('notification.mp3')  # Play a notification sound
            except:
                break

    def display_message(self, message):
        """Display a received message in the chat area."""
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def close_connection(self):
        """Confirm before closing and disconnect from the server."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.running = False
            self.client_socket.close()
            self.root.destroy()


# Start the GUI client
if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
