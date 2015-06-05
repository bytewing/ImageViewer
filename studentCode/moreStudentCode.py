import math

from viewer import ImageViewer


def gray_scale():
    v = ImageViewer.get_viewer()
    h = v.get_height()
    w = v.get_width()

    for x in range(w):
        for y in range(h):
            r, g, b = v.get_pixel(x, y)
            avg = (r + g + b) // 3
            v.set_pixel(x, y, avg, avg, avg)


def upside_down():
    v = ImageViewer.get_viewer()
    h = v.get_height()
    w = v.get_width()

    # get an empty image (white) of specified size
    img = ImageViewer.blank_image(w, h)

    for x in range(w):
        for y in range(h):
            r, g, b = v.get_pixel(x, y)
            img.set_pixel(x, h - 1 - y, r, g, b)

    v.display_image(img)


def red_filter():
    v = ImageViewer.get_viewer(0)
    for x in range(v.get_width()):
        for y in range(v.get_height()):
            r, g, b = v.get_pixel(x, y)
            v.set_pixel(x, y, r, 0, 0)


def redSquare():
    v = ImageViewer.get_viewer()
    for j in range(50):
        for i in range(50):
            v.set_pixel(20 + i, 20 + j, 255, 0, 0)


# copy a square region from the image in the active ImageViewer to the image in ImageViewer 1
def slingPixels():
    x = input("Enter a number: ")

    v = ImageViewer.get_viewer()
    v1 = ImageViewer.get_viewer(1)
    width = v.get_width()
    height = v.get_height()
    for x in range(0, width):
        for y in range(0, height // 2):
            r, g, b = v.get_pixel(x, y)
            v1.set_pixel(x, y + height // 2, r, g, b)
            # time.sleep(0.001)

    print("Hello there!")

def console_io():
    s = input("Enter ?? ")
    print("Helloo...",s)

def __get_avg(v):

    width = v.get_width()
    height = v.get_height()
    cx = width // 2
    cy = height // 2
    #return v.get_pixel(cx, cy)

    r_t = 0
    g_t = 0
    b_t = 0

    dx = 20
    dy = 20
    for x in range(cx - dx, cx + dx):
        for y in range(cy - dy, cy + dy):
            r, g, b = v.get_pixel(x, y)
            r_t += r
            g_t += g
            b_t += b

    r_avg = r_t // (dx * dy)
    g_avg = g_t // (dx * dy)
    b_avg = b_t // (dx * dy)

    return r_avg, g_avg, b_avg


def __distance(r, g, b, ra, ga, ba):
    return math.sqrt((r - ra) ** 2 + (g - ga) ** 2 + (b - ba) ** 2)


def color_face():
    v = ImageViewer.get_viewer()

    width = v.get_width()
    height = v.get_height()

    v1 = ImageViewer.get_viewer(1)
    ra, ga, ba = __get_avg(v)
    ra_1, ga_1, ba_1 = __get_avg(v1)

    for x in range(width):
        for y in range(height):
            r, g, b = v.get_pixel(x, y)
            if __distance(r, g, b, ra, ga, ba) < 80:
                v.set_pixel(x, y, ra_1, ga_1, ba_1)


if __name__ == '__main__':
    ImageViewer()
