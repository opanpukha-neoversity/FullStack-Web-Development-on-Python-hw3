from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime
import json
import mimetypes

from jinja2 import Environment, FileSystemLoader


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
DATA_FILE = STORAGE_DIR / "data.json"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def ensure_storage():
    STORAGE_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")


def load_messages():
    ensure_storage()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_message(username: str, message: str):
    data = load_messages()
    timestamp = str(datetime.now())
    data[timestamp] = {
        "username": username,
        "message": message
    }

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == "/":
            self.send_html_file("index.html")
        elif path == "/index.html":
            self.send_html_file("index.html")
        elif path == "/message.html":
            self.send_html_file("message.html")
        elif path == "/style.css":
            self.send_static_file(STATIC_DIR / "style.css")
        elif path == "/logo.png":
            self.send_static_file(STATIC_DIR / "logo.png")
        elif path == "/read":
            self.render_read_page()
        else:
            self.send_html_file("error.html", status=404)

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/message":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data_parse = parse_qs(body)

            username = data_parse.get("username", [""])[0]
            message = data_parse.get("message", [""])[0]

            save_message(username, message)

            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_html_file("error.html", status=404)

    def send_html_file(self, filename, status=200):
        file_path = BASE_DIR / filename

        if not file_path.exists():
            self.send_response(404)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1>")
            return

        self.send_response(status)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        with open(file_path, "rb") as file:
            self.wfile.write(file.read())

    def send_static_file(self, file_path: Path):
        if not file_path.exists():
            self.send_html_file("error.html", status=404)
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-type", mime_type)
        self.end_headers()

        with open(file_path, "rb") as file:
            self.wfile.write(file.read())

    def render_read_page(self):
        messages = load_messages()
        template = env.get_template("read.html")
        content = template.render(messages=messages)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))


def run(server_class=HTTPServer, handler_class=MyHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    print("Server started on http://127.0.0.1:3000")
    http.serve_forever()


if __name__ == "__main__":
    run()
