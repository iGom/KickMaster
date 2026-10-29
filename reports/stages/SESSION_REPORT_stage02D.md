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

## Końcowa weryfikacja checkpointu — wykonana

`kickmaster-ntscu-checkpoint-stage02D.zip` istnieje, ma3535089 bajtów i zawiera228 plików
objętych manifestem oraz sam manifest. SHA-256:
`dbc9cf8ab43668c8042ed80dc25aeb966579968d7e7b8c39628d62b8af30609a`.

| Kontrola | Faktycznie wykonany wynik |
|---|---|
| Lokalny ZIP, CRC, pełny manifest, próbna ekstrakcja | PASS |
| Pełna ekstrakcja228 plików do nowego katalogu i porównanie hashy | PASS |
| Kompilacja zapisanych źródeł z tej czystej ekstrakcji | PASS |
| Porównanie całego wyniku262160 bajtów z osobnym oryginalnym ROM-em | PASS |
| Zapis ZIP-u i trzech towarzyszących plików | PASS |
| Nowy odczyt tych czterech plików i porównanie bajt po bajcie | PASS |
| CRC i pełny manifest ponownie pobranego ZIP-u | PASS |
| Ponowna próbna ekstrakcja README/RESUME/identity/baseline z pobranego ZIP-u | PASS |
| Brak oryginalnego/odbudowanego ROM-u w archiwum | PASS |

Nie regenerowano źródeł ani nie uruchamiano żadnego zestawu CPU w czystej ekstrakcji.
Nowa kompilacja była obowiązkową kontrolą odtwarzalności nowego02D, nie powtórzeniem analizy02C.
Plik ZIP przesłano raz. Poprzednich checkpointów nie nadpisano ani nie usunięto.

| Plik | Tożsamość trwałego zapisu | SHA-256 |
|---|---|---|
|kickmaster-ntscu-checkpoint-stage02D.zip|libfile_bcb9e2525a84819192dd9ba369387309|dbc9cf8ab43668c8042ed80dc25aeb966579968d7e7b8c39628d62b8af30609a|
|stage02D.verification.json|libfile_3e46de2fea0881918a91e765c8e2a16d|31af96a64736dec718df5410914ffa411c53b11e3be90b890905289aa9d4e130|
|stage02D.reproducibility.json|libfile_90ca9c1778308191a31853e7dc6882c7|54d169f97dafc454611e9738186dfd9ae83d10f8bd35be3d1482afffe377561a|
|KickMaster_STAGE02D_RESUME.md|libfile_82ca3d055e3c81918b2f4617cc965af3|a9bbe54c817a370d7bcd64c87839424bf84e286cf292f36341a3228ed549c50f|

Szczegółowe dowody: `stage02D.verification.json`, `stage02D.reproducibility.json`
i `stage02D.persistence.json`. Oddzielny `stage02D.readback.json` zapisuje także późniejszy
odczyt końcowego raportu i persistence JSON; ten raport nie przypisuje sobie wyniku przyszłego
odczytu. Wyniki tego rozdziału zastępują PENDING w historycznym raporcie umieszczonym wewnątrz ZIP-u.

Następny odcinek: PRG08:$B81D/$B8B5, fizyka `$BCEF` i kontrakt próbkowania terenu,
potem pełniejsze dane wrogów i kontakt `$A2C3`. Wykorzystać istniejące wyniki; domkniętych
konsumentów i wcześniejszych testów nie powtarzać bez konkretnego nowego uzasadnienia.
Aktualne instrukcje i pełny backlog: `KickMaster_STAGE02D_RESUME.md` / archiwalne `RESUME.md`.
