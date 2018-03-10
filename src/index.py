import sys
import ctypes
from sdl2 import *
import sdl2.sdlimage
import numpy as np
from PIL import ImageGrab, Image
import cv2
import time


def drawTriangleToRender(input_renderer):
    SDL_SetRenderDrawColor(input_renderer, 0, 0, 0, SDL_ALPHA_OPAQUE)
    SDL_SetRenderDrawColor(input_renderer, 255, 255, 255, SDL_ALPHA_OPAQUE)
    SDL_RenderDrawLine(input_renderer, 10, 480, 320, 10)
    SDL_RenderDrawLine(input_renderer, 640, 480, 320, 10)
    SDL_RenderDrawLine(input_renderer, 10, 480, 640, 480)

def createRendererContext(input_window):
    return SDL_CreateRenderer(input_window, -1, 0, SDL_RENDERER_ACCELERATED | SDL_RENDERER_TARGETTEXTURE)

def process_img(original_image):
    processed_img = original_image
    processed_img = np.array(original_image)
    processed_img = cv2.cvtColor(processed_img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=200, threshold2=300)
    # processed_img = Image.fromarray(processed_img).convert("RGBA")
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

def main():
    SDL_Init(SDL_INIT_VIDEO)
    window = SDL_CreateWindow(b"Hello World",
                              1000, SDL_WINDOWPOS_CENTERED,
                              800, 560, SDL_WINDOW_SHOWN)
    windowsurface = SDL_GetWindowSurface(window)
    renderer = createRendererContext(window)

    last_time = time.time()
    event = SDL_Event()
    running = True

    last_frame = np.array([])
    prev_frame = np.array([])

    while running:
        print('Process cycle took, %s seconds' % (time.time()-last_time))
        last_time = time.time()

        screen_capture = ImageGrab.grab(bbox=(0, 80, 800, 640))
        diff_img = screen_capture
        processed_image = process_img(screen_capture)
        # processed_image = screen_capture

        if len(last_frame) > 0 or len(prev_frame) > 0:
            diff = cv2.absdiff(last_frame, np.array(processed_image))
            diff_img = Image.fromarray(diff).convert("RGBA")
            last_frame = np.array(processed_image)
        else:
            diff = cv2.absdiff(last_frame, np.array(processed_image))
            diff_img = Image.fromarray(diff).convert("RGBA")
            prev_frame = np.array(processed_image)


        image_surface = convertPILImageToSDLRGBSurface(diff_img)
        image_texture = SDL_CreateTextureFromSurface(renderer, image_surface)
        SDL_FreeSurface(image_surface)

        SDL_RenderClear(renderer)
        SDL_RenderCopy(renderer, image_texture, None, None)
        # drawTriangleToRender(renderer)
        SDL_RenderPresent(renderer)

        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break

    SDL_DestroyWindow(window)
    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
