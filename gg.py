# hidden_cmd_executor.py

import subprocess
import ctypes
import os

def run_hidden_cmd(command):
    """
    Runs a command in a hidden CMD window.
    """
    # Define the structure for the startup info
    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup_info.wShowWindow = subprocess.SW_HIDE

    try:
        # Run the command in a hidden CMD window
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            startupinfo=startup_info
        )
        stdout, stderr = process.communicate()

        # Print the output and error (if any)
        if stdout:
            print("Output:", stdout.decode())
        if stderr:
            print("Error:", stderr.decode())
    except Exception as e:
        print(f"Error executing command: {e}")

if __name__ == "__main__":
    # Example: Run a command in a hidden CMD window
    while True:
        try:
            # Get user input for the command
            command = input("Enter a command to execute (or type 'exit' to quit): ")
            if command.lower() == "exit":
                print("Exiting...")
                break

            # Execute the command in a hidden CMD window
            run_hidden_cmd(command)
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            break