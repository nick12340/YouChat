from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
import time
import glob
get_file_mode = False
send_file_mode = False
get_file_name_mode = False
file_name = ""
def receive():
    #handle the receiving of message
    global get_file_mode
    global get_file_name_mode
    global file_name

    #intial the f to be a file object and set it state to closed
    f = open('temp','a')
    f.close()
    while True:
        try:
            #if the user want to get file from server
            if get_file_mode == True:
                #keep getting the file
                msg = client_socket.recv(BUFFER_SIZE)
                if msg == bytes("&FILE_DNE",'utf8'):
                    #if the file not in server the server would announced the client
                    error_message = "file does not exist please try again"
                    msg_list.insert(tkinter.END,error_message)
                    get_file_mode = False
                    continue
                if f.closed:
                    #if the file is not opened then open it
                    f = open ("./user_file/%s"%file_name,'wb')
                if msg == bytes("&END_OF_FILE",'utf8'):
                    #server would send &end_of_file to state that the file is finish
                    f.close()
                    get_file_mode = False
                    msg = "The file have been successfully getted"
                    msg_list.insert(tkinter.END,msg)
                    continue
                f.write(msg)
                continue
            #general case
            msg = client_socket.recv(buffer_size).decode('utf8')
            msg_list.insert(tkinter.END, msg)
        except OSError:
            break

def send(event = None):
    #handle the sending of message
    #get the message from the GUI
    msg = my_msg.get()
    #clean the typing
    my_msg.set("")
    #send to server
    global get_file_mode
    global send_file_mode
    global get_file_name_mode
    global file_name
    if msg =="get_file()":
        #if the user want to get file from sever
        #let server know user wants to get file
        client_socket.send(bytes(msg,'utf8'))
        file_message = "You are going to get a file"
        msg_list.insert(tkinter.END,file_message)

        #file_list = client_socket.recv(buffer_size)
        file_message = "Here's all the files in the server:"
        msg_list.insert(tkinter.END,file_message)
        #msg_list.insert(tkinter.END,file_list.decode('utf8'))
        file_message = "Please type the name of the file you want"
        msg_list.insert(tkinter.END,file_message)
        get_file_name_mode = True 
        get_file_mode = True    
        return

    if get_file_name_mode == True:
        #get the file name
        file_name = msg
        #stop getting file name
        get_file_name_mode = False
        client_socket.send(bytes(msg,'utf8'))
        return

    if msg == "send_file()":
        file_message = "You are going to send a file"
        msg_list.insert(tkinter.END,file_message)
        file_list =""
        #to show all the file in user'folder the folder could be the name of user
        for filename in glob.glob(r'./user_file/*'):
            filename = filename[12:]
            file_list = file_list + filename + "  "
        
        file_message = "Here's all the file you have"
        msg_list.insert(tkinter.END,file_message)
        msg_list.insert(tkinter.END,file_list)
        file_message = "Please type the name of the file"
        msg_list.insert(tkinter.END,file_message)
        send_file_mode = True
        #to let the server know the sending is began
        client_socket.send(bytes("send_file()",'utf8'))
        return

    if send_file_mode == True:
        file_name = msg
        msg_list.insert(tkinter.END,msg)
        try:
            f = open("./user_file/%s" % file_name,'rb')
        except IOError:
            #if the file doesn't exist than let uesr retry
            error_message = "file does not exist please try again"
            msg_list.insert(tkinter.END,error_message)
            send_file_mode = False
            return
        while True:
            #keep sending the file
            buffer = f.read(BUFFER_SIZE)
            while buffer:
                client_socket.send(buffer)
                #print('Sent ',repr(l))
                buffer = f.read(BUFFER_SIZE)
            f.close()
            #send a end message of file
            client_socket.send(bytes("&END_OF_FILE",'utf8'))
            file_done_message = "The file have been successfully sended to the server"
            msg_list.insert(tkinter.END,file_done_message)
            break
        send_file_mode = False
        return

    if msg == "help()":
        # a menu for user
        help_message = "0.Type whatever you want to chat with online users"
        msg_list.insert(tkinter.END,help_message)
        help_message = "1.Type quit() to quit"
        msg_list.insert(tkinter.END,help_message)
        help_message = "2.Type send_file() to send file"
        msg_list.insert(tkinter.END,help_message)
        help_message = "3.Type get_file() to get file"
        msg_list.insert(tkinter.END,help_message)
        return
    client_socket.send(bytes(msg,'utf8'))
    if msg == "quit()":
        client_socket.close()  # close the socket
        top.quit()   # quit the GUI

def on_closing(event = None):
    my_msg.set("quit()")
    send()

def get_input(input_type,range):
    #validation of input
    while True:
        x = input("Please type the %s:(type nothing but enter to remain default):" %input_type)
        if x == "":
            return x
        if input_type == "Host_IP":
            if checkIPV4Addr(x):
                return x
        elif checkrange(x,range):
                return int(x)

def checkrange(portstr,range):
    #validation of input
    try:
        portstr = int(portstr)
    except:
        print("Wrong typing please try again!")
        return False
    if (int(portstr) < range[0]) or (int(portstr) > range[1]):
        print("The input is out of range(%d ~ %d)" &(range[0],range[1]))
        return False
    return True

def checkIPV4Addr(ipstr):
    #validation of ip
    ip_split_list = ipstr.split('.')
    if len(ip_split_list)!=4:
        return False
    for i in range(4):
        try:
            ip_split_list[i] = int(ip_split_list[i])
        except:
            print("IP is invalid:" + ipstr)
            return False
    for i in range(4):
        if ip_split_list[i] >255 or ip_split_list <0:
            return False
    return True

if __name__ == "__main__":
    Host = get_input('Host_IP',[])  #get the host ip
    Port = get_input('Port',[200,30000]) #get the port number
    #Default
    if Host == '':
        Host = '127.0.0.1'
    if Port == '':
        Port = 2018
    #BUFFER_SIZE is larger buffer for file
    #buffer_size is smaller for general use
    buffer_size = 1024
    BUFFER_SIZE = 4096
    #connect to server
    addr = (Host, Port)
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(addr)

    #set up for GUI
    top = tkinter.Tk()
    top.title("Youchat")
    #the place user typing
    messages_frame = tkinter.Frame(top)
    my_msg = tkinter.StringVar()
    my_msg.set("")
    #build a scrollbar for more text to show
    scrollbar = tkinter.Scrollbar(messages_frame)

    msg_list = tkinter.Listbox(messages_frame, height = 15, width =50, yscrollcommand = scrollbar.set)
    scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
    msg_list.pack(side = tkinter.LEFT, fill = tkinter.BOTH)
    msg_list.pack()
    messages_frame.pack()
    #get the enter event
    entry_field = tkinter.Entry(top, textvariable=my_msg)
    entry_field.bind("<Return>", send)
    entry_field.pack()
    send_button = tkinter.Button(top, text="Send", command=send)
    send_button.pack()

    top.protocol("WM_DELETE_WINDOW", on_closing)

    receive_thread = Thread(target = receive)
    receive_thread.start()
    tkinter.mainloop()