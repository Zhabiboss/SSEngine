import pygame
import sys
import os
from typing import Callable
import math

class Object:
    def __init__(self, layers: list[pygame.Surface], scale: tuple[float, float] | list[float, float] = None, 
                 position: tuple[float, float] | list[float, float] = [0, 0], height = None):
        
        """
            An object in the engine (a sprite)
            Arguments:
                layers: the images that will be used for the layers of the sprite
                scale: the resolution (on the scaled down display ref. Engine) of the sprite layers
                position: position on the scaled down display
                height: the height in pixels (also on the scaled down display if you haven't guess that by now)
            Functions:
                scale_: changes the scale of the object
                render: render the object (wow i was wondering why it's called that)
        """

        self.layers = layers
        self.scale = scale
        if scale == None:
            self.scale = layers[0].get_size()
        self.scale_(scale)
        self.position = position
        self.rotation = 0
        if height == None:
            height = len(self.layers)
        self.height = height
        self.renderCache = {}

    def scale_(self, scale: tuple[float, float] | list[float, float]) -> None:
        """
            Changes the scale of the object
        """

        self.scale = scale
        for i, layer in enumerate(self.layers):
            self.layers[i] = pygame.transform.scale(layer, scale)

    def render(self, screen: pygame.Surface) -> None:
        """
            Render the object (wow i was wondering why it's called that)
        """

        spread = self.height // len(self.layers)
        for i, image in enumerate(self.layers):
            if not (i, self.rotation, spread) in self.renderCache:
                rotatedImage = pygame.transform.rotate(image, self.rotation)
                self.renderCache[i, self.rotation, spread] = rotatedImage

            else:
                rotatedImage = self.renderCache[i, self.rotation, spread]

            screen.blit(rotatedImage, (self.position[0] - rotatedImage.get_width() // 2, self.position[1] - rotatedImage.get_height() // 2 - i * spread))

class Engine:
    def __init__(self, resolution: list[int, int] | tuple[int, int] = (640, 480), scaledDownResolution: list[int, int] | tuple[int, int] = (128, 96), 
                 fps: int = 144, title: str = "SSEngine pygame window"):
        
        """
            SSEngine core
            Arguments:
                resolution: the resolution of the window.
                scaledDownResolution: used for pixelated graphics, the resolution of the pixel art and the drawing surface for all object
                fps: the framerate
                title: the window caption
            Functions:
                generateFont: generates a pygame font with given size
                setOnUpdate: set the function that will be called every update (default is empty)
                addObject: add an object (wow who could've guessed)
                deltaTime (property): the time it takes for a single frame to pass (1 / fps)
                update: the function that gets called every frame
                run: runs the engine (as if it wasn't obvious)
        """

        pygame.init()
        self.resolution = self.width, self.height = resolution
        self.scaledDownResolution = self.sdWidth, self.sdHeight = scaledDownResolution
        self.screen = pygame.display.set_mode(self.resolution)
        self.display = pygame.Surface(self.scaledDownResolution)
        self.objects: list[Object] = []
        self.fps = fps
        self.title = title
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.onUpdate: None | Callable = None
        self.showFpsCounterOnCaption = False
        self.showFpsCounterOnWindow = False
        self.fpsFont = self.generateFont(16)

    def generateFont(self, fontSize: int):
        """
            Generates a pygame font with the size <fontSize> of the font Ac437_Acer710_CGA-2y
        """
        
        return pygame.font.Font("Fonts/Ac437_Acer710_CGA-2y.ttf", fontSize)

    def setOnUpdate(self, function: Callable):
        """
            Set the function that will be called every update
            Arguments:
                function: the function that will be called every update
        """

        self.onUpdate = function

    def addObject(self, object: Object) -> None:
        """
            Add an object (wow who could've guessed)
            Arguments:
                object: an instance of the Object class, the object that will be added
        """

        self.objects.append(object)

    @property
    def deltaTime(self) -> float:
        """
            The time it takes for a single frame to pass (1 / fps)
        """

        return 1 / self.clock.get_fps() if self.clock.get_fps() != 0 else 1 / self.fps

    def update(self) -> None:
        """
           The function that gets called every frame 
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.display.fill((0, 0, 0))

        if self.onUpdate: self.onUpdate()

        [object_.render(self.display) for object_ in self.objects]
        self.screen.blit(pygame.transform.scale(self.display, self.resolution), (0, 0))

        if self.showFpsCounterOnCaption: pygame.display.set_caption(f"{self.title} | fps: {self.clock.get_fps() :.1f}")
        if self.showFpsCounterOnWindow:
            self.screen.blit(self.fpsFont.render(f"fps: {self.clock.get_fps() :.1f}", True, "gray", "black"), (2, 2))

        pygame.display.update()
        self.clock.tick(self.fps)

    def run(self) -> None:
        """
            Runs the engine (as if it wasn't obvious)
        """
        while True:
            self.update()

if __name__ == "__main__":
    """
        Example engine usage
        Yes very useful example
    """

    engine = Engine(title = "Example SSEngine program")
    images = [pygame.image.load(f"exampleResources/{image}") for image in os.listdir("exampleResources")]
    engine.addObject(Object(images, (20, 20), (engine.sdWidth // 2, engine.sdHeight // 2)))
    clock = 0
    def onUpdate():
        global clock
        engine.objects[0].rotation += engine.deltaTime * 45
        engine.objects[0].height = int(60 * abs(math.sin(clock)))
        clock += engine.deltaTime
    engine.setOnUpdate(onUpdate)
    engine.showFpsCounterOnWindow = True
    engine.run()