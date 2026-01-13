import random


def in_range(height, width, cell):
    """Return True when a cell coordinate falls inside the board."""
    return 0 <= cell[0] < height and 0 <= cell[1] < width


class Minesweeper:
    """Immutable board state tracking hidden mines."""

    def __init__(self, height=9, width=9, mines=9):
        """Create a new Minesweeper board with randomly placed mines.

        Summary:
            Generates a grid of the given size and scatters a number of mines.
        Params:
            height: Number of rows in the grid.
            width: Number of columns in the grid.
            mines: Count of mines to place.
        Outputs:
            Initializes `board`, `mines`, and tracking sets on the instance.
        """

        if mines >= height * width:
            raise Exception(
                "mines count cant be more than the height and width of the board"
            )

        self.height = height
        self.width = width
        self.mines = set()
        self.mines_found = set()
        self.board = []

        # initialize the board
        for i in range(height):
            row = []
            for j in range(width):
                row.append(False)
            self.board.append(row)

        # throw the mines randomly
        while len(self.mines) != mines:
            (i, j) = (
                random.randint(0, self.height - 1),
                random.randint(0, self.width - 1),
            )
            self.board[i][j] = True
            self.mines.add((i, j))

    # checking if the cell is in the range of the board
    # def in_range(self, i, j):
    #     return 0 <= i < self.height and 0 <= j < self.width

    # checking if the giving cell in mine
    def is_mine(self, cell):
        """Return True if the provided cell hides a mine."""
        i, j = cell
        if not in_range(self.height, self.width, (i, j)):
            raise Exception("out of range!")

        return self.board[i][j]

    # how many mines are near by
    def nearby_mines(self, cell):
        """Count mines in the 8-neighborhood around a given cell."""
        row, col = cell
        if not in_range(self.height, self.width, (row, col)):
            raise Exception("out of range!")

        mines = 0
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if (i, j) == (0, 0):
                    continue
                if (
                    in_range(self.height, self.width, (row + i, col + j))
                    and self.board[row + i][col + j]
                ):
                    mines += 1

        return mines

    # ckecking if we found all the mines
    def won(self):
        """Return True if all mines have been flagged."""
        return self.mines_found == self.mines


class Sentence:
    """Logical statement of the form set(cells) = count mines."""

    def __init__(self, cells, count):
        """Create a new sentence tying cells to a mine count."""
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        """Return True when both cell sets and counts match."""
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        """Printable form used in debugging output."""
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """Return all cells proven to be mines under this sentence."""
        if len(self.cells) == self.count and self.count != 0:
            return self.cells

    def known_safes(self):
        """Return all cells proven to be safe under this sentence."""
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """Remove a cell from the sentence when it is confirmed a mine."""
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """Remove a cell from the sentence when it is confirmed safe."""
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """Knowledge-based AI agent for playing Minesweeper."""

    def __init__(self, h=8, w=8):
        """Initialize bookkeeping structures for the game board."""

        # set initial height and width
        self.height = h
        self.width = w
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        """Record a cell as a mine and update all sentences."""
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """Record a cell as safe and update all sentences."""
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def infer_new_sentences(self):
        """Infer additional sentences via subset relationships."""
        new_knowledge = []

        # compare every pair of sentences
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                    # infer a new sentence
                    inferred_cells = sentence2.cells - sentence1.cells
                    inferred_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(inferred_cells, inferred_count)

                    if (
                        new_sentence not in self.knowledge
                        and new_sentence not in new_knowledge
                    ):
                        new_knowledge.append(new_sentence)

        # add any new sentences to the knowledge base
        self.knowledge.extend(new_knowledge)

    def add_knowledge(self, cell, count):
        """Incorporate a revealed safe cell and nearby mine count."""
        self.moves_made.add(cell)
        self.mark_safe(cell)

        count_mines = 0
        undtermined_moves = []

        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if (di, dj) == (0, 0):
                    continue

                neighbor = (cell[0] + di, cell[1] + dj)

                if neighbor in self.mines:
                    count_mines += 1

                if (
                    in_range(self.height, self.width, neighbor)
                    and neighbor not in self.safes
                    and neighbor not in self.mines
                ):
                    undtermined_moves.append(neighbor)

        self.knowledge.append(Sentence(undtermined_moves, count - count_mines))

        # update the knowledge based on the current knowledge
        for sentence in self.knowledge:
            if sentence.known_mines():
                for cell in sentence.known_mines().copy():
                    self.mark_mine(cell)
            if sentence.known_safes():
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)

        # infer new sentences, compares the current sentences if one is a subset of the other it infers a new sentence
        self.infer_new_sentences()

    def make_safe_move(self):
        """Return a known safe cell that has not yet been played."""
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """Choose a random move among untried, unknown cells."""
        moves = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    moves.append((i, j))
        return random.choice(moves) if len(moves) != 0 else None
