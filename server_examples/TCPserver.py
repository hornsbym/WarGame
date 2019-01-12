import socket

def Main():
    HOST = "127.0.0.1"
    PORT = 5000

    s = socket.socket()
    s.bind((HOST,PORT))

    print("Listening on port", PORT)
    s.listen(1)

    client, address = s.accept()
    print("Connection from", address)

    while True:
        data = client.recv(1024).decode('utf-8')
        if not data:
            break
        print("From connected user:", data)
        data = data.upper()
        print("Sending", data)
        client.send(data.encode('utf-8'))
    
    client.close()

if __name__ == "__main__":
    Main()