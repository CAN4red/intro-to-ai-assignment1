from typing import Tuple, Dict, Set, List

INT_INFINITY = 2 ** 31 - 1
MIN_COORD: int = 0
MAX_COORD: int = 8
POSSIBLE_MOVES = ((1, 0), (0, 1), (-1, 0), (0, -1))
DANGER_ITEMS = ('P', 'A', 'S')
NEUTRAL_ITEMS = ('K', 'B', 'N')


def get_neighbours(coord: Tuple[int, int]) -> Set[Tuple[int, int]]:
    """
    Gets the valid neighbours for a given position.

    :param coord: The coordinate for which to find neighbors.
    :return: A set of valid neighboring coordinates.
    """
    neighbours = set()
    for dx, dy in POSSIBLE_MOVES:
        new_x, new_y = coord[0] + dx, coord[1] + dy
        if 0 <= new_x < MAX_COORD and 0 <= new_y < MAX_COORD:
            neighbours.add((new_x, new_y))
    return neighbours


class Cell:
    def __init__(self, coords: Tuple[int, int], from_init: int, to_goal: int,
                 path_from_init: List[Tuple[int, int]]) -> None:
        """
        :param coords: The coordinates of the cell.
        :param from_init: The cost from the initial position to this cell.
        :param to_goal: The estimated cost from this cell to the goal.
        :param path_from_init: The path taken from the initial position to this cell.
        """
        self.coords = coords
        self.from_init = from_init
        self.to_goal = to_goal
        self.total_path = from_init + to_goal
        self.path_from_init: List[Tuple[int, int]] = path_from_init
        self.neighbours: Set[Tuple[int, int]] = get_neighbours(coords)

    def __lt__(self, other: 'Cell') -> bool:
        """
        Compares two Cell objects based on their total path cost.

        :param other: The other Cell object to compare against.
        :return: True if this cell has a lower total path cost than the other.
        """
        if self.total_path == other.total_path:
            return self.to_goal < other.to_goal
        return self.total_path < other.total_path


def _init_to_goals(keymaker_position: Tuple[int, int]) -> Dict[Tuple[int, int], int]:
    """
    Initializes a map of each coordinate to
    its Manhattan distance from the keymaker's position.

    :param keymaker_position: The coordinates of the keymaker.
    :return: A dictionary mapping coordinates.
    """
    to_goals: Dict[Tuple[int, int], int] = {}

    for x in range(MIN_COORD, MAX_COORD + 1):
        for y in range(MIN_COORD, MAX_COORD + 1):
            distance = abs(keymaker_position[0] - x) + abs(keymaker_position[1] - y)
            to_goals[(x, y)] = distance

    return to_goals


def read_response() -> Dict[Tuple[int, int], str]:
    """
    Reads the response of the system for performed move.

    :return: A dictionary mapping coordinates to their item types.
    """
    items_number = int(input())
    items: Dict[Tuple[int, int], str] = dict()
    for _ in range(items_number):
        x, y, item = input().split()
        x = int(x)
        y = int(y)
        items[(x, y)] = item
    return items


def from_current_to_best(current_cell: Cell, best_cell: Cell) -> None:
    """
    Performs the moves from the current cell to the best open cell.

    :param current_cell: The current cell.
    :param best_cell: The best cell to move to.
    """
    for coord in current_cell.path_from_init[:-1][::-1]:
        print("m", *coord)
        read_response()
    for coord in best_cell.path_from_init[1:-1]:
        print("m", *coord)
        read_response()


