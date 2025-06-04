import tkinter
import tkinter.font

from scipy.signal import chirp

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
        self.document = []

    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT: continue
            if cmd.bottom < self.scroll: continue
            cmd.execute(self.scroll, self.canvas)
        # self.draw_scrollbar()



    def load(self, url_obj):
        body = url_obj.request()
        self.nodes = HTMLparser(body).parse()
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

    def scrollup(self, e):
        if self.scroll > 0:
            self.scroll -= SCROLL_STEP
            self.draw()

    def scrolldown(self, e):
        max_y = max(self.document.height + 2 * VSTEP - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
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
        self.document = DocumentLayout(self.nodes)
        self.document.layout()
        self.display_list = []
        paint_tree(self.document, self.display_list)
        self.draw()

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []
        # self.display_list = []
        self.x = HSTEP
        self.y = VSTEP
        self.width = WIDTH - 2 * HSTEP


    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()
        self.width = WIDTH - 2 * HSTEP
        self.x = HSTEP
        self.y = VSTEP

        self.height = child.height


    def paint(self):
        return []

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]

class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

        self.x = 0
        self.y = None
        self.width = 0
        self.height = 0

        self.display_list = []
        self.line = []
        self.superscripts = False
        self.width = 0
        self.center = False
        self.cursor_x = HSTEP
        self.cursor_y = 0
        self.weight = "normal"
        self.style = "roman"
        self.size = 12


    def layout(self):
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        self.x = self.parent.x
        self.width = self.parent.width

        mode = self.layout_mode()
        if mode == "block":
            self.height = sum([child.height for child in self.children])
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 12
            self.height = self.cursor_y
            self.line = []
            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

    def paint(self):
        cmds = []
        if isinstance(self.node, Element) and self.node.tag == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, "gray")
            cmds.append(rect)
        if self.layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))
        return cmds

    def layout_intermediate(self):
        previous = None
        for child in self.node.children:
            next = BlockLayout(child, self, previous)
            self.children.append(next)
            previous = next


    def layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and child.tag in BLOCK_ELEMENTS for child in self.node.children]):
            return "block"
        elif self.node.children :
            return "inline"
        else:
            return "block"

    def open_tag(self, tag):
        if tag == "b":
            self.weight = "bold"
        elif tag == "i":
            self.style = "italic"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "br":
            self.flush()
        elif tag == "h1":
            self.flush()
            self.center = True
        elif tag == "sup":
            self.size = self.size // 2
            self.superscripts = True

    def close_tag(self, tag):
        if tag == "/b":
            self.weight = "normal"
        elif tag == "/i":
            self.style = "roman"
        elif tag == "/small":
            self.size += 2
        elif tag == "/big":
            self.size -= 4
        elif tag == "/p":
            self.flush()
            self.cursor_y += VSTEP
        elif tag == "/h1":
            self.flush()
            self.center = False
        elif tag == "/sup":
            self.size = self.size * 2
            self.superscripts = False

    def recurse(self, tree):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self.word(word)
        else:
            self.open_tag(tree.tag)
            for child in tree.children:
                self.recurse(child)
            self.close_tag(tree.tag)

    def word(self, word):
        font = get_font(self.size, self.weight, self.style)
        width = font.measure(word)

        if self.cursor_x + width >= self.width:
            self.flush()
            self.cursor_y += VSTEP
            self.cursor_x = HSTEP
        self.line.append((self.cursor_x, word, font))
        self.cursor_x += width + HSTEP

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        max_descent = max([metric["descent"] for metric in metrics])

        line_height = 1.25 * (max_ascent + max_descent)

        baseline = self.cursor_y + (max_ascent)
        #
        # if self.center:
        #     total_width = sum([font.measure(word) + HSTEP for x, word, font in self.line])
        #     start_x = (self.width - total_width) / 2
        #     cursor = start_x
        #     for rel_x,word, font in self.line:
        #         x = self.x + rel_x
        #         y = self.y + baseline - font.metrics("ascent")
        #         self.display_list.append(DrawText(x, y, word, font))
        #         cursor += font.measure(word) + HSTEP

        # else:
        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
                # if sup:
                #     y -= 10
            self.display_list.append(DrawText(x, y, word, font))


        self.cursor_y += max_ascent + max_descent + 5
        self.cursor_x = HSTEP
        print("baseline:", baseline, "cursor_y:", self.cursor_y)
        self.line = []


    def paint(self):
        cmds = []
        if isinstance(self.node, Element) and self.node.tag == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, "gray")
            cmds.append(rect)
        if self.layout_mode() == "inline":
            for cmd in self.display_list:
                cmds.append(cmd)
        return cmds


def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


class DrawText:
    def __init__(self, x1, y1, text, font):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")

    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            anchor='nw')

class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=0,
            fill=self.color)



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