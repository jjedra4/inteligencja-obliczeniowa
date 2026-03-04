# Projekt 1 — eksperymenty AI dla gry TicTacDoh

## 1. Opis gry i modyfikacji

W projekcie użyto gry opartej na klasycznym kółko-krzyżyk (`easyAI/games/TicTacToe.py` jako punkt wyjścia), zapisanej w pliku `TicTacDoh.py`.

Reprezentacja planszy:
- plansza 3x3,
- pola numerowane od 1 do 9,
- `0` oznacza puste pole, `1` i `2` oznaczają ruchy graczy.

Warunek wygranej:
- gracz wygrywa, gdy ma trzy symbole w jednej linii (poziomo, pionowo lub na przekątnej).

Najważniejsza modyfikacja względem wariantu deterministycznego:

```python
if random.random() < 0.2 and not self.deterministic:
    return
```

Interpretacja:
- gdy `deterministic=True`, gra jest klasycznym deterministycznym kółko-krzyżyk,
- gdy `deterministic=False`, ruch może zostać pominięty z prawdopodobieństwem 20% (wariant probabilistyczny).

Dodatkowo do eksperymentów dodano:
- wielokrotne rozgrywanie meczów AI vs AI,
- naprzemienną zmianę gracza rozpoczynającego,
- zliczanie zwycięstw/remisów,
- pomiar średniego czasu wyboru ruchu (na decyzję) dla każdego AI.

## 2. Metodyka eksperymentów

Eksperymenty uruchamiane były skryptem `experiments_negamax.py`.

Porównane algorytmy:
1. **Negamax z odcięciem alfa-beta (AB)** — implementacja `easyAI.Negamax`.
2. **Negamax bez odcięcia alfa-beta (no-AB)** — własna implementacja pełnego przeglądu drzewa bez okna $[\alpha,\beta]$.

Dla każdego wariantu testowano dwie głębokości:
- `d4`,
- `d6`.

Parowania (AI-1 vs AI-2):
- AB d4 vs AB d6,
- no-AB d4 vs no-AB d6,
- AB d4 vs no-AB d4,
- AB d6 vs no-AB d6.

Dla każdego parowania wykonano:
- 60 gier w trybie deterministycznym,
- 60 gier w trybie probabilistycznym,
- z naprzemiennym starterem (`player 1` i `player 2` na zmianę).

Mierzone metryki:
- liczba zwycięstw AI-1 (`ai_1`),
- liczba zwycięstw AI-2 (`ai_2`),
- liczba remisów (`draw`),
- średni czas wyboru ruchu AI-1 (`ai_1_avg_time`),
- średni czas wyboru ruchu AI-2 (`ai_2_avg_time`).

Czasy mierzono przez `time.perf_counter()` i uśredniano po liczbie podjętych decyzji.

## 3. Wyniki eksperymentów

### 3.1. Wariant deterministyczny (`deterministic=True`)

| Parowanie | Wygrane AI-1 | Wygrane AI-2 | Remisy | Śr. czas AI-1 [s] | Śr. czas AI-2 [s] |
|---|---:|---:|---:|---:|---:|
| AB d4 vs AB d6 | 24 | 30 | 6 | 0.000398 | 0.002498 |
| no-AB d4 vs no-AB d6 | 18 | 34 | 8 | 0.003743 | 0.085181 |
| AB d4 vs no-AB d4 | 31 | 22 | 7 | 0.000391 | 0.004049 |
| AB d6 vs no-AB d6 | 33 | 20 | 7 | 0.002542 | 0.099710 |

### 3.2. Wariant probabilistyczny (`deterministic=False`)

| Parowanie | Wygrane AI-1 | Wygrane AI-2 | Remisy | Śr. czas AI-1 [s] | Śr. czas AI-2 [s] |
|---|---:|---:|---:|---:|---:|
| AB d4 vs AB d6 | 25 | 30 | 5 | 0.000430 | 0.002850 |
| no-AB d4 vs no-AB d6 | 16 | 36 | 8 | 0.004100 | 0.096141 |
| AB d4 vs no-AB d4 | 26 | 26 | 8 | 0.000380 | 0.003996 |
| AB d6 vs no-AB d6 | 29 | 27 | 4 | 0.002589 | 0.097401 |

