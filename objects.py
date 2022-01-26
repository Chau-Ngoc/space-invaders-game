import random
import sys

import pygame
from pygame.sprite import Group, Sprite

from settings import *


class Bullet(Sprite):
    """The Bullet class."""

    def __init__(self, image: pygame.Surface, position: tuple,
                 direction=-1) -> None:
        """
        Initialize the Bullet object.

        :param direction: the direction to guide the Bullet.
            Default value is -1, accepted values are 1 or -1.
        :type direction: int
        :param image: the image Surface of the Bullet.
        :type image: pygame.Surface
        :param position: (x, y) the position to blit the Bullet image.
        :type position: tuple
        """
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = position

        self.velocity = BULLET_VELOCITY
        self.direction = direction

    def update(self):
        """
        The Bullet is fired. Override the **update** method of the parent class.
        """
        self.rect.y += self.direction * self.velocity

        # remove the Bullet from the Bullet Group if the Bullet
        # moves off the screen
        if self.rect.bottom < 0 or self.rect.top > WINDOW_HEIGHT:
            self.kill()


class SpaceShip(Sprite):
    """The SpaceShip object. Inherited the pygame.sprite.Sprite."""

    def __init__(self):
        """
        Initialize the SpaceShip object.
        """
        super().__init__()
        self.image = pygame.image.load("space_invaders_assets/player_ship.png")
        self.rect = self.image.get_rect(centerx=WINDOW_WIDTH // 2,
                                        bottom=WINDOW_HEIGHT)
        self.velocity = SHIP_VELOCITY
        self.lives = SHIP_LIVES
        # self.lives = 1
        self.fire_sound = pygame.mixer.Sound(
            "./space_invaders_assets/player_fire.wav")

        self.bullet_group = Group()

    def update(self, surface):
        """
        Call the **update** method on all the Bullets contained in the
        **bullet_group** and draw them on a given Surface.

        :param surface: the Surface on which to draw the Bullets.
        :type surface: pygame.Surface
        """
        self.bullet_group.update()
        self.bullet_group.draw(surface)

    def strife_left(self):
        """
        Move the SpaceShip to the left.
        """
        self.rect.x -= self.velocity

    def strife_right(self):
        """
        Move the SpaceShip to the right.
        """
        self.rect.x += self.velocity

    def shoot(self):
        """
        The SpaceShip fires a bullet. This method does not actually fire a
        bullet. It instead creates a Bullet object and adds it into the
        **bullet_group** attribute.

        The SpaceShip's bullet capacity is not endless but rather limited.
        Default is 5 bullets in its capacity. Each time it shoots, it draws
        one bullet. If the ship empties out its capacity, it has to refill. In
        order for the SpaceShip to refill, it has to wait for the fired bullets
        to leave the game window.

        The player can change the SpaceShip's bullet capacity by changing the
        constant **SHIP_BULLET_CAPACITY** in the **settings.py** file.
        """
        if len(self.bullet_group) < SHIP_BULLET_CAPACITY:
            bullet_image = pygame.image.load(
                "./space_invaders_assets/green_laser.png")
            bullet = Bullet(bullet_image, self.rect.center)
            self.fire_sound.play()
            self.bullet_group.add(bullet)

    def reset_position(self):
        self.rect.centerx = WINDOW_WIDTH // 2


