# KickMaster NTSC-U — raport sesji 02A

Kontynuacja od zweryfikowanego checkpointu 01B. Zachowano poprzednie archiwa i wyniki.
Nie powtarzano bazowych badań źródeł ani wcześniejszych testów bez konkretnej potrzeby.
Nie korzystano z oddzielnych notatek użytkownika o adresach HP/EXP.

## Wynik sesji

- Ustalono oba źródła `$03B9`: 32 konfiguracje scen oraz 17 konfiguracji układów specjalnych.
- Odtworzono pozycje gracza i kamery, podstawy scrolla, profile IRQ i układ profilu palety/CHR.
- Wyeksportowano 192 wskaźniki scen z poprawnym rozróżnieniem banków w oknach R6 i R7.
- Odtworzono tablice 111 normalnych i 5 alternatywnych par kodów stanu/klatki gracza.
  W zwykłej rodzinie są 22 różne cele procedur; nie wszystkie są już przeanalizowane.
- Niezależnie potwierdzono bieżące HP `$06B9`, kopię paska `$06BA` i pojemność paska `$06BB`.
  Pełna komórka odpowiada 16 jednostkom wewnętrznym; kompletne leczenie i awanse pozostają otwarte.
- Prześledzono odejmowanie HP, reakcję na trafienie, śmierć, upadek i połączenie z restartem.
  Wynik dokładnie zero bez pożyczki nie wchodzi w gałąź śmierci tej procedury.

Szczegóły, adresy, diagram i ograniczenia: `reports/subsystems/PLAYER_SCENE_FOUNDATIONS.md`.

## Zakres

| Miara | Po 01B | Po 02A |
|---|---:|---:|
| Zakresy kodu | 68 | 101 |
| Zakresy danych PRG | 11 | 45 |
| Przejrzane instrukcje | 1463 | 2355 |
| Bajty PRG z lokalną interpretacją | 3444 | 6829 |
| Udział w PRG | 2,6276% | 5,2101% |
| Wpisy RAM | 56 | 80 |
| Symbole | 135 | 226 |

Nowy etap obejmuje 3385 bajtów: 1742 kodu i 1643 danych. Zakresy z wieloma wejściami oraz
tablice skoków nie są liczone jako zbiór całkowicie zrozumianych funkcji.

## Weryfikacja

18 nowych grup CPU, 10137 przypadków: **PASS**. Zapisano 5921 reprezentatywnych wierszy śladu.
Wśród testów: wszystkie 32 inicjalizacje scen, wszystkie 232 kody w obu rodzinach i kierunkach,
4096 poprawnych wejść normalizacji Y, granice odejmowania HP, pełne 90 aktualizacji śmierci
bez atrap w procedurach gracza, 2904 konfiguracje paska HP oraz 1536 próbek klasyfikacji terenu.
Tam, gdzie użyto atrap, wynik jawnie wskazuje granice testu. Testy starszych etapów zachowano.

Pełna przebudowa ca65/ld65: **PASS**, wszystkie 262160 bajtów identyczne z oryginałem.
SHA-256 ROM-u: `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
6845 bajtów jawnego źródła obejmuje nagłówek; 255315 bajtów nadal pochodzi z `.incbin`.
Audyt potwierdza spójność zakresów, instrukcji, wskaźników, 226 symboli i 198 zakresów
klasyfikujących cały plik. Graf zawiera 325 krawędzi call/jump/table.

Nie wykonano pełnej emulacji NES, obserwacji obrazu, natywnego importu MesenCE/Ghidra ani CDL.
Zgodność binarna nie dowodzi pełnego zrozumienia gry. Czasów procedur nie przeliczono na sekundy.

## Checkpoint i dalsza praca

Nowe archiwum: `kickmaster-ntscu-checkpoint-stage02A.zip`. Zawiera aktualny RESUME, źródła,
raporty, indeksy, testy, wyniki, narzędzia i manifest SHA-256. Oryginalny i przebudowany ROM
pozostają poza paczką; RESUME wskazuje oryginalny załącznik.
Końcowy hash ZIP, wynik czystej przebudowy po rozpakowaniu i ponownego odczytu zapisanej kopii
znajdują się w zewnętrznym raporcie/kwitach, aby uniknąć samoodwołania hasha archiwum.

Następnie: pozostałe procedury gracza i kolizji; zapisy HP w leczeniu; producenci indeksu
pojemności w `$D3`; powiązanie z EXP i pickupami. Wymagają też domknięcia formaty map,
wywołania PRG08:$ABC5 i PRG09:$BE90, kontrakt `$A1` z NMI oraz pełne bankowanie pętli.
