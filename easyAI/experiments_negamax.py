import json
import random
import time
from dataclasses import dataclass
from typing import Callable

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


class ExpectiNegamaxAlphaBeta:
    """Expecti-negamax with alpha-beta pruning on decision nodes.

    The algorithm models TicTacDoh stochasticity directly:
    - with probability p_success, the move is applied,
    - with probability p_fail, the move is skipped and turn changes.
    """

    def __init__(self, depth, scoring=None, fail_probability=0.2):
        self.depth = depth
        self.scoring = scoring
        self.fail_probability = fail_probability

    def __call__(self, game):
        scoring_fn = self.scoring if self.scoring else (lambda g: g.scoring())
        possible_moves = game.possible_moves()
        if not possible_moves:
            return None

        # Deterministic mode has no failed moves.
        p_fail = self.fail_probability if not getattr(game, "deterministic", True) else 0.0
        p_success = 1.0 - p_fail

        alpha = float("-inf")
        beta = float("inf")
        best_move = possible_moves[0]
        best_value = float("-inf")
        has_unmake = hasattr(game, "unmake_move")

        for move in possible_moves:
            if has_unmake:
                # Success branch: move is made.
                game.make_move(move)
                game.switch_player()
                success_value = -self._expecti_negamax(
                    game, self.depth - 1, -beta, -alpha, scoring_fn
                )
                game.switch_player()
                game.unmake_move(move)

                # Failure branch: board unchanged, only turn switches.
                game.switch_player()
                failure_value = -self._expecti_negamax(
                    game, self.depth - 1, -beta, -alpha, scoring_fn
                )
                game.switch_player()
            else:
                success_state = game.copy()
                success_state.make_move(move)
                success_state.switch_player()
                success_value = -self._expecti_negamax(
                    success_state, self.depth - 1, -beta, -alpha, scoring_fn
                )

                failure_state = game.copy()
                failure_state.switch_player()
                failure_value = -self._expecti_negamax(
                    failure_state, self.depth - 1, -beta, -alpha, scoring_fn
                )

            value = p_success * success_value + p_fail * failure_value

            if value > best_value:
                best_value = value
                best_move = move

            if value > alpha:
                alpha = value

            if alpha >= beta:
                break

        return best_move

    def _expecti_negamax(self, game, depth, alpha, beta, scoring_fn):
        if depth == 0 or game.is_over():
            return scoring_fn(game)

        possible_moves = game.possible_moves()
        if not possible_moves:
            return scoring_fn(game)

        p_fail = self.fail_probability if not getattr(game, "deterministic", True) else 0.0
        p_success = 1.0 - p_fail
        best_value = float("-inf")
        has_unmake = hasattr(game, "unmake_move")

        for move in possible_moves:
            if has_unmake:
                game.make_move(move)
                game.switch_player()
                success_value = -self._expecti_negamax(
                    game, depth - 1, -beta, -alpha, scoring_fn
                )
                game.switch_player()
                game.unmake_move(move)

                game.switch_player()
                failure_value = -self._expecti_negamax(
                    game, depth - 1, -beta, -alpha, scoring_fn
                )
                game.switch_player()
            else:
                success_state = game.copy()
                success_state.make_move(move)
                success_state.switch_player()
                success_value = -self._expecti_negamax(
                    success_state, depth - 1, -beta, -alpha, scoring_fn
                )

                failure_state = game.copy()
                failure_state.switch_player()
                failure_value = -self._expecti_negamax(
                    failure_state, depth - 1, -beta, -alpha, scoring_fn
                )

            value = p_success * success_value + p_fail * failure_value

            if value > best_value:
                best_value = value

            if value > alpha:
                alpha = value

            if alpha >= beta:
                break

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
    factory: Callable


def build_ab(depth):
    return Negamax(depth)


def build_no_ab(depth):
    return NegamaxNoAlphaBeta(depth)


def build_expecti(depth):
    return ExpectiNegamaxAlphaBeta(depth)


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
        "ab_d8": AIConfig("Negamax_AB_d8", lambda: build_ab(8)),
        "noab_d4": AIConfig("Negamax_noAB_d4", lambda: build_no_ab(4)),
        "noab_d6": AIConfig("Negamax_noAB_d6", lambda: build_no_ab(6)),
        "expecti_d4": AIConfig("ExpectiNegamax_AB_d4", lambda: build_expecti(4)),
        "expecti_d6": AIConfig("ExpectiNegamax_AB_d6", lambda: build_expecti(6)),
    }

    pairings = [
        ("ab_d4", "ab_d6"),
        ("ab_d4", "ab_d8"),
        ("noab_d4", "noab_d6"),
        ("ab_d6", "noab_d6"),
        ("ab_d8", "noab_d6"),
        ("expecti_d4", "expecti_d6"),
        ("ab_d6", "expecti_d6"),
        ("noab_d6", "expecti_d6"),
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
