from tkinter import *
from copy import deepcopy

'''
    Board parameters:
    - player : White goes first (0 is white and player,1 is black and computer)
    - game_ended : Game continues until the state of game_ended will become True
    - passed : If player has no move, then should pass to opponent
    - matrix : 2D array representing the game board
    - old_matrix : Previous state of matrix
'''

# Variable setup
nodes = 0
depth = 4
moves = 0

# Tkinter setup
w = Tk()
canvas = Canvas(w, width=500, height=500, background="#F0C060")
canvas.pack()


class Board:
    def __init__(self):
        self.player = 0
        self.passed = False
        self.game_ended = False

        '''Initialize an empty board'''
        self.matrix = []
        for x in range(8):
            self.matrix.append([])
            for y in range(8):
                self.matrix[x].append(None)

        self.matrix[3][3] = "w"
        self.matrix[3][4] = "b"
        self.matrix[4][3] = "b"
        self.matrix[4][4] = "w"

        self.old_matrix = self.matrix

    '''Update the screen according to the values in the matrix'''
    def update(self):
        canvas.delete("highlight")
        canvas.delete("tile")

        for x in range(8):
            for y in range(8):
                if self.old_matrix[x][y] == "w":
                    canvas.create_oval(54 + 50 * x, 54 + 50 * y, 96 + 50 * x, 96 + 50 * y,
                                       tags="tile {0}-{1}".format(x, y), fill="#F3ECDD")

                elif self.old_matrix[x][y] == "b":
                    canvas.create_oval(54 + 50 * x, 54 + 50 * y, 96 + 50 * x, 96 + 50 * y,
                                       tags="tile {0}-{1}".format(x, y), fill="#25221C")

        '''Draw circle highlights'''
        for x in range(8):
            for y in range(8):
                if self.player == 0:
                    if valid(self.matrix, self.player, x, y):
                        canvas.create_oval(68 + 50 * x, 68 + 50 * y, 32 + 50 * (x + 1), 32 + 50 * (y + 1),
                                           tags="highlight", fill="#568022", outline="#568022")

        '''Make move if it is AI's turn'''
        if not self.game_ended:
            # Player 1 is AI
            if self.player == 1:

                self.old_matrix = self.matrix
                alpha_beta_result = self.alpha_beta(self.matrix, depth, -float("inf"), float("inf"), 1)
                self.matrix = alpha_beta_result[1]

                if len(alpha_beta_result) == 3:
                    position = alpha_beta_result[2]
                    self.old_matrix[position[0]][position[1]] = "b"

                self.player = 1 - self.player

                nodes = 0
                self.pass_test()
        else:
            canvas.create_text(250, 550, anchor="c", font=("Consolas", 15), text="The game is done!")

    '''Move to the position (x,y)'''
    def board_move(self, x, y):
        global nodes
        self.old_matrix = self.matrix
        self.old_matrix[x][y] = "w"
        self.matrix = move(self.matrix, x, y)

        # Switch Player
        self.player = 1 - self.player
        self.update()

        self.pass_test()
        self.update()

    '''Check if player must pass: if they do, switch the player'''
    def pass_test(self):
        must_pass = True

        for x in range(8):
            for y in range(8):
                if valid(self.matrix, self.player, x, y):
                    must_pass = False

        if must_pass:
            self.player = 1 - self.player

            if self.passed:
                self.game_ended = True
            else:
                self.passed = True
            self.update()
        else:
            self.passed = False

    # AlphaBeta pruning on the minimax tree
    # http://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning
    def alpha_beta(self, node, depth, alpha, beta, maximizing):
        global nodes
        nodes += 1
        boards = []
        choices = []

        for x in range(8):
            for y in range(8):
                if valid(self.matrix, self.player, x, y):
                    test = move(node, x, y)
                    boards.append(test)
                    choices.append([x, y])

        if depth == 0 or len(choices) == 0:
            return [ai_method(node, maximizing), node]

        if maximizing:
            v = -float("inf")
            best_board = []
            best_choice = []
            for board in boards:
                board_value = self.alpha_beta(board, depth - 1, alpha, beta, 0)[0]
                if board_value > v:
                    v = board_value
                    best_board = board
                    best_choice = choices[boards.index(board)]
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return [v, best_board, best_choice]
        else:
            v = float("inf")
            best_board = []
            best_choice = []
            for board in boards:
                board_value = self.alpha_beta(board, depth - 1, alpha, beta, 1)[0]
                if board_value < v:
                    v = board_value
                    best_board = board
                    best_choice = choices[boards.index(board)]
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return [v, best_board, best_choice]


