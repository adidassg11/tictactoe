
#!/usr/bin/python

### GLOBALS ###
DEBUG_ON = False

def print_debug(msg):
    if DEBUG_ON:
        print(msg)

### EXCEPTIONS ###
class BoardUpdateException(Exception):
    pass


### GAME ###
class UserInput(object):
    def __init__(self, size):
        self.size = size

    def get_input(self):
        print 'enter [X|O] [row #] [col #] , use zero-based numbers'
        user_input = raw_input()
        args = user_input.split()

        # Error checking
        if len(args) != 3:
            raise Exception('Incorrect number of arguments')

        player = args[0]
        row = int(args[1])
        col = int(args[2])

        if player not in ('X', 'O'):
            raise Exception('Player must be X or O')

        if col < 0 or col >= self.size \
            or row < 0 or row >= self.size:
            raise Exception('Row and column number must be within board size')

        # Store values
        self.player = player #not used for now?
        self.row = row
        self.col = col

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col


class WinDetector(object):
    def __init__(self, size, board, cur_player):
        self.size = size
        self.board = board
        self.cur_player = cur_player

    # TODO: does self.board act as a pointer/reference or do i need to keep updating it?
    def has_won(self, cur_player, board=None):
        if board:
            self.board = board

        self.cur_player = cur_player

        winning_combination = 'O' * self.size if self.cur_player == 'O' \
                                              else 'X' * self.size
        # Check rows
        for i in xrange(self.size):
            row_chars = ''
            start_index = i*self.size
            row_chars = self.board[start_index : start_index+self.size]
            if row_chars == winning_combination:
                print_debug('winning row # %s' % (i))
                return True

        # Check columns
        for i in xrange(self.size):
            column_chars = ''
            for j in xrange(self.size):
                column_chars += self.board[i + j*self.size]
            if column_chars == winning_combination:
                print_debug('winning col # %s' % (i))
                return True

        # Check diagonal 1
        diag_chars = ''
        for i in xrange(self.size):
            diag_chars += self.board[i + i*self.size]
            if diag_chars == winning_combination:
                print_debug('winning diagonal backslash')
                return True

        # Check diagonal 2
        diag_chars = ''
        for i in xrange(self.size):
            # derived from diag 1 formula
            diag_chars += self.board[self.size - i - 1 + i*self.size]
            if diag_chars == winning_combination:
                print_debug('winning diagonal forward slash')
                return True

        return False


class Game(object):
    MAX_INPUT_FAILURES = 3
    user_input = None
    EMPTY_SPACE_CHAR = '-'

    def __init__(self, size):
        self.size = size
        self.board = self.EMPTY_SPACE_CHAR*size*size # this is the game board grid represented as string
        self.current_player = 'X'
        self.win_detector = WinDetector(self.size, self.current_player,
                                            self.board)
        print 'Game object initialized'

    def start_game(self):
        winner_exists = False
        round_number = 1

        while not winner_exists:
            print '\n== ROUND %s ==' % round_number
            self.print_board()
            self.get_input()
            try:
                self.update_board(self.current_player, self.user_input.get_row(),
                                  self.user_input.get_col())
            except BoardUpdateException as e:
                print e.msg
                continue

            winner_exists = self.win_detector.has_won(self.current_player,
                                                      self.board)
            if winner_exists:
                print 'Player %s wins!\n' % self.current_player
                return

            # Prep for next round
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            round_number += 1

        print 'Draw!'

    def update_board(self, player, row, col):
        index = col + row*self.size

        if self.board[index] != self.EMPTY_SPACE_CHAR:
            raise BoardUpdateException('Exceeded max input failure threshold of %s'
                            % (self.MAX_INPUT_FAILURES))
        # TODO: this is dirty, change board to list instead of string
        #self.board[col+ row*self.size] = player
        self.board = self.board[:index] + player + self.board[index + 1:]

    def print_board(self):
        print_debug(self.board)
        for i in xrange(self.size):
            start_slice = i * self.size
            end_slice = start_slice + self.size
            # print 'start, end slice: %s %s' % (start_slice, end_slice)
            print '%s' % self.board[start_slice:end_slice]

    def get_input(self):
        attempt_num = 1
        while attempt_num <= self.MAX_INPUT_FAILURES:
            user_input = UserInput(self.size)
            try:
                user_input.get_input()
            except Exception as e:
                print 'user input error: %s' % e
                attempt_num += 1
                continue

            # Got valid input
            self.user_input = user_input
            return

        raise Exception('Exceeded max input failure threshold of %s'
                        % (self.MAX_INPUT_FAILURES))


class WinDetectorTest(object):
    win_detector = None
    def __init__(self):
        pass

    def test_size3_rows(self):
        self.win_detector = WinDetector(3, 'XX-OO----', 'X')
        neither_has_won = not self.win_detector.has_won('X')
        assert neither_has_won

        self.win_detector = WinDetector(3, 'XXXOO----', 'X')
        x_has_won = self.win_detector.has_won('X')
        assert x_has_won

        self.win_detector = WinDetector(3, 'XX-OOO---', 'O')
        o_has_won = self.win_detector.has_won('O')
        assert o_has_won


    def test_size3_cols(self):
        self.win_detector = WinDetector(3, 'X--X--X--', 'X')
        x_has_won = self.win_detector.has_won('X')
        assert x_has_won

        self.win_detector = WinDetector(3, 'X-OX-O--O', 'O')
        o_has_won = self.win_detector.has_won('O')
        assert o_has_won

    def test_size3_diags(self):
        self.win_detector = WinDetector(3, 'X---X---X', 'X')
        x_has_won = self.win_detector.has_won('X')
        assert x_has_won

        self.win_detector = WinDetector(3, '--X-X-X--', 'X')
        x_has_won = self.win_detector.has_won('X')
        assert x_has_won

    def test_size4_row(self):
        self.win_detector = WinDetector(4, 'XXX-XXXX---O----', 'X')
        x_has_won = self.win_detector.has_won('X')
        assert x_has_won

    def run_tests(self):
        self.test_size3_rows()
        self.test_size3_cols()
        self.test_size3_diags()
        self.test_size4_row()


### Program entry point ###
if __name__ == "__main__":
    # tests = WinDetectorTest().run_tests()
    print 'Starting Tic Tac Toe game...'
    ttt_game = Game(3)
    ttt_game.start_game()
    print 'GAME OVER'
