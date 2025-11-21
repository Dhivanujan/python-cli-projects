import socket
import threading

HOST = "127.0.0.1"
PORT = 55555


def receive_messages(client):
    """Listen for messages from the server."""
    while True:
        try:
            msg = client.recv(1024).decode()

            if msg == "QUIT":
                print("[SERVER] You were disconnected.")
                client.close()
                break

            print(msg)

        except:
            print("Disconnected from server.")
            client.close()
            break


def send_messages(client, nickname):
    """Send user-entered messages to server."""
    while True:
        msg = input("")
        try:
            client.send(msg.encode())
        except:
            print("Connection error.")
            client.close()
            break


def main():
    nickname = input("Enter your nickname: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # When connected, server asks for nickname
    if client.recv(1024).decode() == "NICK":
        client.send(nickname.encode())

    print("Connected! Type messages to chat.")
    print("Commands: /list  /rename newName  /kick user  /quit")

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
    threading.Thread(target=send_messages, args=(client, nickname), daemon=True).start()


if __name__ == "__main__":
    main()
