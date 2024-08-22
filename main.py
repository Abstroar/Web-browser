import base64
import socket
import ssl
import os

class URL:
    def __init__(self, url):
        if "://" in url:
            self.scheme, url = url.split("://", 1)
        else:
            # Handle the case where there is no scheme (e.g., data URLs)
            self.scheme = "data"
        assert self.scheme in ["http", "https","file","data"]
        if self.scheme in ["http","https"]:
            self.port = 443 if self.scheme =="https" else 80
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

    def request(self):
        if self.scheme in ["http", "https"]:
            s = socket.socket(
                family=socket.AF_INET,
                type=socket.SOCK_STREAM,
                proto=socket.IPPROTO_TCP
            )
            s.connect((self.host, self.port))

            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)

            header = {
                "Host": self.host,
                "Connection":"close",
                "User-Agent":"Abstro_browser/1.0",
            }

            request = "GET {} HTTP/1.0\r\n".format(self.path)
            for i,j in header.items():
                request += f"{i}: {j}\r\n"
            request += "\r\n"

            s.send(request.encode("utf8"))
            response = s.makefile("r", encoding="utf8", newline="\r\n")
            statusline = response.readline()
            version, status, explanation = statusline.split(" ",2)
            response_headers = {}
            while True:
                line = response.readline()
                if line == "\r\n":break
                header, value = line.split(":",1)
                response_headers[header.casefold()] = value.strip()
            assert "transfer-encoding" not in response_headers
            assert "content-encoding" not in response_headers
            content = response.read()
            s.close()
            return content
        elif self.scheme == "file":
            try:
                with open(self.path, "r", encoding="utf8") as file :
                    return file.read()
            except FileNotFoundError:
                return f"File not found at the path :{self.path}"
            except Exception as e:
                return f"exception occoured :{e}"
        elif self.scheme == "data":
            if self.is_base64:
                return base64.b64decode(self.data).decode("utf8")
            else:
                return self.data
    def show(self, body):
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
        body = url.request()
        self.show(body)


if __name__ == "__main__":
    import sys
    default_file_path = "D:/New python/Web Browser/example/index.html"
    if len(sys.argv) < 2:
        url = f"file:///{default_file_path}"
    else:
        url = sys.argv[1]
    browser = URL(url)
    browser.load(URL(url))

