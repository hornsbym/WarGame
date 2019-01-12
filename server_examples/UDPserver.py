import socket 

def Main():
    HOST = "127.0.0.1"
    PORT = 5000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST,PORT))

    print("UDP Server started at",PORT)

    while True:
        data, address = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Message from:", address)
        print("Data:", data)
        data = data.upper()
        print("Returning",data)
        s.sendto(data.encode('utf-8'),address)
    
    s.close()

if __name__ == "__main__":
    Main()

