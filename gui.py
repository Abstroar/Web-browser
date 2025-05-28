import tkinter
import tkinter.font


# from Tkinter import *
from main import *


FONTS = {}
def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight,
            slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]


WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
weight = "normal"
style = "roman"




class Browser:
    def __init__(self):
        self.window=tkinter.Tk()
        self.width = WIDTH
        self.height = HEIGHT
        self.canvas = tkinter.Canvas(
            self.window,
            width=self.width,
            height=self.height )
        self.canvas.pack(fill=tkinter.BOTH, expand=True)
        self.scroll = 0
        self.display_list = ""
        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind_all("<MouseWheel>", self.on_mousewheel) ##binds the event globally
        self.window.bind("<Configure>", self.on_resize)

    def draw(self):
        self.canvas.delete("all")

        for x, y, c, font in self.display_list:
            if y > self.scroll + self.height: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y-self.scroll, font=font,text=c, anchor="nw")
        self.draw_scrollbar()



    def load(self, url_obj):
        body = url_obj.request()
        self.tokens = lex(body)
        self.display_list = Layout(self.tokens, self.width).display_list
        self.draw()

    def scrollup(self, e):
        if self.scroll > 0:
            self.scroll -= SCROLL_STEP
            self.draw()
    def scrolldown(self, e):
        if self.display_list:
            max_y = max(max(y for _, y, _ , _ in self.display_list),1)
            if self.height + self.scroll < max_y:
                self.scroll += SCROLL_STEP
                self.draw()
    def draw_scrollbar(self):
        if not self.display_list:
            return
        max_y =  max(y for _, y, _ , _ in self.display_list)
        if max_y <= self.height:
            return
        bar_top = (self.scroll / max_y) * self.height
        bar_height = self.height * (self.height / max_y)

        x0 = self.width - 10
        x1 = self.width
        y0 = bar_top
        y1 = bar_top + bar_height
        self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue")

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
        self.display_list = Layout(self.tokens, self.width).display_list
        self.draw()

class Layout:
    def __init__(self, tokens, width):
        self.display_list = []
        self.line = []
        self.superscripts = False
        self.tokens = tokens
        self.width = width
        self.center = False
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 12
        for tok in tokens:
            self.token(tok)
        self.flush()


    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif isinstance(tok, Element):
            if tok.tag == "b":
                self.weight = "bold"
            elif tok.tag == "/b":
                self.weight = "normal"
            elif tok.tag == "i":
                self.style = "italic"
            elif tok.tag == "/i":
                self.style = "roman"
            elif tok.tag == "small":
                self.size -= 2
            elif tok.tag == "/small":
                self.size += 2
            elif tok.tag == "big":
                self.size += 4
            elif tok.tag == "/big":
                self.size -= 4
            elif tok.tag == "br":
                self.flush()
            elif tok.tag == "/p":
                self.flush()
                self.cursor_y += VSTEP
            elif tok.tag == "h1":
                self.flush()
                self.center = True
            elif tok.tag == "/h1":
                self.flush()
                self.center = False
            elif tok.tag == "sup":
                self.size = self.size//2
                self.superscripts = True
            elif tok.tag == "/sup":
                self.size = self.size * 2
                self.superscripts = False



    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        # self.display_list.append((self.cursor_x, self.cursor_y, word, font))
        width = font.measure(word)

        if self.cursor_x + width >= self.width - HSTEP:
            self.flush()
            self.cursor_y += VSTEP
            self.cursor_x = HSTEP
        self.line.append((self.cursor_x, word, font, self.superscripts))
        self.cursor_x += width + HSTEP

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font,_ in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent
        if self.center == True:
            total_width = sum([font.measure(word) + HSTEP for x, word, font, _ in self.line])
            start_x = (self.width - total_width) / 2
            cursor = start_x
            for _, word, font, sup in self.line:
                y = baseline - font.metrics("ascent")
                if sup:
                    y -= 10
                self.display_list.append((cursor, y, word, font))
                cursor += font.measure(word) + HSTEP

        else:
            for x, word, font, sup in self.line:
                y = baseline - font.metrics("ascent")
                if sup:
                    y -= 10
                self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []





if __name__ == "__main__":
    import sys


    url = sys.argv[1] if len(sys.argv) > 1 else "file:///example/index.html"
    try:
        url_obj = URL(url)
    except Exception as e:
        print("Malformed URL, loading about:blank:", e)
        url_obj = URL("about:blank")
    browser = Browser()
    browser.load(url_obj)
    tkinter.mainloop()