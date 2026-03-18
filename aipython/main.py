from stripsProblem import Strips, STRIPS_domain, Planning_problem
from stripsForwardPlanner import Forward_STRIPS
from searchGeneric import AStarSearcher

# ==========================================
# 1. DEFINICJA DZIEDZINY (MAGIC WORLD)
# ==========================================

magic_actions = [
    # --- RUCH ---
    Strips('move(town, forest)', preconds={'loc': 'town', 'guarded_forest': False}, effects={'loc': 'forest'}),
    Strips('move(forest, cave)', preconds={'loc': 'forest', 'guarded_cave': False}, effects={'loc': 'cave'}),
    Strips('move(cave, mountain)', preconds={'loc': 'cave', 'guarded_mountain': False}, effects={'loc': 'mountain'}),
    Strips('move(mountain, castle)', preconds={'loc': 'mountain', 'guarded_castle': False}, effects={'loc': 'castle'}),
    
    # --- INTERAKCJE ZE SKRZYNIAMI ---
    # Skrzynia w lesie (Ogień)
    Strips('open_chest_forest', preconds={'loc': 'forest', 'chest_forest_open': False}, effects={'chest_forest_open': True}),
    Strips('collect_fire',
           preconds={'loc': 'forest', 'chest_forest_open': True, 'chest_forest_empty': False}, 
           effects={'chest_forest_empty': True, 'has_fire': True}),
           
    # Skrzynia w jaskini (Ziemia)
    Strips('open_chest_cave', preconds={'loc': 'cave', 'chest_cave_open': False}, effects={'chest_cave_open': True}),
    Strips('collect_earth',
           preconds={'loc': 'cave', 'chest_cave_open': True, 'chest_cave_empty': False}, 
           effects={'chest_cave_empty': True, 'has_earth': True}),
           
    # --- CRAFTING ---
    Strips('build_fireball',
           preconds={'has_fire': True, 'has_earth': True}, 
           effects={'has_fireball': True, 'has_fire': False, 'has_earth': False}),
           
    # --- WALKA ---
    # Atakujemy potwora na górze stojąc w jaskini (wymaga kuli ognia!)
    Strips('attack_mountain_monster',
           preconds={'loc': 'cave', 'has_fireball': True, 'guarded_mountain': True}, 
           effects={'guarded_mountain': False, 'has_fireball': False})
]

boolean = {False, True}
magic_feature_domains = {
    'loc': {'town', 'forest', 'cave', 'mountain', 'castle'},
    'guarded_forest': boolean,
    'guarded_cave': boolean,
    'guarded_mountain': boolean,
    'guarded_castle': boolean,
    'chest_forest_open': boolean,
    'chest_forest_empty': boolean,
    'chest_cave_open': boolean,
    'chest_cave_empty': boolean,
    'has_fire': boolean,
    'has_earth': boolean,
    'has_fireball': boolean,
}
magic_domain = STRIPS_domain(magic_feature_domains, magic_actions)


# ==========================================
# 2. DEFINICJA PROBLEMU (EPIC QUEST)
# ==========================================
# Cel: Dojść do zamku. Problem polega na tym, że droga przez góry jest
# zablokowana przez potwora. Robot musi zebrać żywioły, zrobić broń i zabić potwora.

init_state = {
    'loc': 'town',
    'guarded_forest': False,
    'guarded_cave': False,
    'guarded_mountain': True,  # POTWÓR BLOKUJE DROGĘ!
    'guarded_castle': False,
    'chest_forest_open': False,
    'chest_forest_empty': False,
    'chest_cave_open': False,
    'chest_cave_empty': False,
    'has_fire': False,
    'has_earth': False,
    'has_fireball': False
}

goal_state = {'loc': 'castle'}

problem1 = Planning_problem(magic_domain, init_state, goal_state)


# ==========================================
# 3. ROZWIĄZYWANIE (FORWARD PLANNING)
# ==========================================

# Konwertujemy problem STRIPS na problem przeszukiwania grafu (Forward Planning)
search_problem = Forward_STRIPS(problem1)

# Używamy A* Search (lub podstawowego Searcher), aby znaleźć ścieżkę
print("Szukam rozwiązania. Może to potrwać kilka sekund...")
searcher = AStarSearcher(search_problem)
solution = searcher.search()

if solution:
    actions = []
    current = solution
    while current.arc is not None:
        actions.append(current.arc.action.name)
        current = current.initial
    actions.reverse()

    print(f"\nZnaleziono rozwiązanie! Liczba akcji: {len(actions)}")
    print("Sekwencja akcji:")
    for action_name in actions:
        print(f" -> {action_name}")
else:
    print("Nie znaleziono rozwiązania w zadanym czasie.")