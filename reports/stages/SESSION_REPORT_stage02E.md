# KickMaster NTSC-U — Stage 02E

Raport z 2026-10-21. Ukończono ograniczony etap sterowania normalną postacią, faz skoku,
wyboru ataków i kontraktu odczytu terenu. Pełna rekonstrukcja gry pozostaje w toku.
Najpierw zweryfikowano istniejący checkpoint02D; nie powtarzano wcześniejszych analiz ani zestawów CPU.

## Wyniki

- Rozpoznano normalne procedury gracza od stania i chodu przez skok/kucanie po lokalne
  przebiegi stanów ataków. Wybór zależy od poziomu, przycisków i zwrotu; osobne wejścia
  omijają niektóre zamiany technik. Nazw z instrukcji nie przypisano bez porównania animacji/hitboxów.
- Potwierdzono8 wywołań na fazę chodu. Przyczyną jest carry odziedziczone przed SBC07,
  a nie jawny licznik porównywany z8.
- Odtworzono rolę D1 jako fazy i flag skoku, tabelę pionowych kroków oraz wpływ przytrzymania A
  i dwóch bitów historii. Różne bity terenu odpowiadają za sufit i podłoże.
- Zidentyfikowano strony po64 bajty, metatile i cztery atrybuty na metatil. Wykonano3840
  odczytów z rzeczywistych danych sceny00 i porównano je z niezależnym odczytem struktury ROM.
- Ustalono różnicę usług: C75B zwraca rzeczywisty atrybut z ROM-u; C767/DB02 na tej gałęzi
  korzysta z pozostawionego3C=03. Odczyt cache ma inny kontrakt. Nie zgadywano zamiaru autorów.
- Dodano eksporty kierunków, wyboru ataków, kroków skoku, sekwencji42, flag cache i próbek sceny00.
  Szczegóły i bankowane adresy: `reports/subsystems/PLAYER_CONTROL_JUMP_AND_TERRAIN.md`.

## Wznowienie i trwałość wcześniejszych etapów

02D ponownie odczytano wraz z sześcioma osobnymi plikami. ZIP:3535089 bajtów,
SHA-256 `dbc9cf8ab43668c8042ed80dc25aeb966579968d7e7b8c39628d62b8af30609a`.
CRC, pełny manifest228 plików, pełna ekstrakcja i porównanie sześciu sidecarów:PASS.
Dowód: `manifests/stage02D_resume_verification.json`.
Nie przesyłano poprawnego archiwum ponownie; nie uruchamiano buildów/testów02D.
Domknięte wcześniej02B/02C pozostają zachowane wraz z raportami i potwierdzeniami.

## Przyrost i stan rekonstrukcji

| Miara | Po02D | Po02E |
|---|---:|---:|
| Zakresy kodu |190|231|
| Zakresy danych |84|92|
| Instrukcje |4611|5624|
| Bajty PRG z przejrzaną lokalną semantyką |12945|15194|
| Udział128KiB PRG |9,876251%|11,592102%|
| Role RAM |131|133|
| Symbole |405|456|
| Wpisy dispatchu pośredniego |224|256|
| Krawędzie deduplikowanego grafu |465|563|

G01–G49:41 zakresów kodu,8 danych,1013 instrukcji,2249 nowych bajtów.
Zaktualizowano RAM, symbole, bankowane offsety, odwołania, źródła assemblera i eksporty.
Odbudowa całego ROM-u jest identyczna:262160 bajtów.15210 bajtów zapisano jawnie w źródłach
(z nagłówkiem);246950 nadal pochodzi z jawnych fragmentów incbin oryginalnego pliku.
Zgodna odbudowa nie jest pełnym zrozumieniem pozostałego kodu/danych.

## Wykonane kontrole i granice

| Kontrola | Wynik |
|---|---|
| Nowe CPU02E |PASS:14 grup,11868 przypadków,34866 wierszy śladu|
| Modyfikacja bajtów ROM / podstawiane procedury |nie stosowano|
| Spójność indeksów, zakresów, instrukcji i tabel |PASS, dataset_audit.json|
| Lokalna kompilacja02E |PASS, pełna zgodność262160 bajtów|
| Hashy oryginalnego poradnika, ZIP-u i8 PNG; wymiary PNG |PASS, zachowane bez zmian|
| Testy wcześniejszych etapów |zachowane wyniki; nie wykonywano ponownie|
| Natywny MesenCE/Ghidra / pełny NES / timing |NOT_TESTED|
| Pełne porównanie map PNG z geometrią ROM |NOT_TESTED|

Nieudane próby są jawne w `analysis/stage02E_development_notes.json`.
Pierwsza rejestracja zakresów wykryła nakładanie na już przejrzane C37 i przerwała przed
modyfikacją tabel. Usunięto duplikat. Grupa CPU14 początkowo nie ustawiała ponownie A=0
przed wejściem ACF7. Skorygowano inicjalizację testu, udokumentowano kontrakt i ponowiono
wyłącznie grupę14; zaliczone grupy1–13 wykorzystano z zapisu częściowego.

