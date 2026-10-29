# KickMaster NTSC-U — Stage 02D

Raport z 2026-10-21. Zakres: domknięcie trwałości 02C oraz następny odcinek programu/RAM,
obejmujący pociski, lokalne kolizje, rozliczanie HP przeciwników i konsumentów tarczy/trzęsienia.
Pełny reverse engineering gry pozostaje w toku.

## Najważniejsze wyniki

- Kolejkowane obrażenia trafiają do rzeczywistego HP przez PRG0F:$E32A z nasyceniem do zera.
  Flaga akceptacji zapobiega powtórnemu odejmowaniu; zwykła lokalna reakcja wraca do akceptacji
  po10 wywołaniach przy licznikach początkowych0.
- Force Shield pochłania10 kwalifikujących się przecięć z pociskami wroga; jedenaste przechodzi
  do procedury obrażeń gracza. To wynik konkretnej ścieżki, nie dowód ochrony przed wszystkim.
- Licznik Earthquake od seedu1 wygasa po240 wywołaniach konsumenta, z dodatkową flagą przy
  wywołaniu210. Nie przypisano mu czasu w sekundach ani kompletnej semantyki AI wszystkich wrogów.
- Odtworzono32 profile magicznych pocisków,101 par profili kolizji gracza,13 ograniczeń skanu slotów
  i32 wpisy dispatchu pocisków. W badanej ścieżce Lightning sprawdza sloty1/0 mimo trzech obiektów.
- Potwierdzono wzrost Pulse Wave, odbijanie osi Bouncing Bulb przez oryginalne samplery terenu
  oraz cykle segmentów Lightning. Osobno oznaczono syntetyczne wartości liczników i flag.
- Rozpoznano alias `$0440`: indeks9 tablicy HP nakłada się na pole zerowane/kopiowane przez
  przebieg przeciwników. Jego pełna rola i liczba niezależnych żywych wrogów pozostają otwarte.

Pełny opis, adresy, granice i tabela prób:
`reports/subsystems/PROJECTILE_COLLISION_AND_ENEMY_HITS.md`.

## Trwałość Stage 02C

Istniejący `kickmaster-ntscu-checkpoint-stage02C.zip` został ponownie pobrany i zweryfikowany.
Rozmiar:2597797 bajtów. SHA-256:
`9abf1f5c0bdbba3f264bb34ffd9112a5e3bb3803fcd1ba87e84e493e26650a3d`.
CRC ZIP, komplet manifestu i ekstrakcja wszystkich206 plików z porównaniem SHA-256:PASS.
Nie przesłano ZIP-u ponownie i nie zmieniono wcześniejszych checkpointów.

Brakujące `stage02C.persistence.json` i `KickMaster_STAGE02C_REPORT.md` zapisano, ponownie
pobrano i porównano bajt po bajcie. Dowód wraz z tożsamościami plików:
`manifests/stage02C_closure_readback.json`. Same zweryfikowane kopie są w
`manifests/stage02C.persistence.json` i `reports/stages/SESSION_REPORT_stage02C.md`.
Odczytano też istniejące02C verification/reproducibility/RESUME. Wcześniejszą udaną kompilację
z czystej ekstrakcji z2026-10-20 wykorzystano jako zachowany wynik; nie uruchamiano jej ponownie.

## Nowe artefakty i pokrycie

| Miara | Stage02C | Stage02D |
|---|---:|---:|
| Przejrzane zakresy kodu | 168 | 190 |
| Przejrzane zakresy danych | 71 | 84 |
| Instrukcje w przejrzanych zakresach | 3930 | 4611 |
| Bajty PRG z udokumentowaną lokalną semantyką | 10818 | 12945 |
| Udział w128KiB PRG | 8,253479% | 9,876251% |
| Lokalne role RAM | 112 | 131 |
| Symbole/etykiety MLB | 351 | 405 |
| Wpisy tablic pośredniego dispatchu | 192 | 224 |
| Krawędzie deduplikowanego grafu call/table | 442 | 465 |

Nowy przyrost F01–F35:22 zakresy kodu,13 danych,681 instrukcji i2127 bajtów.
Nie ma nakładających się zakresów ROM. Każdy rekord podaje bank, adres CPU, offset bankowy,
PRG i plikowy oraz warunek mapowania. Indeksy symboli, struktur danych, odwołań, dostępu do RAM,
klasyfikacja całego pliku i źródła assemblera zostały uaktualnione.

Nowe pliki analityczne: `projectile_collision_profiles.csv`, `projectile_object_dispatch.csv`,
`player_hurtbox_profiles.csv`, `magic_collision_slot_limits.csv`, `stage02D_static_summary.json`
oraz komplet wyników `cpu_stage02D*`. Skrypty `architecture_stage02d.py`,
`annotate_stage02d.py` i `cpu_stage02d.py` zachowują procedury odtwarzania.

