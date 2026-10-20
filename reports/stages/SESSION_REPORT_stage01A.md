# KickMaster NTSC-U — raport sesji

Wykonano etap 00, opracowano bazę źródeł etapu 00A i wykonano etap 01A obejmujący podstawy architektury.
Pełny reverse engineering gry pozostaje otwarty. Nie korzystano z osobnych notatek badawczych użytkownika.

## Najważniejsze wyniki

- ROM: 262160 bajtów, NES 2.0, mapper 4, PRG/CHR po 128 KiB. CRC32 obu części oraz całego payloadu
  zgadzają się z NesCartDB. Oryginał nie został zmodyfikowany ani zastąpiony.
- Rozpoznano RESET, NMI, IRQ, początkowe mapowanie banków, procedurę ponawiającą zapis MMC3,
  wywołanie między bankami, tablicę dyspozytora PPU i transfery korzystające tymczasowo ze stosu.
- RESET zachowuje dziewięć bajtów RAM: 0100 oraz 0300-0307. Znacznik 68 steruje inicjalizacją części tego obszaru.
- Licznik A6 jest zmieniany przez NMI i IRQ; przypisanie mu roli zwykłego licznika klatek byłoby zbyt mocne.
- W źródłach rozgrywki odnotowano sprzeczne wejścia ataków, koszt tarczy, błędne sumy przedmiotów,
  niepewny czas lotu i różne sposoby liczenia żyć.

## Zakres i weryfikacja

| Element | Wynik |
|---|---:|
| Wpisy bazy mechanik z odnośnikami | 51 |
| Planowane eksperymenty rozgrywki/systemów | 29 |
| Ręcznie przejrzane wpisy kodu | 24 |
| Ręcznie przejrzane obszary danych PRG | 3 |
| Nazwane lokalne role RAM | 35 |
| Symbole ogółem | 62 |
| Opisany kod/dane PRG | 925 + 44 = 969 bajtów |
| Automatycznie zdekodowane kandydaty | 6248 bajtów, poza metryką zrozumienia |
| Testy parsera nagłówka | 5/5 |
| Izolowane przypadki wykonania CPU | 57/57 |
| Zapisane wiersze śladu CPU | 3595 |
| Rozmiar identycznego wyniku budowania | 262160 bajtów |

Wynik ca65/ld65 jest identyczny bajt w bajt z wejściem:
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Jest to **szkielet zależny od oryginalnego ROM-u**: 261175 bajtów pochodzi nadal z jawnych fragmentów `.incbin`.
Zgodność binarna nie jest dowodem pełnej rekonstrukcji semantycznej. Udział przejrzanych zakresów PRG wynosi
969/131072 = 0,7393%, wyliczony z zapisanych zakresów.

## Granice ustaleń

Testy CPU używały py65 i jawnych atrap rejestrów; nie uruchomiono pełnej gry w emulatorze NES.
Nie potwierdzono jeszcze mechanik rozgrywki w kodzie, numerów skanlinii, timingu PPU/APU ani zachowania haseł.
Etykiety MLB sprawdzono składniowo według źródła MesenCE; faktyczny import MLB, DBG i danych do Ghidry
pozostaje nieprzetestowany. Brak natywnego projektu Ghidry, CDL i savestate'ów jest jawnie udokumentowany.

Lista ośmiu map została potwierdzona, lecz ich obrazy były niedostępne. Analiza geometrii tych map nie jest
ukończona. Odczyt MobyGames również blokował HTTP 403. Oryginalna instrukcja PDF była dostępna i została
przejrzana wizualnie. Całe instrukcje, poradniki i obrazy cudzych map nie są dołączone do archiwum.

## Trwałość i dalsza praca

Checkpointy stage00 i stage00A zapisano, pobrano ponownie i sprawdzono: hash, ZIP, manifest i próbne pliki.
Ich hashe i identyfikatory znajdują się w RESUME.md oraz manifests/*_persistence.json.
Nowy checkpoint sesji nosi nazwę `kickmaster-ntscu-checkpoint-stage01A.zip`.
Jego końcowy SHA-256 i wynik odczytu zapisanej kopii znajdują się w zewnętrznym raporcie/receipt, aby uniknąć
samoodwołującego się hasha archiwum. Manifest SHA256SUMS obejmuje wszystkie dołączone pliki poza samym sobą.

Oryginalny i odbudowany ROM są wyłączone z archiwum. RESUME zawiera identyfikator osobnego załącznika ROM-u
oraz polecenia wznowienia; ponowne wykonywanie zakończonych analiz nie jest potrzebne.
Następny etap: PRG0E:CF50, punkty wejścia banku 09, maszyna stanów, kontroler i kontekst przełączania banków,
a następnie niezależne ustalenie reprezentacji HP/MP/EXP.
