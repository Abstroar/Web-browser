import tkinter



# from Tkinter import *
from main import URL
WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

class Browser:
    def __init__(self):
        self.window=tkinter.Tk()
        self.width = WIDTH
        self.height = HEIGHT
        self.canvas = tkinter.Canvas(
            self.window,
            width=self.width,
            height=self.height
        )

        self.canvas.pack(fill=tkinter.BOTH, expand=True)
        self.scroll = 0
        self.display_list = ""
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind_all("<MouseWheel>", self.on_mousewheel) ##binds the event globally
        self.window.bind("<Configure>", self.on_resize)

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + self.height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y-self.scroll, text=c)

    def re_layout(self, text):
        display_list = []
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in text:
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += HSTEP
            if cursor_x >= self.width - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP

        return display_list

    def load(self, url_obj):
        self.url_obj = url_obj
        body = url_obj.request()
        body = body.replace("</p>", "\n")

        self.text = url_obj.lex(body)
        self.display_list = self.re_layout(self.text)
        self.draw()


    def scrollup(self, e):
        if self.scroll > 0:
            self.scroll -= SCROLL_STEP
            self.draw()
    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def on_mousewheel(self, event):
        if event.delta > 0:
            self.scrollup(event)
        elif event.delta < 0:
            self.scrolldown(event)

    def on_resize(self,event):
        width = event.width
        height = event.height - 10
        self.width = width
        self.height = height
        self.display_list = self.re_layout(self.text)
        self.draw()


if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "file:///example/index.html"
    url_obj = URL(url)
    browser = Browser()
    browser.load(url_obj)
    tkinter.mainloop()