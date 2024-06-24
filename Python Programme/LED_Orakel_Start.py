import time
import board
import neopixel

pixel_pin = board.D18
num_pixels = 24

ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
)

for i in range (5):
    pixels.fill((200, 200, 200))
    pixels.show()
    time.sleep(0.1)

    pixels.fill((0, 0, 0))
    pixels.show()
    time.sleep(0.1)

pixels.fill((200, 0, 0))
pixels.show()
time.sleep(5)

pixels.fill((10, 0, 20))
pixels.show()