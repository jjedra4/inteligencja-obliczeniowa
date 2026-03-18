# Sprawozdanie: STRIPS (Blocksworld) — forward planning, heurystyka, podcele

## Cel ćwiczenia

Zdefiniowanie dziedziny STRIPS oraz trzech przykładowych problemów (o przestrzeni stanów co najmniej 50), a następnie:

- rozwiązanie metodą **forward planning**,
- zaproponowanie i użycie **heurystyki** (wymagane: znalezienie rozwiązania),
- zdefiniowanie **podcelów** (min. 2 na problem) i ponowne rozwiązanie z podcelami:
  - bez heurystyki,
  - z heurystyką,
- zestawienie rozwiązań (ciągów akcji) i czasów.

Implementacja znajduje się w `aipython/main.py`, a wyniki wykonania w logu terminala.

---

## 1) Dziedzina STRIPS i problemy

### Dziedzina: Blocksworld (STRIPS)

Wykorzystano dziedzinę **Blocksworld** z trzema klockami `a,b,c` i trzema stołami `t1,t2,t3`.

- **Cechy stanu** (przykładowo):
  - `on_a`, `on_b`, `on_c` — położenie klocka (na innym klocku lub na stole),
  - `clear_a`, `clear_b`, `clear_c`, `clear_t1`, `clear_t2`, `clear_t3` — czy dana powierzchnia jest wolna.
- **Akcje STRIPS**:
  - `move(b, x, y)` — przesunięcie klocka `b` ze stołu `x` na stół `y`,
  - `stack(upper, x, lower)` — położenie `upper` (ze stołu `x`) na `lower`,
  - `unstack(upper, lower, y)` — zdjęcie `upper` z `lower` na stół `y`.

Dziedzina została zdefiniowana jako `STRIPS_domain(...)`, a problemy jako `Planning_problem(...)`.

### Uwaga o liczbie stanów

Dla 3 klocków i 3 stołów liczba możliwych konfiguracji (osiągalnych stanów) jest **zdecydowanie większa niż 50**.
Dodatkowo w logach uruchomienia widać, że algorytm rozwija setki/tysiące ścieżek (np. `paths expanded` rzędu 400–1400), co potwierdza nietrywialną przestrzeń przeszukiwania.

### Problemy

Każdy z problemów ma rozwiązanie składające się z co najmniej 4 akcji.

#### Problem 1

- **Start**: `on_a=b, on_b=t1, on_c=t2`
- **Cel**: `on_a=b, on_b=t2, on_c=t1`

#### Problem 2

- **Start**: `on_a=t1, on_b=t2, on_c=t3`
- **Cel**: `on_a=b, on_b=c, on_c=t1`

#### Problem 3

- **Start**: `on_a=b, on_b=c, on_c=t1`
- **Cel**: `on_a=b, on_b=c, on_c=t3`

---

## 2) Rozwiązywanie metodą forward planning (bez heurystyki)

Zastosowano forward planning przez `Forward_STRIPS(problem)` oraz przeszukiwanie A* (`AStarSearcher`).

### Znalezione rozwiązania (ciągi akcji)

#### Problem 1 (5 akcji)

1. `unstack(a,b,t3)`
2. `stack(b,t1,a)`
3. `move(c,t2,t1)`
4. `unstack(b,a,t2)`
5. `stack(a,t3,b)`

#### Problem 2 (5 akcji)

1. `stack(c,t3,b)`
2. `move(a,t1,t3)`
3. `unstack(c,b,t1)`
4. `stack(b,t2,c)`
5. `stack(a,t3,b)`

#### Problem 3 (7 akcji)

1. `unstack(a,b,t2)`
2. `unstack(b,c,t3)`
3. `stack(c,t1,a)`
4. `move(b,t3,t1)`
5. `unstack(c,a,t3)`
6. `stack(b,t1,c)`
7. `stack(a,t2,b)`

---

## 3) Heurystyka

### Definicja heurystyki

Zastosowano heurystykę:

