import time
import board
import neopixel

pixel_pin = board.D18
num_pixels = 24

ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=1.0, auto_write=False, pixel_order=ORDER
)

pixels.fill((0, 0, 0))
pixels.show()
