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
        for key in self.inputDict:
            # If the key is a valid input...
            if keys[key]:
                # ...do the appropriate thing.
                if key == pg.K_DOWN:
                    self.reverse(dt)
                    break
                elif key == pg.K_LEFT:
                    self.turn(-self.turnRate, dt)
                elif key == pg.K_RIGHT:
                    self.turn(self.turnRate, dt)
                if key == pg.K_UP:
                    self.thrust(-self.thrustRate, dt)

    def reverse(self, dt):
        """Rotates player to face backwards along their velocity vector."""

        antiVelocityAngle = math.degrees(
            math.atan2(self.velocity[0], self.velocity[1]))
        calculationAngle = -antiVelocityAngle + self.heading

        calculationAngle %= 360

        # Don't take the long way around.
        if calculationAngle > 180:
            outputAngle = -calculationAngle
        else:
            outputAngle = calculationAngle

        self.turn(outputAngle, dt)

    def turn(self, rot, dt):
        """Rotates player by an arbitrary amount no greater than the turn rate."""
        
        rot = saturate(rot, self.turnRate)
        finalRot = rot * self.turnRate * dt

        self.heading -= finalRot
        self.heading %= 360
        self.updateCenter()

    def thrust(self, speed, dt):
        """Changes the velocity of the player."""

        finalSpeed = speed * self.thrustRate * dt
        headingInRadians = math.radians(self.heading)
        self.velocity[0] += math.sin(headingInRadians) * finalSpeed
        self.velocity[1] += math.cos(headingInRadians) * finalSpeed

    def update(self, keys, dt):
        """Updates our player appropriately every frame."""

        # Update heading and velocity
        self.controlPlayer(keys, dt)

        # Update position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.rect.center = self.position

    def draw(self, surface):
        """Draws the player to the target surface."""
        surface.blit(self.image, self.rect)


def saturate(var, saturation):
    if var > saturation:
        output = saturation
    elif var < -saturation:
        output = -saturation
    else:
        output = var

    return output


class Control(object):

    """Keep things under control."""

    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        pg.display.set_caption("pySpace")
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.screenRect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = 60.0
        self.done = False
        self.keys = pg.key.get_pressed()
        self.player = self.makePlayer()

    def makePlayer(self):
        """Create a player and set player.position and player.rect.center equal."""
        player = Player(CONFIG)
        player.position = list(self.screenRect.center)
        return player

    def eventLoop(self):
        """One event loop. Never cut your game off from the event loop."""
        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def mainLoop(self):
        """One game loop. Simple and clean."""
        while not self.done:
            dt = self.clock.tick(self.fps) / 1000.0
            self.eventLoop()
            self.player.update(self.keys, dt)
            self.screen.fill(BLACK)
            self.player.draw(self.screen)
            pg.display.update()


if __name__ == "__main__":
    run = Control()
    run.mainLoop()
    pg.quit()
    sys.exit()
