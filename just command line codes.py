#1
#PS D:\New python\Web Browser> python main.py http://example.org/

#2 in build command to read a http scheme in the port
# PS D:\New python\Web Browser> python -m http.server 8000 -d "D:\New python\Web Browser\example"
# Serving HTTP on :: port 8000 (http://[::]:8000/) ...
# ::1 - - [21/Aug/2024 22:01:51] "GET / HTTP/1.1" 200 -
# ::1 - - [21/Aug/2024 22:01:52] "GET /index.html HTTP/1.1" 200 -

#3 for scheme data
# python main.py "data:text/plain;base64,SGVsbG8gd29ybGQh"

#python gui.py https://browser.engineering/examples/xiyouji.html
#python main.py view-source:http://example.com

#to redirect
#python main.py http://browser.engineering/redirect


#### 2.1
# def lex(self, body):
#     text = ""
#     if self.view == True:
#         print("Showing view-source content:")
#         print(body)
#         return body
#     in_tag = False
#     i = 0
#     while i < len(body):
#         if body[i] == "<":
#             if body[i:i + 4].lower() == "<br":
#                 text += "\n"
#                 i += 4
#             elif body[i:i + 2].lower() == "</p":
#                 text += "\n"
#                 i += 3
#             else:
#                 in_tag = True
#         elif body[i] == ">":
#             in_tag = False
#         elif not in_tag:
#             text += body[i]
#         i += 1
#     print(text)
#     return text
