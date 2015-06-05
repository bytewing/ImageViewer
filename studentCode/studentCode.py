import math
import time

from viewer import ImageViewer

def abbey1():
    print("abbey 1")
    gray_scale()

def abbey():
    v = ImageViewer.get_viewer()
    h = v.get_height()
    w = v.get_width()

    red = int(input("How much %$#$%??? many red do you want? "))
    green = int(input ("How much *&*&*&* many green do you want? "))
    blue = int(input ("How much &&&& blue do you want? "))

    for x in range(w):
        for y in range(h):
            v.set_pixel(x,y,red,green,blue)

def gray_scale():
    v = ImageViewer.get_viewer()
    h = v.get_height()
    w = v.get_width()

    for x in range(w):
        for y in range(h):
            r, g, b = v.get_pixel(x, y)
            avg = (r + g + b) // 3
            v.set_pixel(x, y, avg, avg, avg)

def blank_square():
     v = ImageViewer.get_viewer()
     img = v.blank_image(400, 400)

     for x in range(img.get_width()):
        for y in range(img.get_height()):
            if x > y:
                img.set_pixel(x,y,255,0,0)
            else:
                img.set_pixel(x,y,0,255,0)

     v.display_image(img)

def upside_down():
    v = ImageViewer.get_viewer()
    v.show_message("Executing upside down")

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
            v.set_pixel(x, y, r,b,g)

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
    return v.get_pixel(cx, cy)

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

def __dist(x1,y1, x2,y2):
    return math.sqrt( (x1-x2)**2 + (y1-y2)**2)

def xy_foo():
    v = ImageViewer.get_viewer()

    w = v.get_width()
    h = v.get_height()

    cx = w//2
    cy = h//2

    red,green,blue = 255,0,0

    r_max = 0
    for theta in range(0, 360):
        if theta > 0 and theta % 20 == 0:
            red,green = green,red
        for r in range(0, r_max):
            __mark_pixel(blue, cx, cy, green, r, red, theta, v)
            time.sleep(0.00001)

        r_max += 1
        r_max = min(r_max, h//2)


def __mark_pixel(blue, cx, cy, green, r, red, theta, v):
    angle = theta * math.pi / 180
    x = cx + r * math.cos(angle)
    y = cy + r * math.sin(angle)
    v.set_pixel(x, y, red, green, blue)

def four_corners():
    v = ImageViewer.get_viewer()

    w = v.get_width()
    h = v.get_height()

    d = 300
    for y in range(h):
        for x in range(w):
            if __dist(x,y, 0, 0) < d or  __dist(x,y, 0, h-1) < d or __dist(x,y,w-1,0 ) < d or __dist(x, y, w-1, h-1) < d:
                    v.set_pixel(x, y, 255, 0, 0)
            else:
                    v.set_pixel(x, y, 0, 255, 0)



def xy_spiral():
    v = ImageViewer.get_viewer()

    w = v.get_width()
    h = v.get_height()

    cx = w//2
    cy = h//2

    red,green,blue = 255,0,0

    theta = 0
    r = 0
    while r < h//2:
        for w in range(-5,1):
            __mark_pixel(blue, cx, cy, green, r+w, red, theta, v)
        time.sleep(0.00001)
        r += 0.005
        theta += 0.1


def xy_red():
    v = ImageViewer.get_viewer()

    w = v.get_width()
    h = v.get_height()
    cx = w//2
    cy = h//2

    for y in range(h):
        for x in range(w):
            d = __dist(x,y, cx, cy)
            r,g,b = 0,0,0
            if d < 75:
                r = 255
            elif 75 <= d and d < 150:
                g = 255
            elif 150 <= d and d < 225:
                b = 255
            else:
                r = g = b = 255

            v.set_pixel(x,y,r,g,b)

def horizontal_stripes():
    v = ImageViewer.get_viewer()

    w = v.get_width()
    h = v.get_height()

    for y in range(h):
        for x in range(w):
            r,g,b = 0,0,0
            if y < h//3:
                r = 255
            elif h/3 <= y and y < 2*h/3:
                g = 255
            else:
                b = 255
            v.set_pixel(x,y,r,g,b)


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
            if __distance(r, g, b, ra, ga, ba) < 40:
                v.set_pixel(x, y, ra_1, ga_1, ba_1)


if __name__ == '__main__':
    import tkinter
    #ImageViewer(tkinter.Tk())
    ImageViewer()