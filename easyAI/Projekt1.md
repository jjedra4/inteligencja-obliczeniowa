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
3. **ExpectiNegamax z odcięciem alfa-beta** — wariant uwzględniający niepewność ruchu w środowisku probabilistycznym.

W eksperymentach użyto głębokości:
- `d4`,
- `d6`,
- `d8` (w wybranych parach).

Parowania (AI-1 vs AI-2):
- AB d4 vs AB d6,
- AB d4 vs AB d8,
- no-AB d4 vs no-AB d6,
- AB d6 vs no-AB d6,
- AB d8 vs no-AB d6,
- ExpectiNegamax AB d4 vs ExpectiNegamax AB d6,
- AB d6 vs ExpectiNegamax AB d6,
- no-AB d6 vs ExpectiNegamax AB d6.

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
| AB d4 vs AB d6 | 0 | 30 | 30 | 0.000326 | 0.001764 |
| AB d4 vs AB d8 | 0 | 30 | 30 | 0.000309 | 0.007150 |
| no-AB d4 vs no-AB d6 | 0 | 30 | 30 | 0.002635 | 0.037829 |
| AB d6 vs no-AB d6 | 0 | 0 | 60 | 0.001356 | 0.033439 |
| AB d8 vs no-AB d6 | 0 | 0 | 60 | 0.006279 | 0.033446 |
| ExpectiNegamax AB d4 vs ExpectiNegamax AB d6 | 0 | 30 | 30 | 0.004240 | 0.087955 |
| AB d6 vs ExpectiNegamax AB d6 | 0 | 0 | 60 | 0.001363 | 0.077215 |
| no-AB d6 vs ExpectiNegamax AB d6 | 0 | 0 | 60 | 0.033502 | 0.077058 |

### 3.2. Wariant probabilistyczny (`deterministic=False`)

| Parowanie | Wygrane AI-1 | Wygrane AI-2 | Remisy | Śr. czas AI-1 [s] | Śr. czas AI-2 [s] |
|---|---:|---:|---:|---:|---:|
| AB d4 vs AB d6 | 23 | 34 | 3 | 0.000441 | 0.002848 |
| AB d4 vs AB d8 | 28 | 26 | 6 | 0.000424 | 0.013366 |
| no-AB d4 vs no-AB d6 | 22 | 28 | 10 | 0.003780 | 0.083292 |
| AB d6 vs no-AB d6 | 32 | 23 | 5 | 0.002499 | 0.094324 |
| AB d8 vs no-AB d6 | 32 | 21 | 7 | 0.013106 | 0.099731 |
| ExpectiNegamax AB d4 vs ExpectiNegamax AB d6 | 29 | 24 | 7 | 0.011853 | 0.441030 |
| AB d6 vs ExpectiNegamax AB d6 | 28 | 28 | 4 | 0.002903 | 0.462852 |
| no-AB d6 vs ExpectiNegamax AB d6 | 15 | 43 | 2 | 0.114227 | 0.449909 |

Pełne dane zapisano też w `experiment_results.json`.

## 4. Analiza i obserwacje

### 4.1. Wpływ głębokości przeszukiwania

- W wariancie deterministycznym większa głębokość daje przewagę bardzo wyraźną: w parach AB i no-AB konfiguracja głębsza wygrywa wszystkie partie nieremisowe (np. AB d4 vs AB d6: `0-30-30`, AB d4 vs AB d8: `0-30-30`).
- W wariancie probabilistycznym trend jest słabszy i zależny od konkretnej pary: AB d6 dominuje AB d4 (`34` wygrane vs `23`), ale AB d8 nie jest już jednoznacznie lepsze od AB d4 (`26` vs `28`).

Wniosek: większa głębokość poprawia jakość gry głównie tam, gdzie losowość nie zaburza planowania; w środowisku probabilistycznym zysk z dalszego pogłębiania może maleć.

### 4.2. Wpływ odcięcia alfa-beta

