import socket
import random
import struct
import threading
import time

STUN_SERVER = ("stun.l.google.com", 19302)
LOCAL_PORT = 12345


def build_request():
    return struct.pack(
        "!HHI12s",
        0x0001,
        0,
        0x2112A442,
        bytes(random.getrandbits(8) for _ in range(12))
    )


def parse_response(data):
    i = 20
    while i < len(data):
        attr_type, attr_length = struct.unpack("!HH", data[i:i+4])
        value = data[i+4:i+4+attr_length]

        if attr_type == 0x0020:
            x_port = struct.unpack("!H", value[2:4])[0]
            port = x_port ^ 0x2112

            x_ip = struct.unpack("!I", value[4:8])[0]
            ip = x_ip ^ 0x2112A442

            ip_str = ".".join(map(str, ip.to_bytes(4, 'big')))
            return ip_str, port

        i += 4 + attr_length

    return None, None


def stun_keep_alive(sock):
    counter = 0

    while True:
        counter += 1
        try:
            sock.sendto(build_request(), STUN_SERVER)
            print(f"[STUN] отправлен keep-alive #{counter}")
        except Exception as e:
            print("[STUN] ошибка:", e)

        time.sleep(1)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", LOCAL_PORT))

    print(f"Локальный порт: {LOCAL_PORT}")

    # первый STUN запрос
    sock.sendto(build_request(), STUN_SERVER)
    data, _ = sock.recvfrom(1024)
    ip, port = parse_response(data)

    print(f"Твой внешний адрес: {ip}:{port}")
    print("\nОжидание входящих сообщений...\n")

    # запускаем keep-alive поток
    threading.Thread(target=stun_keep_alive, args=(sock,), daemon=True).start()

    # основной цикл приёма
    while True:
        data, addr = sock.recvfrom(1024)

        # STUN ответы (бинарные)
        if len(data) >= 20 and data[0] == 0x01:
            print("[STUN] получен ответ")
            continue

        try:
            text = data.decode()
            print(f"[PEER] от {addr}: {text}")
        except:
            print(f"[UNKNOWN] от {addr}: {data}")


if __name__ == "__main__":
    main()