Wyniki CPU dotyczą oryginalnych instrukcji uruchamianych z kontrolowaną pamięcią. Przypadki
wyboru ataku nie dowodzą jego obrażeń, a liczby wywołań nie są pomiarem klatek/sekund NES.
Odczyt16 wpisów stron sceny00 nie ustala długości poziomu: ostatni wpis powtarza stronę0E.
Map nie zmieniano ani nie dzielono; pełna geometria i32 sceny→8 sektorów nadal czekają na porównanie.
Nie wykorzystano oddzielnych notatek RE ani repozytorium użytkownika jako źródła odkryć.

## Checkpoint i dalsza praca

Planowany plik tego zamrożonego snapshotu: `kickmaster-ntscu-checkpoint-stage02E.zip`.
W chwili zapisu raportu wewnętrznego: utworzenie ZIP-u, jego końcowy SHA, czysta ekstrakcja/build,
zapis i ponowny odczyt są PENDING. Ten raport nie oznacza tych przyszłych kontroli jako PASS.
Rzeczywiste późniejsze wyniki, identyfikatory i hash są w osobnych `stage02E.verification.json`,
`stage02E.reproducibility.json`, `stage02E.persistence.json`, `stage02E.readback.json`
i końcowym `KickMaster_STAGE02E_REPORT.md`. Raport zewnętrzny zastępuje ten status PENDING.

Następny odcinek: kontakt/rozliczenie ataku PRG08:A2C3, pełniejsze definicje przeciwników,
C773 i producenci cache. Potem dalsza geometria z porównaniem do oryginalnych map,
przy zachowaniu bieżącego planu i niezależności. Szczegółowe kroki i polecenia: `RESUME.md`.
Nie powtarzać zaliczonych selektorów, fizyki, konsumentów trafień czy testów bez nowej konkretnej potrzeby.


## Końcowa weryfikacja checkpointu — wykonana

`kickmaster-ntscu-checkpoint-stage02E.zip` ma4361394 bajty i251 plików objętych manifestem
oraz sam manifest. SHA-256:
`1ae70fe401ac890e7e083e1c2ec4d5763e3ac314bf4b4ae698ccb1107f55759c`.

| Kontrola | Faktycznie wykonany wynik |
|---|---|
| Lokalny ZIP: CRC, pełny manifest, próbna ekstrakcja |PASS|
| Czysta pełna ekstrakcja251 plików i porównanie hashy |PASS|
| Kompilacja zapisanych źródeł z czystej ekstrakcji |PASS|
| Porównanie całego ROM-u262160 bajtów |PASS|
| Zapis ZIP-u,verification,reproducibility i RESUME |PASS|
| Nowy odczyt tych czterech plików i porównanie bajt po bajcie |PASS|
| SHA-256 ponownie odczytanego ZIP-u |PASS, zgodny z powyższym|
| CRC, cały manifest i pełna ponowna ekstrakcja251 plików po odczycie |PASS|
| Bieżący RESUME wewnątrz ZIP-u identyczny z osobnym RESUME |PASS|
| Brak oryginalnego i odbudowanego ROM-u w archiwum |PASS|

Czysta kompilacja była wymaganą kontrolą nowego02E. Nie regenerowano w niej źródeł ani
nie wykonywano żadnego zestawu CPU. Archiwum przesłano raz; wcześniejszych checkpointów
nie nadpisywano, nie usuwano ani ponownie nie przesyłano.

| Plik | Tożsamość trwałego zapisu | SHA-256 |
|---|---|---|
|kickmaster-ntscu-checkpoint-stage02E.zip|libfile_de8838c573c48191882debd818871feb|1ae70fe401ac890e7e083e1c2ec4d5763e3ac314bf4b4ae698ccb1107f55759c|
|stage02E.verification.json|libfile_7f9800d2e03881918e5bb24e9984513c|916d601c6dfceca4680ad003ef32c59f25e665e003dd00189ceba7457b71e973|
|stage02E.reproducibility.json|libfile_41d59b8e219c81918dec480dd651d5bb|c5978cc9b73ddd05098703b8c24cad5b49dd91ed3f19baf2605774a5ee8b8aa5|
|KickMaster_STAGE02E_RESUME.md|libfile_36e14cd83690819198554503cef74aa0|537a20319f1de2aebb00f9bab3665b6c961d7d46a52d7659d799c33f8bd7cfbf|

Dowody: `stage02E.verification.json`, `stage02E.reproducibility.json` i `stage02E.persistence.json`.
Osobny `stage02E.readback.json` zapisuje późniejszy odczyt tego końcowego raportu i persistence JSON.
Ten raport nie przypisuje sobie wyniku przyszłego odczytu. Powyższe wykonane kontrole zastępują
PENDING w historycznej części raportu i snapshotcie wewnątrz ZIP-u.

Dalsza praca według `KickMaster_STAGE02E_RESUME.md`: PRG08:A2C3 i pełniejsze rozliczanie
kontaktu/ataków, definicje wrogów, destrukcja i uzupełnianie cache, potem porównanie geometrii
z niezmienionymi mapami. Zachować bieżące wyniki i nie ponawiać testów bez nowej konkretnej potrzeby.
