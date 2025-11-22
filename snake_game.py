import pygame
import random
from enum import Enum
from typing import Optional

# Define possible directions for cleaner code
class Direction(Enum): 
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame: 
    """
    Manages the state, movement, and drawing of the Snake game.
    Also handles the main execution loop for a self-contained Pygame application.
    """
    
    def __init__(self, screen_width: int = 600, screen_height: int = 600):
        # Game settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.tile_size = 30 # Size of each block (30x30 pixels)
        self.grid_cols = screen_width // self.tile_size
        self.grid_rows = screen_height // self.tile_size
        
        # Colors (Classic Green Theme)
        self.BACKGROUND = (10, 20, 10)
        self.GRID_COLOR = (20, 40, 20)
        self.SNAKE_HEAD = (100, 255, 100)
        self.SNAKE_BODY = (50, 200, 50)
        self.FOOD = (255, 50, 50)
        self.TEXT_COLOR = (255, 255, 255)
        
        # Initialize pygame systems
        pygame.init()
        self.display_surface = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Single-File Pygame Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        
        # Game state and time tracking
        self.running = True
        self.last_update_time = 0
        self.reset_state()
        
    def reset_state(self): 
        """Resets the snake position, direction, and score."""
        start_x = self.grid_cols // 2
        start_y = self.grid_rows // 2
        self.snake_body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.current_direction = Direction.RIGHT
        self.pending_direction = Direction.RIGHT
        
        self.current_score = 0
        self.is_game_over = False
        self.game_speed = 8 # Snake movements per second (FPS for game logic)
        
        self.place_food()
        
    def place_food(self): 
        """Places the food block at a random location not occupied by the snake."""
        while True:
            x = random.randint(0, self.grid_cols - 1)
            y = random.randint(0, self.grid_rows - 1)
            if (x, y) not in self.snake_body:
                self.current_food = (x, y)
                break
    
    def change_direction(self, input_direction: Direction): 
        """Updates the pending direction, preventing illegal 180-degree turns."""
        if self.is_game_over:
            return
            
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if input_direction != opposite.get(self.current_direction):
            self.pending_direction = input_direction
    
    def update(self):
        """Moves the snake and checks for collisions and food consumption."""
        if self.is_game_over:
            return
        
        self.current_direction = self.pending_direction
        
        head_x, head_y = self.snake_body[0]
        dx, dy = self.current_direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # --- 1. Collision Check ---
        if (new_head[0] < 0 or new_head[0] >= self.grid_cols or 
            new_head[1] < 0 or new_head[1] >= self.grid_rows or
            new_head in self.snake_body[1:]): 
            
            self.is_game_over = True
            return
        
        self.snake_body.insert(0, new_head)
        
        # --- 2. Food Check ---
        if new_head == self.current_food:
            self.current_score += 1
            self.place_food()
        else:
            self.snake_body.pop() # Pop the tail to simulate movement
    
    def draw_grid(self, surface): 
        """Draws the subtle grid lines for visual reference."""
        for x in range(0, self.screen_width, self.tile_size):
            pygame.draw.line(surface, self.GRID_COLOR, (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, self.tile_size):
            pygame.draw.line(surface, self.GRID_COLOR, (0, y), (self.screen_width, y))
    
    def draw(self):
        """Draws all game elements to the screen."""
        self.display_surface.fill(self.BACKGROUND)
        self.draw_grid(self.display_surface)
        
        # Draw Food (as a circle for better contrast)
        food_rect = pygame.Rect(self.current_food[0] * self.tile_size, self.current_food[1] * self.tile_size, self.tile_size, self.tile_size)
        pygame.draw.circle(self.display_surface, self.FOOD, food_rect.center, self.tile_size // 2 - 2)
        
        # Draw Snake
        for i, segment in enumerate(self.snake_body):
            pixel_x = segment[0] * self.tile_size
            pixel_y = segment[1] * self.tile_size
            # Create a small border around the segment
            segment_rect = pygame.Rect(pixel_x + 1, pixel_y + 1, self.tile_size - 2, self.tile_size - 2)
            
            color = self.SNAKE_HEAD if i == 0 else self.SNAKE_BODY
            pygame.draw.rect(self.display_surface, color, segment_rect, border_radius=5)
            
        self.render_ui()
        pygame.display.flip()
    
    def render_ui(self): 
        """Renders the score and game over overlay."""
        score_text = self.font.render(f"Score: {self.current_score}", True, self.TEXT_COLOR)
        self.display_surface.blit(score_text, (10, 10))
        
        if self.is_game_over:
            overlay = pygame.Surface((self.screen_width, self.screen_height))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.display_surface.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, self.FOOD)
            restart_text = self.font.render("Press SPACE to restart", True, self.SNAKE_HEAD) 
            
            go_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 25))
            rs_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 25))
            
            self.display_surface.blit(game_over_text, go_rect)
            self.display_surface.blit(restart_text, rs_rect)
    
    def handle_input(self):
        """Processes all Pygame events (keyboard and window closing)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # Directional input mapping
                if event.key == pygame.K_UP:
                    self.change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.change_direction(Direction.RIGHT)
                
                # Restart
                if event.key == pygame.K_SPACE:
                    if self.is_game_over:
                        self.reset_state()

    def run(self):
        """The main execution loop for the game."""
        print("--- Single-File Snake Game Running ---")
        display_fps = 60
        
        while self.running:
            self.handle_input()
            
            # Time-based update for movement
            time_per_update = 1000 / self.game_speed # milliseconds delay
            current_time = pygame.time.get_ticks()

            if current_time - self.last_update_time >= time_per_update:
                self.update()
                self.last_update_time = current_time # Reset the timer

            self.draw()
            self.clock.tick(display_fps) 
            
        self.quit()

    def quit(self):
        """Safely shuts down Pygame."""
        pygame.quit()
        print("Game closed successfully!")

if __name__ == "__main__":
    game = SnakeGame()
    game.run()