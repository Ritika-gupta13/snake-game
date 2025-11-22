import pygame
import random
from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class MangoSnake:  
    def __init__(self, width=600, height=600):
        self.block_size = 30  
        self.grid_w = width // self.block_size
        self.grid_h = height // self.block_size

        
        self.dark_bg = (10, 25, 10)
        self.light_grid = (40, 70, 40)
        self.snake_head = (140, 255, 140)   
        self.snake_body = (80, 230, 80)
        self.mango_color = (255, 190, 50)  
        self.ui_text = (250, 250, 250)

        pygame.init()
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Mango Snake - eat em all!")
        self.fps_clock = pygame.time.Clock()
        self.small_font = pygame.font.Font(None, 34)
        self.title_font = pygame.font.Font(None, 58)  

        self.alive = True
        self.last_tick = 0
        self.restart_game()

    def restart_game(self):
        
        cx = self.grid_w // 2
        cy = self.grid_h // 2
        self.body_parts = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.move_dir = Direction.RIGHT
        self.pending_dir = Direction.RIGHT

        self.mangos_eaten = 0
        self.dead = False
        self.move_speed = 9.2  

        self.drop_mango()

    def drop_mango(self):
        attempts = 0
        while attempts < 100:  
            mx = random.randrange(self.grid_w)
            my = random.randrange(self.grid_h)
            if (mx, my) not in self.body_parts:
                self.mango_pos = (mx, my)
                return
            attempts += 1
       
        self.mango_pos = (0, 0)

    def try_turn(self, newdir):
        if self.dead:
            return
        
        opp_dir = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if newdir != opp_dir.get(self.move_dir):
            self.pending_dir = newdir

    def slither(self):
        if self.dead:
            return

        self.move_dir = self.pending_dir
        hx, hy = self.body_parts[0]
        dx, dy = self.move_dir.value
        next_head = (hx + dx, hy + dy)

        
        if (next_head[0] < 0 or next_head[0] >= self.grid_w or
            next_head[1] < 0 or next_head[1] >= self.grid_h or
            next_head in self.body_parts):
            self.dead = True
            return

        self.body_parts.insert(0, next_head)

        if next_head == self.mango_pos:
            self.mangos_eaten += 1
            self.drop_mango()
            
            if self.mangos_eaten % 4 == 0:
                self.move_speed += 0.8
        else:
            self.body_parts.pop()

    def draw_grid_lines(self):
        w, h = self.window.get_size()
        for x in range(0, w, self.block_size):
            pygame.draw.line(self.window, self.light_grid, (x, 0), (x, h), 1)
        for y in range(0, h, self.block_size):
            pygame.draw.line(self.window, self.light_grid, (0, y), (w, y), 1)

    def paint_screen(self):
        self.window.fill(self.dark_bg)
        self.draw_grid_lines()

       
        mx, my = self.mango_pos
        mrect = pygame.Rect(mx * self.block_size + 4, my * self.block_size + 2,
                            self.block_size - 8, self.block_size - 4)
        pygame.draw.ellipse(self.window, self.mango_color, mrect)
        
        stem_end = (mrect.centerx, mrect.top - 2)
        pygame.draw.line(self.window, (139, 69, 19), mrect.center, stem_end, 3)

        
        for idx, (sx, sy) in enumerate(self.body_parts):
            srect = pygame.Rect(sx*self.block_size + 1, sy*self.block_size + 1,
                                self.block_size - 2, self.block_size - 2)
            col = self.snake_head if idx == 0 else self.snake_body
            pygame.draw.rect(self.window, col, srect, border_radius=7)

        
        score_line = self.small_font.render(f"Mangos: {self.mangos_eaten}", True, self.ui_text)
        self.window.blit(score_line, (15, 15))

        if self.dead:
            
            ov = pygame.Surface(self.window.get_size())
            ov.set_alpha(140)
            ov.fill((0,0,0))
            self.window.blit(ov, (0,0))

            over_txt = self.title_font.render("MANGO OVER", True, self.mango_color)
            retry_txt = self.small_font.render("SPACE to munch more - ESC quit", True, self.snake_head)
            orect = over_txt.get_rect(center=(self.window.get_width()//2, self.window.get_height()//2 - 20))
            rrect = retry_txt.get_rect(center=(self.window.get_width()//2, self.window.get_height()//2 + 40))
            self.window.blit(over_txt, orect)
            self.window.blit(retry_txt, rrect)

        pygame.display.flip()

    def check_keys(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.alive = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.alive = False
                if ev.key == pygame.K_UP or ev.key == pygame.K_w:
                    self.try_turn(Direction.UP)
                if ev.key == pygame.K_DOWN or ev.key == pygame.K_s:
                    self.try_turn(Direction.DOWN)
                if ev.key == pygame.K_LEFT or ev.key == pygame.K_a:
                    self.try_turn(Direction.LEFT)
                if ev.key == pygame.K_RIGHT or ev.key == pygame.K_d:
                    self.try_turn(Direction.RIGHT)
                if ev.key == pygame.K_SPACE and self.dead:
                    self.restart_game()

    def main_loop(self):
        print("Mango Snake go!,eat mangos")
        while self.alive:
            self.check_keys()

            current_tick = pygame.time.get_ticks()
            step_delay = 1000 / self.move_speed
            if current_tick - self.last_tick >= step_delay:
                self.slither()
                self.last_tick = current_tick

            self.paint_screen()
            self.fps_clock.tick(60)

        pygame.quit()
        print("yay we got mangoes!!!")


if __name__ == "__main__":
    
    snake_game = MangoSnake()
    snake_game.main_loop()
