"""
POP3 Protocol Client
RFC1939
"""

import socket
import ssl


POP3_PORT = 995
CRLF = '\r\n'


class Pop3Client:
    def __init__(self):
        self.socket = None
        self.file = None
        self.in_inbox = 0
        pass

    def connect(self, server, port=POP3_PORT):
        self.socket = ssl.wrap_socket(socket.socket())
        self.socket.connect((server, port))
        self.file = self.socket.makefile("r")

    def send_command(self, cmd, param=""):
        if not param:
            self.socket.sendall(bytes(cmd + CRLF, "utf-8"))
        else:
            self.socket.sendall(bytes(cmd + " " + param + CRLF, "utf-8"))

    def authenticate(self, user, passwd):
        self.send_command("USER", user)
        resp = self.get_response()
        if resp[:3] != "+OK":
            print("Authentication failed after user name, server responded: " + resp)
            return False
        self.send_command("PASS", passwd)
        resp = self.get_response()
        if resp[:3] != "+OK":
            print("Authentication failed after password, server responded: " + resp)
            return False
        self.in_inbox = int(resp.split(' ')[1])
        return True

    def get_response(self):
        resp = str(self.socket.recv(1024), "utf-8")
        if resp[-2:] == CRLF:
            resp = resp[:-2]
        elif resp[-1:] in CRLF:
            resp = resp[:-1]
        return resp

    def get_multiline_resp(self):
        full_resp = ""
        while True:
            resp = str(self.socket.recv(1024), "utf-8")
            if resp[:5] == "\r\n.\r\n":
                break
            full_resp += resp
        return full_resp

    def retrive_nmessages(self):
        self.send_command("STAT")
        resp = self.get_response()
        return int(resp.split(' ')[1])

    def retrieve_list(self):
        self.send_command("LIST")
        resp = self.get_multiline_resp()
        print(resp)

    def retrieve_email(self, num):
        self.send_command("RETR", str(num))
        resp = self.get_multiline_resp()
        return resp

    def retrieve_emails(self):
        num = self.retrive_nmessages()
        mail_list = {}
        for i in range(1, num+1):
            email = self.retrieve_email(i)
            mail_list[i] = email
        return mail_list

    def get_title(self, email):

        pass


def test_func():
    pop3 = Pop3Client()
    pop3.connect("pop.yandex.ru")
    resp = pop3.get_response()
    if pop3.authenticate("mchr", "<<password>>"):
        print("Authentication successful")
        print("Messages in inbox: %d" % pop3.in_inbox)
        email = pop3.retrieve_email(7)
        print(email)
    pop3.send_command("QUIT")
    print(pop3.get_response())




if __name__ == "__main__":
    test_func()