class Alien(Sprite):
    """The Alien class represents each alien."""

    def __init__(self, position: tuple):
        """
        Initialize the Alien object.

        :param position: (x, y) the position to blit the alien.
        :type position: tuple
        """
        super().__init__()
        self.image = pygame.image.load("./space_invaders_assets/alien.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = position

        self.starting_x = position[0]
        self.starting_y = position[1]

        self.velocity = ALIEN_VELOCITY
        self.direction = 1

        self.fire_sound = pygame.mixer.Sound(
            "./space_invaders_assets/alien_fire.wav")
        self.fire_sound.set_volume(0.01)

        self.bullet_group = Group()

    def update(self, surface, current_round):
        """
        Update the Alien's movements. Override the **update** method of the
        parent class.

        :param current_round: the higher the round number the faster the
            alien movement.
        :type current_round: int
        :param surface: the Surface on which to draw the bullets. This
            parameter will be passed into the **shoot** method.
        :type surface: pygame.Surface
        """
        self.rect.x += self.direction * self.velocity * current_round

        self.shoot(surface)

    def shoot(self, surface):
        """The Alien fires a bullet.

        :param surface: the Surface on which to draw the bullets.
        :type surface: pygame.Surface
        """
        if random.randint(0, 1000) > 999 and len(self.bullet_group) < 2:
            self.fire_sound.play()
            bullet_image = pygame.image.load(
                "./space_invaders_assets/red_laser.png")
            bullet = Bullet(bullet_image, self.rect.center, 1)
            self.bullet_group.add(bullet)
        self.bullet_group.update()
        self.bullet_group.draw(surface)


class GameManager:
    """The GameManager class governs the gameplay."""

    def __init__(self, spaceship: SpaceShip, alien_group: Group):
        """
        The GameManager class manages the gameplay.

        :param spaceship: the SpaceShip to manage.
        :type spaceship: SpaceShip
        :param alien_group: the Alien Group to manage.
        :type alien_group: Group
        """
        self.spaceship = spaceship
        self.alien_group = alien_group

        self.score = 0
        self.current_round = 1

        # sound effects
        self.next_level_sound = pygame.mixer.Sound(
            "./space_invaders_assets/new_round.wav"
        )
        self.next_level_sound.set_volume(0.1)

        self.breach_sound = pygame.mixer.Sound(
            "./space_invaders_assets/breach.wav")

        self.spaceship_hit_sound = pygame.mixer.Sound(
            "./space_invaders_assets/player_hit.wav"
        )
        self.spaceship_hit_sound.set_volume(0.1)

        self.alien_hit_sound = pygame.mixer.Sound(
            "./space_invaders_assets/alien_hit.wav"
        )

        # text font
        self.font = pygame.font.Font("./space_invaders_assets/Facon.ttf",
                                     FONT_SIZE)

    def blit_hud(self, surface: pygame.Surface):
        """
        Blit the HUD onto the given Surface.

        :param surface: the surface on which to blit the HUD.
        :type surface: pygame.Surface
        """
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        score_text_rect = score_text.get_rect()
        score_text_rect.centerx = WINDOW_WIDTH // 2
        score_text_rect.top = PADY

        round_text = self.font.render(f"Round: {self.current_round}", True,
                                      TEXT_COLOR)
        round_text_rect = round_text.get_rect()
        round_text_rect.topleft = (PADX, PADY)

        lives_text = self.font.render(
            f"Lives: {self.spaceship.lives}", True, TEXT_COLOR
        )
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.topright = (WINDOW_WIDTH - PADX, PADY)

        line_start_pos = (PADX, FONT_SIZE + PADY + 10)
        line_end_pos = (WINDOW_WIDTH - PADX, FONT_SIZE + PADY + 10)
        pygame.draw.line(surface, TEXT_COLOR, line_start_pos, line_end_pos, 4)

        bottomline_start_pos = (PADX, WINDOW_HEIGHT - 100)
        bottomline_end_pos = (WINDOW_WIDTH - PADX, WINDOW_HEIGHT - 100)
        pygame.draw.line(
            surface, TEXT_COLOR, bottomline_start_pos, bottomline_end_pos, 4
        )

        surface.blit(score_text, score_text_rect)
        surface.blit(round_text, round_text_rect)
        surface.blit(lives_text, lives_text_rect)

    def populate_aliens(self):
        """
        Generate aliens in a rows * cols fashion.
        """
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                alien = Alien((20 + 70 * col, 100 + 70 * row))
                self.alien_group.add(alien)

    def blit_aliens(self, surface):
        """
        Blit the aliens' images and the bullets onto the given
        surface.

        :param surface: the surface on which to draw the aliens and the bullets.
        :type surface: pygame.Surface
        """
        self.alien_group.draw(surface)
        self.alien_group.update(surface, self.current_round)

    def advance_aliens(self):
        """If the alien group reaches the right or the left side of the
        window. It advances 1 increment closer to the SpaceShip."""
        # check if any aliens have hit the (left or right) edge.
        shift = False
        for alien in self.alien_group:
            if alien.rect.right >= WINDOW_WIDTH or alien.rect.left <= 0:
                shift = True

        # if hit, then shift the aliens closer to the SpaceShip.
        if shift:
            for alien in self.alien_group:
                alien.rect.y += ALIEN_ADVANCE_INCREMENT

                alien.direction *= -1
                alien.rect.x += alien.direction * (
                            alien.velocity * self.current_round)

    def alien_is_hit(self) -> bool:
        """
        Check if the ship shoots down any alien.

        :return: alien shot or not.
        :rtype: bool
        """
        # check collision between the SpaceShip's bullet with any alien
        alien_is_hit = False
        hit = pygame.sprite.groupcollide(
            self.spaceship.bullet_group, self.alien_group, True, True
        )

        if hit:
            alien_is_hit = True

        return alien_is_hit

    def ship_is_hit(self) -> bool:
        """
        Check whether the ship is hit.

        :return: hit or not.
        :rtype: bool
        """
        ship_is_hit = False
        for alien in self.alien_group:
            hit = pygame.sprite.spritecollide(self.spaceship,
                                              alien.bullet_group, True)

            if hit:
                ship_is_hit = True
                break

        return ship_is_hit

    def is_breached(self):
        """
        Check if the aliens have breached the boundary.

        :return: breached or not. Default is False.
        :rtype: bool
        """
        breached = False
        for alien in self.alien_group:
            if alien.rect.bottom > WINDOW_HEIGHT - 100:
                breached = True

        return breached

    def display_prompt(
            self,
            surface: pygame.Surface,
            main_text: str,
            subtext: str = "Press 'Enter' to continue!",
    ):
        """
        Display different prompts on the display surface. This function can
        also be used to simply pause the game.

        :param main_text: the main text to display current status (i.e next
            round, gameover or paused).
        :type main_text: str
        :param subtext: the subtext used to prompt users.
        :type subtext: str
        :param surface: the surface on which to blit the pause text.
        :type surface: pygame.Surface
        """
        main_text = self.font.render(main_text, True, TEXT_COLOR)
        main_text_rect = main_text.get_rect()
        main_text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        sub_text = self.font.render(subtext, True, TEXT_COLOR)
        subtext_rect = sub_text.get_rect()
        subtext_rect.center = (
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + FONT_SIZE + 10,
        )

        surface.fill(BACKGROUND_COLOR)
        surface.blit(main_text, main_text_rect)
        surface.blit(sub_text, subtext_rect)
        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def to_next_round(self):
        self.current_round += 1
        self.spaceship.bullet_group.empty()
        self.spaceship.reset_position()
        self.populate_aliens()

    def reset_game(self, from_round_one: bool = False):
        """
        Reset the game. If the SpaceShip has not drained all its lives,
        reset the game to the current round. Else, reset the game from the
        beginning.

        :param from_round_one: set this to True to reset the game from the
            beginning.
        :type from_round_one: bool
        """
        if from_round_one:
            self.score = 0
            self.current_round = 1
            self.spaceship.lives = SHIP_LIVES
        self.alien_group.empty()
        self.populate_aliens()
        self.spaceship.bullet_group.empty()
        self.spaceship.reset_position()
