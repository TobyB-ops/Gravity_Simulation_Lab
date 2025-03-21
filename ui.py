import pygame, sys, vectors 
from enum import Enum
pygame.init()

#background image
BG = pygame.image.load('Background.png')
buttonColour = (155,0,255)

#class to handle different font sizes for different block objects
class blockType(Enum):
    '''
    holds options for different size buttons
    '''
    DEFAULT = 24
    TITLE = 32
    SMALL = 16


#define classes for pygame objects
class Block:
    '''
    defines a coloured box with text 
    '''
    def __init__(
        self,
        area: pygame.Rect,
        text: str,
        color: tuple[int, int, int],
        type
    ):
        self.area = area
        self.type = type
        self.text = text
        self.color = color

    def draw(self, window: pygame.surface.Surface):
        pygame.draw.rect(window, self.color, self.area)
        if self.text != "":
            font = pygame.font.SysFont("arial", self.type.value)
            text = font.render(self.text, True, (0, 0, 0))
            window.blit(
                text,
                (
                    self.area.left + (self.area.width / 2 - text.get_width() / 2),
                    self.area.top + (self.area.height / 2 - text.get_height() / 2),
                ),
            )

class Button(Block):
    '''
    defines a block that activates a function on click
    '''
    def __init__(
        self,
        area: pygame.Rect,
        text: str,
        color: tuple[int, int, int],
        type,
        on_click: callable,          
    ):
        super().__init__(area, text, color, type)
        self.on_click = on_click

class Textbox(Button):
    '''
    defines a button in which the user can write text
    '''
    def __init__(
        self,
        area : pygame.Rect,
        text : str,
        color: tuple[int,int,int],
        type,
        on_click: callable,
        active : bool,
    ):
        super().__init__(area,text,color,type, on_click)
        self.active = active

