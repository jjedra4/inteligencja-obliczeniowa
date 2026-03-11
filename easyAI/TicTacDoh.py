from easyAI import TwoPlayerGame
from easyAI.Player import Human_Player
import random
import time

random.seed(42)

class TicTacDoh(TwoPlayerGame):
    """The board positions are numbered as follows:
    1 2 3
    4 5 6
    7 8 9
    """

    def __init__(self, players):
        self.players = players
        self.board = [0 for i in range(9)]
        self.current_player = 1  # player 1 starts.
        self.deterministic = True

    def possible_moves(self):
        return [i + 1 for i, e in enumerate(self.board) if e == 0]

    def has_three_in_line(self, player_index):
        return any(
            [
                all([(self.board[c - 1] == player_index) for c in line])
                for line in [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9],
                    [1, 4, 7],
                    [2, 5, 8],
                    [3, 6, 9],
                    [1, 5, 9],
                    [3, 5, 7],
                ]
            ]
        )

    def make_move(self, move):
        if random.random() < 0.2 and not self.deterministic:
            return
        self.board[int(move) - 1] = self.current_player

    def unmake_move(self, move):  # optional method (speeds up the AI)
        self.board[int(move) - 1] = 0

    def lose(self):
        """ Has the opponent "three in line ?" """
        return self.has_three_in_line(self.opponent_index)

    def win(self):
        return self.has_three_in_line(self.current_player)

    def winner(self):
        if self.has_three_in_line(1):
            return 1
        if self.has_three_in_line(2):
            return 2
        return 0

    def is_over(self):
        return (self.possible_moves() == []) or self.lose()

    def show(self):
        print(
            "\n"
            + "\n".join(
                [
                    " ".join([[".", "O", "X"][self.board[3 * j + i]] for i in range(3)])
                    for j in range(3)
                ]
            )
        )

    def scoring(self):
        if self.win():
            return 100
        if self.lose():
            return -100
        return 0


class TimedAIPlayer:
    def __init__(self, ai_algo, key):
        self.ai_algo = ai_algo
        self.key = key
        self.total_time = 0.0
        self.move_count = 0

    def ask_move(self, game):
        start = time.perf_counter()
        move = self.ai_algo(game)
        self.total_time += time.perf_counter() - start
        self.move_count += 1
        return move


if __name__ == "__main__":

    from easyAI import AI_Player, Negamax

    ai_algo_1 = Negamax(6)
    ai_algo_2 = Negamax(10)
    # TicTacDoh([Human_Player(), AI_Player(ai_algo)]).play()
    results = {
        "ai_1": 0,
        "ai_2": 0,
        "draw": 0,
        "ai_1_avg_time": 0.0,
        "ai_2_avg_time": 0.0,
    }
    ai_1_total_time = 0.0
    ai_2_total_time = 0.0
    ai_1_total_moves = 0
    ai_2_total_moves = 0

    for i in range(100):
        ai_1_player = TimedAIPlayer(ai_algo_1, "ai_1")
        ai_2_player = TimedAIPlayer(ai_algo_2, "ai_2")
        game = TicTacDoh([ai_1_player, ai_2_player])
        game.current_player = 1 if i % 2 == 0 else 2
        game.play()

        ai_1_total_time += ai_1_player.total_time
        ai_2_total_time += ai_2_player.total_time
        ai_1_total_moves += ai_1_player.move_count
        ai_2_total_moves += ai_2_player.move_count

        winner = game.winner()
        if winner == 1:
            results["ai_1"] += 1
        elif winner == 2:
            results["ai_2"] += 1
        else:
            results["draw"] += 1

    results["ai_1_avg_time"] = (
        ai_1_total_time / ai_1_total_moves if ai_1_total_moves else 0.0
    )
    results["ai_2_avg_time"] = (
        ai_2_total_time / ai_2_total_moves if ai_2_total_moves else 0.0
    )
    print(results)