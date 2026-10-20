# KickMaster NTSC-U — raport sesji 01B

Kontynuowano od checkpointu 01A, którego SHA-256 i pełną zawartość manifestu ponownie zweryfikowano.
Zachowano wcześniejsze wyniki. Nie powtarzano badań źródeł, bazowej analizy ROM-u ani 57 wcześniejszych
przypadków CPU. Nie korzystano z osobnych notatek badawczych użytkownika.

## Najważniejsze ustalenia

- Zlokalizowano synchronizację pętli z NMI: `$0095` jest sygnałem oczekiwania, a `$0097` zmienia się
  w każdej iteracji oczekiwania. Dodatkowa procedura miesza `$0097` z X; pełna rola RNG pozostaje otwarta.
- Kontroler jest odczytywany dwukrotnie. `$0020` przechowuje AND obu próbek, `$001F` nowo naciśnięte
  przyciski, `$0021` historię A, a `$0713/$0714` starsze wartości przycisków trzymanych.
- Główna pętla od `$D046` zawiera cztery rozwinięte fazy i 34 wywołania. Ustalono pierwsze cele wrapperów
  banków 07/08/09 bez zakładania, że nieznani callees zachowują mapowanie.
- Prześledzono lokalne przejścia front endu, nakładki uruchamianej Startem i menu po wyzerowaniu licznika.
  Nakładka usuwa adres powrotu ze stosu i skacze do początku cyklu.
- Odczytano trzy 32-bajtowe tablice następników, ponowienia i kontynuacji. Wewnętrzne indeksy nie mają
  jeszcze przypisanych nazw ośmiu etapów gry.

Szczegółowy raport, adresy, równania i diagram: `reports/subsystems/MAIN_LOOP_INPUT_STATE.md`.

## Zakres rekonstrukcji

| Miara | Etap 01A | Po etapie 01B |
|---|---:|---:|
| Przejrzane obszary kodu | 24 | 68 |
| Przejrzane obszary danych PRG | 3 | 11 |
| Przejrzane instrukcje | 431 | 1463 |
| Bajty PRG z lokalną interpretacją | 969 | 3444 |
| Udział w PRG | 0,7393% | 2,6276% |
| Nazwane lokalne role RAM | 35 | 56 |
| Symbole ogółem | 62 | 135 |

Nie jest to liczba kompletnie zrozumianych funkcji: tablice skoków i obszary z wieloma wejściami są
liczone jako zakresy. Same tablice usług obejmują 88 wpisów. Automatyczne kandydaty nie zwiększają
metryki zrozumienia. Pełny reverse engineering pozostaje otwarty.

## Testy i budowanie

18 nowych grup CPU / 2295 wektorów: **PASS**. Obejmują wszystkie 256 masek kontrolera, zmiany wejścia,
AND próbek, historię, rzeczywisty handler NMI dostarczony syntetycznie, arytmetykę stanu97, banki,
porządek faz, ścieżki menu, wybrane efekty palety i granice przewijania. Zapisano 14033 wiersze wybranych
śladów, a wyniki wszystkich wektorów zachowano w JSON/CSV.

Pełny `$D90C` uruchomiono z rzeczywistą procedurą audio w zainicjalizowanym stanie nieaktywnym.
Testy przejść menu jawnie zastępują wybrane callees. Nie jest to pełna emulacja NES ani weryfikacja
renderingu, DMC, skanlinii i timingu APU. Nie wykonano natywnego importu do MesenCE/Ghidry.

Rozszerzony szkielet ca65/ld65 ponownie odtwarza wszystkie 262160 bajtów oryginału:
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
3460 bajtów ma jawną reprezentację w źródle, w tym 16 bajtów nagłówka. Pozostałe 258700 bajtów nadal
pochodzi z `.incbin`. Wymagany jest oryginalny ROM. Zgodność binarna nie oznacza pełnej rekonstrukcji.

## Trwałość i dalsze zadania

Nowa paczka: `kickmaster-ntscu-checkpoint-stage01B.zip`. Poprzednie checkpointy pozostawiono bez zmian.
Archiwum zawiera aktualny RESUME, raporty, mapy, źródła, indeksy, skrypty, wyniki i manifest SHA-256.
Oryginalny i odbudowany ROM pozostają poza paczką. Identyfikator osobnego załącznika jest w RESUME.
Końcowy hash ZIP, wynik rozpakowania i odczytu zapisanej kopii są dopisywane do zewnętrznego raportu
po utworzeniu archiwum, aby uniknąć samoodwołującego się hasha.

Następny etap: producenci CE/D3/03B9 i ciała głównych procedur banków 07/08/09, następnie niezależne
ustalenie HP/MP/EXP i powiązanie indeksów scen z danymi świata. Nadal brakuje obrazów map z etapu 00A
oraz rzeczywistych testów pełnej gry i integracji debuggerów.
