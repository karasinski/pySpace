import os
import sys
import math
import pygame as pg


SCREEN_SIZE = (1280, 720)

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)

CONFIG = {'thrustRate': 1,
          'turnRate': 10}


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

        self.position = [0, 0]
        self.velocity = [0, 0]
        self.thrustRate = config['thrustRate']
        self.turnRate = config['turnRate']
        self.heading = 0

        self.inputDict = {pg.K_LEFT:  'LEFT',
                          pg.K_RIGHT: 'RIGHT',
                          pg.K_UP:    'UP',
                          pg.K_DOWN:  'DOWN'}

    def updateCenter(self):
        oldCenter = self.rect.center
        self.image = pg.transform.rotate(self.imageMaster, self.heading)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

    def controlPlayer(self, keys, dt):
        for key in self.inputDict:                      # If the key is a valid input
            if keys[key]:                               # and if you press the key
                if key == pg.K_LEFT:
                    self.turn(-self.turnRate, dt)
                if key == pg.K_RIGHT:
                    self.turn(self.turnRate, dt)
                if key == pg.K_UP:
                    self.thrust(-self.thrustRate, dt)
                if key == pg.K_DOWN:
                    a = self.calculateAntiVelocityVector()
                    self.turn(a, dt)

    def calculateAntiVelocityVector(self):
        if self.velocity[0] < 0:
            angle = math.degrees(math.atan2(self.velocity[0],self.velocity[1]))
            if angle <= 0:
                angle -= self.heading
            elif angle > 0:
                angle += self.heading
        else:
            angle = -math.degrees(math.atan2(self.velocity[0],self.velocity[1]))
            if angle <= 0:
                angle += self.heading
            elif angle > 0:
                angle -= self.heading    


        angle = abs(angle)
        angle %= 360

        print(self.velocity, self.heading, angle)

        if abs(angle) > self.turnRate:
            angle = math.copysign(1, angle) * self.turnRate

        # print(self.heading, angle)
        return angle

    def turn(self, rot, dt):
        """Rotates player."""

        frame_speed = self.thrustRate * dt
        self.heading -= rot * frame_speed * self.turnRate
        self.heading %= 360
        self.updateCenter()

    def thrust(self, delv, dt):
        """Changes the velocity of the player."""

        final_speed = delv * self.thrustRate * dt
        heading_in_radians = math.radians(self.heading)
        self.velocity[0] += math.sin(heading_in_radians) * final_speed
        self.velocity[1] += math.cos(heading_in_radians) * final_speed

    def update(self, screen_rect, keys, dt):
        """Updates our player appropriately every frame."""

        # Update heading and velocity
        self.controlPlayer(keys, dt)

        # Update position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.rect.center = self.position

        # print(self.rect.center, self.heading)

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
