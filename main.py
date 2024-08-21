import socket
import ssl
import os

class URL:
    def __init__(self, url):
        self.scheme,url = url.split("://", 1)
        assert self.scheme in ["http", "https","file"]
        if self.scheme == ["http","https"]:
            self.port = 80 if self.scheme =="https" else 443
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
        elif self.scheme=="file":
            try:
                with open(self.path, "r", encoding="utf8") as file :
                    return file.read()
            except FileNotFoundError:
                return f"File not found at the path :{self.path}"
            except Exception as e:
                return f"exception occoured :{e}"
    def show(self,body):
        in_tag = False
        for c in body:
            if c =="<":
                in_tag = True
            elif c ==">":
                in_tag = False
            elif not in_tag:
                print(c, end="")

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

