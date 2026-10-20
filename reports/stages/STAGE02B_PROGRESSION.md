# Etap 02B — postęp, przedmioty i leczenie

Zamknięty zakres etapu: cyfrowe liczniki EXP/MP/wyniku, awans, dwa efekty leczące,
zbieranie przedmiotów, dodatkowe próby i snapshot postępu. Cały projekt pozostaje otwarty.

- Szczegółowa dokumentacja: `../subsystems/PROGRESSION_PICKUPS_MAGIC.md`.
- Nowe zakresy: D01–D42 w `analysis/reviewed_ranges.csv`, 700 instrukcji i 1729 bajtów.
- Dane: `progression_levels.csv`, `pickup_effects.csv`, `selected_spell_dispatch.csv`,
  `score_thresholds.csv`, `numeric_formats.csv`, `progression_snapshot_layout.csv`.
- Dowody CPU: `cpu_stage02B.json`, `cpu_stage02B_vectors.csv`, `cpu_stage02B_trace.csv`.
- Generatory: `scripts/architecture_stage02b.py`, `scripts/cpu_stage02b.py`.
- Zbiorczy raport zamknięcia: `SESSION_REPORT.md`; stan do wznowienia: `RESUME.md` w katalogu głównym.

16 grup / 52382 przypadki / 9976 wierszy śladu: PASS. Brak atrap podprogramów;
testy samych dispatcherów jawnie kończą się przed ich docelowymi handlerami.
Cały odbudowany obraz 262160 bajtów jest identyczny z oryginałem, z zachowaniem
wymogu oryginalnego wejścia dla pozostałych `.incbin`.