class AStar:
    def __init__(self, keymaker_position: Tuple[int, int]) -> None:
        """
        :param keymaker_position: The coordinates of the keymaker.
        """
        self.keymaker_position = keymaker_position
        self.visited: Dict[Tuple[int, int], Cell] = dict()
        self.dangers: Set[Tuple[int, int]] = set()
        self.available_cells: Dict[Tuple[int, int], Cell] = dict()
        self.to_goals = _init_to_goals(keymaker_position)

    def _is_valid(self, coords: Tuple[int, int]) -> bool:
        """
        Checks if the given coordinates are valid for a move.

        :param coords: The coordinates to check.
        :return: True if the coordinates are valid, False otherwise.
        """
        x, y = coords
        x_valid = (MIN_COORD <= x <= MAX_COORD)
        y_valid = (MIN_COORD <= y <= MAX_COORD)
        is_safe = coords not in self.dangers
        is_unvisited = coords not in self.visited.keys()
        return x_valid and y_valid and is_safe and is_unvisited

    def _update_visited(self, cell: Cell) -> None:
        """
        Updates the visited cells with the current cell.

        :param cell: The cell to mark as visited.
        """
        self.visited[cell.coords] = cell

    def _get_available_coords(self, coord: Tuple[int, int]) -> Set[Tuple[int, int]]:
        """
        Gets the available coordinates (open positions)
        that can be moved to from the current position.

        :param coord: The current coordinate.
        :return: A set of available coordinates.
        """
        available: Set[Tuple[int, int]] = set()
        x, y = coord
        for dx, dy in POSSIBLE_MOVES:
            new_coord = (x + dx, y + dy)
            if self._is_valid(new_coord):
                available.add(new_coord)
        return available

    def _update_available(self, coord: Tuple[int, int]) -> None:
        """
        Updates the available (open) cells based on the current coordinate.

        :param coord: The current coordinate to update from.
        """
        for new_coord in self._get_available_coords(coord):
            new_from_init = self.visited[coord].from_init + 1
            to_goal = self.to_goals[new_coord]

            if new_coord in self.available_cells.keys():
                old_from_init = self.available_cells[new_coord].from_init

                self.available_cells[new_coord] = Cell(
                    new_coord,
                    min(new_from_init, old_from_init),
                    to_goal,
                    self.visited[coord].path_from_init + [new_coord]
                )
            else:
                self.available_cells[new_coord] = Cell(
                    new_coord,
                    new_from_init,
                    to_goal,
                    self.visited[coord].path_from_init + [new_coord]
                )

    def _update_all_available(self) -> None:
        """
        Updates all available cells by clearing the current
        available cells and recalculating them.
        """
        self.available_cells.clear()
        for coord in self.visited.keys():
            self._update_available(coord)

    def _get_best_cell(self) -> Cell | None:
        """
        Gets the best cell to move to based on the total path cost.

        :return: The best Cell object or None if no available cells exist.
        """
        if len(self.available_cells.keys()) == 0:
            return None

        best_available_cell = Cell(
            (0, 0),
            INT_INFINITY,
            INT_INFINITY,
            []
        )

        for cell in self.available_cells.values():
            if cell < best_available_cell:
                best_available_cell = cell
        return best_available_cell

    def _update_dangers(self, items: Dict[Tuple[int, int], str]) -> None:
        """
        Updates the set of dangerous items by adding new dangers.

        :param items: A dictionary of new dangers.
        """
        for coord in items.keys():
            if items[coord] in DANGER_ITEMS:
                self.dangers.add(coord)

    def _zeroth_move(self) -> Cell:
        """
        Performs the initial move from the starting position and updates the state.

        :return: The Cell object representing the initial position after the move.
        """
        zero_coord = (0, 0)
        zeroth_move = Cell(zero_coord, 0, self.to_goals[zero_coord], [(0, 0)])
        print("m 0 0")
        items_around = read_response()
        self._update_dangers(items_around)
        self._update_visited(zeroth_move)
        self._update_all_available()
        return zeroth_move

    def find_path(self):
        """
        Executes the A* algorithm to find the path to the keymaker.
        """
        best_move = self._zeroth_move()
        while True:
            current_move = best_move
            best_move = self._get_best_cell()

            if best_move is None:
                print("e -1")
                break

            if best_move.coords == self.keymaker_position:
                print("e", best_move.from_init)
                break

            if best_move.coords not in current_move.neighbours:
                from_current_to_best(current_move, best_move)

            print("m", *best_move.coords)

            items_around = read_response()
            self._update_dangers(items_around)
            self._update_visited(best_move)
            self._update_all_available()


def read_initial_input() -> Tuple[int, int]:
    """
    Reads the initial input of the system.

    :return: A keymaker coordinates.
    """
    perception_zone = int(input())
    x, y = input().split()
    return int(x), int(y)


def main() -> None:
    keymaker_position = read_initial_input()
    a_star = AStar(keymaker_position)
    a_star.find_path()


if __name__ == '__main__':
    main()
