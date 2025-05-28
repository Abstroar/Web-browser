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

#
# def re_layout(self, tokens):
#     display_list = []
#     cursor_x, cursor_y = HSTEP, VSTEP
#     weight = "normal"
#     style = "roman"
#     for tok in tokens:
#         if isinstance(tok, Text):
#             for word in tok.text.split():
#                 font = tkinter.font.Font(size=16, weight=weight, slant=style)
#                 display_list.append((cursor_x, cursor_y, word, font))
#                 cursor_x += HSTEP * len(word) + HSTEP
#                 if cursor_x >= self.width - HSTEP - 100:
#                     cursor_y += VSTEP
#                     cursor_x = HSTEP
#
#         elif isinstance(tok, Element):
#             if tok.tag == "br" or tok.tag == "p":
#                 cursor_y += VSTEP * 2
#                 cursor_x = HSTEP
#             elif tok.tag == "b":
#                 weight = "bold"
#             elif tok.tag == "/b":
#                 weight = "normal"
#             elif tok.tag == "i":
#                 style = "italic"
#             elif tok.tag == "/i":
#                 style = "roman"
#
#     return display_list