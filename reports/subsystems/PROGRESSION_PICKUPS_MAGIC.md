# Postęp postaci, przedmioty i dwa zaklęcia leczące — etap 02B

Analiza dotyczy wyłącznie dostarczonego ROM-u NTSC-U o SHA-256
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Nie wykorzystano osobnych notatek reverse engineeringu użytkownika jako źródła ustaleń.
Adresy kodu podano z bankiem PRG; adresy RAM nie wymagają banku.
Wartości szesnastkowe zapisano bez znaku dolara; liczby dziesiętne oznaczono słownie,
gdy kontekst mógłby być niejednoznaczny. Przedziały adresów są prawostronnie otwarte.

## Zakres dowodów

Etap obejmuje 42 nowe zakresy: 33 kodu i 9 danych, 700 instrukcji, 1729 bajtów PRG.
`analysis/reviewed_ranges.csv` i `reviewed_instructions.csv` zawierają serię D01–D42,
oryginalne bajty, adres CPU, numer banku, offset bankowy, offset PRG i offset pliku.
Banki 07/08/09 wymagają okna R7 przy $A000; 0E i 0F są stałe w badanym trybie MMC3 0.
Nowe odwołania mają rozstrzygnięty bank, lecz część ich procedur docelowych pozostaje
nieprzejrzana. Rozstrzygnięcie banku nie jest rozstrzygnięciem semantyki procedury.

W `cpu_stage02B.json` zapisano 16 grup i 52382 przypadki PASS; osobne CSV przechowują
wszystkie przypadki i 9976 wierszy śladu. Oryginalnych bajtów ROM-u nie zmieniano.
Żadna grupa nie zastępuje wywoływanych procedur atrapami. Próby samych dispatcherów
kończą się przed wykonaniem wskazanej procedury i są tak oznaczone.
Model magistrali/MMC3/PPU nie odtwarza czasu pełnego NES-a, obrazu ani przebiegu rozgrywki.

## Liczniki i poziom

| Pole RAM | Długość | Znaczenie i format |
|---|---:|---|
| $00EA–$00ED | 3 | bieżące MP; cyfry dziesiętne +60 hex, najmniej znacząca pierwsza |
| $00ED–$00F1 | 4 | bieżące EXP; ten sam format, zakres 0–9999 dziesiętnie |
| $00F1–$00F5 | 4 | następny próg EXP; ten sam format |
| $00F5–$00F8 | 3 | maksymalne MP; ten sam format |
| $00D3 | 1 | poziom w bitach 0–2; wyższe bity mają także role stanu gracza |
| $06B9 / $06BA / $06BB | po 1 | bieżące HP / kopia dla paska / maksymalne HP |
| $0306–$030C | 6 | wynik punktowy; cyfry dziesiętne +20 hex, najmniej znacząca pierwsza |
| $030E | 1 | liczba prób łącznie z bieżącą; zapis binarny |
| $030F | 1 | offset bajtowy następnego progu dodatkowej próby |

To cyfry w osobnych bajtach, nie liczby binarne ani spakowany BCD. Na przykład
123 MP ma bajty 63 62 61 w RAM. Tabele ROM przechowują cyfry w odwrotnej kolejności.
Osobnym formatem jest argument kosztu dla PRG09:$BD46: dwie cyfry dziesiętne
w połówkach jednego bajtu, np. 60 hex oznacza koszt 60 dziesiętnie.

| Bieżący poziom | Następny próg EXP, dzies. | Maks. MP, dzies. | Maks. HP, hex | Pełne komórki HP |
|---:|---:|---:|---|---:|
| 0 | 1000 | 100 | 40 | 4 |
| 1 | 2000 | 200 | 50 | 5 |
| 2 | 3000 | 300 | 60 | 6 |
| 3 | 4000 | 400 | 70 | 7 |
| 4 | 5000 | 500 | 80 | 8 |
| 5 | 6000 | 600 | 90 | 9 |
| 6 | 7000 | 700 | A0 | 10 |
| 7 | 9999 | 999 | B0 | 11 |

Źródła: PRG0F:$FDA8–$FDC8 (EXP), $FDC8–$FDE0 (MP), $FDE0–$FDE8 (HP).
Ostatni wpis EXP to 9999, nie 8000. Nie oznacza poziomu 8: przed awansem kod
sprawdza, czy dolne trzy bity $D3 są już równe 7. Pełne lokalizacje każdej pozycji
zawiera `progression_levels.csv`.

## Dodawanie EXP i awans

PRG08:$A6AB, $A6B4 i $A6BD dezaktywują przedmiot, po czym dodają odpowiednio
10, 30 lub 50 EXP dziesiętnie. Wspólna ścieżka $A6C4 przenosi cyfry od dziesiątek.
Jeżeli przeniesienie wychodzi poza czwartą cyfrę, $A6D9 zapisuje 9999 i natychmiast
wraca: pomija porównanie progu i zapis polecenia dźwięku.

