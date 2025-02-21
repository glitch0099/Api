# client.py

import socket
import sys

# Server Configuration
SERVER_IP = 's8.serv00.com'
SERVER_PORT = 63098

def connect_to_server():
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the server
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
        return client_socket
    except Exception as e:
        print(f"Error connecting to server: {e}")
        sys.exit(1)

def send_command(client_socket):
    while True:
        # Get command from user
        command = input("Enter command (or 'exit' to quit): ").strip()
        if command.lower() == 'exit':
            print("Exiting client...")
            client_socket.close()
            break

        # Send command to server
        try:
            client_socket.send(command.encode('utf-8'))
            # Receive response from server
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Server response:\n{response}")
        except Exception as e:
            print(f"Error communicating with server: {e}")
            client_socket.close()
            break

if __name__ == '__main__':
    # Connect to the server
    client_socket = connect_to_server()
    if client_socket:
        # Start sending commands
        send_command(client_socket)