# KickMaster NTSC-U — raport sesji 02B

Data: 2026-10-20. Ukończono ograniczony etap postępu postaci, zbierania przedmiotów
i dwóch zaklęć leczących. Całościowa rekonstrukcja gry trwa.

## Najważniejsze ustalenia

- EXP, bieżące MP i maksymalne MP są cyframi dziesiętnymi w osobnych bajtach,
  z przesunięciem 60 hex; RAM przechowuje najmniej znaczącą cyfrę najpierw.
  Bieżące MP zajmuje $EA–$EC, EXP $ED–$F0, następny próg $F1–$F4, maksymalne MP $F5–$F7.
- Awans aktualizuje maksymalne HP/MP oraz następny próg, ale nie uzupełnia bieżących
  HP ani MP. Następuje najwyżej jeden awans na zebranie przedmiotu.
  Ostatni próg EXP w tabeli to 9999 dziesiętnie; poziom kończy się na 7.
- Dwa prześledzone efekty leczą 2 lub 4 komórki HP, za odpowiednio 60 lub 90 MP.
  Koszt jest pobierany także przy pełnym HP. Nieudane odjęcie MP przywraca licznik.
- Odtwarzanie snapshotu najpierw kopiuje zapisane HP, potem nadpisuje je pełną
  wartością z tabeli poziomu. Ta procedura nie aktualizuje $06BB i nie ogranicza
  bieżącego MP do maksimum; nie uogólniamy tego na wszystkie warianty continue/hasła.
- Wynik punktowy używa sześciu cyfr z przesunięciem 20 hex. Progi dodatkowych prób
  wynoszą 10000, 50000, 100000, 200000, 500000 i 999999 dziesiętnie.
  HUD wyświetla liczbę prób o jeden mniejszą niż $030E.
- Powstały kompletne mapowania 24 par typów przedmiotów i 13 wyborów zaklęcia.
  To mapowania wskaźników; 12 par przedmiotów prowadzących do $A7DB oraz większość
  efektów magicznych nadal nie mają zatwierdzonej pełnej semantyki.

Szczegóły, warunki wejściowe, odstępstwa przy sztucznych stanach i źródła kodowe:
`reports/subsystems/PROGRESSION_PICKUPS_MAGIC.md`.

## Przyrost projektu

| Miara | Po 02A | Po 02B |
|---|---:|---:|
| Zakresy kodu | 101 | 134 |
| Zakresy danych PRG | 45 | 54 |
| Przejrzane instrukcje | 2355 | 3055 |
| Bajty kodu PRG | 5020 | 6484 |
| Bajty danych PRG | 1809 | 2074 |
| Suma bajtów PRG z lokalną interpretacją | 6829 | 8558 |
| Odsetek PRG | 5,2101% | 6,5292% |
| Wpisy RAM | 80 | 101 |
| Symbole | 226 | 289 |
| Krawędzie pośrednich tabel | 138 | 180 |
| Krawędzie grafu call/jump/table | 325 | 386 |

Nowa seria D01–D42 wnosi 1729 bajtów i 700 instrukcji. Historyczne dekodowanie
kandydatów nie liczy się do pokrycia semantycznego. CHR nadal nie ma pełnej interpretacji.

## Weryfikacja

Nowe testy CPU: 16 grup, 52382 przypadki, 9976 wierszy śladu; wszystkie PASS.
Obejmują pełne domeny liczbowe EXP i poprawnych MP, przeniesienia, cofnięcie wydatku,
progi awansu/wyniku, granice prostokąta i prędkości podnoszenia, bramki i SP,
sloty efektu poziomu oraz snapshot. Integracja leczenia przechodzi przez rzeczywisty
wybór efektu, pętlę obiektów i rysowanie. Nie użyto atrap wywoływanych podprogramów.
Osobne próby dispatcherów zatrzymują się przed handlerem, co jest zapisane w ich wynikach.

Starsze testy 01A (57), 01B (18 grup/2295 przypadków) i 02A (18 grup/10137 przypadków)
zachowano bez ponownego wykonywania. Nie uruchamiano pełnego emulatora NES.

Odbudowa źródeł ca65/ld65 daje dokładnie oryginalne 262160 bajtów:
SHA-256 `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Jawne źródło obejmuje 8574 bajty z nagłówkiem; 253586 bajtów pochodzi nadal z `.incbin`.
Zgodność całego obrazu nie dowodzi pełnej rekonstrukcji semantycznej.

Audyt PASS: bajty i granice kodu, pokrycie, symbole, klasyfikacja całego pliku,
wcześniejsze 192 wskaźniki scen i 116 par stanów, nowe tabele oraz pliki dowodowe.
289 etykiet MLB ma sprawdzoną składnię; import w MesenCE/Ghidra pozostaje NIEPRZETESTOWANY.

## Wznowienie i checkpoint

Na początku sesji ponownie pobrano etap 02A wskazany identyfikatorem
`libfile_66e039ad85b08191b3f07f153c6f0afa`. Hash archiwum oraz 159 plików manifestu
były poprawne. Wszystkie 159 lokalnych plików odpowiadało archiwum; wykorzystano
istniejący projekt. Oryginalny identyfikator wcześniejszego zapisu 02A zachowano osobno.
Poprzednich archiwów 00, 00A, 01A, 01B i 02A nie nadpisano.

Nowe archiwum to `kickmaster-ntscu-checkpoint-stage02B.zip`. Zawiera źródła, dane,
raporty, narzędzia i `RESUME.md`; nie zawiera oryginalnego ani odbudowanego ROM-u.
Manifest obejmuje każdy zawarty plik poza sobą samym.
Hash gotowego ZIP-u, wynik czystej odbudowy oraz potwierdzenie ponownego odczytu
po zapisie znajdują się w zewnętrznym raporcie `KickMaster_STAGE02B_REPORT.md`
i towarzyszących JSON-ach. Nie umieszczamy przyszłych wyników zapisu wewnątrz
archiwum, którego hash właśnie od nich by zależał.

## Następny zakres

1. PRG08:$A7DB i pozostałe efekty: odblokowanie czarów, flagi, koszty, czas i obrażenia.
2. Pozostali producenci $D3 i $01A5, hasła i cała ścieżka odtwarzania postępu.
3. Ruch/ataki gracza, próbki kolizji i geometria scen; mapowanie 32 indeksów na etapy.
4. Pełny kontrakt NMI/IRQ/PPU i natywna walidacja emulatorowa.

Oryginalny ROM pozostaje jedynym wejściem. Osobnych notatek użytkownika nie użyto
jako źródła odkryć; nie wprowadzono modyfikacji mechaniki gry.
