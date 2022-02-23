import socket
import threading
from http import client
import select
import sys


def connect():
    host = "132.198.11.12"
    port = 12000

    # create socket
    cl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # host = input("Please enter the server hostname or IPv4 address: ")
    # port = input("Please enter the server port number: ")

    try:
        cl.connect((host, int(port)))
    except Exception as e:
        print(e)

    print("Connected to {} on port {}".format(host, port))
    return cl


def process(connection):
    cl = connection
    handshake = "HELLO \n"
    cl.send(handshake.encode('utf-8'))
    response = cl.recv(1024)

    login = False
    while not login:
        user = input("Please enter a username: ")
        password = input("Please enter a password: ")
        authen = "AUTH:{}:{} \n".format(user, password)
        cl.send(authen.encode('utf-8'))
        authenticated = cl.recv(1024)
        authenticated = authenticated.rstrip()
        if authenticated == b'AUTHNO':
            print("Incorrect username and/or password")
        elif authenticated == b'UNIQNO':
            print("User already logged in")
        elif authenticated == b'AUTHYES':
            print("You are now authenticated")
            cl.recv(1024)
            login = True

    e = False
    while not e:
        print("Choose an Option:")
        print("1. List online users")
        print("2. Send someone a message")
        print("3. Sign off")
        choice = input()

        if choice == "1":
            # Lists users online
            list_command = "LIST \n"
            cl.send(list_command.encode('utf-8'))
            users = (cl.recv(1024))
            users = users.decode()
            print("Users currently logged in: \n {}".format(users))

        elif choice == "2":
            to_user = input("User you would like to message: ")
            message = input("Message: ")
            message_command = "To:{}:{}".format(to_user, message)
            cl.send(message_command.encode('utf-8'))
            # if "sent":
            #     print("Message Sent")
            # elif "not sent":
            #     print("Message not Sent")
        elif choice == "3":
            bye_command = "BYE \n"
            cl.send(bye_command.encode('utf-8'))
            bye_message = cl.recv(1024)
            user_signed_off = cl.recv(1024)
            e = True
            cl.close()


def main():
    conn = connect()
    process(conn)


if __name__ == "__main__":
    thread = threading.Thread(target=connect)
    thread.daemon = True
    thread.start()
    main()
