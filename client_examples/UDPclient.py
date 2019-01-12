import socket

def Main():
    HOST = '127.0.0.1'
    PORT = 5001
    SERVER = ('127.0.0.1',5000)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST,PORT))

    message = str(input("->"))
    while message != "q":
        s.sendto(message.encode('utf-8'), SERVER)
        data , address = s.recvfrom(1024)
        data = data.decode('utf-8')
        print(data)
        message = str(input("->"))
    
    s.close()

if __name__ == "__main__":
    Main()