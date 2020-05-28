# Block Run Game

import pygame as pg
import random
import os
from setting import *
from sprites import *

current_dir = os.path.dirname(__file__)

class Game(object):
    """Game object contains game loop and controls events

    Attributes:
        jump_sound (Sound): game sounds      
        hit_sound (Sound): game sounds 
        score_sound (Sound): game sounds
        screen (Surface): surface on which game is played
        clock (Clock): keeps track of in-game time
        running (bool): keeps track if game is running
        font_name (str): font used for text writing
    """    
    def __init__(self):
        # initialize game window, sprite, etc.
        pg.init()
        pg.mixer.init()
        self.jump_sound = pg.mixer.Sound(os.path.join(current_dir, 'Sounds', 'block_jump.wav'))
        self.hit_sound = pg.mixer.Sound(os.path.join(current_dir, 'Sounds', 'hit.wav'))
        self.score_sound = pg.mixer.Sound(os.path.join(current_dir, 'Sounds', 'Pickup_Coin.wav'))
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)

    def load_data(self):
        """Read in highscores.txt and generate highscore"""        
        if os.path.exists('highscores.txt'):        # if highscores exist then read into file_contents
            self.file = open('highscores.txt', 'r')
            self.high_score_text = self.file.read()
            self.file.close()
        else:
            self.high_score_text = '00000'
        # number value of high_score for comparisons later
        if self.high_score_text == '00000':  
            self.high_score = 0
        else:
            self.high_score = int(self.high_score_text.lstrip('0'))

    def new_game(self):
        '''Start a new game'''
        self.count = 0
        self.score = 0
        self.timer = 0
        # score is based on game survival time
        self.score_timer = 0
        # the leading zeros that will go infront of the score
        self.leading_zeros = '0000'
        # the obstacle generation time is moves downward as game progresses
        self.obs_gen_time = 1500
        self.load_data()

        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.non_collidable_platforms = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.clouds = pg.sprite.Group()

        # generates 4 clouds somewhere randomly on screen
        for x in range(1, 5):
            # x placement will be somewhere within each quadrant of WIDTH
            x_placement = random.randint(round((x-1)/4 * WIDTH), round(x/4 * WIDTH))
            y_placement = random.randint(50, round(1/3 * HEIGHT))
            # clouds are composed of 14 sub clouds
            for y in range(14):
                # if sprite group is divisible by 7 then use random placement
                # otherwise placement will be base on the first cloud of the group
                if len(self.clouds) % 14 == 0:
                    c = Cloud(x_placement, y_placement, CLOUD_WIDTH, CLOUD_HEIGHT, CLOUD_GREY, self)
                else:
                    # position is based on position of previously generate cloud (self.clouds[-1])
                    # but it is shifted either up, down, left, or right by WIDTH//2
                    x_movement = random.choice([-1, 1])
                    # stacking zeros so that y change will only vary slightly
                    y_movement = random.choice([-1, 0, 0, 0, 0, 0, 1])
                    c = Cloud(self.clouds.sprites()[-1].rect.centerx + (CLOUD_WIDTH//2 * x_movement), 
                              self.clouds.sprites()[-1].rect.centery + (CLOUD_WIDTH//2 * y_movement), 
                              CLOUD_WIDTH, CLOUD_HEIGHT, CLOUD_GREY, self)
                self.clouds.add(c)
                self.all_sprites.add(c)
        # Generate main character
        self.block = Block(self)
        self.platform_black = Platform(0, HEIGHT - 110, WIDTH, 2, BLACK)
        # Platform_white is colored same as background to keep invisible
        self.platform_white = Platform(0, HEIGHT - 100, WIDTH, 2, WHITE)
        self.all_sprites.add(self.platform_black)
        self.all_sprites.add(self.platform_white)
        self.all_sprites.add(self.block)
        self.platforms.add(self.platform_white)
        self.non_collidable_platforms.add(self.platform_black)
        
        self.run()

    def run(self):
        '''Run game while playing'''
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.current_time = pg.time.get_ticks()
            self.events()
            self.update()
            self.draw()

    def update(self):
        '''Update all events that are internal to the game (collisions, movements, etc.)'''
        # game loop - update
        self.all_sprites.update()
        # Search for collisions between block and platform
        hits = pg.sprite.spritecollide(self.block, self.platforms, False)
        if hits:
            self.block.pos.y = hits[0].rect.top
            self.block.vel.y = 0
            self.block.rect.midbottom = self.block.pos

        obstacle_hits = pg.sprite.spritecollide(self.block, self.obstacles, False)
        if obstacle_hits:
            # If obstacle is hit, end game
            self.playing = False

        for obstacle in self.obstacles:
            # if scrolled off the screen, remove object
            if obstacle.rect.right < 0:
                obstacle.kill()

        for cloud in self.clouds:
            if cloud.rect.right < 0:
                cloud.rect.left = WIDTH

        # Every 200 game points reduct time inbetween cactus generations up to a limit of 800ms
        if self.score % 200 == 0 and self.obs_gen_time > 700:
            self.obs_gen_time -= 50

        # if greater than timer generate new obstacles (cacti)
        if self.current_time - self.timer > self.obs_gen_time: # 1 second has passed by
            # Obstacle x position called before inner loop because spacing
            # and positioning around number of obstacles must remain the same
            obs_x_pos = random.randint(WIDTH, WIDTH + 100)
            # Generate obstacles in groups 1-3 spaced apart by amt spacing.
            for n in range(1, random.randint(1,4)):
                obs_height = random.randrange(50, 80)
                self.generate_cacti(obs_x_pos, obs_height, n)

            # Reset of timer at end of this mess
            self.timer = self.current_time

        if self.current_time - self.score_timer > 100:
                self.score += 1
                self.score_timer = self.current_time

        if self.score % 100 == 0:
            self.score_sound.play()

    def events(self):
        '''Process external user input'''
        # game loop - events
        for event in pg.event.get():
            # check for closing window
            # events are what happen outside of your game!
            if event.type == pg.QUIT:
                #if self.playing:
                self.playing = False
                self.running = False

        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE]:
            self.block.jump()
                    
    def draw(self):
        '''Draw all game objects to screen'''
        # game loop - draw
        # render
        self.screen.fill(WHITE)
        self.all_sprites.draw(self.screen)
        # draw the 'eye' of the block
        pg.draw.circle(self.screen, BLACK, (self.block.rect.centerx + 10, self.block.rect.centery - 10), 2)
        # draw score to screen
        self.draw_text(self.leading_zeros[len(str(self.score)) - 1:] + str(self.score), 30, BLACK, WIDTH - 80, 15)
        self.draw_text(self.high_score_text, 30, L_GRAY, WIDTH - 160, 15)

        pg.display.flip() # flip after drawing everything to screen

    def generate_cacti(self, obs_x_pos, obs_height, n):
        """Generate cactus obstacle off screen.

        Args:
            obs_x_pos (int): randomly selected x position for cactus
            obs_height (int): random selected height for cactus
            n (int): the nth number of cactus in a grouping. Used to determine spacing.
        """        
        # The arm positions of the block cactuses have two settings 1/2 height or 2/3 height.
        # This position is randomly chosen.
        arm_y_pos = [OBS_Y_POS - round(obs_height * 2/3), OBS_Y_POS - round(obs_height * 1/2)]
        l_choose = random.choice(arm_y_pos)
        r_choose = random.choice(arm_y_pos)
        # Arm bump positions have two possible positions; on top of the arm or on bottom
        # This bump position is dependent on the overall arm position just chosen
        # and is then randomly choosen between top and bottom
        l_arm_bump_pos = [l_choose - ARM_HEIGHT, l_choose + 5]
        r_arm_bump_pos = [r_choose - ARM_HEIGHT, r_choose + 5]
        l_bump_choose = random.choice(l_arm_bump_pos)
        r_bump_choose = random.choice(r_arm_bump_pos)
        # create obstacle (cactus body) along with the arms and bumps
        obs = Obstacles(obs_x_pos + OBS_SPACING * (n - 1), 
                        OBS_Y_POS, OBS_WIDTH, obs_height, WHITE, self)
        left_arm = Obstacles(obs_x_pos + OBS_SPACING * (n - 1) - ARM_WIDTH, 
                        l_choose, ARM_WIDTH, ARM_HEIGHT, WHITE, self)
        right_arm = Obstacles(obs_x_pos + OBS_SPACING * (n - 1) + OBS_WIDTH, 
                        r_choose, ARM_WIDTH, ARM_HEIGHT, WHITE, self)
        left_arm_bump = Obstacles(obs_x_pos + OBS_SPACING * (n - 1) - ARM_WIDTH, 
                        l_bump_choose, 5, 5, WHITE, self)
        right_arm_bump = Obstacles(obs_x_pos + OBS_SPACING * (n - 1) + OBS_WIDTH + ARM_WIDTH - 5, 
                        r_bump_choose, 5, 5, WHITE, self)
        # Add everything to the all_sprites and obstacles sprite groups.
        self.obstacles.add(obs)
        self.obstacles.add(right_arm)
        self.obstacles.add(left_arm)
        self.obstacles.add(right_arm_bump)
        self.obstacles.add(left_arm_bump)
        self.all_sprites.add(obs)
        self.all_sprites.add(right_arm)
        self.all_sprites.add(left_arm)
        self.all_sprites.add(right_arm_bump)
        self.all_sprites.add(left_arm_bump)

    def write_highscores(self):
        '''Determine if current score is high score and write to outfile'''
        # if new score is greater than highscore, replace, and write to file
        self.outfile = open('highscores.txt', 'w')  # open up file in 'w' under same name to overwrite scores in new order

        if self.score > self.high_score:
            self.high_score = self.score
            self.outfile.write(self.leading_zeros[len(str(self.score)) - 1:] + str(self.high_score))
        else:
            self.outfile.write(str(self.high_score_text))
        self.outfile.close()
        
    def show_start_screen(self):
        '''Display start screen while waiting for user input'''
        self.paused = True
        self.opening_sprites = pg.sprite.Group()
        self.start_game_block = Block(self)
        self.opening_sprites.add(self.start_game_block)

        while self.paused:
            self.screen.fill(WHITE)
            self.draw_text('No internet', 35, BLACK, round(WIDTH*1/3) + 20, round(HEIGHT*1/3))
            self.draw_text('Try:', 20, BLACK, round(WIDTH*1/3) + 20, round(HEIGHT*1/3) + 35)
            self.draw_text('> Checking the network cables, modem, and router', 20, 
                           BLACK, round(WIDTH*1/3) + 35, round(HEIGHT*1/3) + 55)
            self.draw_text('> Reconnecting to Wi-Fi', 20, BLACK, 
                           round(WIDTH*1/3) + 35, round(HEIGHT*1/3) + 75)
            self.draw_text('ERR_INTERNET_DISCONNECTED', 20, BLACK, round(WIDTH*1/3) + 20,
                           round(HEIGHT*1/3) + 105)
            self.draw_text('Hint: Press Spacebar to Start', 20, L_GRAY, round(WIDTH*1/3) + 20,
                           HEIGHT - 20)

            self.opening_sprites.draw(self.screen)
            pg.draw.circle(self.screen, BLACK, (self.start_game_block.rect.centerx + 10, 
                           self.start_game_block.rect.centery - 10), 2)
            pg.draw.line(self.screen, BLACK, (self.start_game_block.rect.left - 20, HEIGHT - 110),
                                             (self.start_game_block.rect.left, HEIGHT - 110), 2)
            pg.draw.line(self.screen, BLACK, (self.start_game_block.rect.right + 20, HEIGHT - 110),
                                             (self.start_game_block.rect.right, HEIGHT - 110), 2)
            pg.display.flip()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.paused = False
                    if self.playing:
                        self.playing = False
                    self.running = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.paused = False

    def show_end_screen(self):
        '''Display end game screen while waiting for user input'''
        self.paused = True
        self.hit_sound.play()
        self.write_highscores()

        while self.paused:
            self.draw_text('G  A  M  E    O  V  E  R', 35, L_GRAY, round(WIDTH*1/3) +20, HEIGHT//2 - 15)
            pg.draw.circle(self.screen, BLACK, (self.block.rect.centerx + 10, self.block.rect.centery - 10), 8, 2)
            pg.draw.circle(self.screen, BLACK, (self.block.rect.centerx + 10, self.block.rect.centery - 10), 2)
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.paused = False
                    if self.playing:
                        self.playing = False
                    self.running = False

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.paused = False

    def draw_text(self, text, size, color, x, y):
        """Draw text to screen

        Args:
            text (str): Text to be displayed to screen
            size (int): Font size of text displayed to screen
            color (tuple): RGB color value of font to screen
            x (int): x position of text on screen
            y (int): y position of text on screen
        """        
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, False, color)
        text_rect = text_surface.get_rect()
        text_rect.left = x
        text_rect.centery = y
        self.screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    g = Game()
    g.show_start_screen()
    # this loop will continue to replay game if the user so chooses
    while g.running:
        g.new_game()
        if g.running:
            g.show_end_screen()

    pg.quit()