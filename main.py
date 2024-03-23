from json import dumps
from socketserver import TCPServer
from http.server import BaseHTTPRequestHandler

import requests
import configs


class MyHTTPHandler(BaseHTTPRequestHandler):

    @staticmethod
    def send_msg_to_google_chat(text: str):
        """Send message to Google Chat using a POST request

        Args:
            text (str): message to be sent

        Returns:
            response (Response): response from Google
        """
        url = configs.GOOGLE_WEBHOOK_URL
        headers = {"Content-Type": "application/json; charset=UTF-8"}
        message = {"text": text}
        response = requests.post(url, headers=headers,
                                 data=dumps(message), timeout=5)
        return response

    def do_invalid_method(self):
        self.send_header("Connection", "close")
        self.send_response(403)
        self.end_headers()
        self.log_error(
            "%s", f"Invalid method {self.command}. Request discarded.")

    def do_POST(self):
        if self.path == "/bgp-tools":
            self.send_header("Connection", "close")
            self.send_response(200)
            self.end_headers()
            self.log_message(
                "%s", "Valid request from bgp.tools."
                "Sending message to Google Workspace...")

            text = ""
            for line in self.rfile:
                text += line.decode()
            response = self.send_msg_to_google_chat(text)
            print(response.json())
        else:
            self.send_header("Connection", "close")
            self.send_response(403)
            self.end_headers()
            self.log_error(
                "%s", f"Invalid request path {self.path}. Request discarded.")

    def do_GET(self):
        self.do_invalid_method()

    def do_OPTIONS(self):
        self.do_invalid_method()

    def do_HEAD(self):
        self.do_invalid_method()


class MyTCPServer(TCPServer):

    def server_actions(self):
        print()
        super().server_actions()


def main():
    with MyTCPServer((configs.HOST, configs.PORT), MyHTTPHandler) as httpd:
        print("Server started.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt as err:
            print()
            print(err)
            print("Server aborted")


if __name__ == "__main__":
    main()
