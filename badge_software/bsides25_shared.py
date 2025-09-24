from machine import Pin, I2C
from writer.writer import Writer
import writer.freesans20 as freesans20
import writer.font10 as font10
import writer.font6 as font6
import ssd1306, neopixel


# -----------------------
# Settings
# -----------------------
I2C_SCL = 1
I2C_SDA = 0
OLED_WIDTH = 128
OLED_HEIGHT = 64

NEOPIXEL_PIN = 3
NEOPIXEL_COUNT = 16
NEOPIXEL_FPS = 50

# Buttons
BTN_NEXT_PIN = 5      # Next / Increase
BTN_PREV_PIN = 8      # Previous / Decrease
BTN_SELECT_PIN = 4    # Enter
BTN_BACK_PIN = 9      # Back
DEBOUNCE_MS = 50

# Auto-repeat
REPEAT_DELAY = 500     # ms before auto-repeat starts
REPEAT_INTERVAL = 10  # ms between repeats

INACTIVITY_TIMEOUT = 5000  # ms
LOGO_PERIOD = 3000  # ms

SSID = "bsides-badge"
PASSWORD = "bsidestallinn"
URL = "https://badge.bsides.ee"
URL_QR = "badge.bsides.ee"

# -----------------------
# Globals
# -----------------------
button_event = None
last_button = None
last_activity = 0

BTN_NEXT = 1
BTN_PREV = 2
BTN_SELECT = 3
BTN_BACK = 4

#btn_state = {}       # {btn_id: pressed or not}
#repeat_tasks = {}    # {btn_id: task}
#_last_event_ms = {}  # debounce tracking

i2c_oled = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c_oled)
wri6  = Writer(oled, font6, verbose=False)
wri10 = Writer(oled, font10, verbose=False)
wri20 = Writer(oled, freesans20, verbose=False)

username_wri = wri20
username_lines = None

# -----------------------
# Screen base class
# -----------------------
class Screen:
    def __init__(self, oled):
        self.oled = oled
        self.do_animate = False

    def render(self):
        pass

    async def animate_task(self):
        pass

    async def handle_button(self, btn):
        pass


menuscreen_items = []
class MenuScreen(Screen):
    items = menuscreen_items

    def __init__(self, oled):
        super().__init__(oled)
        self.index = 0
        self.render()

    def render(self):
        self.oled.fill(0)
        wri20.set_textpos(self.oled, 17, 20)
        wri20.printstring(MenuScreen.items[self.index][0])
        self.oled.show()

    async def handle_button(self, btn):
        if btn == BTN_NEXT:
            self.index = (self.index+1) % len(MenuScreen.items)
            self.render()
        elif btn == BTN_PREV:
            self.index = (self.index-1) % len(MenuScreen.items)
            self.render()
        elif btn == BTN_SELECT:
            return MenuScreen.items[self.index][1](self.oled)
        return self

class TextScreen(Screen):
    def __init__(self, oled, writer, text):
        super().__init__(oled)
        self.wri = writer

        # wrap long text
        self.text = self._wrap_text(text)

        # metrics
        self.line_height = self.wri.font.height()
        self.rows = oled.height // self.line_height
        self.offset = 0

    def _wrap_text(self, text):
        lines = []
        # split paragraphs by explicit newline
        for para in text.split("\n"):
            words = para.split()
            line = ""
            for word in words:
                test_line = (line + " " + word).strip()
                if self.wri.stringlen(test_line) <= self.oled.width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
            if para == "":  # preserve blank lines
                lines.append("")
        return lines

    def render(self):
        self.oled.fill(0)
        y = 0
        for i in range(self.offset, min(len(self.text), self.offset + self.rows)):
            self.wri.set_textpos(self.oled, y, 0)
            self.wri.printstring(self.text[i])
            y += self.line_height
        self.oled.show()

    async def handle_button(self, btn):
        if btn == BTN_NEXT and self.offset + self.rows < len(self.text):
            self.offset += 1
        elif btn == BTN_PREV and self.offset > 0:
            self.offset -= 1
        elif btn == BTN_BACK:
            return MenuScreen(self.oled)
        return self

def hsv_to_rgb(h, s, v):
    """Convert hue [0–360], saturation [0–1], value [0–1] to RGB tuple."""
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (int((r + m) * 255),
            int((g + m) * 255),
            int((b + m) * 255))
