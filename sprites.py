# Contains all our game sprites.
import pygame as pg
from setting import *
vec = pg.math.Vector2

class Platform(pg.sprite.Sprite):
    """Platform objects are stationary platforms the player can stand on

    Args:
        x (int): x location of platform
        y (int): y location of playform
        width (int): width of platform
        height (int): height of platform
        color (tuple): RGB color value of platform

    Attributes:
        image (Surface): surface displayed on screen
        rect(tuple): rectangular positioning of surface
    """    
    def __init__(self, x, y, width, height, color):
        pg.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.rect.x = x
        self.rect.y = y


class Obstacles(Platform):
    """Obstacles objects move across screen and can make contact with player.

    Args:
        x (int): x location of obstacle
        y (int): y location of obstacle
        width (int): width of obstacle
        height (int): height of obstacle
        color (tuple): RGB color value of obstacle
        game (Game): instance of game currently being played

    Attributes:      
        image (Surface): surface displayed on screen
        rect (tuple): rectangular positioning of image
        inner_border_width (int): inner border width of block
        inner_width (int): width of inner rect created by border width
        inner_height (int): widtheighth of inner rect created by border width
        arm_image (Surface): surface displayed on screen
        arm_rects (tuple): rectangular positioning of cactus arms
        velocity (int): movement speed across screen
        vel_chng_rt (int): amount score must increment before changing velo
    """    
    def __init__(self, x, y, width, height, color, game):
        super().__init__(x, y, width, height, color)
        self.game = game
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.inner_border_width = 3
        self.inner_width = self.width - 2*self.inner_border_width
        self.inner_height = self.height - 2*self.inner_border_width
        self.image.fill(color, rect=(self.rect.x + self.inner_border_width, 
                                     self.rect.top + self.inner_border_width, self.inner_width, 
                                     self.inner_height))
        self.rect.x = x
        self.rect.bottom = y

        self.arm_image = pg.Surface((self.width//2, 5))
        self.arm_rects = self.arm_image.get_rect()
        self.arm_image.fill(RED)
        self.arm_rects.right = self.rect.left
        self.arm_rects.bottom = self.rect.bottom + height//2
        self.velocity = 6
        self.vel_chng_rt = 200

    def update(self):
        '''Move obstacle across screen'''
        # progress left
        # change velocity at certain score intervals in game
        if self.game.score % self.vel_chng_rt == 0:
            self.velocity += 1

        self.rect.x -= self.velocity

class Cloud(Obstacles):
    """Clouds are inert and move across screen 

    Args:
        x (int): x location of cloud
        y (int): y location of cloud
        width (int): width of cloud
        height (int): height of cloud
        color (tuple): RGB color value of cloud
        game (Game): instance of game currently being played

    Attributes:
        image (Surface): surface displayed on screen
        rect (tuple): rectangular positioning of image
        velo (int): movement speed across the screen
    """    
    def __init__(self, x, y, width, height, color, game):
        super().__init__(x, y, width, height, color, game)
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.image.fill(color)
        self.rect.centerx = x
        self.rect.centery = y
        self.velo = 1

    def update(self):
        '''Move left across screen'''
        self.rect.centerx -= self.velo


class Block(pg.sprite.Sprite):
    """Block is main sprite controlled by user

    Args:
        game (Game): instance of game currently being played

    Attributes:
        height (int): height of the block
        width (int): width of the block        
        image (Surface): surface displayed on screen
        rect (tuple): rectangular positioning of image
        inner_border_width (int): inner border width of block
        inner_width (int): width of inner square created by border width
        pos_orig (tuple): constant positional vector
        pos (tuple): positional vector
        vel (tuple): velocity vector
        acc (tuple): acceleration vector

    """
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.height = 50
        self.width = 50
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        # Set inner rect borders so the Surface will appear hollow when filled.
        self.inner_border_width = 3
        self.inner_width = self.width - 2*self.inner_border_width
        self.image.fill(WHITE, rect=(self.inner_border_width, 
                                     self.inner_border_width, self.inner_width, 
                                     self.inner_width))
        self.rect.centerx = WIDTH*1//4
        self.rect.bottom = HEIGHT - 100
        self.pos_orig = vec(self.rect.centerx, self.rect.bottom)
        self.pos = vec(self.rect.centerx, self.rect.bottom)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def jump(self):
        '''Move upward'''
        # Move sprite down one pixel and check for collision
        self.rect.y += 1
        # if collision occured then sprite is currently on a platform
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        # Move back to original position
        self.rect.y -= 1
        # If on a platform, allow jump velocity (keeps from double jumping)
        if hits:
            self.vel.y = PLAYER_JUMP
            self.game.jump_sound.play()

    def update(self):
        '''Accelerate downward'''
        self.acc = vec(0, GRAVITY)

        keys = pg.key.get_pressed()
        
        # If holding down spacebar, it will lessen the effects of gravity
        # giving the effect of a more forceful jump!
        if keys[pg.K_SPACE]:
            self.vel.y += ANTIGRAVITY
        
        # Acceleration affects velocity
        self.vel += self.acc

        # Position is affected by velocity and acceleration.
        self.pos += self.vel + 0.5*self.acc
        
        self.rect.midbottom = self.pos