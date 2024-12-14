import socket
import threading
import sys
import os

# Bluetooth device addresses
peer_addr = "B8:27:EB:10:BB:88"  # Address of the peer Bluetooth device
local_addr = "2C:0D:A7:6F:99:C8"  # Address of the local Bluetooth device

# Bluetooth communication channel
port = 30

# Function to start the Bluetooth server and receive files
def start_server(local_addr, port):
    '''
    Initializes a Bluetooth server to receive files.
    '''
    try:
        # Create a Bluetooth socket using RFCOMM protocol
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        sock.bind((local_addr, port))
        sock.listen(1)

        print("Bluetooth server started. Waiting for connection...")
        while True:
            # Accept incoming client connections
            client_sock, address = sock.accept()
            print(f"Connection established with {address[0]}:{address[1]}")

            # Receive file metadata (name and size)
            file_info = client_sock.recv(1024).decode()
            filename, filesize = file_info.split("::")
            filesize = int(filesize)

            print(f"Receiving file: {filename} ({filesize} bytes)")

            # Receive file data
            with open(f"received_{filename}", "wb") as f:
                received = 0
                while received < filesize:
                    data = client_sock.recv(1024)
                    f.write(data)
                    received += len(data)
                    print(f"Progress: {received}/{filesize} bytes received", end="\r")

            print(f"\nFile {filename} received successfully.")
            client_sock.close()
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit()

# Function to send a file to a Bluetooth device
def send_file(filepath, peer_addr, port):
    '''
    Sends a file to the specified Bluetooth device.
    '''
    try:
        # Check if the file exists
        if not os.path.exists(filepath):
            print(f"Error: The file '{filepath}' does not exist.")
            return

        filesize = os.path.getsize(filepath)
        filename = os.path.basename(filepath)

        # Connect to the peer Bluetooth device
        with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
            sock.connect((peer_addr, port))
            print(f"Connected to {peer_addr}:{port}")

            # Send file metadata (name and size)
            sock.send(f"{filename}::{filesize}".encode())

            # Send file data
            with open(filepath, "rb") as f:
                sent = 0
                while sent < filesize:
                    data = f.read(1024)
                    sock.send(data)
                    sent += len(data)
                    print(f"Progress: {sent}/{filesize} bytes sent", end="\r")

            print(f"\nFile {filename} sent successfully.")
    except Exception as e:
        print(f"Error sending file: {e}")

# Initialize the server in a separate thread
server = threading.Thread(target=start_server, args=(local_addr, port))
server.daemon = True
server.start()

# User interface for sending files
print("Enter the file path to send or 'exit' to quit:")
while True:
    filepath = input("> ").strip()
    if filepath.lower() == "exit":
        print("Closing program...")
        break
    send_file(filepath, peer_addr, port)

sys.exit()
