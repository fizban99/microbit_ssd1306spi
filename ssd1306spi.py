from microbit import spi, pin16, pin14, pin15, Image


class SSD1306:
    def __cmd(self, c):
        pin16.write_digital(0)
        spi.write(bytearray(c))
        pin16.write_digital(1)

    def __init__(self):
        c = b'\xAE\xA4\xD5\xF0\xA8\x3F\xD3\x00\x00\x8D'  \
              b'\x14\x20\x00\x21\x00\x7F\x22\x00\x3F\xa1'  \
              b'\xc8\xDA\x12\x81\xCF\xd9\xF1\xDB\x40\xA6\xd6\x00\xaf'
        pin14.write_digital(0)
        spi.init(miso=pin15, baudrate=8000000)
        pin14.write_digital(1)
        self.__cmd(c)
        self.screen = bytearray(1024)

    def __set_pos(self, col=0, page=0):
        c1, c2 = col * 2 & 0x0F, col >> 3
        self.__cmd([0xb0 | page, 0x00 | c1, 0x10 | c2])

    def clear_oled(self):
        for i in range(0, 1024):
            self.screen[i] = 0
        self.draw_screen()

    def draw_screen(self):
        self.__set_pos()
        spi.write(self.screen)

    def draw_sprite(self, x, y, sprite, color, d=1):
        page, shiftPage = divmod(y, 8)
        i = x + (page << 7)
        if i >= 0:
            for col in range(0, 8):
                index = i + col
                b = (self.screen[index] | (sprite[col] << shiftPage)
                     ) if color else (self.screen[index] &
                                      ~ (sprite[col] << shiftPage))
                self.screen[index] = b
        i += 128
        if i < 1024:
            for col in range(0, 8):
                index = i + col
                b = (self.screen[index] | (sprite[col] >> (8 - shiftPage))
                     ) if color else self.screen[index] & \
                    ~ (sprite[col] >> (8 - shiftPage))
                self.screen[index] = b
        if d:
            self.draw_screen()

    def show_bitmap(self, filename):
        self.__set_pos()
        with open(filename, 'rb') as my_file:
            for i in range(0, 16):
                spi.write(my_file.read(64))

    def set_px(self, x, y, color):
        page, shiftPage = divmod(y, 8)
        i = x + page * 128 + 1
        b = self.screen[i] | (1 << shiftPage) if color else self.screen[
            i] & ~ (1 << shiftPage)
        self.screen[i] = b
        self.__set_pos(x, page)
        spi.write(bytearray([b]))

    def get_px(self, x, y):
        page, shiftPage = divmod(y, 8)
        i = x + page * 128 + 1
        return (self.screen[i] & (1 << shiftPage)) >> shiftPage

    def add_text(self, x,  y, text, s=1):
        for i in range(0,  min(len(text), 25//s - x)):
            for c in range(0, 5):
                col = 0
                for r in range(1, 6):
                    p = Image(text[i]).get_pixel(c, r - 1)
                    col = col | (1 << r * s) if (p != 0) else col
                    if s == 2:
                        col = col | (1 << (r * s)-1) if (p != 0) else col
                ind = x * 5 * s + y * 128 + i * 5 * s + c * s + 1
                if s == 2:
                    self.screen[ind+128],self.screen[ind] = divmod(col, 0x100)
                    self.screen[ind+1]=self.screen[ind]
                    self.screen[ind+129]=self.screen[ind+128]
                else:
                    self.screen[ind] = col
        self.draw_screen()