Najbardziej widoczny efekt to czas:
- dla `d6` średni czas decyzji AB to ok. `0.0014–0.0029 s`,
- dla `d6` bez AB to ok. `0.033–0.114 s`.

Przyspieszenie jest rzędu od kilkunastu do kilkudziesięciu razy (w zależności od parowania i trybu gry).

Jakość gry nie spada, a często nawet rośnie:
- AB d6 vs no-AB d6 (det): `0-0-60` (jakość porównywalna przy perfekcyjnym przebiegu),
- AB d6 vs no-AB d6 (prob): `32-23-5` na korzyść AB.

Wniosek: odcięcie alfa-beta istotnie redukuje koszt obliczeń i w praktyce pozwala utrzymać mocniejszą grę w tym samym budżecie czasu.

### 4.3. Deterministyczny vs probabilistyczny wariant gry

Wariant probabilistyczny (20% pominięcia ruchu) zwiększa losowość i rozmywa przewagi strategiczne:
- część meczów staje się bardziej „chaotyczna”,
- przewaga silniejszego AI nadal jest widoczna, ale zwykle mniejsza,
- remisy maleją względem wariantu deterministycznego (z `30-60` remisów do nawet `2-10`), a wyniki częściej kończą się zwycięstwem jednej ze stron.

To zachowanie jest zgodne z intuicją: losowe pomijanie ruchu zaburza planowanie wieloetapowe.

### 4.4. Uwagi o remisie w grze deterministycznej

W rozszerzonym zestawie wyników deterministycznych remis dominuje: w wielu parach występuje `60/60` remisów, a pozostałe mają układ `30` remisów i `30` wygranych mocniejszej konfiguracji. To sugeruje stabilną, „szachową” naturę gry przy braku losowości i wystarczająco mocnym przeszukiwaniu.

Wniosek praktyczny: przy grze deterministycznej różnice algorytmiczne najczęściej ujawniają się jako przewaga przy słabszym przeciwniku lub płytszym przeszukiwaniu, ale górny pułap jakości często prowadzi do remisu.

### 4.5. Dodatkowe obserwacje o ExpectiNegamax

- `ExpectiNegamax` ma najwyższy koszt obliczeń w całym zestawie: w trybie probabilistycznym `~0.441-0.463 s` na ruch dla `d6`.
- W bezpośrednim starciu AB d6 vs ExpectiNegamax d6 (prob) wynik jest `28-28-4`, czyli jakość końcowa porównywalna, ale uzyskana wielokrotnie większym kosztem czasu po stronie ExpectiNegamax.
- ExpectiNegamax wyraźnie wygrywa z no-AB d6 w trybie probabilistycznym (`43-15-2`), co sugeruje, że modelowanie niepewności opłaca się szczególnie wtedy, gdy przeciwnik nie używa efektywnego przycinania.

Wniosek: ExpectiNegamax może być dobrym wyborem jakościowym w środowisku losowym, ale jego koszt czasowy jest bardzo wysoki i wymaga większego budżetu obliczeniowego.

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
- większa głębokość zwykle pomaga, ale w trybie probabilistycznym zysk z dalszego pogłębiania nie zawsze rośnie monotonicznie,
- odcięcie alfa-beta daje duże przyspieszenie (od kilkunastu do kilkudziesięciu razy) przy jakości co najmniej porównywalnej,
- losowość (`20%` pominięcia ruchu) znacząco zmienia rozkład wyników: mniej remisów, więcej partii rozstrzygniętych,
- `ExpectiNegamax` bywa bardzo skuteczny wobec wolniejszych konfiguracji no-AB, ale jest zdecydowanie najdroższy czasowo,
- pomiar średniego czasu decyzji jest kluczowy przy porównywaniu jakości i kosztu obliczeń.

Praktycznie najlepszy kompromis jakość/czas w tym zestawie daje **Negamax z alfa-beta** (`d6` lub `d8` zależnie od budżetu czasu), natomiast **ExpectiNegamax** warto rozważać, gdy priorytetem jest jakość w środowisku probabilistycznym i dostępny jest większy czas na ruch.
