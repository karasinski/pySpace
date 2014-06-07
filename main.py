import os
import sys
import math
import pygame as pg


SCREEN_SIZE = (1280, 720)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)

DIRECT_DICT = {pg.K_LEFT  : (-1, 0),
               pg.K_RIGHT : ( 1, 0),
               pg.K_UP    : ( 0,-1),
               pg.K_DOWN  : ( 0, 1)}

CONFIG = {'speed': 100,
          'turn_rate': 0.5}


class Player(object):

    """This class will represent our user controlled character."""

    def __init__(self, config):
        """
        Arguments are the player's speed (in pixels/second) and the player's
        rect (all rect style arguments accepted).
        """
        pg.sprite.Sprite.__init__(self)
        self.imageMaster = pg.image.load("ship.bmp")
        self.imageMaster = self.imageMaster.convert()
        self.image = self.imageMaster
        self.rect = self.image.get_rect()
        # self.rect.center = (0, 0)

        self.position = list(self.rect.center)
        self.speed = config['speed']
        self.turn_rate = config['turn_rate']
        self.angle = 0

    def update_center(self):
        oldCenter = self.rect.center
        self.image = pg.transform.rotate(self.imageMaster, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

    def update(self, screen_rect, keys, dt):
        """Updates our player appropriately every frame."""

        # Calculate input vector, normalize
        vector = [0, 0]
        for key in DIRECT_DICT:
            if keys[key]:
                vector[0] += DIRECT_DICT[key][0]
                vector[1] += DIRECT_DICT[key][1]
        frame_speed = self.speed * dt

        # Rotate player image
        self.angle -= vector[0] * frame_speed * self.turn_rate
        self.update_center()

        # Transform to radians
        angle_in_radians = math.radians(self.angle)
        final_speed = vector[1] * frame_speed

        # position the player
        self.position[0] += math.sin(angle_in_radians) * final_speed
        self.position[1] += math.cos(angle_in_radians) * final_speed
        self.rect.center = self.position

        # Make sure that you're bound in the screen
        if not screen_rect.contains(self.rect):
            self.rect.clamp_ip(screen_rect)
            self.position = list(self.rect.center)

        print(self.rect.center, self.image.get_rect())

    def draw(self, surface):
        """Draws the player to the target surface."""
        surface.blit(self.image, self.rect)


class Control(object):

    """Keep things under control."""

    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.display.set_caption("pySpace")
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = self.make_player()

    def make_player(self):
        """Create a player and set player.position and player.rect.center equal."""
        player = Player(CONFIG)
        player.position = list(self.screen_rect.center)
        return player

    def event_loop(self):
        """One event loop. Never cut your game off from the event loop."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def main_loop(self):
        """One game loop. Simple and clean."""
        while not self.done:
            time_delta = self.clock.tick(self.fps) / 1000.0
            self.event_loop()
            self.player.update(self.screen_rect, self.keys, time_delta)
            self.screen.fill(BLACK)
            self.player.draw(self.screen)
            pg.display.update()


if __name__ == "__main__":
    run_it = Control()
    run_it.main_loop()
    pg.quit()
    sys.exit()