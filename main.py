import asyncio
import pygame
import random
import os

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Changed background to a pastel blue
PASTEL_BLUE = (173, 216, 230) # A light blue color

RED = (255, 0, 0) # Apple color
GREEN = (0, 255, 0) # Snake body color
DARK_GREEN = (0, 150, 0) # Snake outline/head color
YELLOW = (255, 255, 0) # Snake eye color
ORANGE = (255, 165, 0) # Level indicator color
PURPLE = (128, 0, 128) # Obstacle color
GRAY = (100, 100, 100) # Lock/barrier color
BLUE = (0, 0, 255) # Special obstacle color

# Snake block size
BLOCK_SIZE = 20

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# High score file path
HIGH_SCORE_FILE = "high_score.txt"

# Level thresholds
LEVEL_THRESHOLDS = {
    1: 0,
    2: 20,
    3: 40,
    4: 60,
    5: 80,
    6: 100
}

def load_high_score():
    """Load the high score from file"""
    try:
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return 0

def save_high_score(score):
    """Save the high score to file"""
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(score))
    except:
        pass

def get_level(score):
    """Determine the current level based on score"""
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS.items():
        if score >= threshold:
            level = lvl
    return level

def generate_obstacles(level, snake_blocks, food_pos):
    """Generate obstacles based on the current level"""
    obstacles = []
    num_obstacles = (level - 1) * 3  # More obstacles per level
    
    if level < 2:
        return obstacles
    
    attempts = 0
    while len(obstacles) < num_obstacles and attempts < 500:
        attempts += 1
        # Generate random obstacle position
        obs_x = round(random.randrange(BLOCK_SIZE * 2, WIDTH - BLOCK_SIZE * 3) / BLOCK_SIZE) * BLOCK_SIZE
        obs_y = round(random.randrange(BLOCK_SIZE * 4, HEIGHT - BLOCK_SIZE * 3) / BLOCK_SIZE) * BLOCK_SIZE
        
        # Check if obstacle doesn't overlap with snake, food, or other obstacles
        obstacle_pos = [obs_x, obs_y]
        if obstacle_pos not in snake_blocks and obstacle_pos != food_pos and obstacle_pos not in obstacles:
            obstacles.append(obstacle_pos)
    
    return obstacles

