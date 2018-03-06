import sys
import ctypes
from sdl2 import *
import sdl2.sdlimage
import numpy as np
from PIL import ImageGrab
import cv2
import time


def convertPILImageToSDLSurface(pil_image_input):
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

def main():
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"Hello World",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              592, 460, SDL_WINDOW_SHOWN)
    windowsurface = SDL_GetWindowSurface(window)


    running = True
    event = SDL_Event()
    while running:
        image = ImageGrab.grab(bbox=(0, 80, 800, 640))
        imagesurface = convertPILImageToSDLSurface(image)

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
