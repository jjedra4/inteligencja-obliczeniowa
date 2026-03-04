import json
import random
import time
from dataclasses import dataclass

from easyAI import Negamax

from TicTacDoh import TicTacDoh


random.seed(42)


class NegamaxNoAlphaBeta:
    def __init__(self, depth, scoring=None):
        self.depth = depth
        self.scoring = scoring

    def __call__(self, game):
        scoring_fn = self.scoring if self.scoring else (lambda g: g.scoring())
        state = game
        possible_moves = state.possible_moves()
        if not possible_moves:
            return None

        best_move = possible_moves[0]
        best_value = float("-inf")
        unmake_move = hasattr(state, "unmake_move")

        for move in possible_moves:
            if not unmake_move:
                game = state.copy()

            game.make_move(move)
            game.switch_player()
            value = -self._negamax(game, self.depth - 1, scoring_fn)

            if unmake_move:
                game.switch_player()
                game.unmake_move(move)

            if value > best_value:
                best_value = value
                best_move = move

        return best_move

    def _negamax(self, game, depth, scoring_fn):
        if depth == 0 or game.is_over():
            return scoring_fn(game)

        state = game
        possible_moves = state.possible_moves()
        if not possible_moves:
            return scoring_fn(state)

        best_value = float("-inf")
        unmake_move = hasattr(state, "unmake_move")

        for move in possible_moves:
            if not unmake_move:
                game = state.copy()

            game.make_move(move)
            game.switch_player()
            value = -self._negamax(game, depth - 1, scoring_fn)

            if unmake_move:
                game.switch_player()
                game.unmake_move(move)

            if value > best_value:
                best_value = value

        return best_value


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


@dataclass
class AIConfig:
    name: str
    factory: callable


def build_ab(depth):
    return Negamax(depth)


def build_no_ab(depth):
    return NegamaxNoAlphaBeta(depth)


def run_matchup(config_1, config_2, n_games, deterministic):
    results = {
        "ai_1": 0,
        "ai_2": 0,
        "draw": 0,
        "ai_1_avg_time": 0.0,
        "ai_2_avg_time": 0.0,
        "n_games": n_games,
        "deterministic": deterministic,
        "ai_1_name": config_1.name,
        "ai_2_name": config_2.name,
    }

    ai_1_total_time = 0.0
    ai_2_total_time = 0.0
    ai_1_total_moves = 0
    ai_2_total_moves = 0

    for game_idx in range(n_games):
        ai_1_player = TimedAIPlayer(config_1.factory(), "ai_1")
        ai_2_player = TimedAIPlayer(config_2.factory(), "ai_2")
        game = TicTacDoh([ai_1_player, ai_2_player])
        game.deterministic = deterministic
        game.current_player = 1 if game_idx % 2 == 0 else 2
        game.play(verbose=False)

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

    return results


def main():
    n_games = 60
    configs = {
        "ab_d4": AIConfig("Negamax_AB_d4", lambda: build_ab(4)),
        "ab_d6": AIConfig("Negamax_AB_d6", lambda: build_ab(6)),
        "noab_d4": AIConfig("Negamax_noAB_d4", lambda: build_no_ab(4)),
        "noab_d6": AIConfig("Negamax_noAB_d6", lambda: build_no_ab(6)),
    }

    pairings = [
        ("ab_d4", "ab_d6"),
        ("noab_d4", "noab_d6"),
        ("ab_d4", "noab_d4"),
        ("ab_d6", "noab_d6"),
    ]

    all_results = []

    for deterministic in [True, False]:
        for left, right in pairings:
            result = run_matchup(
                configs[left],
                configs[right],
                n_games=n_games,
                deterministic=deterministic,
            )
            all_results.append(result)
            print(
                f"deterministic={deterministic} | {result['ai_1_name']} vs {result['ai_2_name']} "
                f"=> W1={result['ai_1']}, W2={result['ai_2']}, D={result['draw']}, "
                f"T1={result['ai_1_avg_time']:.6f}s, T2={result['ai_2_avg_time']:.6f}s"
            )

    with open("experiment_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print("\nSaved detailed results to experiment_results.json")


if __name__ == "__main__":
    main()
