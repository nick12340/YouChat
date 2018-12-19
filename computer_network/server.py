from threading import Thread
from socket import AF_INET, socket, SOCK_STREAM
import glob
def get_input(input_type,range):    #input valiadation
    while True:
        x = input("Please type the %s:" %input_type)
        if x == "":  #nothing then set to default
            return x
        if checkrange(x,range):
            return int(x)

def checkrange(portstr,range):  #check the input with the range
    try:
        portstr == int(portstr)  #check if it is a integer
    except:
        print("Wrong typing please try again!")
        return False
    if (int(portstr) < range[0]) or (int(portstr) > range[1]):
        print("The input is out of range(%d ~ %d)" %(range[0],range[1]))
        return False
    return True

def broadcast(msg, prefix=""):
    # broadcast the message to all users
    for sock in clients:
        sock.send(bytes(prefix, 'utf8')+msg)
def handle_client(client):
    # handle the connected client
    name = client.recv(buffer_size).decode('utf8')
    # To get the user name
    welcome_msg = "Welcome to YouChat %s! You can type \"help()\" to get help" % name
    client.send(bytes(welcome_msg,'utf8'))
    # broadcast the login message to all users
    msg = "%s has joined the chat room!" % name
    broadcast(bytes(msg,'utf8'))
    clients[client] = name
    while True:
        msg = client.recv(buffer_size)

        if msg == bytes("send_file()","utf8"):
            #user want to send a file
            with open ("./server_file/%s_file" % clients[client],'wb') as f:
                while True:
                    #keep recving untill the file is end.
                    msg = client.recv(BUFFER_SIZE)
                    if msg == bytes("&END_OF_FILE",'utf8'):
                        f.close()
                        break
                    f.write(msg)
                msg = ""
            continue

        if msg == bytes("get_file()",'utf8'):
            #user want to get a file
            file_list = ""
            #show all the file in server
            for filename in glob.glob(r'./server_file/*'):
                filename = filename[14:]
                file_list = file_list + filename + "  "
            #print(file_list)
            #send the file_list to user
            client.send(bytes(file_list,'utf8'))
            #get the file name which the user want
            msg = client.recv(buffer_size)
            print ("%s ask for %s file" %(clients[client],msg.decode('utf8')))
            try:
                f = open("./server_file/%s" %msg.decode('utf8'),'rb')
                while True:
                    #keep sending the file until it's end then send a flag
                    buffer = f.read(BUFFER_SIZE)
                    while buffer:
                        client.send(buffer)
                        buffer = f.read(BUFFER_SIZE)
                    client.send(bytes("&END_OF_FILE",'utf8'))
                    print("The file have been successfully sended to the %s" %clients[client])
                    break
                f.close()

            except IOError:
                client.send(bytes("&FILE_DNE",'utf8'))
            continue

        if msg == bytes("quit()","utf8"):
            # if the user type quit() then close the connection and announce other users
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat room"%name,"utf8"))
            msg =""
            break
        else:
            broadcast(msg, name+": ")

def accept_incoming_connections():
    #set up for handle a user
    while True:
        client, client_address = server.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings from YouChat! ","utf8"))
        client.send(bytes("Now let me know who you are!","utf8"))
        addresses[client] = client_address
        #use threading to handle multi users
        Thread(target = handle_client, args = (client,)).start()

clients = {}
addresses = {}
#default host is 127.0.0.1
host = "127.0.0.1"
BUFFER_SIZE = 4096
buffer_size = 1024

print("Set up a YouChat server!")
#set up the port number
port = get_input("Port",[200,30000])
#by default port 2018
if port == "":
    port = 2018
addr = (host, port)
server = socket(AF_INET, SOCK_STREAM)
#bind the service with the port
server.bind(addr)
#to limit the max number of users
max_client = get_input("Max number of clients",[1,100])
if max_client == "":
    max_client = 5
if __name__ == "__main__":
    server.listen(max_client)
    print("Waiting for connection...")
    #use multithreading to handle multi users
    accept_thread = Thread(target = accept_incoming_connections)
    accept_thread.start()
    #join is to make sure the thread finish it's job then close it
    accept_thread.join()
    server.close()