import pygame
import sys

from objects import GameManager, SpaceShip
from settings import *

pygame.init()

# set display surface
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Space Invaders")

# create a clock
clock = pygame.time.Clock()

# create a SpaceShip, Alien Group and GameManager
spaceship = SpaceShip()
alien_group = pygame.sprite.Group()
game_mng = GameManager(spaceship, alien_group)

game_mng.display_prompt(
    display_surface,
    f"Round: {game_mng.current_round}",
)
game_mng.populate_aliens()

# the main game loop
running = True
bullet_fired = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                spaceship.shoot()
            elif event.key == pygame.K_RETURN:
                game_mng.display_prompt(display_surface, "Paused")

    # move the spaceship left or right
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and spaceship.rect.left > 0:
        spaceship.strife_left()
    elif keys[pygame.K_RIGHT] and spaceship.rect.right < WINDOW_WIDTH:
        spaceship.strife_right()

    # fill the display with the background color
    display_surface.fill(BACKGROUND_COLOR)

    # blit the SpaceShip
    display_surface.blit(spaceship.image, spaceship.rect)

    # update and draw the bullet_group attribute of the SpaceShip instance
    spaceship.update(display_surface)

    # draw the alien group, the HUD and all game assets onto the display surface
    game_mng.blit_aliens(display_surface)
    game_mng.blit_hud(display_surface)
    game_mng.advance_aliens()

    # check if the SpaceShip hit any alien
    if game_mng.alien_is_hit():
        game_mng.alien_hit_sound.play()
        game_mng.score += 100

    # check if the ship is hit
    if game_mng.ship_is_hit():
        game_mng.spaceship_hit_sound.play()
        game_mng.display_prompt(display_surface, "You've been hit.")
        spaceship.lives -= 1
        game_mng.reset_game()

    is_breached = game_mng.is_breached()
    if is_breached:
        # play breach sound
        game_mng.breach_sound.play()
        # prompt the player
        game_mng.display_prompt(display_surface, "Breached", "You lose 1 life!")
        # empty the alien group
        game_mng.alien_group.empty()
        # spaceship lose a life and reposition
        spaceship.lives -= 1
        spaceship.bullet_group.empty()
        spaceship.reset_position()
        # repopulate aliens
        game_mng.populate_aliens()

    if len(game_mng.alien_group) == 0:
        game_mng.next_level_sound.play()
        game_mng.to_next_round()
        game_mng.display_prompt(display_surface,
                                f"Round: {game_mng.current_round}")
    if spaceship.lives == 0:
        game_mng.display_prompt(display_surface, "Gameover", "")
        game_mng.display_prompt(
            display_surface,
            f"Final score: {game_mng.score}",
            "Press 'Enter' to reset the game",
        )
        game_mng.reset_game(from_round_one=True)

    # update the display and tick the clock
    pygame.display.update()
    clock.tick(FPS)

# remove all Bullets from the bullet_group
spaceship.bullet_group.empty()

pygame.quit()
sys.exit()
