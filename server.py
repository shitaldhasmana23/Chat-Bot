import socket
import threading

# Server Configuration
HOST = '127.0.0.1'  # Localhost
PORT = 12345        # Port to listen on

# List to keep track of connected clients
clients = []

# Function to broadcast messages to all clients
def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            client.send(message)

# Function to handle individual client
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)  # Receive message from client
            if message:
                decoded_message = message.decode('utf-8')
                if decoded_message.startswith("/typing"):
                    # Broadcast typing indicator
                    broadcast(message, sender=client_socket)
                else:
                    print(f"Received: {decoded_message}")
                    broadcast(message)
        except:
            # Remove client from the list and close connection
            if client_socket in clients:
                clients.remove(client_socket)
            client_socket.close()
            break

# Start the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Allow up to 5 connections
    print(f"Server started on {HOST}:{PORT}")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"New connection: {addr}")
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
