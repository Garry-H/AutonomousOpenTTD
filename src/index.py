import sys
import ctypes
from sdl2 import *
import sdl2.sdlimage
import numpy as np
from PIL import ImageGrab, Image
import cv2
import time


def process_img(original_image):
    processed_img = original_image
    processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    return processed_img

def convertPILImageToSDLRGBSurface(pil_image_input):
    pxbuf = pil_image_input.tobytes()
    mode = pil_image_input.mode
    width, height = pil_image_input.size
    rmask = gmask = bmask = amask = 0
    if mode in ("1", "L", "P"):
        # 1 = B/W, 1 bit per byte
        # "L" = greyscale, 8-bit
        # "P" = palette-based, 8-bit
        pitch = width
        depth = 8
    elif mode == "RGB":
        # 3x8-bit, 24bpp
        if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
            rmask = 0x0000FF
            gmask = 0x00FF00
            bmask = 0xFF0000
        else:
            rmask = 0xFF0000
            gmask = 0x00FF00
            bmask = 0x0000FF
        depth = 24
        pitch = width * 3
    elif mode in ("RGBA", "RGBX"):
        # RGBX: 4x8-bit, no alpha
        # RGBA: 4x8-bit, alpha
        if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
            rmask = 0x000000FF
            gmask = 0x0000FF00
            bmask = 0x00FF0000
            if mode == "RGBA":
                amask = 0xFF000000
        else:
            rmask = 0xFF000000
            gmask = 0x00FF0000
            bmask = 0x0000FF00
            if mode == "RGBA":
                amask = 0x000000FF
        depth = 32
        pitch = width * 4
    else:
        # We do not support CMYK or YCbCr for now
        raise TypeError("unsupported image format")

    imgsurface = SDL_CreateRGBSurfaceFrom(pxbuf, width, height, depth, pitch, rmask, gmask, bmask, amask)
    imgsurface = imgsurface.contents
    # the pixel buffer must not be freed for the lifetime of the surface
    imgsurface._pxbuf = pxbuf

    return imgsurface

# while(True):
#     screen = np.array(ImageGrab.grab(bbox=(0,80, 800, 640)))
#     new_screen = process_img(screen)
#     pil_screen = Image.fromarray(new_screen)

#     cv2.imshow('window', new_screen)
#     # cv2.imshow('window', cv2.cvtColor(np.array(printscreen_pil), cv2.COLOR_BGR2RGB))
#     print('Process cycle took, %s seconds' % (time.time()-last_time))
#     last_time = time.time()
#     if cv2.waitKey(25) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break

def main():
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"Hello World",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              800, 560, SDL_WINDOW_SHOWN)
    windowsurface = SDL_GetWindowSurface(window)

    last_time = time.time()
    event = SDL_Event()
    running = True

    while running:
        print('Process cycle took, %s seconds' % (time.time()-last_time))
        last_time = time.time()
        screen_capture = ImageGrab.grab(bbox=(0, 80, 800, 640))
        np_image = np.array(screen_capture)
        processed_image = process_img(np_image)
        pil_image = Image.fromarray(processed_image).convert("RGBA")
        # pil_image.save("img.png", "PNG")
        # print(pil_image.mode)
        # cv2.imshow('window', processed_image)
        # print(Image.fromarray(processed_image))
        imagesurface = convertPILImageToSDLRGBSurface(pil_image)

        SDL_BlitSurface(imagesurface, None, windowsurface, None)
        SDL_UpdateWindowSurface(window)
        SDL_FreeSurface(imagesurface)
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break

    SDL_DestroyWindow(window)
    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
