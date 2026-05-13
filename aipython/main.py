from stripsProblem import Strips, STRIPS_domain, Planning_problem
from stripsForwardPlanner import Forward_STRIPS
from searchGeneric import AStarSearcher
import time

boolean = {False, True}
timing_results = []

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

    timing_results.append(
        {
            "section": "Bez heurystyki (bez podcelów)",
            "problem": label,
            "time": execution_time,
            "solved": solution is not None,
        }
    )


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

    timing_results.append(
        {
            "section": "Z heurystyką (bez podcelów)",
            "problem": label,
            "time": execution_time,
            "solved": solution is not None,
        }
    )

# Rozwiązujemy wszystkie 3 problemy, używając pomiaru czasu
solve_problem_with_heuristic(bw_problem1, "Blocksworld - Problem 1")
solve_problem_with_heuristic(bw_problem2, "Blocksworld - Problem 2")
solve_problem_with_heuristic(bw_problem3, "Blocksworld - Problem 3")


# ==========================================
# 4. ROZWIĄZYWANIE Z PODCELAMI
# ==========================================


def apply_actions(current_state, actions_sequence):
    """Pomocnicza funkcja aktualizująca stan planszy po wykonaniu serii akcji z podcelu."""
    new_state = current_state.copy()
    for action in actions_sequence:
        new_state.update(action.effects)
    return new_state

def solve_with_subgoals(domain, init_state, subgoals, label, use_heuristic=False):
    print(f"\n{'='*40}")
    print(f"=== {label} | Heurystyka: {'TAK' if use_heuristic else 'NIE'} ===")
    print(f"{'='*40}")
    
    current_state = init_state.copy()
    total_actions_names = []
    total_time = 0.0
    
    for i, subgoal in enumerate(subgoals, 1):
        # Ostatni element to cel końcowy
        step_name = "Cel końcowy" if i == len(subgoals) else f"Podcel {i}"
        print(f"-> Szukam rozwiązania dla: {step_name} {subgoal}")
        
        problem = Planning_problem(domain, current_state, subgoal)
        
        start_time = time.time()
        if use_heuristic:
            search_problem = Heuristic_Forward_STRIPS(problem)
        else:
            search_problem = Forward_STRIPS(problem)
            
        searcher = AStarSearcher(search_problem)
        solution = searcher.search()
        end_time = time.time()
        
        total_time += (end_time - start_time)
        
        if solution:
            # Odzyskiwanie akcji dla tego etapu
            step_actions = []
            current = solution
            while current.arc is not None:
                step_actions.append(current.arc.action)
                current = current.initial
            step_actions.reverse()
            
            # Dodawanie nazw akcji do ogólnej puli i aktualizacja stanu na planszy
            total_actions_names.extend([a.name for a in step_actions])
            current_state = apply_actions(current_state, step_actions)
        else:
            print(f"❌ Nie udało się osiągnąć: {step_name}")
            timing_results.append(
                {
                    "section": "Z podcelami",
                    "problem": label,
                    "mode": "Z heurystyką" if use_heuristic else "Bez heurystyki",
                    "time": total_time,
                    "solved": False,
                }
            )
            return
            
    print(f"\n✅ ROZWIĄZANO CAŁY PROBLEM Z PODCELAMI!")
    print(f"⏱️ Całkowity czas: {total_time:.5f} sekund")
    print(f"Liczba akcji łącznie: {len(total_actions_names)}")
    for i, a_name in enumerate(total_actions_names, 1):
        print(f" {i}. {a_name}")

    timing_results.append(
        {
            "section": "Z podcelami",
            "problem": label,
            "mode": "Z heurystyką" if use_heuristic else "Bez heurystyki",
            "time": total_time,
            "solved": True,
        }
    )


def print_time_summary():
    print("\n\n" + "=" * 60)
    print("PODSUMOWANIE CZASÓW")
    print("=" * 60)

    for result in timing_results:
        mode = result.get("mode", "-")
        status = "OK" if result["solved"] else "BRAK ROZWIĄZANIA"
        print(
            f"[{result['section']}] {result['problem']} | tryb: {mode} | "
            f"czas: {result['time']:.5f}s | status: {status}"
        )

    solved_times = [r["time"] for r in timing_results if r["solved"]]
    if solved_times:
        print("-" * 60)
        print(f"Suma czasów (udane): {sum(solved_times):.5f}s")
        print(f"Średni czas (udane): {sum(solved_times) / len(solved_times):.5f}s")


# ==========================================
# DEFINICJE LIST PODCELÓW DLA KAŻDEGO PROBLEMU
# ==========================================

p1_subgoals = [
    {"on_c": "t1"},                                  # Podcel 1
    {"on_b": "t2", "on_c": "t1"},                    # Podcel 2
    {"on_a": "b", "on_b": "t2", "on_c": "t1"}        # Cel ostateczny
]

p2_subgoals = [
    {"on_c": "t1"},                                  # Podcel 1
    {"on_b": "c", "on_c": "t1"},                     # Podcel 2
    {"on_a": "b", "on_b": "c", "on_c": "t1"}         # Cel ostateczny
]

p3_subgoals = [
    {"on_c": "t3"},                                  # Podcel 1
    {"on_b": "c", "on_c": "t3"},                     # Podcel 2
    {"on_a": "b", "on_b": "c", "on_c": "t3"}         # Cel ostateczny
]

