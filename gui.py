import tkinter
from main import URL
WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

class Browser:
    def __init__(self):
        self.window=tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.display_list = ""
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y-self.scroll, text=c)

    def load(self,  url_obj):
        body = url_obj.request()
        text = url_obj.lex(body)
        self.display_list = layout(text)
        self.draw()


    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        self.draw()
    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()







def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:

        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP

    return display_list

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "file:///example/index.html"
    url_obj = URL(url)
    browser = Browser()
    browser.load(url_obj)
    tkinter.mainloop()