## Wykonane kontrole

| Kontrola | Wynik i zakres |
|---|---|
| Nowe próby CPU02D | PASS:16 grup,26832 wektory,117943 wiersze śladu |
| Patchowanie ROM / zastępowanie callees | nie stosowano; zakresy zatrzymania opisane w wynikach |
| Zgodność instrukcji i tabel z bajtami oryginału | PASS, bieżący audyt zbioru danych |
| Nowa kompilacja02D | PASS, wszystkie262160 bajtów identyczne |
| Symbole, klasyfikacja, format generowanego podzbioru MLB | PASS, kontrole lokalne |
| Oryginały źródeł użytkownika | PASS, dziesięć hashy i wymiary ośmiu PNG |
| Próby CPU wcześniejszych etapów | wykorzystano zapisane wyniki; nie wykonywano ponownie |
| Natywny NES / MesenCE / Ghidra | NOT_TESTED |
| Geometria map sprays względem ROM-u | NOT_TESTED w tym podetapie |

Próby wykonują oryginalne instrukcje w py65 z modelem MMC3 i uproszczeniem PPU.
Wektor może być wariantem wejściowym albo krokiem dłuższej sekwencji. Nie są to nagrania z gry,
pełna emulacja sprzętu ani pomiary czasu rzeczywistego. F_CPU13 zatrzymuje zerowe limity przed
nieprzeanalizowanym kontaktem z ciałem przeciwnika.

Rozwój nowych prób ujawnił dwa błędne początkowe oczekiwania testu: ignorowanie bramki
parzystości pętli Pulse Wave oraz szczególny wrap syntetycznego bocznego licznika Lightning=1.
Poprawiono oczekiwania na podstawie kodu i wykonania; nie poprawiano ROM-u.
F_CPU11–13 powtórzono wyłącznie dlatego, że ich wyników zabrakło w odczytanym pliku częściowym.
Pozostałe zaliczone grupy wykorzystano bez powtarzania. Szczegóły i powód tego wyjątku:
`analysis/stage02D_test_development.json`.

Rekonstrukcja nadal zależy od oryginalnego wejścia:12961 bajtów jest jawnie zapisanych w źródłach
(w tym nagłówek), a249199 pochodzi z oznaczonych fragmentów `.incbin`.
Pełna zgodność binarna nie jest pełnym zrozumieniem gry. SHA-256 oryginału i wyniku:
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.

## Źródła, niezależność i ograniczenia

Zachowano oryginalny TXT Wyrentha, `maps.zip` i osiem oryginalnych PNG sprays bez zmiany
rozdzielczości. Aktualny indeks dostępności wskazuje dostępne materiały oraz oczekujące porównanie
z ROM-em. Nie powtarzano Stage00A. Nie importowano wyników osobistych badań użytkownika.
Nazwy czarów pozostają korelacją z wcześniej udokumentowanymi źródłami; szczegóły implementacji
mają osobne dowody ROM/CPU.

Otwarte pozostają: pełny kontrakt i format terenu, scrolling/przejścia/spawny, mapowanie32 scen
na osiem sektorów, ruch/ataki gracza, kontakt z przeciwnikami, odporności i AI bossów, generowanie
dropów, targeting sobowtóra, pełny inwentarz zapisów poziomu/HP, `$01A5`, hasła i pozostałe grafika/audio.
Rozwiązany bank docelowy nie oznacza przeanalizowanej treści wywoływanej procedury.

## Checkpoint i następny krok

Planowany plik tego snapshotu: `kickmaster-ntscu-checkpoint-stage02D.zip`.
Ten raport znajduje się wewnątrz snapshotu i dlatego nie zawiera jego własnego końcowego SHA-256
ani wyników późniejszego zapisu/odczytu. W chwili jego utrwalenia te bramki są PENDING.
Ostateczne wyniki podają osobne `stage02D.verification.json`, `stage02D.reproducibility.json`,
`stage02D.persistence.json` i `KickMaster_STAGE02D_REPORT.md`; nie wolno wnioskować PASS z planu.
Oryginalny ani odbudowany ROM nie jest dołączony; wymagany jest osobny, dokładnie zidentyfikowany plik.

Następny odcinek: PRG08:$B81D/$B8B5, fizyka `$BCEF` i kontrakt próbkowania terenu,
potem pełniejsze dane wrogów i kontakt `$A2C3`. Nie powtarzać domkniętych lokalnych konsumentów
ani wcześniejszych testów bez konkretnego nowego uzasadnienia. Szczegółowa kolejność: `RESUME.md`.
