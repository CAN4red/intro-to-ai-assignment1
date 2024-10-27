from collections import deque
from typing import Tuple, List, Dict, Deque

MIN_COORD = 0
MAX_COORD = 8
INT_INFINITY = 2 ** 31 - 1
POSSIBLE_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DANGER_ITEMS = ('P', 'A', 'S')
INITIAL_POS = (0, 0)


def is_valid(pos: Tuple[int, int]) -> bool:
    x, y = pos

    x_valid = MIN_COORD <= x <= MAX_COORD
    y_valid = MIN_COORD <= y <= MAX_COORD

    return x_valid and y_valid


def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    neighbors = []
    x, y = pos

    for dx, dy in POSSIBLE_MOVES:
        new_pos = (x + dx, y + dy)
        if is_valid(new_pos):
            neighbors.append(new_pos)

    return neighbors


def read_response() -> Dict[Tuple[int, int], str]:
    dangers: Dict[Tuple[int, int], str] = dict()
    num_of_items = int(input())

    for _ in range(num_of_items):
        x, y, item_type = input().split()
        x = int(x)
        y = int(y)
        if item_type in DANGER_ITEMS or item_type == 'K':
            dangers[(x, y)] = item_type

    return dangers


class GameMap:
    def __init__(self):
        self.game_map: List[List[str | None]] = [[None for _ in range(9)] for _ in range(9)]
        self.visited_path: Deque[Tuple[int, int]] = deque()
        self.is_first_backtrack: bool = True

    def get_available_neighbours(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        available_neighbors = []

        for neighbor_pos in get_neighbors(pos):
            if self.get_info(neighbor_pos) is None:
                available_neighbors.append(neighbor_pos)

        return available_neighbors

    def get_neighbour(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        return self.get_available_neighbours(pos)[0]

    def has_available_neighbours(self, pos: Tuple[int, int]) -> bool:
        neighbors = self.get_available_neighbours(pos)
        return len(neighbors) != 0

    def get_info(self, pos: Tuple[int, int]) -> str | None:
        x, y = pos
        return self.game_map[x][y]

    def change_info(self, pos: Tuple[int, int], info: str) -> None:
        x, y = pos
        self.game_map[x][y] = info

    def add_dangers(self, dangers: Dict[Tuple[int, int], str]) -> None:
        for pos in dangers.keys():
            self.change_info(pos, dangers[pos])

    def add_visited(self, pos: Tuple[int, int]) -> None:
        x, y = pos
        if self.game_map[x][y] is None:
            self.game_map[x][y] = '.'

    def move_to(self, pos: Tuple[int, int]) -> None:
        print('m', *pos)
        dangers = read_response()

        self.add_dangers(dangers)
        self.add_visited(pos)
        self.visited_path.append(pos)

    def get_current_pos(self) -> Tuple[int, int]:
        if len(self.visited_path) == 0:
            return 0, 0
        return self.visited_path[-1]

    def backtrack(self) -> Tuple[int, int]:
        return self.visited_path.pop()

    def fill_map(self) -> None:
        self.move_to(INITIAL_POS)
        while True:
            current_pos = self.get_current_pos()

            if current_pos == INITIAL_POS and not self.has_available_neighbours(current_pos):
                return

            if self.has_available_neighbours(current_pos):
                if not self.is_first_backtrack:
                    print('m', *current_pos)
                    read_response()
                    self.is_first_backtrack = True

                neighbour_pos = self.get_neighbour(current_pos)
                self.move_to(neighbour_pos)
            else:
                if self.is_first_backtrack:
                    self.backtrack()
                    self.is_first_backtrack = False
                prev_pos = self.backtrack()
                print('m', *prev_pos)
                read_response()


class PathFinder:
    def __init__(self, keymaker_position):
        self.game_map: GameMap = GameMap()
        self.keymaker_position = keymaker_position
        self.distances: List[List[int]] = [[INT_INFINITY for _ in range(9)] for _ in range(9)]
        self.cells_queue: Deque[Tuple[int, int]] = deque()

    def get_available_neighbours(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        available_neighbors = []

        for neighbor_pos in get_neighbors(pos):
            if (self.get_distance(neighbor_pos) >= INT_INFINITY and
                    self.game_map.get_info(neighbor_pos) not in DANGER_ITEMS):
                available_neighbors.append(neighbor_pos)

        return available_neighbors

    def update_queue(self, pos: Tuple[int, int]) -> None:
        available_cells = self.get_available_neighbours(pos)
        for cell in available_cells:
            self.cells_queue.append(cell)

    def get_current_cell(self) -> Tuple[int, int]:
        return self.cells_queue.popleft()

    def get_distance(self, pos: Tuple[int, int]) -> int:
        x, y = pos
        return self.distances[x][y]

    def set_distance(self, pos: Tuple[int, int], distance: int) -> None:
        x, y = pos
        self.distances[x][y] = distance

    def set_min_distance_to(self, pos: Tuple[int, int]) -> None:
        neighbours = get_neighbors(pos)
        neighbour_distances = [self.get_distance(pos) for pos in neighbours]
        min_distance = min(neighbour_distances) + 1
        self.set_distance(pos, min_distance)

    def find_path(self) -> None:
        self.game_map.fill_map()

        self.set_distance(INITIAL_POS, 0)
        self.update_queue(INITIAL_POS)

        while True:
            if len(self.cells_queue) == 0:
                print('e -1')
                return

            current_pos = self.get_current_cell()
            self.set_min_distance_to(current_pos)
            self.update_queue(current_pos)

            if self.game_map.get_info(current_pos) == 'K':
                print('e', self.get_distance(current_pos))
                return


def read_input():
    perception_zone = int(input())
    x, y = input().split()
    x = int(x)
    y = int(y)
    return x, y


def main():
    keymaker_position = read_input()
    path_finder = PathFinder(keymaker_position)
    path_finder.find_path()
    # for row in path_finder.distances:
    #     print(row)
    #
    # print('e')
    # for row in path_finder.game_map.game_map:
    #     print(*row)


if __name__ == '__main__':
    main()
