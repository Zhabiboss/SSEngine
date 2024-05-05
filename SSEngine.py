import pygame
import sys
import os
from typing import Callable
import math

pygame.init()

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

def generateFont(fontSize: int) -> pygame.font.Font:
    """
        Generates a pygame font with the size <fontSize> of the font Ac437_Acer710_CGA-2y.
        Yes great info as everyone knows what that font looks like
    """
    
    return pygame.font.Font("Fonts/Ac437_Acer710_CGA-2y.ttf", fontSize)

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
                setOnUpdate: set the function that will be called every update (default is empty)
                setAfterOnUpdate: set the function that will be called after every update (default is empty)
                addObject: add an object (wow who could've guessed)
                deltaTime (property): the time it takes for a single frame to pass (1 / fps)
                update: the function that gets called every frame
                run: runs the engine (as if it wasn't obvious)
        """

        self.resolution = self.width, self.height = resolution
        self.scaledDownResolution = self.sdWidth, self.sdHeight = scaledDownResolution
        self.screen = pygame.display.set_mode(self.resolution, flags = pygame.SRCALPHA)
        self.display = pygame.Surface(self.scaledDownResolution, flags = pygame.SRCALPHA)
        self.objects: list[Object] = []
        self.fps = fps
        self.title = title
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.onUpdate: None | Callable = None
        self.onAfterUpdate: None | Callable = None
        self.showFpsCounterOnCaption = False
        self.showFpsCounterOnWindow = False
        self.fpsFont = generateFont(16)

    def setOnUpdate(self, function: Callable):
        """
            Set the function that will be called every update
            Arguments:
                function: the function that will be called every update
        """

        self.onUpdate = function

    def setOnAfterUpdate(self, function: Callable):
        """
            Set the function  that will be called after every update
            Arguments:
                function: the function that will be called after every update
        """
        self.onAfterUpdate = function

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

        if self.onAfterUpdate: self.onAfterUpdate()

        pygame.display.update()
        self.clock.tick(self.fps)

    def run(self) -> None:
        """
            Runs the engine (as if it wasn't obvious)
        """
        while True:
            self.update()

class Button:
    def __init__(self, position: tuple[int, int] | list[int, int], text: str, width: str, height: str, function: Callable, screen: pygame.Surface,
                 font: pygame.font.Font = generateFont(16), backgroundColor = "gray", textColor = "black", highlightBackgroundColor = "lime"):
        
        """
            Button class, used by UIBase
        """

        self.position = position
        self.text = text
        self.width, self.height = width, height
        self.font = font
        self.renderedText = self.font.render(self.text, True, textColor)
        self.backgroundColor = backgroundColor
        self.isPressed = False
        self.function = function
        self.screen = screen
        self.highlightBackgroundColor = highlightBackgroundColor
    
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position[0], self.position[1], self.width, self.height)

    def update(self) -> None:
        if pygame.mouse.get_pressed()[0]:
            if not self.isPressed and self.rect.collidepoint(*pygame.mouse.get_pos()):
                self.function()
                self.isPressed = True
        else:
            self.isPressed = False

    def draw(self) -> None:
        pygame.draw.rect(self.screen, "black", (self.position[0] + 10, self.position[1] + 10, self.width, self.height))
        color = self.backgroundColor if not self.rect.collidepoint(*pygame.mouse.get_pos()) else self.highlightBackgroundColor
        pygame.draw.rect(self.screen, color, self.rect)
        self.screen.blit(self.renderedText, (self.position[0] + self.width // 2 - self.renderedText.get_width() // 2,
                                             self.position[1] + self.height // 2 - self.renderedText.get_height() // 2))
        
class Label:
    def __init__(self, position: tuple[int, int] | list[int, int], text: str, screen: pygame.Surface, 
                 font: pygame.font.Font = generateFont(16), backgroundColor = None, textColor = "black"):
        
        """
            Label class, used by UIBase
        """

        self.position = position
        self.text = text
        self.font = font
        self.renderedText = self.font.render(self.text, True, textColor, backgroundColor)
        self.screen = screen

    def draw(self):
        self.screen.blit(self.renderedText, self.position)

class UIBase:
    def __init__(self, engine):

        """
            User Interface class
            Used to make menus and stuff and is a parent class. To make a menu you have to make a class that is a child to this.
            To use the UI just add a property to the engine instance that is the child of this class and in the onAfterUpdate function execute the update function.
            
            Arguments:
                engine: the SSEngine core (Engine) that the UIBase is rendering on
        """

        self.engine: Engine = engine
        self.buttons: list[Button] = []
        self.labels: list[Label] = []
        self.overlay = pygame.Surface(self.engine.resolution, pygame.SRCALPHA)
        self.overlay.fill((100, 100, 100, 128))

    def update(self):
        self.engine.screen.blit(self.overlay, (0, 0))

        [label.draw() for label in self.labels]
        for button in self.buttons:
            button.draw()
            button.update()

if __name__ == "__main__":
    """
        Example engine usage
        Yes very useful example
    """

    engine = Engine(title = "Example SSEngine program")
    images = [pygame.image.load(f"exampleResources/img_{i}.png") for i in range(7)]
    engine.addObject(Object(images, (20, 20), (engine.sdWidth // 2, engine.sdHeight // 2)))
    clock = 0

    class UI(UIBase):
        def __init__(self):
            super().__init__(engine)
            self.buttons.append(Button([80, 80], "Close", 60, 30, self.close, engine.screen))
            self.labels.append(Label([80, 10], "Example", self.engine.screen, generateFont(32), "yellow"))
            self.isEnabled = True

        def close(self):
            self.isEnabled = False

    ui = UI()

    def onUpdate():
        global clock, showUI
        engine.objects[0].rotation += engine.deltaTime * 45
        engine.objects[0].height = int(36 * abs(math.sin(clock)))
        clock += engine.deltaTime

        if pygame.key.get_pressed()[pygame.K_ESCAPE]: showUI = True

    showUI = True
    def onAfterUpdate():
        global showUI
        if showUI:
            ui.update()
            if not ui.isEnabled:
                showUI = False
                ui.isEnabled = True

    engine.setOnUpdate(onUpdate)

    engine.setOnAfterUpdate(onAfterUpdate)

    print(engine.onAfterUpdate())

    engine.showFpsCounterOnWindow = True
    engine.run()