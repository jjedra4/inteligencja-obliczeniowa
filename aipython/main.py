from stripsProblem import Strips, STRIPS_domain, Planning_problem
from stripsForwardPlanner import Forward_STRIPS
from searchGeneric import AStarSearcher
import time

boolean = {False, True}

# ==========================================
# 1. DZIEDZINA I PROBLEMY (BLOCKSWORLD)
# ==========================================

blocks = {"a", "b", "c"}
tables = {"t1", "t2", "t3"}
surfaces = blocks | tables

blocksworld_feature_domains = {
    "on_a": surfaces - {"a"},
    "on_b": surfaces - {"b"},
    "on_c": surfaces - {"c"},
    "clear_a": boolean,
    "clear_b": boolean,
    "clear_c": boolean,
    "clear_t1": boolean,
    "clear_t2": boolean,
    "clear_t3": boolean,
}


def clear_feature(surface):
    return f"clear_{surface}"


blocksworld_actions = []

for b in blocks:
    on_b = f"on_{b}"
    clear_b = clear_feature(b)
    for x in tables:
        for y in tables:
            if x == y:
                continue
            blocksworld_actions.append(
                Strips(
                    f"move({b},{x},{y})",
                    preconds={on_b: x, clear_b: True, clear_feature(y): True},
                    effects={on_b: y, clear_feature(x): True, clear_feature(y): False},
                )
            )

for upper in blocks:
    for lower in blocks:
        if upper == lower:
            continue
        on_upper = f"on_{upper}"
        clear_upper = clear_feature(upper)
        clear_lower = clear_feature(lower)
        for x in tables:
            blocksworld_actions.append(
                Strips(
                    f"stack({upper},{x},{lower})",
                    preconds={on_upper: x, clear_upper: True, clear_lower: True},
                    effects={on_upper: lower, clear_feature(x): True, clear_lower: False},
                )
            )

for upper in blocks:
    for lower in blocks:
        if upper == lower:
            continue
        on_upper = f"on_{upper}"
        clear_upper = clear_feature(upper)
        clear_lower = clear_feature(lower)
        for y in tables:
            blocksworld_actions.append(
                Strips(
                    f"unstack({upper},{lower},{y})",
                    preconds={on_upper: lower, clear_upper: True, clear_feature(y): True},
                    effects={on_upper: y, clear_lower: True, clear_feature(y): False},
                )
            )

blocksworld_domain = STRIPS_domain(blocksworld_feature_domains, blocksworld_actions)

# Problem 1: wersja wymagająca co najmniej 4 akcji
bw_problem1_init = {
    "on_a": "b",
    "on_b": "t1",
    "on_c": "t2",
    "clear_a": True,
    "clear_b": False,
    "clear_c": True,
    "clear_t1": False,
    "clear_t2": False,
    "clear_t3": True,
}
bw_problem1_goal = {"on_a": "b", "on_b": "t2", "on_c": "t1"}
bw_problem1 = Planning_problem(blocksworld_domain, bw_problem1_init, bw_problem1_goal)


# Problem 2: wersja wymagająca co najmniej 4 akcji
bw_problem2_init = {
    "on_a": "t1",
    "on_b": "t2",
    "on_c": "t3",
    "clear_a": True,
    "clear_b": True,
    "clear_c": True,
    "clear_t1": False,
    "clear_t2": False,
    "clear_t3": False,
}
bw_problem2_goal = {"on_a": "b", "on_b": "c", "on_c": "t1"}
bw_problem2 = Planning_problem(blocksworld_domain, bw_problem2_init, bw_problem2_goal)

# Problem 3: wersja wymagająca co najmniej 4 akcji
bw_problem3_init = {
    "on_a": "b",
    "on_b": "c",
    "on_c": "t1",
    "clear_a": True,
    "clear_b": False,
    "clear_c": False,
    "clear_t1": False,
    "clear_t2": True,
    "clear_t3": True,
}
bw_problem3_goal = {"on_a": "b", "on_b": "c", "on_c": "t3"}
bw_problem3 = Planning_problem(blocksworld_domain, bw_problem3_init, bw_problem3_goal)


# ==========================================
# 2. ROZWIĄZYWANIE (FORWARD PLANNING)
# ==========================================

def solve_problem(problem, label):
    print(f"\n=== {label} ===")
    print("Szukam rozwiązania...")

    # Startujemy stoper
    start_time = time.time()

    search_problem = Forward_STRIPS(problem)
    searcher = AStarSearcher(search_problem)
    solution = searcher.search()

    # Zatrzymujemy stoper
    end_time = time.time()
    execution_time = end_time - start_time

    if solution:
        actions_seq = []
        current = solution
        while current.arc is not None:
            actions_seq.append(current.arc.action.name)
            current = current.initial
        actions_seq.reverse()

        print(f"Znaleziono rozwiązanie! Liczba akcji: {len(actions_seq)}")
        print(f"Czas rozwiązywania: {execution_time:.5f} sekund")
        for action_name in actions_seq:
            print(f" -> {action_name}")
    else:
        print("Nie znaleziono rozwiązania.")
        print(f"Czas rozwiązywania: {execution_time:.5f} sekund")


solve_problem(bw_problem1, "Blocksworld - Problem 1")
solve_problem(bw_problem2, "Blocksworld - Problem 2")
solve_problem(bw_problem3, "Blocksworld - Problem 3")


# ==========================================
# 3. ROZWIĄZYWANIE Z HEURYSTYKĄ I CZASEM
# ==========================================

# Tworzymy nową klasę, która uczy algorytm naszej heurystyki
class Heuristic_Forward_STRIPS(Forward_STRIPS):
    def heuristic(self, node):
        """
        Liczy, ile elementów obecnego stanu nie zgadza się z celem.
        """
        # A* przekazuje tutaj obiekt State (z polem assignment), a nie node.state.
        state = node.assignment if hasattr(node, "assignment") else node
        mismatches = 0
        # self.problem.goal to słownik z celem, np. {"on_a": "b", "on_b": "c"}
        for feature, expected_value in self.goal.items():
            if state.get(feature) != expected_value:
                mismatches += 1
        return mismatches

def solve_problem_with_heuristic(problem, label):
    print(f"\n=== {label} ===")
    print("Szukam rozwiązania (A* z heurystyką)...")
    
    # Startujemy stoper
    start_time = time.time()
    
    # Używamy naszej nowej klasy z heurystyką
    search_problem = Heuristic_Forward_STRIPS(problem)
    searcher = AStarSearcher(search_problem)
    solution = searcher.search()
    
    # Zatrzymujemy stoper
    end_time = time.time()
    execution_time = end_time - start_time

    if solution:
        actions_seq = []
        current = solution
        while current.arc is not None:
            actions_seq.append(current.arc.action.name)
            current = current.initial
        actions_seq.reverse()

        print(f"✅ Znaleziono rozwiązanie!")
        print(f"⏱️ Czas rozwiązywania: {execution_time:.5f} sekund")
        print(f"Liczba akcji: {len(actions_seq)}")
        for i, action_name in enumerate(actions_seq, 1):
            print(f" {i}. {action_name}")
    else:
        print("❌ Nie znaleziono rozwiązania.")

# Rozwiązujemy wszystkie 3 problemy, używając pomiaru czasu
solve_problem_with_heuristic(bw_problem1, "Blocksworld - Problem 1")
solve_problem_with_heuristic(bw_problem2, "Blocksworld - Problem 2")
solve_problem_with_heuristic(bw_problem3, "Blocksworld - Problem 3")