$$
h(s) = \left|\left\{(f \rightarrow v)\in \text{cel} : s[f] \neq v\right\}\right|
$$

czyli **liczbę niedopasowanych cech celu** (ile warunków celu nie jest spełnionych w aktualnym stanie).

### Dlaczego ta heurystyka jest pomocna?

- Preferuje stany, które mają **więcej spełnionych warunków celu**.
- Zwykle zmniejsza liczbę niepotrzebnie eksplorowanych ścieżek i szybciej kieruje A* w stronę stanów obiecujących.

### Rozwiązania z heurystyką (ciągi akcji)

Wszystkie 3 problemy zostały rozwiązane z heurystyką. Przykładowe ciągi z logów:

#### Problem 1 (5 akcji)

1. `unstack(a,b,t3)`
2. `stack(c,t2,a)`
3. `move(b,t1,t2)`
4. `unstack(c,a,t1)`
5. `stack(a,t3,b)`

#### Problem 2 (5 akcji)

1. `stack(c,t3,b)`
2. `move(a,t1,t3)`
3. `unstack(c,b,t1)`
4. `stack(b,t2,c)`
5. `stack(a,t3,b)`

#### Problem 3 (7 akcji)

1. `unstack(a,b,t3)`
2. `unstack(b,c,t2)`
3. `stack(c,t1,b)`
4. `move(a,t3,t1)`
5. `unstack(c,b,t3)`
6. `stack(b,t2,c)`
7. `stack(a,t1,b)`

---

## 4) Podcele (zadania na 6 punktów)

Zastosowano strategię podcelów: problem jest rozwiązywany etapami. Po osiągnięciu podcelu stan jest aktualizowany efektami wykonanych akcji i rozwiązywany jest kolejny etap.

### Podcele

#### Problem 1

- Podcel 1: `{'on_c': 't1'}`
- Podcel 2: `{'on_b': 't2', 'on_c': 't1'}`
- Cel końcowy: `{'on_a': 'b', 'on_b': 't2', 'on_c': 't1'}`

#### Problem 2

- Podcel 1: `{'on_c': 't1'}`
- Podcel 2: `{'on_b': 'c', 'on_c': 't1'}`
- Cel końcowy: `{'on_a': 'b', 'on_b': 'c', 'on_c': 't1'}`

#### Problem 3

- Podcel 1: `{'on_c': 't3'}`
- Podcel 2: `{'on_b': 'c', 'on_c': 't3'}`
- Cel końcowy: `{'on_a': 'b', 'on_b': 'c', 'on_c': 't3'}`

---

## 5) Czasy wykonania

Poniżej zestawienie czasów (na podstawie podsumowania z logów uruchomienia).

| Tryb | Problem 1 | Problem 2 | Problem 3 |
|---|---:|---:|---:|
| Bez heurystyki (bez podcelów) | 0.06824 s | 0.06148 s | 0.52445 s |
| Z heurystyką (bez podcelów) | 0.00073 s | 0.00197 s | 0.01071 s |
| Z podcelami, bez heurystyki | 0.00235 s | 0.00066 s | 0.00299 s |
| Z podcelami, z heurystyką | 0.00046 s | 0.00046 s | 0.00072 s |

Dodatkowo (z logów):

- **Suma czasów (udane)**: 0.67522 s
- **Średni czas (udane)**: 0.05627 s

---

## 6) Wnioski i „sprawdzenie” wymagań

- **Dziedzina STRIPS + 3 problemy**: wykonane (Blocksworld).
- **Co najmniej 50 stanów**: spełnione dla tej dziedziny (duża przestrzeń stanów; potwierdzona liczbą rozwinięć w logach).
- **Forward planning**: wykonane (`Forward_STRIPS` + A*).
- **Minimum 4 akcje w rozwiązaniu**: spełnione (5/5/7).
- **Heurystyka + rozwiązanie znalezione**: wykonane (wszystkie 3 rozwiązane; czasy zebrane).
- **Podcele (min. 2) + rozwiązanie z podcelami (bez i z heurystyką)**: wykonane (dla wszystkich 3).

