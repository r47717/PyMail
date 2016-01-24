"""
POP3 Protocol Client
RFC821
"""

import socket
import ssl
import base64

SMTP_PORT = 465
CRLF = '\r\n'


def goodresp(resp): return resp[0] in ["2","3"]



class SmtpClient:
    def __init__(self):
        self.socket = None

    def connect(self, server, port=SMTP_PORT):
        self.socket = ssl.wrap_socket(socket.socket())
        self.socket.connect((server, port))
        resp = self.get_response()
        print(resp)
        if resp[0:1] != "2":
            print("Connection failed")
            return False
        return True

    def send_command(self, cmd, param=""):
        if not param:
            self.socket.sendall(bytes(cmd + CRLF, "utf-8"))
        else:
            self.socket.sendall(bytes(cmd + " " + param + CRLF, "utf-8"))

    def greeting(self):
        self.send_command("HELO", "r47717")
        resp = self.get_response()
        print(resp)
        return True

    def auth(self, login, pwd):
        self.send_command("AUTH LOGIN")
        resp = self.get_response()
        if not goodresp(resp):
            return False
        self.socket.sendall(base64.b64encode(bytes(login, "utf-8")))
        self.socket.sendall(bytes(CRLF, "utf-8"))
        resp = self.get_response()
        if not goodresp(resp):
            return False
        self.socket.sendall(base64.b64encode(bytes(pwd, "utf-8")))
        self.socket.sendall(bytes(CRLF, "utf-8"))
        resp = self.get_response()
        if not goodresp(resp):
            return False
        return True

    def send_data(self, data_bytes):
        self.socket.sendall(data_bytes)

    def send_string(self, string):
        self.socket.sendall(bytes(string, "utf-8"))

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

    def send_header(self, email):
        """ e-mail headers are described in RFC822 """
        self.send_string("Subject: " + email["subject"] + CRLF)
        self.send_string("From: " + email["from"] + CRLF)
        self.send_string("To: " + email["to"] + CRLF)
        self.send_string("Content-Type: text/html"+ CRLF)

    def send_body(self, email):
        self.send_string(email["body"])
        self.send_string(CRLF + "." + CRLF)   # end of message marker

    def send_mail(self, email):
        self.send_command("MAIL", "FROM: %s" % email["from"])
        resp = self.get_response()
        print(resp)
        self.send_command("RCPT", "TO: %s" % email["to"])  # TODO: allow list of recipients
        resp = self.get_response()
        print(resp)
        self.send_command("DATA")
        resp = self.get_response()
        print(resp)
        self.send_header(email)
        self.send_string("\r\n")
        self.send_body(email)
        resp = self.get_response()
        print(resp)


def test_func():
    client = SmtpClient()
    if not client.connect("smtp.yandex.ru"):
        return
    client.greeting()
    if not client.auth("mchr", "<<password>>"):
        return
    email = {
        "from": "mchr@yandex.ru",
        "to": "mchr@yandex.ru",
        "subject": "Hello from Python",
        "body": """
        <html><body>
        <h1>Привет, друг!</h1>
        <p>Это параграф</p>
        <p>Это другой параграф</p>
        </body></html>
        """
    }
    client.send_mail(email)
    client.send_command("QUIT")
    resp = client.get_response()
    print(resp)



if __name__ == "__main__":
    test_func()