# ==========================================
# URUCHOMIENIE TESTÓW (BEZ HEURYSTYKI I Z HEURYSTYKĄ)
# ==========================================

print("\n\n" + "#"*50 + "\nROZWIĄZYWANIE BEZ HEURYSTYKI (Z PODCELAMI)\n" + "#"*50)
solve_with_subgoals(blocksworld_domain, bw_problem1_init, p1_subgoals, "Problem 1", use_heuristic=False)
solve_with_subgoals(blocksworld_domain, bw_problem2_init, p2_subgoals, "Problem 2", use_heuristic=False)
solve_with_subgoals(blocksworld_domain, bw_problem3_init, p3_subgoals, "Problem 3", use_heuristic=False)

print("\n\n" + "#"*50 + "\nROZWIĄZYWANIE Z HEURYSTYKĄ (Z PODCELAMI)\n" + "#"*50)
solve_with_subgoals(blocksworld_domain, bw_problem1_init, p1_subgoals, "Problem 1", use_heuristic=True)
solve_with_subgoals(blocksworld_domain, bw_problem2_init, p2_subgoals, "Problem 2", use_heuristic=True)
solve_with_subgoals(blocksworld_domain, bw_problem3_init, p3_subgoals, "Problem 3", use_heuristic=True)

# ==========================================
# 8 PUNKTÓW: 3 DODATKOWE PROBLEMY Z PODCELAMI (>=20 AKCJI)
# ==========================================

blocks_8 = ["a", "b", "c", "d"]
tables_8 = ["t1", "t2", "t3"]
surfaces_8 = set(blocks_8) | set(tables_8)

blocksworld8_feature_domains = {
    "on_a": surfaces_8 - {"a"},
    "on_b": surfaces_8 - {"b"},
    "on_c": surfaces_8 - {"c"},
    "on_d": surfaces_8 - {"d"},
    "clear_a": boolean,
    "clear_b": boolean,
    "clear_c": boolean,
    "clear_d": boolean,
    "clear_t1": boolean,
    "clear_t2": boolean,
    "clear_t3": boolean,
}

blocksworld8_actions = []

for b in blocks_8:
    on_b = f"on_{b}"
    clear_b = clear_feature(b)
    for x in tables_8:
        for y in tables_8:
            if x == y:
                continue
            blocksworld8_actions.append(
                Strips(
                    f"move({b},{x},{y})",
                    preconds={on_b: x, clear_b: True, clear_feature(y): True},
                    effects={on_b: y, clear_feature(x): True, clear_feature(y): False},
                )
            )

for upper in blocks_8:
    for lower in blocks_8:
        if upper == lower:
            continue
        on_upper = f"on_{upper}"
        clear_upper = clear_feature(upper)
        clear_lower = clear_feature(lower)
        for x in tables_8:
            blocksworld8_actions.append(
                Strips(
                    f"stack({upper},{x},{lower})",
                    preconds={on_upper: x, clear_upper: True, clear_lower: True},
                    effects={on_upper: lower, clear_feature(x): True, clear_lower: False},
                )
            )

for upper in blocks_8:
    for lower in blocks_8:
        if upper == lower:
            continue
        on_upper = f"on_{upper}"
        clear_upper = clear_feature(upper)
        clear_lower = clear_feature(lower)
        for y in tables_8:
            blocksworld8_actions.append(
                Strips(
                    f"unstack({upper},{lower},{y})",
                    preconds={on_upper: lower, clear_upper: True, clear_feature(y): True},
                    effects={on_upper: y, clear_lower: True, clear_feature(y): False},
                )
            )

blocksworld8_domain = STRIPS_domain(blocksworld8_feature_domains, blocksworld8_actions)

bw8_init = {
    "on_a": "t1",
    "on_b": "a",
    "on_c": "b",
    "on_d": "c",
    "clear_a": False,
    "clear_b": False,
    "clear_c": False,
    "clear_d": True,
    "clear_t1": False,
    "clear_t2": True,
    "clear_t3": True,
}

p8_1_subgoals = [
    {"on_d": "t2"},
    {"on_c": "d"},
    {"on_b": "t1"},
    {"on_a": "b"},
    {"on_d": "t3"},
    {"on_c": "t1"},
    {"on_b": "c"},
    {"on_a": "d"},
]

p8_2_subgoals = [
    {"on_d": "t3"},
    {"on_c": "t2"},
    {"on_b": "d"},
    {"on_a": "t3"},
    {"on_d": "a"},
    {"on_c": "b"},
    {"on_b": "t1"},
    {"on_a": "c"},
]

p8_3_subgoals = [
    {"on_a": "c"},
    {"on_a": "b"},
    {"on_a": "d"},
    {"on_b": "a"},
    {"on_b": "c"},
    {"on_c": "t2"},
    {"on_d": "b"},
    {"on_a": "b"},
]

print("\n\n" + "#" * 50 + "\nZADANIA NA 8 PUNKTÓW (DODATKOWE PROBLEMY)\n" + "#" * 50)
print("Uruchomienie wariantu z podcelami i heurystyką dla 4 klocków.")
solve_with_subgoals(blocksworld8_domain, bw8_init, p8_1_subgoals, "Problem 8.1", use_heuristic=True)
solve_with_subgoals(blocksworld8_domain, bw8_init, p8_2_subgoals, "Problem 8.2", use_heuristic=True)
solve_with_subgoals(blocksworld8_domain, bw8_init, p8_3_subgoals, "Problem 8.3", use_heuristic=True)

print_time_summary()