Pełne dane zapisano też w `experiment_results.json`.

## 4. Analiza i obserwacje

### 4.1. Wpływ głębokości przeszukiwania

- W obu wariantach gry (det/prob) większa głębokość (`d6`) zwykle daje więcej zwycięstw niż `d4`.
- Przykład: no-AB d4 vs no-AB d6:
  - deterministycznie: 18 vs 34,
  - probabilistycznie: 16 vs 36.

Wniosek: nawet przy tej samej rodzinie algorytmu zwiększenie głębokości poprawia jakość decyzji.

### 4.2. Wpływ odcięcia alfa-beta

Najbardziej widoczny efekt to czas:
- dla `d6` średni czas decyzji AB to ok. `0.0025 s`,
- dla `d6` bez AB to ok. `0.097–0.100 s`.

Przyspieszenie rzędu około $\frac{0.10}{0.0025} \approx 40$ razy.

Jakość gry nie spada, a często nawet rośnie:
- AB d6 vs no-AB d6 (det): 33–20,
- AB d6 vs no-AB d6 (prob): 29–27.

Wniosek: odcięcie alfa-beta istotnie redukuje koszt obliczeń i w praktyce pozwala utrzymać mocniejszą grę w tym samym budżecie czasu.

### 4.3. Deterministyczny vs probabilistyczny wariant gry

Wariant probabilistyczny (20% pominięcia ruchu) zwiększa losowość i rozmywa przewagi strategiczne:
- część meczów staje się bardziej „chaotyczna”,
- przewaga silniejszego AI nadal jest widoczna, ale zwykle mniejsza,
- remisy i wyniki bliskie 50/50 pojawiają się częściej dla zbliżonych konfiguracji.

To zachowanie jest zgodne z intuicją: losowe pomijanie ruchu zaburza planowanie wieloetapowe.

### 4.4. Uwagi o remisie w grze deterministycznej

W klasycznym kółko-krzyżyk przy perfekcyjnej grze oczekuje się remisu. W eksperymentach przy głębokościach `d4` i `d6` nie zawsze obserwowano dominację remisów, co oznacza, że wyszukiwanie nie zawsze było „perfekcyjne” przy tych ustawieniach i implementacji punktowania.

Wniosek praktyczny do projektu: obserwacja „w deterministycznym wariancie przy odpowiednio silnym Negamaxie często pojawia się remis” jest jakościowo prawdziwa, ale w przeprowadzonych pomiarach nie wystąpiła jako reguła absolutna dla wszystkich konfiguracji.

## 5. Napotkane problemy

1. **Nadmierne logowanie „Move skipped, unlucky!”**
   - Komunikat był wypisywany wielokrotnie podczas wewnętrznych symulacji Negamax.
   - Rozwiązanie: ograniczenie wypisywania i/lub przejście na pomiary bez verbose.

2. **Interpretacja wyniku końcowego**
   - Sama funkcja `scoring` nie służy bezpośrednio do liczenia zwycięstw konkretnego AI po zakończeniu całej partii.
   - Rozwiązanie: dodano jawne `winner()` i zliczanie zwycięstw po stronie gracza 1/2.

3. **Pomiar czasu**
   - Potrzebny był pomiar „na decyzję”, a nie tylko czas całej gry.
   - Rozwiązanie: `TimedAIPlayer`, który mierzy każde `ask_move` i liczy średnią.

## 6. Podsumowanie

W projekcie porównano kilka konfiguracji Negamax (z i bez alfa-beta, przy różnych głębokościach) w dwóch wariantach gry: deterministycznym i probabilistycznym.

Najważniejsze wnioski:
- większa głębokość zwykle poprawia wyniki,
- odcięcie alfa-beta radykalnie skraca czas decyzji (w testach nawet ~40x),
- wariant probabilistyczny zmniejsza stabilność przewagi i zwiększa nieprzewidywalność wyników,
- pomiar średniego czasu decyzji jest kluczowy przy porównywaniu jakości i kosztu obliczeń.

Praktycznie najlepszy kompromis jakość/czas w tym zestawie dał **Negamax z alfa-beta** na większej głębokości.