Bez przepełnienia porównanie od najbardziej znaczącej cyfry uruchamia awans przy
EXP równym lub większym od progu. Procedura podnosi poziom najwyżej o jeden na wywołanie,
ładuje nowy próg, maksimum MP i maksimum HP, próbuje utworzyć obiekt efektu poziomu,
ustawia $03D5 na B4 i polecenie dźwięku $01 na E4. Zwykłe zebranie EXP zapisuje 2B.
Brak wolnego obiektu nie cofa awansu ani polecenia dźwięku.

Bieżące HP, kopia paska HP i bieżące MP pozostają niezmienione przez awans.
Zwiększenie maksymalnej pojemności nie jest automatycznym uzupełnieniem liczników.

Ważny warunek lokalny: po `INC $D3` instrukcja PRG08:$A6FD ładuje do Y całe $D3,
bez maskowania, do odczytu tabeli HP. MP i EXP korzystają następnie z dolnych trzech bitów.
Normalne ustalenia o pojemnościach dotyczą $D3 zawierającego sam poziom 0–7.
Bezpośrednie próby z bitami 10/40/80 potwierdzają odczyt poza ośmioma wpisami HP;
nie ustalono osiągalności takiego przypadku w rozgrywce. Bramka zbierania blokuje
bity A0, lecz sama nie dowodzi wszystkich globalnych niezmienników stanu.

Dowody CPU: D_CPU01 bada wszystkie 10000 poprawnych wartości EXP dla trzech dodatków;
D_CPU02 bada progi, rozbieżny poziom/EXP i jawnie sztuczne stany z wyższymi bitami.

## MP: podnoszenie przedmiotów i opłacanie efektów

PRG08:$A73D dodaje 5 MP, $A744 dodaje 10 MP dziesiętnie. Kod najpierw obsługuje
przeniesienia i nasycenie do 999, potem ogranicza wynik do maksimum $F5–$F7.
Dezaktywuje przedmiot i zapisuje polecenie dźwięku 2B. D_CPU03 obejmuje wszystkie
poprawne wartości MP od zera do maksimum dla każdego z ośmiu poziomów.

PRG09:$BD46 przyjmuje koszt jako dwie cyfry w bajcie A. Po pomyślnym odjęciu
zwraca carry=0. Gdy środków brakuje, przywraca wszystkie trzy oryginalne cyfry MP
z $38–$3A i zwraca carry=1. Dokładnie wystarczająca liczba MP daje sukces oraz zero.
Rollback dotyczy MP; nie oznacza przywrócenia wszystkich bajtów roboczych.

Niezerowe $01A5 daje sukces bez opłaty, jeszcze przed sprawdzeniem bitu 80 w $D3.
Przy zerowym $01A5 ujemne $D3 blokuje wydatek. Nazwa flagi opisuje lokalny efekt;
nie przypisano jej oficjalnego trybu debug ani sposobu aktywacji.
D_CPU04 sprawdza 1000 wartości MP i dziesięć kosztów, D_CPU05 kolejność obu bramek.

## Leczenie i wybrane efekty

Serce, wejście PRG08:$A78A, dodaje 10 hex surowych jednostek HP (jedną komórkę),
ogranicza wynik do $06BB, dezaktywuje przedmiot i zapisuje polecenie A1.
Wspólne leczenie PRG09:$BD98 ogranicza do tego samego maksimum.
Twierdzenie o `min(HP + leczenie, maksimum)` wymaga poprawnego zakresu: samo ADC
nie ma obsługi przepełnienia. Zwykłe maksimum B0 i największy sprawdzony dodatek 40
nie przepełniają bajtu; sztuczne HP=F0 z dodatkiem 40 daje zawinięcie do 30.

| $06BD | Typ obiektu | Procedura w PRG09 | Koszt MP, dzies. | Dodatek HP, hex | Komórki |
|---|---|---|---:|---|---:|
| 00 | 70 | $B6BA | 60 | 20 | 2 |
| 01 | 72 | $B6CD | 90 | 40 | 4 |

Obie procedury wymagają nowego naciśnięcia Select, bitu 20 w $1F.
Sprawdzają powodzenie opłaty przed leczeniem. Pobierają koszt również wtedy,
gdy HP już jest pełne. Nazwy oficjalnych czarów i kolejność ich zdobywania nie są
potrzebne do rozstrzygnięcia tej ścieżki i nie zostały wywnioskowane z samych indeksów.

