import contextlib
from typing import Tuple, List

with contextlib.redirect_stdout(None):
    import pygame

from sprite import Sprite
from enums import Tile, Direction

TB = List[List[Tile]]
PACMAN_SPEED = 2

pygame.font.init()
font = pygame.font.SysFont("Font.ttf", 24)

def load(file: str) -> pygame.Surface:
    path = "../assets/" + file + ".png"
    return pygame.image.load(path)


PACMAN_OPEN_RIGHT = load("pacman_open_right")
PACMAN_OPEN_LEFT = load("pacman_open_left")
PACMAN_OPEN_DOWN = load("pacman_open_down")
PACMAN_OPEN_UP = load("pacman_open_up")
PACMAN_CLOSED = load("pacman_closed")

class PacmanSprite(Sprite):
    def __init__(self, app):
        self.current_direction: Direction = Direction.NONE
        self.next_direction: Direction = Direction.NONE
        self.score: int = 0
        self.won: bool = False

        super().__init__(app, app.display, PACMAN_OPEN_RIGHT, (24, 48))

    def check_board(self, direction: Direction, pos: Tuple[int, int], board: TB) -> bool:
        if not (pos[0] % 24 == 0 and pos[1] % 24 == 0):
            return True
        if direction == Direction.RIGHT:
            return board[pos[1] // 24][pos[0] // 24 + 1] != Tile.WALL
        elif direction == Direction.LEFT:
            return board[pos[1] // 24][pos[0] // 24 - 1] != Tile.WALL
        elif direction == Direction.DOWN:
            return board[pos[1] // 24 + 1][pos[0] // 24] != Tile.WALL
        elif direction == Direction.UP:
            return board[pos[1] // 24 - 1][pos[0] // 24] != Tile.WALL
        elif direction == Direction.NONE:
            return True


    def eat_coin(self, b: TB) -> TB:
        x, y = self.position
        y -= 24

        current = b[y // 24][x // 24]
        if current == Tile.COIN:
            self.score += 10
            b[y // 24][x // 24] = Tile.BLANK

            def check() -> bool:
                nonlocal b
                flattened: List[Tile] = [item for sublist in b for item in sublist]
                return Tile.COIN not in flattened

            if check():
                self.won = True

        return b


    def isinverse(self, directions: Tuple[Direction, Direction]) -> bool:
        inverse_dict = {
            Direction.RIGHT: Direction.LEFT,
            Direction.LEFT: Direction.RIGHT,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.NONE: Direction.NONE,
        }
        return inverse_dict[directions[0]] == directions[1]

    def update(self) -> None:


        x, y = self.position
        y -= 24

        if (x % 24 == 0 and y % 24 == 0) or self.isinverse(
            (self.current_direction, self.next_direction)
        ):
            direction = self.next_direction
            if not self.check_board(self.next_direction, (x, y), self.app.board):
                direction = self.current_direction
            if not self.check_board(self.current_direction, (x, y), self.app.board):
                direction = Direction.NONE
            self.current_direction = direction
            if x % 24 == 0 and y % 24 == 0:
                self.app.board = self.eat_coin(self.app.board)
        else:
            direction = self.current_direction

        img = self.image

        y += 24
        if direction == Direction.RIGHT:
            x += PACMAN_SPEED
            img = PACMAN_OPEN_RIGHT
        elif direction == Direction.LEFT:
            x -= PACMAN_SPEED
            img = PACMAN_OPEN_LEFT
        elif direction == Direction.UP:
            y -= PACMAN_SPEED
            img = PACMAN_OPEN_UP
        elif direction == Direction.DOWN:
            y += PACMAN_SPEED
            img = PACMAN_OPEN_DOWN

        if x % 24 > 12 or y % 24 > 12:
            img = PACMAN_CLOSED

        super().update(img, (x, y))
        if self.won:
            surf = font.render("You won!", False, (255, 255, 255))
        else:
            surf = font.render("Score: " + str(self.score), False, (255, 255, 255))
        self.app.display.blit(surf, (5, 5))