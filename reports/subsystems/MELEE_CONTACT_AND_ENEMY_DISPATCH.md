# Kopnięcia, kontakt z przeciwnikiem i wejścia AI — Stage02F

Analiza niezależna, wyłącznie na bajtach oryginalnego ROM-u o SHA-256
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Ustalenia są lokalne: STATIC oznacza przejrzany kod/dane, CPU_TEST — wykonanie
oryginalnych instrukcji w kontrolowanym modelu pamięci, bez zastępowania callee.
Nie wykonano pełnej emulacji NES, obserwacji grafiki ani natywnego importu debuggerów.

## Trzy drogi kolizji

| Wejście | Obszar przeciwnika | Obszar gracza | Skutek |
|---|---|---|---|
| PRG08:A197 | ciało przez A354 | atak przez A452 | kolejka obrażeń jednego przeciwnika |
| PRG08:A2C3 | ciało przez A354 | hurtbox przez A4EC | obrażenia gracza przez 0E:C76D |
| PRG08:A075 | dodatkowy atak przez A0B0 | hurtbox przez A4EC | obrażenia gracza przez 0E:C76D |

Wszystkie skanują indeksy malejąco od `06F8−1`. Wymagają obu bitów C0 w 0469,Y
i zerowych dwóch dolnych bitów 0473,Y. A075 i A197 jawnie obsługują licznik zero;
A2C3 nie ma takiego warunku. Testy A2C3 używają wyłącznie liczników 1..10.
Nie wynika stąd dziesięć niezależnych slotów HP: `0437+9` aliasuje 0440.

A2C3 wywołuje A05B na kolejnych iteracjach; bramka może usunąć adres powrotu
ze stosu i zakończyć wyższą procedurę. D3 z maską A0 blokuje tę ścieżkę.
A075 sam nie wykonuje A05B; jego normalny wrapper fazy 1 robi to wcześniej.
D2 i 01A4 są dodatkowo obsługiwane przez wcześniej rozpoznany konsument obrażeń.

## Rekord kolizji przeciwnika

`06:855C + 2×kind` wskazuje tablicę wskaźników stanów. Stan `040F,Y` wybiera
wskaźnik tablicy klatek, a `0419,Y×4` wskazuje rekord czterobajtowy:

| Bajt | Znaczenie lokalne |
|---:|---|
| 0 | surowe obrażenia od ciała |
| 1 | indeks kształtu ciała, tablice od 06:94DC |
| 2 | surowe obrażenia dodatkowego ataku; zero wyłącza A0B0 |
| 3 | indeks kształtu dodatkowego ataku, tablice od 06:9554 |

Fizyczna tablica rodzajów ma 99 wskaźników, indeksy 00..62 hex. Pierwsze dane
stanów zaczynają się w 06:8622. Równoległa tablica renderera 0D:A2B5..A37B
także zawiera 99 wskaźników. To granica danych, a nie potwierdzona lista
99 osiągalnych, prawidłowych przeciwników. Liczby stanów i klatek poszczególnych
rodzajów pozostają otwarte. Wyeksportowano próbkę state=0/frame=0 dla każdego rodzaju.

Kształt ciała wykorzystuje 30-elementowe tablice 94DC, 94FA, 9518, 9536.
Dodatkowy atak używa 48-elementowych tablic 9554, 9584, 95B4, 95E4.
Każdy zestaw zawiera przesunięcie Y, zakres Y i dwa składniki X.
Bit 0 w 0469 decyduje o zamianie składników X. W A0B0 zamiana następuje,
gdy bit jest wyzerowany. Wyniki w 22..25 są bajtami z arytmetyką modulo 256.

Istotna różnica: A354 sprawdza oba końce przedziału X względem strony kamery.
A0B0 korzysta z dolnych bajtów pozycji i nie odrzuca innej strony świata.
Testy obejmują pozycje X=128 i 384 z tym samym dolnym bajtem oraz zawijanie.
Nie jest to dowód błędu widocznego w grze: wcześniejsze warunki aktywacji mogą
ograniczać dostępne pozycje. Wysokie bajty Y nie są częścią tych lokalnych obliczeń.

Przykład z ROM-u: kind=00, state=0, frame=0 prowadzi do 06:9000 i rekordu
`00 00 06 00`. Ciało nie zadaje obrażeń, ale dodatkowy atak zadaje 6 surowych
jednostek. State=1/frame=0 prowadzi do `06 00 00 00`, odwracając te role.

## Geometria kopnięcia i kolejka obrażeń

Gracz wybiera profil `i=CD>>1`; bit 0 CD określa zwrot. Osiem sąsiadujących
tablic po 101 bajtów opisano w `analysis/player_attack_profiles.csv`:

