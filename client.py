import socket
import threading
from http import client
import select
import sys

global r_list, w_list, x_list


def connect():
    # create socket
    cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = input("Please enter the server hostname or IPv4 address: ")
    port = input("Please enter the server port number: ")

    # Try and connect tio socket
    try:
        cl.connect((host, int(port)))
    except Exception as e:
        print(e)

    print("Connected to {} on port {}".format(host, port))

    # Handshake with Server
    shake = "HELLO \n"
    cl.send(shake.encode('utf-8'))

    # Return the socket object
    return cl


def server_messages(connection):
    cl = connection

    # Variables for select.select
    global r_list, w_list, x_list
    arr = [cl]
    r_list, w_list, x_list = select.select(arr, [], [], 0.5)

    # Listens for messages from server
    if len(r_list) != 0:
        message = cl.recv(1024).decode('utf-8')
        if message == "" or message == "\n":
            pass
        elif message[0:5] == "From:":
            print("Message from {}: {}".format(message.split(":")[1], message.split(":")[2]))
        elif message[0:6] == "SIGNIN":
            print("{} signed in".format(message.split(":")[1].rstrip()))
        elif message[0:7] == "SIGNOFF":
            print("{} signed out".format(message.split(":")[1].rstrip()))
        else:
            print(message)


def process(connection):
    global r_list, w_list, x_list
    cl = connection
    login = False
    arr = [cl]

    r_list, w_list, x_list = select.select(arr, [], [], 0.1)
    if len(r_list) != 0:
        message = cl.recv(1024).decode('utf-8')
        if message == "" or message == "\n":
            pass
        elif message[0:5] == "HELLO":
            print("Ready for Authentication")
            while not login:

                # Gets user input
                username = input("Please enter a username: ")
                password = input("Please enter a password: ")

                # Sends user input to server
                authen = "AUTH:{}:{} \n".format(username, password)
                cl.send(authen.encode('utf-8'))
                message = cl.recv(1024).decode('utf-8')

                # Validates user input
                if message[0:6] == "AUTHNO":
                    print("Incorrect username and/or password")
                elif message[0:6] == "UNIQNO":
                    print("User already logged in")
                elif message[0:7] == "AUTHYES":
                    print("You are now authenticated")
                    cl.recv(1024)
                    login = True

    if len(r_list) != 0 and login:

        while True:
            # Display menu for user
            print("Choose an Option:")
            print("1. List online users")
            print("2. Send someone a message")
            print("3. Sign off")
            e = False
            while not e:

                # Listens for keyboard input
                temp = select.select([sys.stdin], [], [], 0.5)[0]
                if temp:
                    sys.stdin.flush()
                    choice = input()

                    # Performs action based on user input
                    if choice == "1":
                        # Lists users online
                        list_command = "LIST \n"
                        cl.send(list_command.encode('utf-8'))
                        users = cl.recv(1024).decode('utf-8')
                        print("Users currently logged in: \n {} ".format(users))
                        e = True

                    elif choice == "2":
                        to_user = input("User you would like to message: ")
                        message = input("Message: ")
                        message_command = "To:{}:{} \n".format(to_user, message)
                        cl.send(message_command.encode('utf-8'))
                        e = True

                    elif choice == "3":
                        bye_command = "BYE \n"
                        cl.send(bye_command.encode('utf-8'))
                        e = True
                        cl.close()
                        exit()

                    else:
                        print("Please pick 1, 2, or 3")

                # If no keyboard input check for server messages
                else:
                    server_messages(cl)


def main():
    conn = connect()
    process(conn)


if __name__ == "__main__":
    main()
