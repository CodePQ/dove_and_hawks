import pygame
import pygame_chart as pyc
import random
import numpy as np
import math
import sys

# Intitialize pygame
pygame.init()

# Setup display window
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dove vs Hawk")

# Create clock object
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (239, 191, 4)

# Text properties
font_info = pygame.font.SysFont("Arial", 24)
font_blob = pygame.font.SysFont("Arial", 50)
text_color = BLACK
box_color = (50, 50, 50)
padding = 100

# Day information
day_text_content = "Day Count"
day_text_surface = font_info.render(day_text_content, True, text_color)
day_text_rect = day_text_surface.get_rect()
day_text_rect.topright = (padding, 20)

# Total population information
pop_text_content = "Population"
pop_text_surface = font_info.render(pop_text_content, True, text_color)
pop_text_rect = pop_text_surface.get_rect()
pop_text_rect.topright = (padding, 50)

# Arena properties
ARENA_CENTER = pygame.Vector2(0.6*SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
ARENA_RADIUS = min(SCREEN_HEIGHT, SCREEN_WIDTH)//2 - 25
CONSTANT_SPEED = 20

# Graph properties
graph_figure = pyc.Figure(screen, SCREEN_WIDTH - 450,
                          SCREEN_HEIGHT//2 - 325, 400, 400)

# Dove population information
dove_text_content = "Dove Average: "
dove_text_surface = font_blob.render(dove_text_content, True, BLUE)
dove_text_rect = dove_text_surface.get_rect()
dove_text_rect.topright = (SCREEN_WIDTH - 150, SCREEN_HEIGHT//2 + 100)

# Hawk population information
hawk_text_content = "Hawk Average: "
hawk_text_surface = font_blob.render(hawk_text_content, True, RED)
hawk_text_rect = hawk_text_surface.get_rect()
hawk_text_rect.topright = (SCREEN_WIDTH - 145, SCREEN_HEIGHT//2 + 200)

# Food properties
FOOD_RADIUS = 3
food_color = YELLOW


def place_food(num_food_per_ring, num_rings):
    foods = []

    for i in range(1, num_rings + 1):
        radius = i * (ARENA_RADIUS - 25) / num_rings
        for j in range(num_food_per_ring):
            angle = math.radians(360/num_food_per_ring) * j + (i + 1) * 35
            pos = pygame.Vector2(ARENA_CENTER[0] + radius*math.cos(angle),
                                 ARENA_CENTER[1] + radius*math.sin(angle))

            foods.append({
                "color": food_color,
                "pos": pos,
                "bits": 2,
                "more_food": True,
                "blob1": None,
                "blob2": None
            })
    return foods


# Blob properties
BLOB_RADIUS = 8


def place_blobs(num_doves, num_hawks):
    num_blobs = num_doves + num_hawks

    blobs = []
    spacing = 360 / num_blobs

    for i in range(num_blobs):
        start_angle = math.radians(i * spacing)
        pos = ARENA_CENTER + pygame.Vector2(math.cos(start_angle),
                                            math.sin(start_angle))*ARENA_RADIUS

        blobs.append({
            "dove": True if i < num_doves else False,
            "color": BLUE if i < num_doves else RED,
            "pos": pos,
            "picked_food": False,
            "food": None,
            "at_food": False,
            "food_side": None,
        })

    return blobs


def draw_population_chart(days, population):
    dove_pop = [pop[0] for pop in population]
    hawk_pop = [sum(pop) for pop in population]
    graph_figure.line("Dove Population", days, dove_pop, color=BLUE)
    graph_figure.line("Hawk Population", days, hawk_pop, color=RED)
    graph_figure.add_title("Population Growth")
    graph_figure.add_xaxis_label("Days")
    graph_figure.add_yaxis_label("Population")
    graph_figure.draw()


# Main game loop
running = True
# -------------------------------------
new_day = True
end_of_day = False
num_day = 1
# -------------------------------------
num_foods = 8
num_rings = 7
foods = []
# -------------------------------------
doves = 5
hawks = 5
num_blobs = doves + hawks
blobs = []
# -------------------------------------
day_history = [0, 1]
blob_history = [[0, 0], [doves, hawks]]
dove_avg = round(np.mean([hist[0]/sum(hist) for hist in blob_history[1:]]), 3)
hawk_avg = 1 - dove_avg
# -------------------------------------
while running:
    # End simulation
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw environment
    screen.fill(WHITE)
    pygame.draw.circle(screen, BLACK, ARENA_CENTER, ARENA_RADIUS, 5)

    # Draw population graph
    draw_population_chart(day_history, blob_history)

    # Load new day environment
    if new_day:
        # Day information
        day_text_content = f"Day Count: {num_day}"
        day_text_surface = font_info.render(day_text_content, True, text_color)
        screen.blit(day_text_surface, day_text_rect)

        # Total population information
        pop_text_content = f"Population: {num_blobs}"
        pop_text_surface = font_info.render(pop_text_content, True, text_color)
        screen.blit(pop_text_surface, pop_text_rect)

        # dove population information
        dove_text_content = f"Dove Average: {dove_avg}"
        dove_text_surface = font_blob.render(dove_text_content, True, BLUE)
        screen.blit(dove_text_surface, dove_text_rect)

        # Hawk population information
        hawk_text_content = f"Hawk Average: {hawk_avg}"
        hawk_text_surface = font_blob.render(hawk_text_content, True, RED)
        screen.blit(hawk_text_surface, hawk_text_rect)

        # Food placement
        foods = place_food(num_foods, num_rings)
        for food in foods:
            pygame.draw.circle(screen, food["color"],
                               (int(food["pos"].x), int(food["pos"].y)), FOOD_RADIUS)
        remaining_food = num_foods * num_rings

        # Blob placement
        blobs = place_blobs(doves, hawks)
        for blob in blobs:
            pygame.draw.circle(screen, blob["color"],
                               (int(blob["pos"].x), int(blob["pos"].y)), BLOB_RADIUS)

        pygame.display.flip()
        pygame.time.wait(100)
        new_day = False

    # Start day simulation
    elif not end_of_day:
        # Draw foods
        for food in foods:
            pygame.draw.circle(screen, food["color"],
                               (int(food["pos"].x), int(food["pos"].y)), FOOD_RADIUS)

        # Blobs movement
        for blob in blobs:
            # Choose a food
            while (not blob["picked_food"]) and (remaining_food > 0):
                choice = random.choice(foods)
                # Check if there is still food where blob is looking
                if choice["more_food"]:
                    # Blob picks food
                    blob["picked_food"] = True
                    blob["food"] = choice
                    blob["food_side"] = 'left' if (
                        choice["bits"] == 2) else 'right'

                    # Food updates
                    choice["bits"] -= 1
                    if choice["blob1"]:
                        choice["blob2"] = blob
                    else:
                        choice["blob1"] = blob
                    # No more bits at chosen food
                    if choice["bits"] == 0:
                        choice["more_food"] = False
                        remaining_food -= 1

            # Blob moves to food
            if not blob["at_food"]:
                # Find distance to food
                dist_vec = blob["pos"] - blob["food"]["pos"]

                # Move closer to food
                if dist_vec.length() >= 10:
                    blob["pos"] -= dist_vec.normalize()*CONSTANT_SPEED

                # Position blob at food
                else:
                    fx, fy = blob["food"]["pos"].x, blob["food"]["pos"].y

                    # Left of food
                    if blob["food_side"] == 'left':
                        blob["pos"] = pygame.Vector2(fx - BLOB_RADIUS - 5, fy)

                    # Right of food
                    if blob["food_side"] == 'right':
                        blob["pos"] = pygame.Vector2(fx + BLOB_RADIUS + 5, fy)

                    # Blob is in position at food
                    blob["at_food"] = True

            pygame.draw.circle(screen, blob["color"],
                               (int(blob["pos"].x), int(blob["pos"].y)), BLOB_RADIUS)

        screen.blit(day_text_surface, day_text_rect)
        screen.blit(pop_text_surface, pop_text_rect)
        screen.blit(dove_text_surface, dove_text_rect)
        screen.blit(hawk_text_surface, hawk_text_rect)
        pygame.display.flip()

        # Check if all blobs that found food are at the food
        blobs_found_food = [blob for blob in blobs if blob["picked_food"]]
        if all(blob["at_food"] for blob in blobs_found_food):
            blobs = blobs_found_food
            end_of_day = True
            pygame.time.wait(250)

    # Blobs eat food and update population
    else:
        doves = 0
        hawks = 0

        for food in foods:
            # No blob chose this food
            if not food["blob1"]:
                continue

            # Only one blob chose this food
            elif food["blob1"] and not food["blob2"]:
                blob = food["blob1"]
                # Blob is a dove
                if blob["dove"]:
                    doves += 2
                # Blob is a hawk
                else:
                    hawks += 2

            # Two blobs chose this food
            else:
                blob1 = food["blob1"]
                blob2 = food["blob2"]

                # Same type of blob
                if blob1["dove"] == blob2["dove"]:
                    # Both are doves, so they share
                    if blob1["dove"]:
                        doves += 2

                    # Both are hawks, so they fight and die
                    else:
                        for _ in range(2):
                            '''Try these different setups to see changes in the simulation.'''
                            # 0% chance hawk survives
                            hawks += 1 if random.randint(1, 1) == 2 else 0

                            # 25% chance hawk survives
                            # hawks += 1 if random.randint(1, 4) == 1 else 0

                            # 50% chance hawk survives
                            # hawks += 1 if random.randint(1, 4) <= 2 else 0

                            # 75% chance hawk survives
                            # hawks += 1 if random.randint(1, 4) != 4 else 0

                # One is dove and one is hawk
                else:
                    # Dove has a 50% chance of surviving
                    doves += 1 if random.randint(0, 1) == 1 else 0

                    # Hawk has a 100% chance of surviving, 50% chance to reproduce
                    hawks += 2 if random.randint(0, 1) == 1 else 1

        # New population of blobs
        num_blobs = doves + hawks

        num_day += 1
        day_history.append(num_day)
        blob_history.append([doves, hawks])

        dove_avg = round(np.mean([hist[0]/sum(hist)
                         for hist in blob_history[1:]]), 3)
        hawk_avg = round(1 - dove_avg, 3)

        new_day = True
        end_of_day = False

        draw_population_chart(day_history, blob_history)

        pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
