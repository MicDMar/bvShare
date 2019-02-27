from os import listdir
from os.path import isfile, join
import os

from socket import *

DEFAULT_ADDRESS = '0.0.0.0'
DEFAULT_PORT = 3000
DEFAULT_REPO_PATH = 'repository'


def get_files(path):
    return [f for f in listdir(path) if isfile(join(path, f))]

def send_int(conn, num, size = 4, form = "big"):
    conn.send(num.to_bytes(size, form))
    
def send_string(conn, string):
    send_int(len(string))
    conn.send(string.encode())

def get_n_bytes(conn, n):
    data = []
    while len(data) < n:
        data += conn.recv(n - len(data))
    return data

if __name__ == "__main__":
    # Retrieve values from environment variables
    address = os.environ.get('ADDRESS', DEFAULT_ADDRESS)
    port = os.environ.get('PORT', DEFAULT_PORT)
    repo = os.environ.get('REPOSITORY', DEFAULT_REPO_PATH)
    
    # Setup the TCP socket
    listener = socket(AF_INET, SOCK_STREAM)
    listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # Allow address to be reused
    listener.bind((address, port))
    listener.listen()

    while True:
        conn, clientAddr = listener.accept()

        file_list = get_files(REPO)
        num_files = len(file_list)
        
        # Send the client the list of files
        send_int(conn, num_files)
        for i in range(num_files):
            send_string(conn, file_list[i])

        # Receive which file the client wants
        selected_file = int.from_bytes(get_n_bytes(conn, 4), "big")

        # Read the contents of the selected file
        contents = []
        with open(file_list[selected_file], "rb") as f:
            contents += f.read()
             
        # Send the contents
        send_int(conn, len(contents))
        conn.send(contents)
        
        conn.close()
