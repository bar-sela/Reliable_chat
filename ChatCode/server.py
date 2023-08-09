import os
import socket
import threading



HOST = ''  # local host
PORT = 50000

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4, TCP
server.bind((HOST, PORT))
server.listen()
print("Users can connect..")

# Lists For Clients and Their Nicknames
clients = []
nicknames = []


# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)


# Handling Messages From Clients
def broadcast_toUser(message, user_name):
    for nick in nicknames:
        if (nick + '\n') == user_name:
            clients[nicknames.index(nick)].send(message)
            break


def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            message = message.decode()
            if message.startswith("SENDTOUSER-->"):
                message = message.removeprefix("SENDTOUSER-->")
                user_name = message[0:message.find('|')]
                message = message.removeprefix(user_name + '|')
                broadcast_toUser(message.encode(), user_name)

            elif message.startswith("FILES-->"):
                files = [f for f in os.listdir('.') if os.path.isfile(f)]
                user_name = message.removeprefix("FILES-->")
                broadcast_toUser(("Files: " + str(files) + '\n').encode(), user_name + '\n')

            elif message.startswith("ONLINEUSERS-->"):
                user_name = message.removeprefix("ONLINEUSERS-->")
                broadcast_toUser(("Online users: " + str(nicknames) + '\n').encode(), user_name + '\n')

            elif message.startswith("FILETODOWNLOAD-->"):
                print("Searching for the file ..")
                file_name = message.removeprefix("FILETODOWNLOAD-->")
                try:
                    # check the file size
                    file_size = os.path.getsize(file_name)
                    if file_size > 64000:
                        print("The file is too big to download\n")
                        exit(0)
                    print("Found")
                    client.send(f'File size = {file_size}\nDownloading...\n'.encode())
                except:
                    print("Not Found")
                    client.send("** File not found **\n".encode())

            else:
                broadcast(message.encode())
        except:  # in case the client left the chat
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('** {} left! **\n'.format(nickname).encode())
            nicknames.remove(nickname)
            break


# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()

        # Request And Store Nickname
        client.send('NICK'.encode())
        nickname = client.recv(1024).decode()
        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        broadcast("** {} joined! **\n".format(nickname).encode())

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