'''Check if a move is valid for a given array'''


def valid(array, player, x, y):

    if player == 0:
        color = "w"
    else:
        color = "b"

    # If there's already a piece there, it's an invalid move
    if array[x][y] is not None:
        return False

    else:
        '''Generate the list of neighbours'''
        neighbour = False
        neighbours = []

        for i in range(max(0, x - 1), min(x + 2, 8)):
            for j in range(max(0, y - 1), min(y + 2, 8)):
                if array[i][j] is not None:
                    neighbour = True
                    neighbours.append([i, j])

        # If there's no neighbours, it's an invalid move
        if not neighbour:
            return False
        else:
            '''Iterate through neighbours to determine if at least one line is formed'''
            is_valid = False
            for neighbour in neighbours:

                neigh_x = neighbour[0]
                neigh_y = neighbour[1]

                # If the neighbour color is equal to your color, it doesn't form a line
                '''Go onto the next neighbour'''
                if array[neigh_x][neigh_y] == color:
                    continue
                else:
                    '''Determine the direction of the line'''
                    delta_x = neigh_x - x
                    delta_y = neigh_y - y
                    temp_x = neigh_x
                    temp_y = neigh_y

                    while 0 <= temp_x <= 7 and 0 <= temp_y <= 7:
                        # If an empty space, no line is formed
                        if array[temp_x][temp_y] is None:
                            break
                        # If it reaches a piece of the player's color, it forms a line
                        if array[temp_x][temp_y] == color:
                            is_valid = True
                            break

                        '''Move the index according to the direction of the line'''
                        temp_x += delta_x
                        temp_y += delta_y

            return is_valid


'''Returns a board after making a move according to the rules, assuming move is valid'''


def move(passed_array, x, y):
    # Copy the passed_array
    array = deepcopy(passed_array)

    if board.player == 0:
        color = "w"
    else:
        color = "b"

    array[x][y] = color

    '''Determine the neighbours to the square'''
    neighbours = []
    for i in range(max(0, x - 1), min(x + 2, 8)):
        for j in range(max(0, y - 1), min(y + 2, 8)):
            if array[i][j] is not None:
                neighbours.append([i, j])

    # Which tiles to convert
    convert = []

    '''For all the generated neighbours, determine if they form a line
       If a line is formed, we will add it to the convert array'''

    for neighbour in neighbours:
        neigh_x = neighbour[0]
        neigh_y = neighbour[1]

        '''Check if the neighbour is of a different color - it must be to form a line'''
        if array[neigh_x][neigh_y] != color:
            # The path of each individual line
            path = []

            '''Determine direction to move'''
            delta_x = neigh_x - x
            delta_y = neigh_y - y

            temp_x = neigh_x
            temp_y = neigh_y

            while 0 <= temp_x <= 7 and 0 <= temp_y <= 7:
                path.append([temp_x, temp_y])
                value = array[temp_x][temp_y]

                # If we reach a blank tile, we're done and there's no line
                if value is None:
                    break

                # If we reach a tile of the player's color, a line is formed
                if value == color:
                    for node in path:
                        convert.append(node)
                    break

                '''Move the tile'''
                temp_x += delta_x
                temp_y += delta_y

    '''Convert all the appropriate tiles'''
    for node in convert:
        array[node[0]][node[1]] = color

    return array


'''Method that weights corner tiles and edge tiles as positive, 
   adjacent to corners (if the corner is not yours) as negative,
   other tiles as one point'''


