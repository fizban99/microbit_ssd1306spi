from ssd1306spi import SSD1306
from microbit import button_a as A,  button_b as B, display as D
from random import randint
from sys import print_exception

try:
    def mv_sprt(oled, x1, y1, x2, y2, sprt):
        oled.draw_sprite(x1, y1, sprt, 0, 0)
        oled.draw_sprite(x2, y2, sprt, 1, 0)

    def init_star(i):
        return randint(0, 1), randint(0, 120), randint(1, 8)

    oled = SSD1306()
    oled.show_bitmap("splash")
    while not (A.is_pressed() or B.is_pressed()):
        pass
    oled.clear_oled()
    starSprite = [bytearray(b'\x1c"\x13"!\x12\x0c\x00'),
                  bytearray(b'\x18>?\x1f>\x1f\x0e\x04')]
    ship = bytearray(b'\x30\xa8\x7e\x81\x7e\xa8\x30\x00')
    starX, starY, star, speed = [0] * 5, [0] * 5, [0] * 5, [0] * 5
    for i in range(0, 5):
        star[i], starX[i], v = init_star(i)
        speed[i], starY[i] = v, -v
    shipX,  score, shipX0 = 64,  0, 64
    gameOver = False
    while not gameOver:
        for i in range(0, 5):
            shipX = shipX - 1 if (A.is_pressed() and shipX > 0) else shipX
            shipX = shipX + 1 if (B.is_pressed() and shipX < 120) else shipX
            mv_sprt(oled, shipX0, 56, shipX, 56, ship)
            shipX0 = shipX
            x, y, v = starX[i], starY[i], speed[i]
            sprt = starSprite[star[i]]
            if y + v > 55:
                score += 1
                oled.draw_sprite(x, y, sprt, 0, 1)
                s, x, v = init_star(i)
                star[i] = s
                sprt = starSprite[s]
                starX[i] = x
                starY[i], speed[i], y = -v, v, -v
            if y == -v:
                y0 = 0
            else:
                y0 = y
            y = y + v
            starY[i] = y
            mv_sprt(oled, x, y0, x, y, sprt)
            oled.draw_screen()
            if y > 47:
                if not (x + 4 < shipX or shipX + 4 < x
                        ):
                    oled.show_bitmap("game_over")
                    D.scroll("Score: " + str(score))
                    gameOver = True
                    break

except Exception as exc:
    print_exception(exc)
