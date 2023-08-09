import pickle
import socket
import time
from  time import time

HOST = "127.0.0.1"
PORT = 50000
# window size
global N
N =4
class UDP_segment:
    def __init__(self, seq_num, checksum_cal, data):
        self.seq_num = seq_num
        self.checksum = checksum_cal
        self.data = data


def checksum_cal(data):
    sum = 0
    for i in range(len(data)):
        sum += int(data[i])
    return sum

def start(addr, file_name, file_size):
    global N
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((HOST, PORT))
    except :
        print()

    SEGMENT_SIZE = 100   # default window size

    # open the file and add all the packets to the buffer
    with open(file_name, "rb") as file:
        segments = []
        seq_num = 0
        rest_to_read = file_size
        flag = True
        while True:
            if (rest_to_read <= file_size/2 or rest_to_read <= SEGMENT_SIZE) and flag:
                data = "0".encode()
                checksum = checksum_cal(data.decode())
                segment = UDP_segment(seq_num, checksum, data)
                segments.append(segment)
                seq_num += 1
                flag = False

            if rest_to_read <= SEGMENT_SIZE:
                # we want to catch the last bit
                data = file.read(rest_to_read-1)
                checksum = checksum_cal(data)
                segment = UDP_segment(seq_num, checksum, data)
                segments.append(segment)
                seq_num += 1

                data = file.read(1)  # last bit
                checksum = checksum_cal(data)
                segment = UDP_segment(seq_num, checksum, data)
                segments.append(segment)
                seq_num += 1
                break

            data = file.read(SEGMENT_SIZE)
            checksum = checksum_cal(data)
            segment = UDP_segment(seq_num, checksum, data)
            segments.append(segment)
            seq_num += 1
            rest_to_read = rest_to_read - SEGMENT_SIZE

    "Go-Back-N"
    send_base = 0  # represents the location of the data we're sending
    seq_num = 0  # represents the number of the segment
    timeout = None
    message = ""
    number_of_errors = 0

    # send segments until almost 50% was sent
    while True:
        if message == 'ACK ' + str(len(segments)):  # all the data sent
            break

        if message == 'ACK ' + str(send_base + 1):  # for the next packet
            N += 1  # the window size increasing
            send_base += 1
            if seq_num == send_base:  # in case none segment is in the "air" and either need to be acked
                # stop time
                timeout = None
            else:
                # start timer
                timeout = time() + 0.5

        if message == 'ACK ' + str(send_base):  # if the packet doesn't arrived
            number_of_errors += 1
            if number_of_errors == 3:
                N = int(N/2)  # window size
                number_of_errors = 0

        if seq_num < send_base + N and seq_num < len(segments):
            current_packet = segments[seq_num]
            print("packet sent...")
            sock.sendto(pickle.dumps(current_packet), addr)  # returns the serialized object directly as a byte array
            print("the packet was sent\n\n")
            seq_num += 1

        if timeout is not None and time() >= timeout:  # looks like timeout
            N = 1  # Reducing the size of the window
            for i in range(send_base, send_base + N):
                if i < len(segments):
                    sock.sendto(pickle.dumps(segments[i]), addr)

        if message == 'WAIT':  # the client need to decide if to continue the download
            deadline = time() + 20.0
            try:
                while True:
                    message = sock.recvfrom(100)[0].decode()
                    if message == 'Y':
                        print("The client chose to continue the download")
                        break
                    elif message == 'N':
                        print("The client chose NOT to continue the download")
                        sock.close()
                        exit(0)
                    if time() >= deadline:
                        print("No respond. Download stopped")
                        sock.close()
                        exit(0)
            except:
                print("Error")
                sock.close()
                exit(0)

        message = sock.recvfrom(100)[0].decode()
        print(f'------- {message} -------')

    file.close()
    print("*** File download complete ***")