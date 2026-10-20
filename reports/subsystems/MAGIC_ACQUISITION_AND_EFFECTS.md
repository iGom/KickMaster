# Zdobywanie, wybór i sterowanie magią — etap 02C

Badany obraz: KickMaster NTSC-U, SHA-256
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Ustalenia wyprowadzono z oryginalnych bajtów ROM-u i ich wykonania w modelu CPU.
Osobnych notatek reverse engineeringu użytkownika nie wykorzystano jako dowodów.
Adresy kodu są kwalifikowane bankiem; liczby w tabelach kosztów są dziesiętne,
identyfikatory, maski i wartości zapisane jako A0/FF itp. — szesnastkowe.

## Zakres i jego granice

Nowa seria E01–E51 obejmuje 34 zakresy kodu i 17 danych: 875 instrukcji,
2260 bajtów PRG. Wszystkie adresy fizyczne i warunki mapowania znajdują się
w `analysis/reviewed_ranges.csv`, `reviewed_instructions.csv` oraz nowych tabelach.
PRG07/08/09 działa tu w oknie R7 przy $A000; dane opisów magii są wskazywane
w banku 03, w oknie R6 przy $8000. Te domeny nie są zamienne.

18 grup CPU / 16460 przypadków / 5906 wierszy śladu: PASS.
Brak modyfikacji ROM-u i atrap wywoływanych procedur. Wybrane próby mają jawne
punkty zatrzymania: prefiks wyboru kończy się przed animacją menu; prezentacja
kończy się przed rendererem tekstu lub usługą zmiany sceny. Pełna pierwsza
aktualizacja nowych efektów przechodzi przez oryginalną pętlę obiektów.
Pozostałe ruchy pocisków, kolizje, rozliczanie HP wrogów i AI wymagają dalszej analizy.
Nie użyto pełnego emulatora NES; liczników nie przeliczono na rzeczywiste sekundy.

## Bity odblokowania i kolejność menu

PRG08:$A831 przekształca typ przedmiotu 50–67 w identyfikator 0–11:
`((typ − 50) & FE) / 2`. Następnie OR-uje maskę z PRG08:$A860–$A878
z dwoma bajtami RAM $06BE/$06BF. Są to maski 0001, 0002, …, 0800.
Górne cztery bity bitsetu zostają zachowane; menu używa dolnych dwunastu.

$04E3 otrzymuje identyfikator właśnie zdobytego efektu. Dwa bajty $06C0/$06C1
przechowują oczekujące identyfikatory ikon: wartość 0C jest znacznikiem pustego
pierwszego pola. Jeżeli pierwsze pole jest puste, zostaje wypełnione; w przeciwnym
razie drugie jest nadpisywane. Kod nie sprawdza duplikatu ani przepełnienia takiej
pary. Nie jest to ogólna kolejka o nieograniczonej długości.

Menu ma 12 komórek w trzech rzędach po cztery. Jego kolejność z PRG07:$AC35 wynosi:
05, 00, 08, 0B / 09, 03, 01, 06 / 04, 0A, 02, 07.
Numer komórki, identyfikator efektu i typ obiektu są odrębnymi wielkościami.

| Efekt, hex | Para przedmiotów, hex | Maska odblokowania, hex | Komórka menu, dzies. | Koszt MP, dzies. | Nazwa referencyjna — korelacja |
|---|---|---|---:|---:|---|
| 00 | 50/51 | 0001 | 1 | 60 | Life Up 1 |
| 01 | 52/53 | 0002 | 6 | 90 | Life Up 2 |
| 02 | 54/55 | 0004 | 10 | 10 okresowo | Harpy Flying / Harpy Wings |
| 03 | 56/57 | 0008 | 5 | 20 | Lightning / Lightning Spirit |
| 04 | 58/59 | 0010 | 8 | 30 | Whip Lightning |
| 05 | 5A/5B | 0020 | 0 | 3 | Bouncing Bulb / Bouncing Bulb Spirit |
| 06 | 5C/5D | 0040 | 7 | 5 | Pulse Wave / Pulse Wave Spirit |
| 07 | 5E/5F | 0080 | 11 | 20 | Earthquake |
| 08 | 60/61 | 0100 | 2 | 20 | Magic Boots |
| 09 | 62/63 | 0200 | 4 | 1 | ?? Magic |
| 0A | 64/65 | 0400 | 9 | 30 | Force Shield |
| 0B | 66/67 | 0800 | 3 | 20 | Twin Power |

