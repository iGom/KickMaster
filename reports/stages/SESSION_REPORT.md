# KickMaster NTSC-U — Stage 02G

Analiza i testy: 2026-10-22. Domknięcie dokumentacji: 2026-10-29.
Ukończono ograniczony etap: rzeczywiste AI rodzaju00, zwykła śmierć i generowanie
dropów, konstruktor oraz cykle obiektów śmierci5B/60, a także ścieżka śmierci rodzaju50.
Pełna rekonstrukcja pozostaje w toku. Nie korzystano z osobnych badań użytkownika.

## Najważniejsze ustalenia

- Zwykła trójka dropów korzysta z powiązanych indeksów s, s+10, s+20 modulo32,
  a nie trzech niezależnych losowań. Oddzielna bramka liczników daje pojedynczy1-UP.
- Bit047D.10 tłumi i drop, i score; pełna pula dropów nie tłumi samego score.
  Śmiertelne zakolejkowane trafienie rozpoczyna śmierć dopiero w następnym przebiegu.
- Spawner nagrody końcowej może wymusić aktywny slot1 i nie zeruje jego licznika/timera.
  To inny kontrakt niż spawner zwykłego dropu.
- Rodzaj00 ma sześć normalnych stanów kolizji i45 rekordów klatek. Trzy wirtualne
  selektory AI śmierci/trafienia/zatrzymania nie są dodatkowymi stanami tych danych.
- Lokalny próg ataku rodzaju00 jest asymetryczny: signed X przeciwnik−cel
  od−32 do−25 albo od24 do31. Nie ma tutaj bramki Y.
- 5B wykonuje128 wybranych wywołań AI, tworzy nagrodę z tabeli12 podtypów,
  następnie czeka100 wywołań;60 ma inny rozrzut i sygnalizację końca.
  Nie przeliczono tych czasów na klatki wideo ani sekundy.
- Rozrzut używa32 nakładających się par z33 bajtów oraz zastanego carry.
  Konstruktor zapisuje wspólną kotwicę i nie inicjalizuje wszystkich pól nowego slotu.
- Jedna instrukcja STA zaczyna się w0E:DFFF i ma operandy w0F:E000/E001.
  Źródła zachowują oba fizyczne fragmenty, a indeks liczy instrukcję raz.

Szczegóły: `reports/subsystems/ENEMY_AI_DEATH_AND_REWARDS.md`.
Oryginały poradnika, maps.zip i ośmiu PNG zachowano bajtowo i w pełnych rozdzielczościach.
Porównanie PNG z geometrią ROM-u i przypisanie32 konfiguracji do8 sektorów nadal oczekują.

## Wznowienie i zachowane dowody

Przed02G odczytano02F ZIP i sześć osobnych plików, porównano SHA-256 i wykonano
kontrolę CRC, pełnego manifestu278 plików oraz pełną ekstrakcję. ZIP4846323 bajty:
`618f67d900fddd41b1d4dc4166a9f67ae24b6637db3dc631ecd26efb61909ca2`.
Dowód: `manifests/stage02F_resume_verification.json`. Finalny raport i pełny resume02F
są zachowane pod reports/stages/. Domknięcia02B/02C i późniejszych checkpointów pozostają
w łańcuchu dowodowym. Nie powtarzano starych testów CPU ani buildów i nie przesyłano
ponownie poprawnych wcześniejszych archiwów.

## Stan rekonstrukcji

| Miara | Po02F | Po02G |
|---|---:|---:|
| Zakresy kodu |243|274|
| Zakresy danych |115|130|
| Instrukcje |6021|6790|
| Bajty PRG z przejrzaną lokalną semantyką |17674|19838|
| Udział128KiB PRG |13,484192%|15,135193%|
| Role RAM |133|139|
| Symbole |491|543|
| Krawędzie pośrednie |349|383|
| Krawędzie grafu wywołań/tablic |653|717|

I01..I46:31 zakresów kodu,15 danych,769 instrukcji i2164 bajty.
Łącznie14318 bajtów kodu i5520 danych. Kompletny lokalny build262160 bajtów jest
zgodny z oryginałem.19854 bajty jawnego źródła obejmują16-bajtowy nagłówek;
242306 bajtów pozostaje zależnymi od ROM-u fragmentami incbin.
Zgodność binarna nie jest dowodem kompletnego zrozumienia programu.

## Testy, problemy i granice

15 nowych grup: **4050 zapisanych przypadków,11437 wierszy trace; wszystkie PASS**.
Bez patchowania ROM-u i atrap callee. Testy obejmują granice odległości, wybory dropów,
presję puli, pola obiektów, cykle śmierci, stany rodzaju00 oraz carry rozrzutu.
Część przypadków zapisuje obserwacje z fixture wykonujących wiele wywołań AI.

Zaliczone grupy1..6 zachowano po błędzie pierwszego oczekiwania grupy7.
Fixture z wyłączonym terenem nie mogło dowodzić ciągłego chodzenia: wynik36=0
wybierał spadanie. Skorygowano oczekiwanie i powtórzono tylko niezaliczoną grupę7,
po czym wykonano nowe8..15. ROM-u nie zmieniono. Wcześniejszy błąd inicjalizacji
generatora wystąpił przed zapisem wyników i został naprawiony.
Później doprecyzowano asymetryczny próg ataku na podstawie już zapisanych testów,
bez ich powtarzania. Pełny dziennik: analysis/stage02G_development_notes.json.

Audyt danych, instrukcji, adresów, eksportów, zakresów źródeł i oryginalnych
materiałów referencyjnych:PASS. Audyt odczytuje stare wyniki, nie uruchamia ich testów.
Lokalny build z bieżącego źródła:PASS. To odrębne od przyszłego czystego buildu z ZIP-u.

NOT_TESTED/UNRESOLVED: natywny NES i timing NMI/IRQ, natywne importy MesenCE/Ghidra,
pełna obsługa terenu E4AC oraz C773/C776/cache, żywe AI rodzaju50 i innych rodzajów,
pełna proweniencja celu Twin Power, globalne prawdopodobieństwa i nazwy bossów,
osiągalność wszystkich syntetycznych kombinacji, mapy PNG↔ROM i32sceny→8sektorów.
Przetestowany licznik wywołań AI nie jest pomiarem czasu wideo.

## Checkpoint i dalsza praca

Nazwa docelowa: `kickmaster-ntscu-checkpoint-stage02G.zip`.
Ten wewnętrzny raport jest migawką sprzed pakowania. Integralność i SHA nowego ZIP-u,
czysty build z archiwum oraz zapis i ponowny odczyt: **PENDING w tej migawce**.
Faktyczne wyniki późniejszych kontroli są zapisywane osobno w stage02G.*.json
i finalnym KickMaster_STAGE02G_REPORT.md. Nie wywodzić PASS z istnienia tego raportu.

Następny Stage02H: pełne C773→DBB7/C776, producenci i odświeżanie cache05B8,
obsługa terenu przeciwników E4AC; dalej geometria wszystkich32 konfiguracji,
kamera, przejścia i porównanie oryginalnych map. RESUME.md zawiera kolejność,
pozostałe zadania oraz procedurę selektywnej reprodukcji i checkpointów.