PRG07:$AE3A wybiera typ z trzynastu bajtów $AE93–$AEA0. Przenosi pozycję gracza
do globalnego slotu 3, zeruje prędkości i pola pomocnicze, ustawia flagi 88 lub 8C,
a także odświeża ikonę przez PRG0F:$F65F. Indeks 0C wyłącza ten slot.
PRG09:$BF3E pobiera wskaźnik grafiki z $AAA5+typ i procedury z $AB87+typ.
Przejrzane są fragmenty tabel dla typów 70–86, nie całe tabele wszystkich obiektów.

D_CPU08 wykonuje inicjalizację, rzeczywistą pętlę PRG09:$BE90, dispatch, opłatę,
leczenie, ruch/culling oraz wejście do rysowania PRG0F:$F6ED. Obejmuje brak MP,
wartość o jeden poniżej kosztu, dokładny koszt, pełne HP i brak naciśnięcia Select.
Żaden z tych wywoływanych podprogramów nie jest zastąpiony atrapą. Grafika końcowa
na PPU i zachowanie w pełnej rozgrywce nie były obserwowane.

## Zbieranie przedmiotów

Dispatcher PRG08:$A64D akceptuje typy 40–6F, zeruje bit 0 i używa jednej z 24 par.
Odczyt wskaźnika ma bazę $A629, ale faktyczny używany fragment danych zaczyna się
od $A669. `pickup_effects.csv` zachowuje pełne mapowanie 24 par i adresy fizyczne.

| Para typów, hex | Lokalny efekt |
|---|---|
| 40/41 | HP +10 hex |
| 42/43, 44/45 | MP +5, +10 dziesiętnie |
| 46/47, 48/49, 4A/4B | EXP +10, +30, +50 dziesiętnie |
| 4C/4D | wynik +100 dziesiętnie |
| 4E/4F | przejście: indeks sceny z pola obiektu $0593,Y |
| 50/51 … 66/67 | 12 par kierujących do nieprzejrzanego $A7DB |
| 68/69, 6E/6F | dezaktywacja, następnie obrażenia 4 surowych jednostek |
| 6A/6B | dodatkowa próba, z bramką równości do 0A |
| 6C/6D | wejście w obrażenia 4 bez początkowej dezaktywacji |

Nie przypisano wyglądu ikon do wszystkich typów. Procedura zmiany sceny jest
przejrzana do wywołań usług; sam przebieg przejścia nie jest nowym testem integracyjnym.
D_CPU16 łączy oba wejścia obrażeń z rzeczywistą procedurą PRG0E:$DDD9, także dla
HP dokładnie równego 4: zostaje zero i reakcja na trafienie, nie gałąź śmierci.

PRG08:$A14F skanuje względne indeksy od $04EF do 1, pomijając 0. Przedmiot musi
być aktywny (bit 80), mieć dopuszczony typ, nakładać się prostokątem i spełniać
warunek prędkości Y: 00–7F lub FB–FF. Wartości 80–FA są odrzucane.
Względny indeks przedmiotu Y odpowiada globalnemu slotowi Y+3.

Próba prostokąta $A528 używa tylko młodszych bajtów pozycji i arytmetyki modulo 256.
Przy zwykłej geometrii zbierania różnica `gracz − przedmiot` mieści się w pionie
od −20 do +26, a w poziomie od −13 do +12 pikseli. Starsze bajty pozycji nie są
sprawdzane. Testy przeszły wszystkie 256 różnic każdej osi oraz 256 prędkości Y.

PRG08:$A05B potrafi wykonać `PLA; PLA; RTS`, odrzucając adres powrotu bezpośredniego
wywołującego. To przerwanie całego zadania nadrzędnego, nie zwykły wynik logiczny.
Bramki obejmują $D3&A0 oraz parę $03D8/$03D9. Gdy pierwsza flaga jest niezerowa,
a druga zerowa, następuje zapis CHR R1=2 przed sprawdzeniem $D3. Testy potwierdzają
powrót z poprawnym SP oraz brak zmiany banków PRG w tej ścieżce.

## Pętla obiektów i efekt poziomu

PRG09:$BE90 zwiększa $D8 oraz licznik $D9/$DA, a parzystość $D9 steruje częścią
aktualizacji/rysowania i wyborem CHR $47. Pętla obejmuje $04EF+4 globalne sloty.
Bit 80 oznacza aktywność; 08 wymusza wywołanie procedury; 04 omija bramki parzystości;
40 pomija dodawanie prędkości; 20 uczestniczy w atrybucie grafiki.
Globalny slot 3 nie jest dezaktywowany przez zwykłe wyjście poza widok.

PRG09:$BF68 dodaje podpisane prędkości do par współrzędnych. Wyjście poza widok
wyznaczają młodsza względna współrzędna Y co najmniej D8 oraz niezerowy starszy
bajt względnego X. Starszy bajt roboczy Y jest odejmowany z carry po `CMP D8`,
nie po pierwotnym odejmowaniu Y: nie przedstawiamy go jako ogólnej poprawnej
16-bitowej odległości Y. Pełny system fizyki wrogów nie jest odtworzony.

