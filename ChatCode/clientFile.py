import os
import socket
import threading
import pickle
import tkinter
from tkinter import simpledialog

import serverFile



def checksum_cal(data):
    sum = 0
    for i in range(len(data)):
        sum += data[i]
    return sum


def keepDownLoading(client, exepting_num, file_name):
    with open(f'./{client.nickname}/{file_name}', "a") as file:
        while True:
            message, address = client.udp_C_socket.recvfrom(1024)
            segment = pickle.loads(message)
            seq_num = segment.seq_num
            checksum = segment.checksum
            content = segment.data

            if len(content) == 1 and checksum_cal(content) == checksum:
                exepting_num += 1

                client.udp_C_socket.sendto(f'ACK {exepting_num}'.encode(), address)
                file.write(content.decode())
                write_last_segment(client, content)
                break

            if seq_num == exepting_num and checksum_cal(content) == checksum:
                exepting_num += 1
                client.udp_C_socket.sendto(f'ACK {exepting_num}'.encode(), address)
                file.write(content.decode())
            elif seq_num != exepting_num:
                print("sd")
                client.udp_C_socket.sendto(f'ACK {exepting_num}'.encode(), address)

    client.udp_C_socket.close()
    client.udp_C_socket = None


def udp_file_transfer(client, file_name, file_size):
    # open udp_socket and bind with port
    client.udp_C_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.udp_C_socket.bind(('127.0.0.1', client.port))
    # entering in case there is a wanted file inside the server
    expecting_seq = 0

    # if not exist create folder named 'data'
    if not os.path.exists(client.nickname):
        os.makedirs(client.nickname)

    with open(f'./{client.nickname}/{file_name}', "w+") as file:
        threading.Thread(target=serverFile.start, args=(('127.0.0.1', client.port), file_name, file_size)).start()
        print("Start downloading ..")
        while True:
            message, address = client.udp_C_socket.recvfrom(1024)
            segment = pickle.loads(message)
            seq_num = segment.seq_num
            checksum = segment.checksum
            content = segment.data

            # if the message is less the 100 bits at first --> a half has been sent
            if content.decode() == '0':
                expecting_seq += 1
                client.udp_C_socket.sendto(f'ACK {expecting_seq}'.encode(), address)
                client.udp_C_socket.sendto("WAIT".encode(), address)
                break
            # if a correct seq number has arrived --- > write it to the file add exeptring seq by 1 and
            # send ACK on the next seq number !
            if seq_num == expecting_seq and checksum_cal(content) == checksum:
                expecting_seq += 1
                client.udp_C_socket.sendto(f'ACK {expecting_seq}'.encode(), address)
                file.write(content.decode())

            # in case not the correct seq number has been sent ---> send ACK on the same seq number
            elif seq_num != expecting_seq:
                client.udp_C_socket.sendto(f'ACK {expecting_seq}'.encode(), address)

        msg = tkinter.Tk()  # tkinter frame
        msg.withdraw()  # hides the wino
        answer = simpledialog.askstring("Answer", "Do you want to continue? (Y/N)", parent=msg)
        while True:
            if answer == "N":
                # User doesn't want to continue
                client.text_area.config(state='normal', font=("Arial", 12))
                client.text_area.insert('end', 'Download stopped\n')
                client.text_area.config(state='disable', font=("Arial", 12))
                client.udp_C_socket.sendto("N".encode(), address)
                client.udp_C_socket.close()
                break
            elif answer == "Y":
                # User wants to continue
                client.text_area.config(state='normal', font=("Arial", 12))
                client.text_area.insert('end', 'Continues to download...\n')
                client.text_area.config(state='disable', font=("Arial", 12))
                client.udp_C_socket.sendto("Y".encode(), address)
                client.udp_C_socket.sendto(f'ACK {expecting_seq}'.encode(), address)
                threading.Thread(target=keepDownLoading, args=(client, expecting_seq, file_name)).start()
                break

            msg = tkinter.Tk()  # tkinter frame
            msg.withdraw()  # hides the wino
            answer = simpledialog.askstring("Answer", "Please insert a valid answer!\n(Y/N) Do you want to continue?",
                                            parent=msg)

def write_last_segment(client, content):
    client.text_area.config(state='normal', font=("Arial", 12))  # the text area is changeable
    client.text_area.insert('end', f'The download is complete\nLast byte in the file = {content.decode()}\n')  # to append the message at the end
    client.text_area.yview('end')  # scroll down to the end with the messages
    client.text_area.config(state='disable', font=("Arial", 12))