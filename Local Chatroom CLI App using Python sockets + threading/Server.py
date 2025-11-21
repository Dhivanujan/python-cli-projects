import socket
import threading

HOST = "127.0.0.1"   # Localhost
PORT = 55555         # Port for chat server

clients = {}  # {client_socket: nickname}


def broadcast(message, sender=None):
    """Send message to all connected clients except sender."""
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode())
            except:
                client.close()
                remove_client(client)


def remove_client(client):
    """Safely remove a client."""
    nickname = clients.get(client, "Unknown")
    print(f"[SERVER] {nickname} disconnected.")
    if client in clients:
        del clients[client]


def handle_client(client):
    """Handles messages from a single client."""
    while True:
        try:
            msg = client.recv(1024).decode()

            if not msg:
                break

            nickname = clients[client]

            # --- Moderation Commands ---
            if msg.startswith("/"):
                parts = msg.split(" ", 1)
                command = parts[0]

                # /list → Show all users
                if command == "/list":
                    user_list = ", ".join(clients.values())
                    client.send(f"[SERVER] Connected users: {user_list}".encode())

                # /rename newName
                elif command == "/rename":
                    if len(parts) < 2:
                        client.send("[SERVER] Usage: /rename new_name".encode())
                    else:
                        new_name = parts[1].strip()
                        broadcast(f"[SERVER] {nickname} renamed to {new_name}")
                        clients[client] = new_name
                        client.send(f"[SERVER] You are now {new_name}".encode())

                # /kick username
                elif command == "/kick":
                    target_name = parts[1].strip() if len(parts) > 1 else None
                    kicked = None
                    for sock, name in clients.items():
                        if name == target_name:
                            kicked = sock
                            break

                    if kicked:
                        kicked.send("[SERVER] You have been kicked!".encode())
                        kicked.close()
                        remove_client(kicked)
                        broadcast(f"[SERVER] {target_name} was kicked by {nickname}")
                    else:
                        client.send("[SERVER] User not found.".encode())

                # /quit → exit chat
                elif command == "/quit":
                    client.send("QUIT".encode())
                    client.close()
                    remove_client(client)
                    break

                continue

            # Broadcast normal message
            broadcast(f"{nickname}: {msg}", sender=client)

        except:
            client.close()
            remove_client(client)
            break


def start_server():
    """Start the main chat server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVER] Chatroom running on {HOST}:{PORT}")

    while True:
        client, addr = server.accept()
        print(f"[SERVER] Connected with {addr}")

        # Ask for nickname
        client.send("NICK".encode())
        nickname = client.recv(1024).decode()

        clients[client] = nickname
        print(f"[SERVER] Nickname set: {nickname}")

        broadcast(f"[SERVER] {nickname} joined the chat!")
        client.send("[SERVER] Connected to server.".encode())

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


if __name__ == "__main__":
    start_server()
