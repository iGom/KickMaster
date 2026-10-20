# KickMaster NTSC-U — raport sesji 02C

Data: 2026-10-20. Uporządkowano trwałość 02B, przyjęto oryginalne źródła użytkownika
oraz przeanalizowano zdobywanie, wybór i sterowanie efektami magicznymi.
Całościowa rekonstrukcja gry pozostaje nieukończona.

## Checkpoint 02B i brakujące raporty

Odczytano istniejące archiwum z Library:
`libfile_2de6444368d08191ad09d2e9fde8dec5`, wersja 0.
Jego SHA-256 wynosi dokładnie
`397afcb28be6c26ce6fa471b5270531162a4a62b61f810cc02d14681fd5ce07b`.
Rozmiar: 1762502 bajty. CRC ZIP, wszystkie 177 plików manifestu, próbne rozpakowanie,
porównanie z lokalnym ZIP-em i stanem projektu: PASS. Archiwum nie było ponownie przesyłane.
Nie ustalamy, która wcześniejsza operacja doprowadziła do pojawienia się tej kopii;
potwierdzamy jej aktualną obecność i właściwe bajty.

Utworzono brakujące, osobne pliki `stage02B.verification.json`,
`stage02B.reproducibility.json` i `stage02B.persistence.json`.
Standardowy zapis nadal zwracał 403; zgodnie z wyraźną zgodą użytkownika zastosowano
zapis bezpośredni. Wszystkie trzy pliki pobrano ponownie i porównano bajt po bajcie: PASS.
Ich identyfikatory i hashe znajdują się w `manifests/stage02B_sidecars_readback.json`.

Odtwarzalność 02B oparto na faktycznie wykonanej wcześniej kompilacji po czystym
rozpakowaniu. Teraz sprawdzono zachowane źródła kompilowane względem zweryfikowanego
archiwum oraz ponownie porównano zachowany wynik z oryginalnym ROM-em. Kompilacji
02B i jego 52382 przypadków CPU nie uruchamiano ponownie. Raport JSON odróżnia
te nowe porównania od zachowanego wyniku wcześniejszego wykonania.
Stare raporty 02B opisujące nieudany zapis są historyczne; nowe potwierdzenia je uzupełniają.

## Źródła użytkownika

W `research/originals/` zachowano pełny poradnik Wyrentha, niezmienione `maps.zip`
i osiem oryginalnych PNG sprays. Każdy plik ma SHA-256 w `originals_manifest.csv`.
Integralność PNG i wymiary sprawdzono bez zmiany rozdzielczości. Indeks źródeł,
indeks map i osiem kart etapów wskazują teraz dostępność lokalnych oryginałów.

Nie powtarzano Stage00A. Z poradnika odczytano celowo sekcję magii; nie deklarujemy
nowego przeczytania całości. Szczegółowa wizualna analiza map i porównanie z ROM-em
pozostają częścią przyszłych prac nad geometrią. Nie przypisano sektorów do indeksów
scen na podstawie samych nazw plików.

## Nowe ustalenia

- $06BE/$06BF to bitset dwunastu odblokowanych efektów. Typy przedmiotów 50–67
  ustawiają odpowiedni bit; numer komórki menu przekładany jest osobną permutacją.
- Zdobycie nie wybiera automatycznie czaru. Uruchamia animację i prezentację;
  od $CF=0 przejście do prezentacji następuje po 96 wywołaniach jej kontrolera.
- Odnaleziono 32 trasy scen po prezentacji magii oraz 12 wskaźników opisów w R6=03.
  Pełne renderowanie prezentacji nie zostało wykonane.
- Potwierdzono koszty i warunki aktywacji pozostałych dziesięciu efektów.
  Pełna pula trzech pocisków nie zużywa MP; lot ponawia koszt 10 MP co 30 aktywnych
  wywołań; kilka efektów ignoruje ponowną aktywację do wygaśnięcia.
- Wyznaczono liczniki oraz fazy błyskawic, ochrony terenu, maski atrybutów i sobowtóra.
  Liczby wywołań nie są przedstawiane jako sekundy bez weryfikacji harmonogramu gry.
- Odróżniono kolejkę żądań trafienia od rzeczywistego odejmowania HP wrogów.
  Tarcza, odporności, końcowe obrażenia, czas ogłuszenia i AI wymagają dalszych badań.

Pełne adresy, warunki wejściowe i ograniczenia: `MAGIC_ACQUISITION_AND_EFFECTS.md`.
Korelacje oficjalnych nazw opierają się na opisach/kosztach źródeł; nie oznaczają
potwierdzenia wszystkich zachowań deklarowanych w poradniku.

## Miary i weryfikacja

| Miara | Po 02B | Po 02C |
|---|---:|---:|
| Zakresy kodu | 134 | 168 |
| Zakresy danych | 54 | 71 |
| Przejrzane instrukcje | 3055 | 3930 |
| Bajty kodu PRG | 6484 | 8376 |
| Bajty danych PRG | 2074 | 2442 |
| Bajty PRG z lokalną interpretacją | 8558 | 10818 |
| Pokrycie PRG | 6,5292% | 8,2535% |
| Wpisy RAM | 101 | 112 |
| Symbole | 289 | 351 |
| Krawędzie tabel pośrednich | 180 | 192 |
| Krawędzie grafu call/jump/table | 386 | 442 |

Nowe testy: 18 grup / 16460 przypadków / 5906 wierszy śladu: PASS.
Starsze zestawy CPU zachowano bez ponownego wykonania. Jawne zatrzymania testów
prefiksu wyboru i prezentacji opisano w danych; nie użyto atrap podprogramów.
To izolowane wykonanie CPU z modelem magistrali, nie test pełnego NES-a.

Aktualna kompilacja ca65/ld65 odtwarza cały obraz 262160 bajtów identycznie:
SHA-256 `00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
10834 bajty jawnego źródła obejmują nagłówek; 251326 bajtów nadal pochodzi z `.incbin`.
Audyt PASS obejmuje bajty, zakresy, tabele, symbole, dowody CPU, źródła użytkownika
oraz potwierdzenia 02B. Import natywny MesenCE/Ghidra nadal NIEPRZETESTOWANY.

## Zamknięcie i następne prace

Nowy checkpoint: `kickmaster-ntscu-checkpoint-stage02C.zip`.
Nie zawiera ROM-u wejściowego ani odbudowanego; zawiera źródła, narzędzia, dane,
raporty, poprawione potwierdzenia 02B oraz oryginalne materiały dostarczone przez użytkownika.
Jego końcowy hash, wynik odbudowy po czystym rozpakowaniu i odczyt po zapisie są
zapisywane w osobnych raportach 02C, po utworzeniu archiwum.

Następny konkretny zakres: ruch i kolizje pocisków, konsument kolejki trafień
$0441/$0469, tarcza i ogłuszenie, następnie pełne powiązanie z ruchem/atakami gracza.
Geometria scen będzie porównywana z dostępnymi już mapami przy ustalaniu transformacji
współrzędnych i mapowania 32 konfiguracji na osiem sektorów.
Poprzednich checkpointów nie nadpisano.
