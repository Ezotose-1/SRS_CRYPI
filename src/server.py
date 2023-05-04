import socket


def server_program():

    host = socket.gethostname()
    port = 5000

    server_socket = socket.socket()
    server_socket.bind((host, port))

    server_socket.listen(2)
    conn, address = server_socket.accept()
    print(f"[*] Connection from: {address}")
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        print(f"[*] from connected user: {data}")
        data = "ACK"
        conn.send(data.encode())

    print(f"[*] Connection closed with {address}")
    conn.close()


if __name__ == '__main__':
    while True:
        server_program()