Identyfikatory, maski, komórki i koszty są dowodami ROM/CPU. Nazwy zestawiono
z opisami i kosztami w dostarczonym poradniku Wyrentha, sekcja Spells,
linie 262–331, oraz z zachowaną bazą instrukcji Taito. Nie wykonano osobnej
wizualnej walidacji nazw glifów. Korelacja nazwy nie potwierdza wszystkich
przypisywanych czarowi zachowań, np. odkrywania ukrytych przedmiotów przez ?? Magic.
Pełna tabela z lokalizacjami: `magic_unlock_menu_map.csv`.

PRG07:$AEA0 przekłada komórkę przez tę samą tabelę, przesuwa kopię bitsetu i zwraca
bit dostępności w carry. PRG07:$AEB6 wyszukuje odwrotne mapowanie bieżącego wyboru;
nieznany identyfikator, w tym 0C, daje komórkę 0. Indeks 0C wyłącza wybrany efekt,
ale nie jest trzynastą widoczną komórką tego menu.

## Przebieg zdobycia magii

PRG08:$A7DB nie dezaktywuje przedmiotu natychmiast. Zapamiętuje jego względny slot
w $D0, wykonuje odblokowanie, zeruje licznik $CF, ustawia stan gracza CC/CD
z zachowaniem kierunku i usuwa bit 0 z $CE. Przedmiot zostaje ustawiony przy
X gracza +5 albo −5 oraz Y gracza −26 hex. Pozostałe role flag są zachowane.
Wybrany czar $06BD nie zmienia się automatycznie.

PRG08:$BBAD ustawia bit 80 w $D3, kasuje bit 20 flag zebranego przedmiotu i zwiększa
$CF. Tabela $BBDC–$BBE9 wybiera stany CC/CE/D0 na podstawie `$CF >> 3`.
Od początkowego $CF=0 dokładnie 96. wywołanie daje stan końcowy 00/01,
zeruje licznik i aktywność przedmiotu, po czym przechodzi do $BD56.
To 96 wywołań tej procedury, nie zmierzony czas rozgrywki.

$BD56 uruchamia prezentację: wygaszanie, dalekie wywołanie PRG07:$A0BD z układem 7,
następnie jawne mapowanie R6=03 i wybór jednego z dwunastu wskaźników opisu.
Wskaźniki PRG08:$BDDB–$BDF3 dotyczą danych PRG03 przy $8000–$9FFF.
Samo renderowanie opisów i pełna pętla prezentacji nie zostały wykonane w nowych testach.

Po Start lub A następuje wybór z osobnej tablicy 32 tras PRG08:$BDBB–$BDDB.
FF prowadzi do usługi przejścia dalej, a inna wartość zastępuje $9A i uruchamia
usługę restartu. Dane są w `magic_acquisition_scene_routes.csv`.
Niektóre wpisy zmieniają indeks sceny, co będzie istotne przy porównywaniu map
i ukrytych przejść. Sam wpis nie dowodzi jednak przypisania sceny do konkretnego sektora.

## Sterowanie menu

PRG07:$ACBD zachowuje pełny bajt nowych naciśnięć $1F. Priorytet kierunków to
Prawo, Lewo, Dół, Góra. Nie ma zawijania krawędzi. Pierwszy naciśnięty kierunek
kończy rozpatrywanie również wtedy, gdy ruch jest zablokowany: np. Prawo+Lewo
na prawej krawędzi nie przesuwa kursora w lewo. Dźwięk 39 jest żądany tylko przy ruchu.
Sprawdzono wszystkie 256 masek wejścia dla 12 pozycji.

PRG07:$AD65 odrzuca wybór nieodblokowanej pozycji. Przy dostępnej pozycji zapisuje
w $06BD identyfikator z tabeli, następnie animuje ikonę przez 16 kroków aktualizacji
i wywołuje $AE3A. Przejrzano lokalny kod animacji, ale nowe testy zatrzymują prefiks
przy $AD81 i jawnie przechodzą do inicjalizacji; pełna pętla animacji z usługami
obrazu i oczekiwaniem na ramkę pozostaje niewykonana.

