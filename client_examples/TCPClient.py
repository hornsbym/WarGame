import socket

def Main():
    HOST = "127.0.0.1"
    PORT = 5000

    s = socket.socket()
    s.connect((HOST,PORT))

    message = str(input("-->"))
    while message != "q":
        s.send(message.encode('utf-8'))
        data = s.recv(1024).decode('utf-8')
        print(data)
        message = str(input("-->"))
    
    s.close()

if __name__ == "__main__":
    Main()