Alokator PRG0F:$E0ED szuka od indeksu $04EF−1 do 1, pomijając 0 i górny indeks
używany przez skan zbierania. Wolny slot daje A=0; brak miejsca A=FF.
PRG08:$A878 tworzy typ 96 z flagą 80, kopiuje pozycję gracza, zeruje prędkość X
i zapisuje prędkość Y=FD. Testy obejmują każdy wolny slot przy parametrze 16 oraz
pełną pulę. Nie uogólniono zachowania na niepoprawne parametry puli 0/1.

## Wynik i dodatkowe próby

Usługa PRG0E:$C746 prowadzi do $D8B5. Górna połówka A oznacza przyrost cyfry,
dolne trzy bity pozycję dziesiętną; 11 daje +10, 12 daje +100 dziesiętnie.
Po zwykłym dodaniu kod porównuje wynik z progiem wskazanym przez $030F.
Tabela PRG0F:$FDE8–$FE0C zawiera 10000, 50000, 100000, 200000, 500000, 999999.

Najwyżej jedna dodatkowa próba przypada na wywołanie. Przy zaliczeniu progu
$030F rośnie o 6 również wtedy, gdy $030E jest już równe 0A i nie może wzrosnąć.
Bramka jest porównaniem równości, nie ogólnym ograniczeniem wartości większych od 10.
Przepełnienie wyniku do 999999 wraca wcześniej, pomijając porównanie i nagrodę.

Ostatni próg jest szczególny: sztuczna wartość osiągająca dokładnie 999999 może
przesunąć indeks poza sześć przejrzanych wierszy. Zwykłe dodatki +10/+100 od wyniku
z zerową cyfrą jedności nie osiągną tej wartości bez ścieżki przepełnienia, która
pomija nagrodę. Nie stwierdzono exploitu ani osiągalności dalszych odczytów w grze.

PRG0F:$F681 zapisuje kafelek poziomu jako `($D3&7)+60`, a prób jako `$030E+5F`.
Przy kodzie cyfry zero równym 60 oznacza to wyświetlanie liczby prób minus jeden:
03 wewnętrznie daje 2, a graniczne 0A daje 9. Dowód dotyczy bufora kafelków,
nie nowej obserwacji ekranu emulatora.

## Zapis i odtwarzanie postępu

PRG07:$AEC6 zapisuje następujące 11 bajtów. Dalszy mechanizm kopiowania do
$06CD–$06D7 był przejrzany w poprzednich etapach.

| Pole snapshotu | Bieżące źródło | Długość |
|---|---|---:|
| $06C2 | $D3&07 | 1 |
| $06C3 | $06B9, HP | 1 |
| $06C4 | $EA, MP | 3 |
| $06C7 | $ED, EXP | 4 |
| $06CB | $06BE, dwa bajty flag | 2 |

PRG07:$AEF7 kopiuje te pola z powrotem, następnie skacze do $B7F4. Ten podprogram
nadpisuje bieżące i wyświetlane HP pełną wartością z tabeli, ustawia maksymalne MP
oraz następny próg EXP. Nie zapisuje $06BB i nie ogranicza bieżącego MP do maksimum.
Nie należy więc interpretować samego kopiowania $06C3 jako zachowania zapisanej
liczby HP. Są to ustalenia lokalnej ścieżki; pełne zachowanie wszystkich wariantów
continue, odtwarzania sceny i haseł wymaga przeglądu pozostałych wywołujących.
Maska indeksu w $B7F4 wynosi 0F, a potwierdzona domena tabel 0–7.

## Co pozostaje otwarte

- Wspólny handler przedmiotów PRG08:$A7DB: odblokowywanie czarów, maski i kolejność.
- Pozostałe dziesięć aktywnych efektów oraz ich obrażenia, czas działania i koszty.
- Producenci $01A5, pełne niezmienniki $D3 oraz parametru $04EF.
- Inne kandydaty zapisów: PRG07:$AD1E (m.in. ścieżka zależna od $01A5), kod haseł
  w okolicy $B645/$B693, końcowe ustawienia HP w PRG09:$A6E8–$A6EE. To tropy,
  nie dodatkowo zatwierdzone zakresy ani twierdzenie o kompletności listy zapisów.
- Pełna geometria, ruch i ataki gracza, RNG, wrogowie, bossowie i przejścia scen.
- Import natywny MesenCE/Ghidra i pełna walidacja na emulatorze z NMI/IRQ/PPU.

Zachowano wcześniejsze 51 twierdzeń zewnętrznych jako historyczną bazę badawczą.
Nie zmieniono masowo ich statusu na potwierdzony: ten raport rozstrzyga konkretne
procedury ROM-u, a nie całą semantykę materiałów zewnętrznych.
