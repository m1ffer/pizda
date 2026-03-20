import socket

def main():
    ip = input("Введите IP: ")
    port = int(input("Введите порт: "))
    message = input("Сообщение: ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.sendto(message.encode(), (ip, port))

    print("Отправлено")


if __name__ == "__main__":
    main()