import pygame
import random
import numpy
import math
import sys

# Intitialize pygame
pygame.init()

# Setup display window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 780
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blob Evolution")

# Create clock object
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (239, 191, 4)

# Text properties
font = pygame.font.SysFont("Arial", 24)
text_color = BLACK
box_color = (50, 50, 50)
padding = 100

# Day information
day_text_content = "Day Count"
day_text_surface = font.render(day_text_content, True, text_color)
day_text_rect = day_text_surface.get_rect()
day_text_rect.topright = (padding, 20)

# Population information
pop_text_content = "Population"
pop_text_surface = font.render(pop_text_content, True, text_color)
pop_text_rect = pop_text_surface.get_rect()
pop_text_rect.topright = (padding, 50)

# Arena properties
ARENA_CENTER = pygame.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
ARENA_RADIUS = min(SCREEN_HEIGHT, SCREEN_WIDTH)//2 - 25
CONSTANT_SPEED = 5

# Food properties
food_radius = 5
food_color = YELLOW


def place_food(num_food_per_ring, num_rings):
    foods = []

    for i in range(1, num_rings + 1):
        radius = i * (ARENA_RADIUS - 50) / 3
        for j in range(num_food_per_ring):
            angle = math.radians(360/num_food_per_ring) * j
            pos = pygame.Vector2(ARENA_CENTER[0] + radius*math.cos(angle),
                                 ARENA_CENTER[1] + radius*math.sin(angle))

            foods.append({
                "pos": pos,
                "color": food_color,
                "bits": 2,
                "more_food": True
            })
    return foods


# Blob properties
blob_radius = 10
blob_unsafe = RED
blob_safe = BLUE


def place_blobs(num_blobs):
    blobs = []
    spacing = 360 / num_blobs

    for i in range(num_blobs):
        start_angle = math.radians(i * spacing)
        pos = ARENA_CENTER + pygame.Vector2(math.cos(start_angle),
                                            math.sin(start_angle))*ARENA_RADIUS

        blobs.append({
            "pos": pos,
            "color": blob_unsafe,
            "food": None,
            "food_side": None,
            "at_food": False,
            "picked_food": False,
            "survive": False,
        })

    return blobs


# Main game loop
running = True
# -------------------------------------
new_day = True
end_of_day = False
num_day = 0
# -------------------------------------
num_foods = 10
num_rings = 3
foods = []
# -------------------------------------
num_blobs = 1
blobs = []
# -------------------------------------
while running:
    # End simulation
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw environment
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLACK, ARENA_CENTER, ARENA_RADIUS, 5)

    '''if (all blobs have found food) or (all food is occupied by two blobs):
        perform dove and hawk responses
        restart the day:
            - new food placement
            - next generation of blobs:
                - updated dove population
                - updated hawk population
    '''
    # Load new day environment
    if new_day and not end_of_day:

        num_day += 1

        # Day information
        day_text_content = f"Day Count: {num_day}"
        day_text_surface = font.render(day_text_content, True, text_color)

        # Population information
        pop_text_content = f"Population: {num_blobs}"
        pop_text_surface = font.render(pop_text_content, True, text_color)

        # Food placement
        foods = place_food(num_foods, num_rings)
        for food in foods:
            pygame.draw.circle(screen, food["color"],
                               (int(food["pos"].x), int(food["pos"].y)), food_radius)
        remaining_food = num_foods * num_rings

        # Blob placement
        blobs = place_blobs(num_blobs)
        for blob in blobs:
            pygame.draw.circle(screen, blob["color"],
                               (int(blob["pos"].x), int(blob["pos"].y)), blob_radius)

        screen.blit(day_text_surface, day_text_rect)
        screen.blit(pop_text_surface, pop_text_rect)
        pygame.display.flip()
        pygame.time.wait(1000)
        new_day = False

    # Start day simulation
    elif not new_day and not end_of_day:
        # Draw foods
        for food in foods:
            pygame.draw.circle(screen, food["color"],
                               (int(food["pos"].x), int(food["pos"].y)), food_radius)

        # Blobs movement
        for blob in blobs:
            # Select food to go to
            while (not blob["picked_food"]) and (remaining_food > 0):
                choice = random.choice(foods)
                # Check if there is still food where blob is looking
                if choice["more_food"]:
                    # Blob picks food
                    blob["picked_food"] = True
                    blob["color"] = blob_safe
                    blob["food"] = choice
                    blob["food_side"] = 'left' if (
                        choice["bits"] == 2) else 'right'
                    blob["survive"] = True
                    choice["bits"] -= 1
                    # No more bits at chosen food
                    if choice["bits"] == 0:
                        choice["more_food"] = False
                        remaining_food -= 1

            # Blob got no food
            if blob["food"] == None:
                blob["survive"] = False

            # Blob moves to food
            elif not blob["at_food"]:
                # Find distance to food
                dist_vec = blob["pos"] - blob["food"]["pos"]
                # Move closer to food
                if dist_vec.length() >= 5:
                    blob["pos"] -= dist_vec.normalize()*CONSTANT_SPEED

                # Position blob at food
                else:
                    fx, fy = blob["food"]["pos"].x, blob["food"]["pos"].y

                    # Left of food
                    if blob["food_side"] == 'left':
                        blob["pos"] = pygame.Vector2(fx - blob_radius - 5, fy)

                    # Right of food
                    if blob["food_side"] == 'right':
                        blob["pos"] = pygame.Vector2(fx + blob_radius + 5, fy)

                    # Blob is in position at food
                    blob["at_food"] = True

            pygame.draw.circle(screen, blob["color"],
                               (int(blob["pos"].x), int(blob["pos"].y)), blob_radius)

        screen.blit(day_text_surface, day_text_rect)
        screen.blit(pop_text_surface, pop_text_rect)
        pygame.display.flip()

        # Check if all blobs that found food are at the food
        blobs_survived = [blob for blob in blobs if blob["survive"]]
        if all(blob["at_food"] for blob in blobs_survived):
            blobs = blobs_survived
            num_blobs = len(blobs_survived)
            end_of_day = True
            pygame.time.wait(500)

    # End day simulation and update population
    else:
        print(F"End of day {num_day}.")
        num_blobs = 0
        for blob in blobs:
            if blob["survive"]:
                num_blobs += 1
            if blob["food"]["more_food"]:
                num_blobs += 1

        new_day = True
        end_of_day = False

    clock.tick(60)

pygame.quit()
sys.exit()
