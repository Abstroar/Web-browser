#1
#PS D:\New python\Web Browser> python main.py http://example.org/

#2 in build command to read a http scheme in the port
# PS D:\New python\Web Browser> python -m http.server 8000 -d "D:\New python\Web Browser\example"
# Serving HTTP on :: port 8000 (http://[::]:8000/) ...
# ::1 - - [21/Aug/2024 22:01:51] "GET / HTTP/1.1" 200 -
# ::1 - - [21/Aug/2024 22:01:52] "GET /index.html HTTP/1.1" 200 -

#3 for scheme data
# python main.py "data:text/plain;base64,SGVsbG8gd29ybGQh"

#
#python main.py view-source:http://example.com