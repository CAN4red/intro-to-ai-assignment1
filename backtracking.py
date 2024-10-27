from collections import deque
from typing import Tuple, List, Dict, Deque

MIN_COORD = 0
MAX_COORD = 8
INT_INFINITY = 2 ** 31 - 1
POSSIBLE_MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DANGER_ITEMS = ('P', 'A', 'S')
INITIAL_POS = (0, 0)


def is_valid(pos: Tuple[int, int]) -> bool:
    """
    Checks if the given position is within the valid grid boundaries.

    :param pos: The coordinates to check.
    :return: True if the position is valid, False otherwise.
    """
    x, y = pos

    x_valid = MIN_COORD <= x <= MAX_COORD
    y_valid = MIN_COORD <= y <= MAX_COORD

    return x_valid and y_valid


def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Gets the valid neighboring positions for a given position.

    :param pos: The position for which to find neighbors.
    :return: A list of valid neighboring positions.
    """
    neighbors = []
    x, y = pos

    for dx, dy in POSSIBLE_MOVES:
        new_pos = (x + dx, y + dy)
        if is_valid(new_pos):
            neighbors.append(new_pos)

    return neighbors


def read_response() -> Dict[Tuple[int, int], str]:
    """
    Reads the response of the system for performed move.

    :return: A dictionary mapping coordinates to their item types.
    """
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

    def _get_available_neighbours(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Gets the available neighboring positions that have not been visited.

        :param pos: The current position.
        :return: A list of available neighboring positions.
        """
        available_neighbors = []

        for neighbor_pos in get_neighbors(pos):
            if self.get_info(neighbor_pos) is None:
                available_neighbors.append(neighbor_pos)

        return available_neighbors

    def _get_neighbour(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Gets the first available neighbor of the current position.

        :param pos: The current position.
        :return: The first available neighboring position.
        """
        return self._get_available_neighbours(pos)[0]

    def _has_available_neighbours(self, pos: Tuple[int, int]) -> bool:
        """
        Checks if there are any available neighbors for the given position.

        :param pos: The current position.
        :return: True if there are available neighbors, False otherwise.
        """
        neighbors = self._get_available_neighbours(pos)
        return len(neighbors) != 0

    def get_info(self, pos: Tuple[int, int]) -> str | None:
        """
        Gets the information stored at the given position on the game map.

        :param pos: The position to retrieve information from.
        :return: The information at the position or None if unvisited.
        """
        x, y = pos
        return self.game_map[x][y]

    def _change_info(self, pos: Tuple[int, int], info: str) -> None:
        """
        Changes the information stored at the given position on the game map.

        :param pos: The position to change information for.
        :param info: The new information to store.
        """
        x, y = pos
        self.game_map[x][y] = info

    def _add_items(self, items: Dict[Tuple[int, int], str]) -> None:
        """
        Adds items to the game map.

        :param items: A dictionary of items and their positions.
        """
        for pos in items.keys():
            self._change_info(pos, items[pos])

    def _add_visited(self, pos: Tuple[int, int]) -> None:
        """
        Marks the given position as visited on the game map.

        :param pos: The position to mark as visited.
        """
        x, y = pos
        if self.game_map[x][y] is None:
            self.game_map[x][y] = '.'

    def _move_to(self, pos: Tuple[int, int]) -> None:
        """
        Moves to the position, updates the game map, and reads the response.

        :param pos: The position to move to.
        """
        print('m', *pos)
        dangers = read_response()

        self._add_items(dangers)
        self._add_visited(pos)
        self.visited_path.append(pos)

    def _get_current_pos(self) -> Tuple[int, int]:
        """
        Gets the current position based on the visited path.

        :return: The current position as a tuple of coordinates.
        """
        if len(self.visited_path) == 0:
            return 0, 0
        return self.visited_path[-1]

    def _backtrack(self) -> Tuple[int, int]:
        """
        Backtracks to the previous position in the visited path.

        :return: The position of the last visited cell.
        """
        return self.visited_path.pop()

    def fill_map(self) -> None:
        """
        Fills the game map by moving through available positions
        until no more moves can be made.
        """
        self._move_to(INITIAL_POS)
        while True:
            current_pos = self._get_current_pos()

            if current_pos == INITIAL_POS and not self._has_available_neighbours(current_pos):
                return

            if self._has_available_neighbours(current_pos):
                if not self.is_first_backtrack:
                    print('m', *current_pos)
                    read_response()
                    self.is_first_backtrack = True

                neighbour_pos = self._get_neighbour(current_pos)
                self._move_to(neighbour_pos)
            else:
                if self.is_first_backtrack:
                    self._backtrack()
                    self.is_first_backtrack = False
                prev_pos = self._backtrack()
                print('m', *prev_pos)
                read_response()


class PathFinder:
    def __init__(self, keymaker_position):
        """
        :param keymaker_position: The coordinates of the keymaker.
        """
        self.game_map: GameMap = GameMap()
        self.keymaker_position = keymaker_position
        self.distances: List[List[int]] = [[INT_INFINITY for _ in range(9)] for _ in range(9)]
        self.cells_queue: Deque[Tuple[int, int]] = deque()

    def _get_available_neighbours(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Gets the available neighbours (open moves) that can be moved to.

        :param pos: The current position.
        :return: A list of available neighbours.
        """
        available_neighbors = []

        for neighbor_pos in get_neighbors(pos):
            if (self._get_distance(neighbor_pos) >= INT_INFINITY and
                    self.game_map.get_info(neighbor_pos) not in DANGER_ITEMS):
                available_neighbors.append(neighbor_pos)

        return available_neighbors

    def _update_queue(self, pos: Tuple[int, int]) -> None:
        """
        Updates the queue of cells to explore based on the current position.

        :param pos: The current position to update from.
        """
        available_cells = self._get_available_neighbours(pos)
        for cell in available_cells:
            self.cells_queue.append(cell)

    def _get_current_cell(self) -> Tuple[int, int]:
        """
        Gets the current cell from the queue.

        :return: The coordinates of the current cell.
        """
        return self.cells_queue.popleft()

    def _get_distance(self, pos: Tuple[int, int]) -> int:
        """
        Gets the distance value for the given position.

        :param pos: The position to get the distance for.
        :return: The distance value at the position.
        """
        x, y = pos
        return self.distances[x][y]

    def _set_distance(self, pos: Tuple[int, int], distance: int) -> None:
        """
        Sets the distance value for the given position.

        :param pos: The position to set the distance for.
        :param distance: The distance value to set.
        """
        x, y = pos
        self.distances[x][y] = distance

    def _set_min_distance_to(self, pos: Tuple[int, int]) -> None:
        """
        Sets the minimum distance to the given position based on its neighbours.

        :param pos: The position to set the minimum distance for.
        """
        neighbours = get_neighbors(pos)
        neighbour_distances = [self._get_distance(pos) for pos in neighbours]
        min_distance = min(neighbour_distances) + 1
        self._set_distance(pos, min_distance)

    def find_path(self) -> None:
        """
        Executes the pathfinding algorithm to the keymaker's position.

        This method fills the game map, initializes distances, and processes the cells queue
        until the keymaker is found or no more cells are available.
        """
        self.game_map.fill_map()

        self._set_distance(INITIAL_POS, 0)
        self._update_queue(INITIAL_POS)

        while True:
            if len(self.cells_queue) == 0:
                print('e -1')
                return

            current_pos = self._get_current_cell()
            self._set_min_distance_to(current_pos)
            self._update_queue(current_pos)

            if self.game_map.get_info(current_pos) == 'K':
                print('e', self._get_distance(current_pos))
                return


def read_initial_input():
    """
    Reads the initial input of the system.

    :return: A keymaker coordinates.
    """
    perception_zone = int(input())
    x, y = input().split()
    x = int(x)
    y = int(y)
    return x, y


def main():
    keymaker_position = read_initial_input()
    path_finder = PathFinder(keymaker_position)
    path_finder.find_path()


if __name__ == '__main__':
    main()
