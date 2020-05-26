# Contains all our game sprites.
import pygame as pg
from setting import *
vec = pg.math.Vector2

class Platform(pg.sprite.Sprite):
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

    def update(self):
        # progress left
        if self.game.score < 200:
            self.rect.x -= 6
        elif self.game.score < 400:
            self.rect.x -= 7
        elif self.game.score < 600:
            self.rect.x -= 8
        elif self.game.score < 800:
            self.rect.x -= 9
        else:
            self.rect.x -= 10


class Cloud(Obstacles):
    def __init__(self, x, y, width, height, color, game):
        super().__init__(x, y, width, height, color, game)
        self.image = pg.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.inner_border_width = 3
        self.image.fill(color)
        self.rect.centerx = x
        self.rect.centery = y
        self.velo = 1

    def update(self):
        self.rect.centerx -= self.velo


class Block(pg.sprite.Sprite):
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