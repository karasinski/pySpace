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
          'turnRate': 180}

lastTime = 0

class Bullet(pg.sprite.Sprite):

    def __init__(self, destination, origin):
        pg.sprite.Sprite.__init__(self)

        self.image = pg.Surface([10, 10])
        self.image.fill(RED)

        self.destination_x, self.destination_y = destination[0], destination[1]
        self.origin = origin

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = origin[0], origin[1]

    def update(self, keys, dt):
        speed = -4.
        maxRange = 200
        distance = [self.destination_x - self.origin[0],
                    self.destination_y - self.origin[1]]
        norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
        direction = [distance[0] / norm, distance[1] / norm]
        bullet_vector = [direction[0] * speed, direction[1] * speed]

        self.rect.x -= bullet_vector[0]
        self.rect.y -= bullet_vector[1]

        # print(norm)
        if norm > maxRange:
            run.allSpritesList.remove(self)


class Player(pg.sprite.Sprite):

    """This class will represent our user controlled character."""

    def __init__(self, config):
        """
        Arguments are the player's speed (in pixels/second) and the player's
        rect (all rect style arguments accepted).
        """
        pg.sprite.Sprite.__init__(self)
        temp = pg.image.load("ship.bmp")
        self.imageMaster = pg.transform.smoothscale(temp.convert(), (66, 52))
        self.image = self.imageMaster
        self.rect = self.image.get_rect()
        # self.rect.center = (0, 0)

        self.position = [0, 0]
        self.velocity = [0, 0]
        self.thrustRate = config['thrustRate']
        self.turnRate = config['turnRate']
        self.heading = 0

        self.lastFired = 0

        self.inputDict = {pg.K_LEFT:  'LEFT',
                          pg.K_RIGHT: 'RIGHT',
                          pg.K_UP:    'UP',
                          pg.K_DOWN:  'DOWN',
                          pg.K_SPACE: 'SPACE'}

    def updateCenter(self):
        oldCenter = self.rect.center
        self.image = pg.transform.rotate(self.imageMaster, self.heading)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter

    def controlPlayer(self, keys, dt):
        reverse = False
        for key in self.inputDict:
            # If the key is a valid input...
            if keys[key]:
                # ...do the appropriate thing.
                if key == pg.K_DOWN:
                    self.reverse(dt)
                    reverse = True
                if not reverse:
                    if key == pg.K_RIGHT:
                        self.turn(self.turnRate, dt)
                    if key == pg.K_LEFT:
                        self.turn(-self.turnRate, dt)
                if key == pg.K_UP:
                    self.thrust(-self.thrustRate, dt)
                if key == pg.K_SPACE:
                    self.fire()

    def fire(self):
        global lastTime
        currentTime = pg.time.get_ticks()
        if currentTime - lastTime > 1000:
            a = [self.position[0] - math.sin(math.degrees(self.heading)),
                 self.position[1] - math.cos(math.degrees(self.heading))]
            b = [self.position[0], self.position[1]]
            bullet = Bullet(a, b)

            run.allSpritesList.add(bullet)
            # print('pew', lastTime, currentTime, currentTime-lastTime)
            # print(run.allSpritesList)
            lastTime = currentTime

    def reverse(self, dt):
        """Rotates player to face backwards along their velocity vector."""

        antiVelocityAngle = math.degrees(
            math.atan2(self.velocity[0], self.velocity[1]))
        calculationAngle = -antiVelocityAngle + self.heading

        # 0 degrees = 360 degrees
        calculationAngle %= 360

        # Don't take the long way around.
        if calculationAngle > 180:
            outputAngle = -calculationAngle
        else:
            outputAngle = calculationAngle

        self.turn(outputAngle, dt)

    def turn(self, rot, dt):
        """Rotates player by an arbitrary amount no greater than the turn rate."""

        self.heading -= saturate(rot, self.turnRate, dt) * dt
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


def saturate(var, saturation, dt=1.):
    """Saturates a value within even bounds."""

    if var / dt > saturation:
        output = saturation
    elif var / dt < -saturation:
        output = -saturation
    else:
        output = var / dt

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
        self.allSpritesList = pg.sprite.Group()
        self.allSpritesList.add(self.player)

    def makePlayer(self):
        """Create a player and set player.position and player.rect.center equal."""
        player = Player(CONFIG)
        player.position = list(self.screenRect.center)
        return player

    def eventLoop(self):
        """Single event loop."""

        # gets coordinates of mouse if the game window is the active window
        # if (pg.mouse.get_focused()): print(pg.mouse.get_pos())

        for event in pg.event.get():
            self.keys = pg.key.get_pressed()
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.done = True

    def mainLoop(self):
        """Game loop."""
        while not self.done:
            dt = self.clock.tick(self.fps) / 1000.0
            self.eventLoop()
            self.allSpritesList.update(self.keys, dt)
            self.screen.fill(BLACK)
            self.allSpritesList.draw(self.screen)
            pg.display.update()

if __name__ == "__main__":
    run = Control()
    run.mainLoop()
    pg.quit()
    sys.exit()