Dodatkowa ścieżka PRG07:$AD03 działa przy nowym B i niezerowym $01A5.
Wtedy `$D3 = (stare D3 & F0) | ((stare D3 + 1) & 07)`.
Kasuje więc także bit 3. Nie przelicza limitów HP/MP. Potwierdzono lokalny efekt
tej flagi, ale nadal nie znaleziono jej kompletnej ścieżki aktywacji w grze.
Nie przedstawiamy tego jako potwierdzonego sposobu włączania trybu debug.

## Pociski i celowanie

Efekt 05, PRG09:$B6DF, kosztuje 3 MP i tworzy typ 10 w jednym z trzech
zarezerwowanych slotów globalnych 0–2. Efekt 06, $B7D4, kosztuje 5 MP,
tworzy typ 00/01 z prędkością X +8/−8 i zerową prędkością Y.

Alokator $BDA8 szuka wolnego slotu od 2 do 0 przed odjęciem MP. Pełna trójka
nie zużywa MP. To inna pula niż alokator zwykłych przedmiotów PRG0F:$E0ED.
Wszystkie kombinacje zajętości, kierunków, kierunku gracza i granicy kosztu
przeszły nowe testy. Ruch/odbicia i kolizje gotowych pocisków są jeszcze otwarte.

Oba efekty aktualizują orb celowania przez $B747. Bieżący indeks $0593 przesuwa się
o jeden ku poprzedniemu celowi $05A7, a dopiero na końcu wyznaczany jest nowy cel
z kierunków trzymanych w $20. Brak kierunku zastępuje Prawo/Lewo według gracza.
Tabele obejmują 16 masek kierunków oraz dziewięć podpisanych przesunięć X/Y.
Sprawdzono wszystkie kombinacje dziewięciu bieżących i docelowych pozycji,
dwóch kierunków gracza i szesnastu masek. `magic_aim_and_velocity.csv` przechowuje wartości.

## Liczniki aktywnych efektów

| Efekt | Potwierdzona ścieżka sterowania |
|---|---|
| 02, lot | start kosztuje 10 MP; ponowna opłata co 30 aktywnych wywołań; Select wyłącza bez kosztu |
| 07, trzęsienie | koszt 20 MP; faza przewijania 1–59, następnie 0 w 60. wywołaniu |
| 08, ochrona terenu | koszt 20 MP; dwa liczniki wygasają po 1008 wywołaniach, licząc aktywację |
| 09, maska atrybutów | koszt 1 MP; zapis F0, potem 240 wywołań do zera; bit 20 w $B8 przełącza się okresowo |
| 0B, sobowtór | koszt 20 MP; licznik C9, czyli 201 aktualizacji przy spełnionym warunku widoczności |

To domeny lokalnych liczników, nie sekundy ani gwarantowane klatki obrazu.
Poradnik opisuje opłatę za lot jako „na sekundę”; kod wyznacza okres 30 wywołań.
Częstotliwość wywoływania należy potwierdzić w pełnej pętli gry.

Lot, PRG09:$BA3B, używa bitu 0 w $CE. Przy aktywacji i wyłączeniu skraca stan $CD
do kierunku. Brak MP na kolejny okres usuwa bit lotu. Ujemne $D3 powoduje powrót
jeszcze przed opłatą, także przy $01A5; ta bramka różni się od samej procedury wydatku MP.
Nie przejrzano tu wszystkich ruchów i ataków stanów alternatywnych gracza.

Ochrona terenu, $B8B7, zapisuje również kolor 16 do $0158 i przy wygaśnięciu
przywraca bajt PRG0F:$FFB5. Młodszy licznik osiąga zero w wywołaniach 240, 496,
752 i 1008. Wcześniej przejrzany warunek obrażeń terenu PRG0E:$DB02 sprawdza
wybór 08 i niezerowe $0593, a nie cały dwubajtowy licznik. Zatem lokalnie jego
wyjątek nie działa przy tych zerach. Nie potwierdzono jeszcze, czy harmonogram
próbkowania terenu pozwala wykorzystać pośrednie zera w rzeczywistej rozgrywce.

Efekt 09, $B830, zmienia maskę $B8 używaną przy atrybucie obiektów.
Przejrzany kod nie dowodzi hipotezy poradnika o ujawnianiu ukrytych przedmiotów.