| PRG06 | Pole | Konsument |
|---|---|---|
| 8194 | składnik Y ataku | 08:A452 |
| 81F9 | zakres Y ataku | 08:A452 |
| 825E | składnik odejmowany od X | 08:A452 |
| 82C3 | składnik dodawany do X | 08:A452 |
| 8328 | surowe obrażenia kopnięcia | 08:A197 |
| 838D | przesunięcie Y próby terenu | 08:A1E8 |
| 83F2 | przesunięcie X próby terenu | 08:A1E8 |
| 8457 | siła próby terenu | 08:A1E8 |

Fizyczny zakres 101 profili nie dowodzi osiągalności wszystkich stanów 00..C9.
Ich użycie zależy od rodzin, bramek i wcześniejszych procedur gracza.

A452 zwraca carry=0 dla trafienia. Dla granic przeciwnika `(ey, eh, ex, ew)`
i współrzędnych gracza `(px, py)` test pionowy brzmi:

`((ey + vo − py) mod 256) < ((eh + ve) mod 256)`.

Składniki X są rozszerzane ze znakiem do 16 bitów, a przy nieparzystym CD
zamieniane miejscami. Sprawdzane są końce `px+plus` oraz `px−minus`.
Jeśli wysoki bajt różnicy koniec−kamera jest niezerowy, dany koniec zastępowany
jest początkiem kamery. Nie jest to zwykłe przycięcie do obu krawędzi ekranu:
także koniec za prawą krawędzią trafia do początku. Odpowiednie składniki stają
się `plus=(camera−px) mod256` lub `minus=(px−camera) mod256`.
Następnie test poziomy ma postać:

`((ex + minus − px) mod 256) < ((ew + plus + minus) mod 256)`.

Przejście A197 kończy się na pierwszym nakładającym się przeciwniku.
Jeżeli jego profil ataku ma obrażenia zero, procedura wraca bez dalszego skanu.
Przy dodatnich obrażeniach zapisuje 0441,Y, ustawia bit 20 w 0469,Y i aktualizuje
dolne trzy bity 047D,Y. Nie ma tutaj mnożnika zależnego od poziomu D3.
CE bit 01 wyłącza tę procedurę. Szkodliwość ciała przeciwnika nie jest warunkiem
przyjęcia kopnięcia: rekord z primary_damage=0 może nadal zostać trafiony.

Profil 22 ma obrażenia 4, Y=32/16, składniki X −8/+16. Profile 34..3A mają
zerowe składniki geometrii, ale obrażenia 1. Zerowa geometria profilu nie oznacza
automatycznego wyłączenia: suma z niezerowym obszarem przeciwnika może dać trafienie.
W testach producenta użyto wszystkich 101 par, obu zwrotów oraz poziomów 0 i 7.
Po dodatnim żądaniu wykonano oryginalny, wcześniej przeanalizowany E32A,
potwierdzając przejście od nowego producenta do zmiany HP. Nie powtarzano
oddzielnych starych testów E32A.

## Kierunek reakcji

08:A5EC odejmuje dolne bajty pozycji przeciwnika od pozycji gracza i interpretuje
różnice jako signed8. Znaki wybierają jedną z czterech grup tabeli A63D.
Wartości bezwzględne `ax, ay` wybierają kubełek:

- gdy `ay<ax`: 0 dla `ay<floor(ax/2)`, w przeciwnym razie 1;
- w pozostałych przypadkach: 2 dla `ay<(2×ax mod256)`, w przeciwnym razie 3.

Tabela zwraca kod 0..7. Wysokie współrzędne nie uczestniczą w obliczeniu.
Nie utożsamiono kodów z nazwami animacji ani pełnym fizycznym odrzutem.
Kierunek obrażeń gracza w A075/A2C3 korzysta z osobnego porównania:
jeśli wysoki bajt gracza jest mniejszy, carry=0; inaczej porównywane są dolne
bajty, także przy większym wysokim bajcie. Nie należy zastępować tego opisem
poprawnego porównania 16-bitowego.

## Scheduler, tablice AI i agregat HP

0E:D759 przy nieaktywnym 0469 bit80 wraca. Dla aktywnego slotu porównuje jego
parzystość z 06F9. Zgodność pomija AI, wykonuje D78B i przechodzi do renderera
0D:A000. Przy niezgodności rodzaj mniejszy od 46 hex wybiera R6=0B,
pozostałe wybierają R6=0A; następnie wywoływany jest dispatcher w 8000.
R7=0D jest kontraktem wcześniejszego D6F0. Po specjalnym AI następuje D78B;
zwykła ścieżka przechodzi od razu do renderera.

