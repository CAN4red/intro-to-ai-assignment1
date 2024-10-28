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
        if item_type in DANGER_ITEMS:
            dangers[(x, y)] = item_type

    return dangers


class GameMap:
    def __init__(self):
        self.game_map: List[List[int]] = [[INT_INFINITY for _ in range(9)] for _ in range(9)]
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
            if self._get_path_len(neighbor_pos) > self._get_path_len(pos) + 1:
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

    def _get_path_len(self, pos: Tuple[int, int]) -> int:
        """
        Gets the path length to the given position on the game map.

        :param pos: The position to retrieve information from.
        :return: The information at the position or None if unvisited.
        """
        x, y = pos
        return self.game_map[x][y]

    def _change_path_len(self, pos: Tuple[int, int], new_path_len: int) -> None:
        """
        Changes the path length for a given position on the game map.

        :param pos: The position to change information for.
        :param new_path_len: The new information to store.
        """
        x, y = pos
        self.game_map[x][y] = new_path_len

    def _add_dangers(self, dangers: Dict[Tuple[int, int], str]) -> None:
        """
        Adds dangers to the game map as negative infinity.

        :param dangers: A dictionary of items and their positions.
        """
        for pos in dangers.keys():
            self._change_path_len(pos, -INT_INFINITY)

    def _move_to(self, pos: Tuple[int, int], path: int) -> None:
        """
        Moves to the position, updates the game map, and reads the response.

        :param pos: The position to move to.
        """
        print('m', *pos)
        dangers = read_response()

        self._add_dangers(dangers)
        self._change_path_len(pos, path)
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

    def _fill_map(self) -> None:
        """
        Fills all the shortest paths on the game map
        by moving through available positions
        until no more moves can be made.
        """
        self._move_to(INITIAL_POS, 0)
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
                self._move_to(neighbour_pos, self._get_path_len(current_pos) + 1)
            else:
                prev_pos = self._backtrack()
                if self.is_first_backtrack:
                    self.is_first_backtrack = False
                    continue
                print('m', *prev_pos)
                read_response()

    def find_path(self, keymaker_position: Tuple[int, int]) -> None:
        """
        Prints the shortest path to the keymaker

        :param keymaker_position: position of the keymaker
        """
        self._fill_map()
        if self._get_path_len(keymaker_position) == INT_INFINITY:
            print("e -1")
        else:
            print('e', self._get_path_len(keymaker_position))


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
    game_map = GameMap()
    game_map.find_path(keymaker_position)


if __name__ == '__main__':
    main()
