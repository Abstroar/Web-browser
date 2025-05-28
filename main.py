import base64
import gzip
import io
import socket
import ssl
import os   
import time
from io import text_encoding


class Text:
    def __init__(self, text, parent):
        self.text = text
        self.children = []
        self.parent = parent
class Element:
    def __init__(self, tag, parent):
        self.tag = tag
        self.children = []
        self.parent = parent


class URL:
    def __init__(self, url):
        self.redirect = 0
        self.cache = {}
        self.socket = None
        if url.startswith("view-source:"):
            self.view = True
            url = url[len("view-source:"):]
        else:
            self.view = False
        if "://" in url:
            # if self.scheme == "view-source":
            #     _,url = url.split("://", 1)
            # else:
            self.scheme, url = url.split("://", 1)
        else:
            # Handle the case where there is no scheme (e.g., data URLs)
            self.scheme = "data"
        assert self.scheme in ["http", "https","file","data", "view-source"]
        if self.scheme in ["http","https"]:
            self.port = 443 if self.scheme == "https" else 80
        # if ":" in self.host:
        #     self.host, port = self.host.split(":", 1)
        #     self.port = int(port)
            if "/" not in url:
                url = url+"/"
            self.host,url = url.split("/",1)
            self.path = "/"+url
            if ":" in self.host:
                self.host, port = self.host.split(":", 1)
                self.port = int(port)
        elif self.scheme == "file":
            if url.startswith("/"):
                url = url[1:]
            self.path = url
        elif self.scheme == "data":
            self.mime_type, data = url.split(",", 1) #mime_type:string that specifies the nature and format of a file or data.
            self.is_base64 = self.mime_type.endswith(";base64")
            if self.is_base64:
                self.mime_type = self.mime_type[:-7]  # Remove ';base64'
            self.data = data

    def create_socket(self):
        if self.socket is None:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )
            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)
            self.socket = s
        return self.socket

    def request(self):
        print(f"path {self.path}")
        if self.path == "about:blank":
            return ""
        try :
            if self.path in self.cache:
                cache_entry = self.cache[self.path]
                cache_headers = cache_entry['headers']

                max_age = int(cache_headers['cache-control'].split('=')[1])
                age = time.time() - cache_entry['timestamp']

                if age < max_age:
                    print("Serving from cache")
                    return cache_entry['content']
                else:
                    print("Cache expired, fetching new content")

            if self.scheme in ["http", "https"]:
                s = self.create_socket()
                print("reached in https")

                header = {
                    "Host": self.host,
                    "User-Agent": "Abstro_browser/1.0",
                    "Accept-Encoding": "gzip",
                }

                request = "GET {} HTTP/1.0\r\n".format(self.path)
                for i,j in header.items():
                    request += f"{i}: {j}\r\n"
                request += "\r\n"

                s.send(request.encode("utf8"))
                print(f"Request sent:\n{request}")
                response = s.makefile("rb", newline="\r\n")
                statusline = response.readline().decode("utf8")
                version, status, explanation = statusline.split(" ",2)
                status = int(status)
                response_headers = {}
                print(f"Status line: {statusline}")
                print(f"status : {status}")


                while True:
                    line = response.readline().decode("utf8")
                    if line == "\r\n":break
                    header, value = line.split(":",1)
                    response_headers[header.casefold()] = value.strip()
                assert "transfer-encoding" not in response_headers
                # assert "content-encoding" not in response_headers

                if status < 400 and status > 300:
                    if self.redirect > 2:
                        return f"error"
                    self.redirect += 1
                    if "://" in response_headers["location"]:
                        new_url = response_headers["location"]
                    else:
                        new_url = (f"{url}{response_headers['location']}")
                    print(f"{new_url} redirected to ")
                    url_obj = URL(new_url)
                    return url_obj.request()

                if response_headers.get("content-encoding") == "gzip":
                    print("hey its gzip on the board")
                    compressed_data = response.read(int(response_headers['content-length']))
                    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
                        content = gz.read()
                else:
                    content = response.read(int(response_headers['content-length']))
                content = content.decode("utf8")
                if status == 200 and "cache-control" in response_headers:
                    self.cache[self.path] = {
                        'content': content,
                        'headers': response_headers,
                        'timestamp': time.time()
                    }
                #print(f"Content cached with max-age {max_age} seconds")
                return content
            elif self.scheme == "file":
                try:
                    with open(self.path, "r", encoding="utf8") as file :
                        return file.read()
                except FileNotFoundError:
                    return f"File not found at the path :{self.path}"
                except Exception as e:
                    return f"exception occurred :{e}"
            elif self.scheme == "data":
                if self.is_base64:
                    return base64.b64decode(self.data).decode("utf8")
                else:
                    return self.data
        except Exception as e:
            print("askksa",e)
            return ""

    def show(self, body):
        print(f"Showing content for scheme: {self.scheme}")
        if self.view == True:
            print("Showing view-source content:")
            print(body)
            return
        in_tag = False
        i = 0
        while i < len(body):
            if body[i] == "<":
                in_tag = True
            elif body[i] == ">":
                in_tag = False
            elif not in_tag:
                if body[i:i+4] == "&lt;":
                    print("<", end="")
                    i+=3
                elif body[i:i+4] == "&gt;":
                    print(">", end="")
                    i += 3
                else:
                    print(body[i], end="")
            i += 1

    def load(self,url):
        # print(f"Loading URL: {url}")
        body = url.request()
        # text = self.lex(body)
        if body is None:
            print("Error: No content received.")
        else:
            self.show(body)
class HTMLparser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []

    def parse(self):
        text = ""
        in_tag = False
        for c in self.body:
            if c == "<":
                in_tag = True
                if text: self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tags(text)
                text = ""
            else:
                text += c
        if not in_tag and text:
            self.add_text(text)
        return self.finish()


    def add_text(self, text):
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def add_tags(self, tag):
        if tag.startswith("/"):
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        else:
            parent = self.unfinished[-1]
            node = Element(tag, parent)
            self.unfinished.append(node)
    def finish(self):
        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)

        return self.unfinished.pop()

def lex(body):
    out = []
    buffer = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
            if buffer: out.append(Text(buffer))
            buffer = ""
        elif c == ">":
            in_tag = False
            out.append(Element(buffer))
            buffer = ""
        else:
            buffer += c
    if not in_tag and buffer:
        out.append(Text(buffer))
    return out

if __name__ == "__main__":
    import sys
    default_file_path = "D:/New python/Web Browser/example/index.html"
    if len(sys.argv) < 2:
        url = f"file:///{default_file_path}"
    else:
        url = sys.argv[1]
    browser = URL(url)
    browser.load(URL(url))
