from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import json
import os
from datetime import datetime
from jinja2 import Template

STORAGE_DIR = os.getenv('STORAGE_DIR', 'storage')
DATA_FILE = os.getenv('DATA_FILE', os.path.join(STORAGE_DIR, 'data.json'))
PORT = int(os.getenv('PORT', 3000))


def save_message(message):
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            messages = json.load(f)
    else:
        messages = {}
    timestamp = datetime.now().isoformat()
    messages[timestamp] = message
    with open(DATA_FILE, 'w') as f:
        json.dump(messages, f, indent=2)


def get_content_type(filename):
    if filename.endswith('.css'):
        return 'text/css'
    elif filename.endswith('.png'):
        return 'image/png'
    else:
        return 'application/octet-stream'


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            self.send_read_page()
        elif pr_url.path == '/logo.png' or pr_url.path == '/style.css':
            self.send_static_file(pr_url.path[1:])
        else:
            self.send_html_file('error.html', 404)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            form_data = urllib.parse.parse_qs(post_data.decode())
            message_data = {
                "username": form_data['username'][0],
                "message": form_data['message'][0]
            }
            save_message(message_data)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static_file(self, filename):
        if os.path.isfile(filename):
            self.send_response(200)
            self.send_header('Content-type', get_content_type(filename))
            self.end_headers()
            with open(filename, 'rb') as fd:
                self.wfile.write(fd.read())
        else:
            self.send_html_file('error.html', 404)

    def send_read_page(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                messages = json.load(f)
        else:
            messages = {}

        with open('read.html', 'r') as template_file:
            template = Template(template_file.read())

        response_html = template.render(messages=messages)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(response_html.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', PORT)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
