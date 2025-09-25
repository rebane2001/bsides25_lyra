import asyncio
import sys
import os
import framebuf
from bsides25_shared import *

def led_eff_trans(np, oldstate, **kwargs):
    """Rainbow running around the circle"""
    pos = (oldstate or 0) % (360*4)
    blue = hsv_to_rgb(160, 1, kwargs["led_brightness"].value/100)
    pink = hsv_to_rgb(310, 1, kwargs["led_brightness"].value/100)
    white = hsv_to_rgb(0, 0, kwargs["led_brightness"].value/100*0.9)
    stuff = [blue,pink,white,pink,blue]
    prev_color = stuff[int(pos/360)]
    next_color = stuff[int(pos/360)+1]
    for i in range(len(np)):
         np[i] = next_color if (pos%360)/360*len(np) < i else prev_color
    #    np[i] = [blue,pink,pink,white,white,pink,pink,blue,blue,pink,pink,white,white,pink,pink,blue][i]
    #    pixel_hue = ((i * 360 // len(np)) + pos) % 360
    #    np[i] = hsv_to_rgb(pixel_hue, kwargs["led_sat"].value/100, kwargs["led_brightness"].value/100)
    return (pos + kwargs["led_speed"].value/10)

def led_eff_trans_static(np, oldstate, **kwargs):
    """Rainbow running around the circle"""
    #pos = oldstate or 0
    blue = hsv_to_rgb(160, 1, kwargs["led_brightness"].value/100)
    pink = hsv_to_rgb(310, 1, kwargs["led_brightness"].value/100)
    white = hsv_to_rgb(0, 0, kwargs["led_brightness"].value/100*0.9)
    for i in range(len(np)):
        np[i] = [blue,pink,pink,white,white,pink,pink,blue,blue,pink,pink,white,white,pink,pink,blue][i]
    #    pixel_hue = ((i * 360 // len(np)) + pos) % 360
    #    np[i] = hsv_to_rgb(pixel_hue, kwargs["led_sat"].value/100, kwargs["led_brightness"].value/100)
    #return (pos + kwargs["led_speed"].value/10) % 360
    return 0

#class LyraScreen(TextScreen):
#    def __init__(self, oled):
#        text = (
#            "Lyra!"
#        )
#        super().__init__(oled, wri6, text)

class ImageScreen(Screen):
    def __init__(self, oled, prop):
        super().__init__(oled)

        # Import logos dynamically
        IMAGES_FOLDER = "images"
        if IMAGES_FOLDER not in sys.path:
            sys.path.append(IMAGES_FOLDER)
        self.image = __import__(prop).fb

    def render(self):
        self.oled.fill(0)
        self.oled.blit(self.image, 0, 0)
        self.oled.show()

    async def handle_button(self, btn):
        if btn == BTN_BACK:
            return LyraScreen(self.oled)
        return self

class AnimScreen(Screen):
    def __init__(self, oled, prop):
        super().__init__(oled)
        self.do_animate = True
        self.is_animating = True
        self.anim_speed = 75

        # Import logos dynamically
        ANIM_FOLDER = "images/anim"
        if ANIM_FOLDER not in sys.path:
            sys.path.append(ANIM_FOLDER)
        frame_files = sorted([f[:-3] for f in os.listdir(ANIM_FOLDER) if f.endswith(".py") and f.startswith(prop)])
        self.frames = list([__import__(f).fb for f in frame_files[::3]])
        #anim = __import__(prop)
        #self.anim_data = anim.anim_data
        #self.anim_diffs = anim.anim_diffs
        self.frame_id = 0

    def render(self):
        self.oled.fill(0)
        #fb = framebuf.FrameBuffer(self.anim_data, 128, 64, framebuf.MONO_HLSB)
        self.oled.blit(self.frames[self.frame_id], 0, 0)
        #self.oled.blit(fb, 0, 0)
        self.oled.show()
        #i = 0
        #anim_diff = self.anim_diffs[self.frame_id]
        #while i*3 < len(anim_diff):
        #    self.anim_data[anim_diff[i]] = anim_diff[i+1]
        #    i+=1
        self.frame_id = (self.frame_id + 1) % len(self.frames)

    async def animate_task(self):
        while self.is_animating:
            self.render()
            await asyncio.sleep_ms(self.anim_speed)

    async def handle_button(self, btn):
        if btn == BTN_PREV:
            self.anim_speed -= 5
            self.anim_speed = min(self.anim_speed, 5)
        if btn == BTN_NEXT:
            self.anim_speed += 5
        if btn == BTN_BACK:
            return LyraScreen(self.oled)
        return self

class LyraScreen(Screen):
    items = [
        ("Pic: LyraRebane",  ImageScreen, "lyra_rebane"),
        ("Pic: CssCriminal", ImageScreen, "css_criminal"),
        #("Test: Lyra 3D", ImageScreen, "lyra_010"),
        ("Anim: Lyra 3D", AnimScreen, "lyra_"),
    ]

    def __init__(self, oled):
        super().__init__(oled)
        self.index = 0
        self.render()

    def render(self):
        self.oled.fill(0)
        wri20.set_textpos(self.oled, 17, 20)
        wri20.printstring(self.items[self.index][0])
        self.oled.show()

    async def handle_button(self, btn):
        if btn == BTN_NEXT:
            self.index = (self.index+1) % len(self.items)
            self.render()
        elif btn == BTN_PREV:
            self.index = (self.index-1) % len(self.items)
            self.render()
        elif btn == BTN_SELECT:
            return self.items[self.index][1](self.oled, self.items[self.index][2])
        elif btn == BTN_BACK:
            return MenuScreen(self.oled)
        return self

for item in [("Lyra", LyraScreen),]:
    menuscreen_items.append(item)