def generate_walls(level):
    """Generate wall/lock barriers based on level"""
    walls = []
    
    if level < 2:
        return walls
    
    # Level 2: Add small wall segments
    if level >= 2:
        # Top wall segment
        for i in range(3):
            walls.append([WIDTH // 4 + i * BLOCK_SIZE, BLOCK_SIZE * 3])
        # Bottom wall segment
        for i in range(3):
            walls.append([WIDTH * 3 // 4 - i * BLOCK_SIZE, HEIGHT - BLOCK_SIZE * 4])
    
    # Level 3: Add more walls
    if level >= 3:
        # Left wall segment
        for i in range(4):
            walls.append([BLOCK_SIZE * 3, HEIGHT // 3 + i * BLOCK_SIZE])
        # Right wall segment
        for i in range(4):
            walls.append([WIDTH - BLOCK_SIZE * 4, HEIGHT * 2 // 3 - i * BLOCK_SIZE])
    
    # Level 4: Add center obstacles
    if level >= 4:
        # Center cross
        for i in range(5):
            walls.append([WIDTH // 2 - 2 * BLOCK_SIZE + i * BLOCK_SIZE, HEIGHT // 2])
        for i in range(3):
            walls.append([WIDTH // 2, HEIGHT // 2 - BLOCK_SIZE - i * BLOCK_SIZE])
            walls.append([WIDTH // 2, HEIGHT // 2 + BLOCK_SIZE + i * BLOCK_SIZE])
    
    # Level 5: Add corner barriers
    if level >= 5:
        # Corner L-shapes
        for i in range(4):
            walls.append([BLOCK_SIZE * 5 + i * BLOCK_SIZE, BLOCK_SIZE * 5])
            walls.append([BLOCK_SIZE * 5, BLOCK_SIZE * 5 + i * BLOCK_SIZE])
            walls.append([WIDTH - BLOCK_SIZE * 6 - i * BLOCK_SIZE, HEIGHT - BLOCK_SIZE * 6])
            walls.append([WIDTH - BLOCK_SIZE * 6, HEIGHT - BLOCK_SIZE * 6 - i * BLOCK_SIZE])
    
    # Level 6+: Add maze-like walls
    if level >= 6:
        # Additional maze elements
        for i in range(6):
            walls.append([WIDTH // 3, HEIGHT // 4 + i * BLOCK_SIZE])
            walls.append([WIDTH * 2 // 3, HEIGHT * 3 // 4 - i * BLOCK_SIZE])
    
    return walls

def draw_obstacles(obstacles):
    """Draw obstacles on the screen"""
    for obs in obstacles:
        pygame.draw.rect(screen, PURPLE, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE])
        pygame.draw.rect(screen, BLACK, [obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE], 2)
        # Add X pattern to obstacles
        pygame.draw.line(screen, BLACK, (obs[0] + 3, obs[1] + 3), (obs[0] + BLOCK_SIZE - 3, obs[1] + BLOCK_SIZE - 3), 2)
        pygame.draw.line(screen, BLACK, (obs[0] + BLOCK_SIZE - 3, obs[1] + 3), (obs[0] + 3, obs[1] + BLOCK_SIZE - 3), 2)

def draw_walls(walls):
    """Draw wall barriers on the screen"""
    for wall in walls:
        pygame.draw.rect(screen, GRAY, [wall[0], wall[1], BLOCK_SIZE, BLOCK_SIZE])
        pygame.draw.rect(screen, BLACK, [wall[0], wall[1], BLOCK_SIZE, BLOCK_SIZE], 2)
        # Add brick-like pattern
        pygame.draw.line(screen, BLACK, (wall[0], wall[1] + BLOCK_SIZE // 2), (wall[0] + BLOCK_SIZE, wall[1] + BLOCK_SIZE // 2), 1)
        pygame.draw.line(screen, BLACK, (wall[0] + BLOCK_SIZE // 2, wall[1]), (wall[0] + BLOCK_SIZE // 2, wall[1] + BLOCK_SIZE // 2), 1)

def draw_score_panel(score, high_score, level):
    """Draw the score panel at the top of the screen"""
    # Draw semi-transparent panel background
    panel_surface = pygame.Surface((WIDTH, 40))
    panel_surface.set_alpha(200)
    panel_surface.fill((50, 50, 50))
    screen.blit(panel_surface, (0, 0))
    
    font = pygame.font.SysFont('arial', 24, bold=True)
    
    # Score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 8))
    
    # High Score
    high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
    screen.blit(high_score_text, (WIDTH // 2 - 80, 8))
    
    # Level with color coding
    level_colors = {1: GREEN, 2: YELLOW, 3: ORANGE, 4: RED, 5: PURPLE, 6: BLUE}
    level_color = level_colors.get(level, WHITE)
    level_text = font.render(f"Level: {level}", True, level_color)
    screen.blit(level_text, (WIDTH - 120, 8))

# Snake drawing function (modified)
def snake_movement(snake_blocks):
    # Draw the snake body
    for block in snake_blocks:
        pygame.draw.rect(screen, GREEN, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])
        # Optional: Add a darker outline to body segments
        pygame.draw.rect(screen, DARK_GREEN, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE], 1) # 1-pixel border

    # Draw the snake head (the last block in the list)
    if snake_blocks: # Ensure there's at least one block
        head_x, head_y = snake_blocks[-1][0], snake_blocks[-1][1]
        pygame.draw.rect(screen, DARK_GREEN, [head_x, head_y, BLOCK_SIZE, BLOCK_SIZE]) # Darker head
        # Optional: Add eyes to the snake head
        eye_size = BLOCK_SIZE // 5
        eye1_x = head_x + BLOCK_SIZE // 4
        eye2_x = head_x + BLOCK_SIZE - BLOCK_SIZE // 4 - eye_size
        eye_y = head_y + BLOCK_SIZE // 4

        pygame.draw.rect(screen, YELLOW, [eye1_x, eye_y, eye_size, eye_size])
        pygame.draw.rect(screen, YELLOW, [eye2_x, eye_y, eye_size, eye_size])


# Main game loop
async def game_loop():
    game_over = False
    game_close = False

    # Load high score
    high_score = load_high_score()

    # Initial position of the snake
    x, y = WIDTH // 2, HEIGHT // 2
    x_change, y_change = 0, 0

    # Snake body
    snake_blocks = []
    snake_length = 1

    # Score tracking
    score = 0
    current_level = 1
    previous_level = 1

    # Food position
    food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
    food_y = round(random.randrange(BLOCK_SIZE * 3, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE

    # Initialize obstacles and walls
    obstacles = []
    walls = generate_walls(current_level)

    # Base speed and speed increment
    base_speed = 6  # Initial slow speed
    speed_increment_per_block = 0.3 # How much speed increases per block
    level_speed_bonus = 1  # Additional speed per level
    max_speed = 25 # Cap the maximum speed

    while not game_over:
        while game_close:
            screen.fill(PASTEL_BLUE)
            
            # Update high score if current score is higher
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            
            # Draw game over panel
            panel_surface = pygame.Surface((500, 200))
            panel_surface.set_alpha(230)
            panel_surface.fill((40, 40, 40))
            screen.blit(panel_surface, (WIDTH // 2 - 250, HEIGHT // 2 - 100))
            
            font_large = pygame.font.SysFont('arial', 48, bold=True)
            font_medium = pygame.font.SysFont('arial', 28)
            font_small = pygame.font.SysFont('arial', 22)
            
            # Game Over text
            game_over_text = font_large.render("GAME OVER!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 80))
            
            # Final score
            score_text = font_medium.render(f"Final Score: {score}  |  Level: {current_level}", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 20))
            
            # High score
            if score >= high_score:
                hs_text = font_medium.render(f"NEW HIGH SCORE: {high_score}!", True, YELLOW)
            else:
                hs_text = font_medium.render(f"High Score: {high_score}", True, YELLOW)
            screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, HEIGHT // 2 + 20))
            
            # Instructions
            instruction_text = font_small.render("Press C to Play Again  |  Press Q to Quit", True, WHITE)
            screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2 + 65))
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        await game_loop()
            
            await asyncio.sleep(0)  # Allow browser to breathe

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Prevent immediate 180-degree turns (e.g., left then immediately right)
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -BLOCK_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = BLOCK_SIZE
                    x_change = 0

        # Update snake position
        x += x_change
        y += y_change

        # Check for collisions with walls
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        # Check for collision with obstacles
        if [x, y] in obstacles:
            game_close = True

        # Check for collision with walls/barriers
        if [x, y] in walls:
            game_close = True

        # Fill the screen with the new pastel background color
        screen.fill(PASTEL_BLUE)

        # Draw walls and obstacles
        draw_walls(walls)
        draw_obstacles(obstacles)

        # Draw the food (now an "apple" with a stem-like rectangle)
        pygame.draw.rect(screen, RED, [food_x, food_y, BLOCK_SIZE, BLOCK_SIZE])
        # Optional: Draw a small stem for the apple
        pygame.draw.rect(screen, DARK_GREEN, [food_x + BLOCK_SIZE // 2 - 1, food_y - 4, 2, 4]) # Stem


        # Update the snake's body
        snake_head = [x, y]
        snake_blocks.append(snake_head)
        if len(snake_blocks) > snake_length:
            del snake_blocks[0]

        # Check for collisions with itself
        for block in snake_blocks[:-1]:
            if block == snake_head:
                game_close = True

        # Draw the snake (using the modified function)
        snake_movement(snake_blocks)

        # Check if the snake eats the food
        if x == food_x and y == food_y:
            # Ensure new food doesn't spawn on the snake, obstacles, or walls
            while True:
                new_food_x = round(random.randrange(0, WIDTH - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                new_food_y = round(random.randrange(BLOCK_SIZE * 3, HEIGHT - BLOCK_SIZE) / BLOCK_SIZE) * BLOCK_SIZE
                if ([new_food_x, new_food_y] not in snake_blocks and 
                    [new_food_x, new_food_y] not in obstacles and 
                    [new_food_x, new_food_y] not in walls):
                    food_x = new_food_x
                    food_y = new_food_y
                    break
            snake_length += 1
            score += 1
            
            # Check for level up
            new_level = get_level(score)
            if new_level > current_level:
                current_level = new_level
                # Regenerate walls for new level
                walls = generate_walls(current_level)
                # Generate new obstacles for new level
                obstacles = generate_obstacles(current_level, snake_blocks, [food_x, food_y])
                # Flash screen to indicate level up
                for _ in range(3):
                    screen.fill(YELLOW)
                    font = pygame.font.SysFont('arial', 72, bold=True)
                    level_up_text = font.render(f"LEVEL {current_level}!", True, RED)
                    screen.blit(level_up_text, (WIDTH // 2 - level_up_text.get_width() // 2, HEIGHT // 2 - 36))
                    pygame.display.update()
                    pygame.time.wait(300)
                    screen.fill(PASTEL_BLUE)
                    pygame.display.update()
                    pygame.time.wait(150)

        # Calculate current speed (increases with level and snake length)
        current_speed = base_speed + (snake_length - 1) * speed_increment_per_block + (current_level - 1) * level_speed_bonus
        if current_speed > max_speed:
            current_speed = max_speed # Cap the speed

        # Draw the score panel
        draw_score_panel(score, high_score, current_level)

        # Update the display
        pygame.display.update()

        # Control the frame rate based on snake length
        clock.tick(current_speed)
        
        await asyncio.sleep(0)  # CRITICAL: Allow browser to breathe

    pygame.quit()
    quit()

# Start the game
asyncio.run(game_loop())