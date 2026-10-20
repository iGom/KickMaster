# Etap 02C — trwałość 02B, źródła i sterowanie magią

Zamknięto lokalny zakres zdobywania/wyboru magii, aktywacji pozostałych dziesięciu
czarów oraz wybranych faz ich kontrolerów. Cały system walki i cała rekonstrukcja gry
pozostają otwarte.

- Szczegóły: `reports/subsystems/MAGIC_ACQUISITION_AND_EFFECTS.md`.
- Nowe zakresy: E01–E51, 875 instrukcji, 2260 bajtów PRG.
- Nowe dane: `magic_unlock_menu_map.csv`, `magic_acquisition_scene_routes.csv`,
  `magic_description_pointers.csv`, `magic_aim_and_velocity.csv`.
- Testy: 18 grup, 16460 przypadków, 5906 wierszy śladu, wszystkie PASS.
- Pełna odbudowa obrazu: 262160 bajtów identycznych z dostarczonym ROM-em.
- Źródła użytkownika: oryginalny poradnik, maps.zip oraz osiem PNG, bez zmian bajtów.
- Brakujące trzy raporty 02B zapisano i odczytano ponownie; kopia archiwum 02B była poprawna
  i nie została ponownie przesłana. Dowody są w `manifests/stage02B*.json`.

Raport końcowy bieżącej sesji: `reports/stages/SESSION_REPORT.md`; wznowienie: `RESUME.md`.
Nie wykonywano ponownie wcześniejszych zestawów CPU ani całego etapu 00A.