| Dispatcher | Wskaźniki | Rodzaje | Sposób skoku |
|---|---|---|---|
| PRG0B:8000 | 8011..8091, 64 wpisy | 00..3F | odczyt adresu−1, PHA high/low, RTS |
| PRG0A:8000 | 8017..8051, 29 wpisów | 46..62 | indeks kind−46, PHA high/low, RTS |

Obie procedury odtwarzają indeks slotu z 2C. Następne bajty po tablicach
zaczynają kod `CMP 0423,X`; nie są dodatkowymi wskaźnikami. Próg schedulera
46 nie dowodzi poprawności rodzajów 40..45. Nie wykonywano tych indeksów.
93 testy skoków zatrzymują się **przed pierwszą instrukcją celu**. Nie oznaczają
zaliczenia AI, bossów, odrzutu, upuszczania przedmiotów ani renderowania.

D78B dodaje HP z 0437,X do 0440 dla kind>=50 z wyjątkami 5B i 60.
Suma nasyca się na AF hex (175 dziesiętnie), również przy carry. D6F0 później
kopiuje ją do 06BC. Dla X=9 źródło HP i cel akumulatora są tą samą komórką;
lokalne wykonanie podwaja wartość i nasyca wynik. Producent agregatu jest już
znany; znaczenie ekranowe oraz globalny limit niezależnych slotów pozostają otwarte.

## Granice prób terenu

08:A1E8 sprawdza 32 flagi scen A8A6 oraz siłę 06:8457[i]. Przy obu niezerowych
kopiuje bazową pozycję gracza do 26..29, siłę do 2C, ładuje Y z 838D i X z 83F2.
Nieparzyste CD neguje X. Następuje C773. Testy zatrzymano przed callee:
potwierdzają argumenty i bramki, a nie modyfikację cache, bloków czy nagród.

08:A120 używa flag scen A8C6 oraz profilu A8F2[i]. Kod zawiera dwie próby
C776 przy X−6/Y+2 i X+6/Y+2. Dynamicznie sprawdzono dojście tylko do pierwszej;
druga pozostaje dowodem statycznym. A8F2 współdzieli pierwszy bajt z końcem
wcześniejszej tabeli F16. Nowy zakres H obejmuje pozostałe 100 bajtów,
bez dublowania źródła. Nie ustalono całkowitej fizycznej długości tablicy poza
101 indeksami obecnego profilu gracza.

## Wykonane eksperymenty

| Grupa H_CPU | Przypadki | Zakres |
|---|---:|---|
| 01 |10908| geometria ataku, kamera, zwrot i granice |
| 02 |648| kierunki signed8 i niezależność od wysokich bajtów |
| 03 |594| dodatkowe kształty z rzeczywistych rekordów 99 rodzajów |
| 04 |404| producent kopnięcia → kolejka → oryginalny konsument HP |
| 05 |601| wybór pierwszego celu, flagi, brak celu, zerowe obrażenia |
| 06 |180| kontakt ciała, blokady, pełna lokalna faza 2 A012 |
| 07 |180| dodatkowy atak, alias strony X, lokalna faza 1 A012 |
| 08 |3570| agregat HP, nasycanie, wyjątki i alias slotu 9 |
| 09 |252| scheduler do granicy AI/renderera |
| 10 |93| rzeczywiste skoki przez tablice AI, bez wykonania celów |
| 11 |6464| argumenty terenu i bramki scen/profili do C773 |
| 12 |3232| bramki pierwszej próby stóp do C776 |

Razem 12 grup, 27126 przypadków i 5223 zachowane wiersze trace: PASS.
`cpu_stage02F.json`, `_vectors.csv`, `_trace.csv` i `.partial.json` zawierają
wyniki, obserwacje i zakresy. `scripts/cpu_stage02f.py --groups N` pozwala
powtórzyć tylko wybraną grupę w razie konkretnej rozbieżności. Nie uruchomiono
starych zestawów CPU. Testy syntetycznych kontraktów nie dowodzą osiągalności
wszystkich kombinacji w normalnej rozgrywce.

## Następne pytania

Priorytet: rzeczywiste procedury AI od zindeksowanych celów, ich stany/klatki,
reakcje na trafienia, śmierć i generowanie nagród. Następnie C773→DBB7,
C776, producenci i odświeżanie cache 05B8, geometria i kamera dla 32 scen.
Porównanie ośmiu map sprays z ROM-em oraz przypisanie scen do sektorów nadal
wymaga osobnego dowodu; oryginalne PNG, maps.zip i poradnik zachowano bez zmian.
Nazwy technik z instrukcji, pełne AI/bossowie, spawny, RNG, hasła, audio/grafika,
alternatywna rodzina gracza i natywne zachowanie NES nie są ukończone.
