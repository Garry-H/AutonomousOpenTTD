from sdl2 import *
import sys
import ctypes


def init():
    if SDL_Init(SDL_INIT_EVERYTHING) != 0:
        return -1
    return 0

def draw(input_renderer):
    SDL_SetRenderDrawColor(input_renderer, 0, 0, 0, SDL_ALPHA_OPAQUE)
    SDL_RenderClear(input_renderer)
    SDL_SetRenderDrawColor(input_renderer, 255, 255, 255, SDL_ALPHA_OPAQUE)
    SDL_RenderDrawLine(input_renderer, 10, 480, 320, 10)
    SDL_RenderDrawLine(input_renderer, 640, 480, 320, 10)
    SDL_RenderDrawLine(input_renderer, 10, 480, 640, 480)

    SDL_RenderPresent(input_renderer)

def createWindowContext(input_title):
    return SDL_CreateWindow(ctypes.c_char_p(input_title.encode('utf-8')), SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 640, 480, SDL_WINDOW_OPENGL)

def createRendererContext(input_window):
    return SDL_CreateRenderer(input_window, -1, 0)

def main():
    init()
    window = createWindowContext("Hello World!")
    renderer = createRendererContext(window)
    draw(renderer)

    running = True
    event = SDL_Event()
    print("Hello World!")

    while running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                running = False
                break

    SDL_Quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