def ai_method(array, player):
    score = 0
    corner_val = 15
    adjacent_val = 5
    side_val = 5

    if player == 1:
        color = "b"
        opponent = "w"
    else:
        color = "w"
        opponent = "b"

    '''Go through all the tiles'''
    for x in range(8):
        for y in range(8):
            # Normal tiles worth 1
            add = 1

            # Adjacent to corners are worth -5
            if (x == 0 and y == 1) or (x == 1 and 0 <= y <= 1):
                if array[0][0] == color:
                    add = side_val
                else:
                    add = -adjacent_val

            elif (x == 0 and y == 6) or (x == 1 and 6 <= y <= 7):
                if array[7][0] == color:
                    add = side_val
                else:
                    add = -adjacent_val

            elif (x == 7 and y == 1) or (x == 6 and 0 <= y <= 1):
                if array[0][7] == color:
                    add = side_val
                else:
                    add = -adjacent_val

            elif (x == 7 and y == 6) or (x == 6 and 6 <= y <= 7):
                if array[7][7] == color:
                    add = side_val
                else:
                    add = -adjacent_val

            # Edge tiles worth 5
            elif (x == 0 and 1 < y < 6) or (x == 7 and 1 < y < 6) or (y == 0 and 1 < x < 6) or (y == 7 and 1 < x < 6):
                add = side_val

            # Corner tiles worth 15
            elif (x == 0 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 0) or (x == 7 and y == 7):
                add = corner_val

            '''Add or subtract the value of the tile corresponding to the color'''
            if array[x][y] == color:
                score += add
            elif array[x][y] == opponent:
                score -= add

    return score


'''Make the move (if valid) when the user clicks'''


def click_handle(event):
    x_mouse = event.x
    y_mouse = event.y

    # If game is not running, start the game first
    if running:
        if x_mouse >= 453 and y_mouse <= 50:
            w.destroy()
        elif x_mouse <= 47 and y_mouse <= 50:
            play_game()
        else:
            '''Check if it is the player's turn'''
            if board.player == 0:
                '''Determine the grid index for where the mouse was clicked'''
                x = int((event.x - 50) / 50)
                y = int((event.y - 50) / 50)

                if 0 <= x <= 7 and 0 <= y <= 7:
                    # If the click is inside the bounds and the move is valid, move to that location
                    if valid(board.matrix, board.player, x, y):
                        board.board_move(x, y)
    else:
        play_game()


'''Draw the gridlines'''


def draw_grid_background():
    canvas.create_rectangle(50, 50, 450, 450, outline="#111")

    for i in range(7):
        line_shift = 50 + 50 * (i + 1)
        # Horizontal line
        canvas.create_line(50, line_shift, 450, line_shift, fill="#111")
        # Vertical line
        canvas.create_line(line_shift, 50, line_shift, 450, fill="#111")


def create_buttons():
    # Restart button
    canvas.create_rectangle(0, 0, 47, 50, fill="#2C2D91", outline="#2C2D91")
    canvas.create_arc(5, 5, 45, 45, fill="#000088", width="2", style="arc", outline="white", extent=300)
    canvas.create_polygon(33, 38, 36, 45, 40, 39, fill="white", outline="white")

    # Quit button
    canvas.create_rectangle(453, 0, 501, 50, fill="#C12644", outline="#C12644")
    canvas.create_line(458, 5, 498, 45, fill="white", width="3")
    canvas.create_line(498, 5, 458, 45, fill="white", width="3")


def run_game():
    global running
    running = False

    canvas.create_text(250, 203, anchor="c", text="Othello", font=("Consolas", 50), fill="#4A6461")
    canvas.create_text(250, 253, anchor="c", text="GE2340 Project", font=("Consolas", 20), fill="#aaa")
    canvas.create_rectangle(180, 310, 310, 355, fill="#2D6114", outline="#30810A")
    canvas.create_text(247, 330, anchor="c", text="Start", font=("Consolas", 30), fill="#E7EFEB")


def play_game():
    global board, running
    running = True
    canvas.delete(ALL)
    board = 0
    create_buttons()

    '''Draw background. Initialize a board and update it'''
    draw_grid_background()
    board = Board()
    board.update()


run_game()

# Binding, setting
canvas.bind("<Button-1>", click_handle)
canvas.focus_set()

w.wm_title("GE2340 Project")
w.mainloop()