Sobowtór, $B930, wymaga zgodności strony X z kamerą i względnego Y w zakresie 0–EF.
Wyjście poza ten obszar lub wyzerowanie licznika przywraca typ gotowości 86.
Wcześniejszy kod aktualizacji gracza pomija kopiowanie jego poprzedniej pozycji,
gdy wybrano efekt 0B i $0593 jest niezerowe; dalsze powiązanie z AI wymaga sprawdzenia.

## Błyskawice, tarcza i żądania trafienia

Efekt 03 po opłacie 20 MP przechodzi przez typy 8C → 8E → 90/92 → 94 → 76.
Śledzi X gracza, unosi się ku górze kamery, po pięciu aktualizacjach oczekiwania
tworzy w slotach 0–2 typy 28, 18, 29, a następnie odlicza 256 aktualizacji
licznika początkowo równego 00. Faza opadania kończy się według niskobajtowego
przedziału wokół Y gracza. Sprawdzono kontroler tych faz; same trzy pociski
mają dalsze, nieprzejrzane zachowania.

Efekt 04 po opłacie 30 MP tworzy trzy kolumny przy X kamery +20/+80/+E0
oraz Y kamery +CF. Kontroler PRG09:$BAC7 wyłącza każdą kolumnę w 30. aktualizacji.
Kolumna 0 w aktualizacjach 8, 16 i 24 wywołuje $BD1B z argumentem 6.

$BD1B **kolejkuje żądanie obrażeń**, nie odejmuje bezpośrednio HP.
Przegląda 10 slotów wrogów, przyjmując tylko te, w których $0469,Y ≥ C0
oraz `$0473,Y & 03 = 0`. Zapisuje żądanie do $0441,Y, ustawia bit 20 w $0469,Y
i kasuje dolne trzy bity $047D,Y. Ostateczne obrażenia, odporności i bossowie
pozostają poza zakresem tej procedury. Nowe testy obejmują wszystkie wartości
pierwszej flagi i osiem reprezentatywnych kombinacji drugiej dla wszystkich 10 slotów.

Efekt 07 przez PRG0E:$D7E7 dotyka tylko pierwszych ośmiu flag $0473–$047A.
Bit 20 wyklucza zmianę; pozostałym usuwa bit 40 i ustawia 10. $03DC dostaje 1.
Czas właściwego unieruchomienia i konsument tych flag nie są jeszcze ustalone;
60-elementowy licznik przewijania nie jest dowodem czasu unieruchomienia wroga.

Efekt 0A ustawia budżet 0A w $05A7 i typ 8A. Kontroler $B964 podąża za graczem,
dopóki bajt budżetu jest nieujemny; wartość ujemna kończy efekt i przywraca typ 84.
Nie ustalono tu konsumenta budżetu ani dokładnego rozliczania trafień tarczy.

## Dostarczone mapy i poradnik

Zachowano bajt po bajcie pełny TXT Wyrentha, oryginalne `maps.zip` i osiem PNG.
Nie zmieniono ich rozdzielczości ani kodowania. Rozmiary obrazów odczytano z plików:
3840×240, 3840×720, 2560×720, 3216×240, 2560×240, 3840×240, 3072×240, 768×3600.
Manifest źródeł zawiera SHA-256, rozmiary i tożsamości załączników.

Usunięto aktualną blokadę dostępności map w indeksie i ośmiu kartach etapów,
zachowując informację historyczną o nieudanym dostępie sieciowym w 00A.
Szczegółowe porównanie pikseli z geometrią, przewijaniem, obiektami i 32 scenami
pozostaje zaplanowane. Nie rozpoczęto ponownie całego Stage00A.
W przyszłości wycinki muszą zachowywać skalę 1:1 i zapisywać prostokąt źródłowy;
żadnego wycinka w tej sesji nie tworzono.

## Następne konkretne granice

- Procedury typów pocisków 00/01, 10/11, 18/19, 28/29 i ich kolizje.
- Konsument żądań $0441 oraz flag $0469/$0473/$047D; czas działania trzęsienia.
- Zużywanie budżetu tarczy $05A7, zachowanie sobowtóra w AI i pełny lot gracza.
- Producent $01A5, pozostałe zapisy poziomu/HP, kod haseł i odtwarzania scen.
- Prezentacja magii i animacja wyboru z pełnym NMI/PPU; opisów tekstowych jeszcze nie odtworzono.
- Rekonstrukcja geometrii i transformacji współrzędnych map; dane z PNG są referencją,
  nie dowodem adresów ani wewnętrznych identyfikatorów ROM-u.
