from microbit import spi, pin16, pin14, pin15


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
        spi.init(miso=pin15, baudrate=16000000)
        pin14.write_digital(1)
        self.__cmd(c)
        c = None
        self.screen = bytearray(1024)

    def __set_pos(self, col=0, page=0):
        self.__cmd([0xb0 | page])  # page number
        # take upper and lower value of col * 2
        c1, c2 = col * 2 & 0x0F, col >> 3
        self.__cmd([0x00 | c1])   # lower start column address
        self.__cmd([0x10 | c2])   # upper start column address

    def clear_oled(self, c=0):
        self.__cmd([0xae])
        self.__set_pos()
        for i in range(0, 1024):
            self.screen[i] = 0
        self.draw_screen()
        self.__cmd([0xaf])

    def draw_screen(self):
        self.__set_pos()
        spi.write(self.screen)

    def draw_sprite(self, x, y, sprite, color, draw=1):
        page, shiftPage = divmod(y, 8)
        ind = x + (page << 7)
        if ind >= 0:
            for col in range(0, 8):
                index = ind + col
                b = (self.screen[index] | (sprite[col] << shiftPage)
                     ) if color else (self.screen[index] &
                                      ~ (sprite[col] << shiftPage))
                self.screen[index] = b
        ind += 128
        if ind < 1024:
            for col in range(0, 8):
                index = ind + col
                b = (self.screen[index] | (sprite[col] >> (8 - shiftPage))
                     ) if color else self.screen[index] & \
                    ~ (sprite[col] >> (8 - shiftPage))
                self.screen[index] = b
        if draw:
            self.draw_screen()

    def show_bitmap(self, filename):
        self.__set_pos()
        self.__cmd([0xae])
        pin16.write_digital(1)
        with open(filename, 'rb') as my_file:
            for i in range(0, 16):
                spi.write(my_file.read(64))
        self.__cmd([0xaf])

    def set_px(self, x, y, color, draw=1):
        page, shiftPage = divmod(y, 8)
        ind = x + page * 128 + 1
        b = self.screen[ind] | (1 << shiftPage) if color else self.screen[
            ind] & ~ (1 << shiftPage)
        self.screen[ind] = b
        if draw:
            self.__set_pos(x, page)
            spi.write(bytearray([b]))

    def get_px(self, x, y):
        page, shiftPage = divmod(y, 8)
        ind = x + page * 128 + 1
        b = (self.screen[ind] & (1 << shiftPage)) >> shiftPage
        return b
