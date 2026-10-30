# AI rodzaju 00, śmierć przeciwników i tworzenie nagród — Stage 02G

Analiza niezależna na oryginalnym ROM-ie NTSC-U o SHA-256
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Analiza i testy: 2026-10-22; domknięcie dokumentacji: 2026-10-29.
STATIC oznacza przejrzane instrukcje/dane; CPU_TEST oznacza wykonanie oryginalnych
instrukcji w kontrolowanej pamięci, bez patchowania ROM-u i zastępowania callee.
Nie przeprowadzono pełnej emulacji NES. Liczby wywołań AI nie są liczbami klatek wideo.

## Zakres i dane dowodowe

I01..I46 dodaje 31 zakresów kodu i 15 danych, 769 instrukcji, 2164 bajty PRG oraz
34 krawędzie pośrednie. Adresy CPU, bankowe, PRG i plikowe oraz warunki mapowania
są zapisane w `analysis/reviewed_ranges.csv`, `functions.csv`, `evidence.csv`
i poszczególnych tabelach. W poniższym tekście adresy, identyfikatory rodzajów,
stanów, maski i surowe bajty są szesnastkowe; liczności i czasy wywołań — dziesiętne.
Zakresy adresów są półotwarte. W PRG0A/0B wymagane jest odpowiednie R6;
PRG0E i PRG0F zajmują stałe okna C000 i E000 w potwierdzonym trybie MMC3.

| Nowy plik w analysis/ | Wiersze | Zawartość |
|---|---:|---|
| enemy_state_and_drop_dispatch.csv | 34 | adresy powrotu stanów i wyborów dropów |
| enemy_drop_choices.csv | 64 | po 32 selektory zwykłej/specjalnej tabeli |
| enemy_drop_triplets.csv | 64 | zależne trójki dla wszystkich indeksów początkowych |
| collectible_spawn_profiles.csv | 24 | flagi typów i wybór sposobu alokacji |
| special_death_rewards.csv | 12 | typ nagrody oraz przesunięcie Y |
| special_death_scatter_pairs.csv | 32 | nakładające się pary z 33 bajtów |
| kind00_collision_frames.csv | 45 | sześć normalnych stanów rodzaju 00 |
| enemy_distance_band_tables.csv | 5 | parametry klasyfikatora odległości |
| cross_bank_instructions.csv | 1 | instrukcja przecinająca granicę stałych banków |

Pełne obserwacje: `cpu_stage02G.json`, `cpu_stage02G_vectors.csv`,
`cpu_stage02G_trace.csv`. Plik `.partial.json` zachowuje wynik każdej grupy.
`stage02G_development_notes.json` dokumentuje także nieudane pierwsze oczekiwanie
testu i jego korektę. Nie ukryto tego przebiegu pod końcowym PASS.

## Rodzaj 00: stany AI nie są tożsame z indeksami kolizji

PRG0B:814C wywołuje 0E:C7A0 → 0F:E2F9 z A=0, Y=6. Dziewięć wskaźników
adres−1 w 0B:815C..816E wybiera normalne stany 0..5 oraz selektory wirtualne:
6 → zwykła śmierć 80D5, 7 → obsługa trafienia C7A3/E35B, 8 → RTS w 8010
przy zatrzymaniu. Nie wolno indeksować nimi wszystkich danych kolizji.

Tablica kolizji rodzaju 00 w 06:8622..862E ma tylko sześć wskaźników.
W 06:9000..90B4 znajduje się 45 czterobajtowych rekordów: 8, 1, 9, 9, 9, 9
klatek dla stanów 0..5. Dane od 90B4 należą do następnego rodzaju.

| Stan | Procedura PRG0B | Kontrakt lokalny |
|---|---|---|
| 0 | 816E | co trzeci wybrany przebieg AI: decyzja o ataku albo krok X o 1 |
| 1 | 81F0 | ruch Y o 5 na wywołanie; ujemny wynik 36 przywraca stan 0 |
| 2..4 | 8211 | 9 klatek, po 3 wywołania: powrót do stanu 0 po 27 |
| 5 | 8228 | 9 klatek, po 2 wywołania: sekwencja 18 wywołań, potem stan 1 |

0B:8091 porównuje okres w A z 0423,X. Gdy okres nie upłynął, usuwa adres powrotu
wywołującego przez PLA/PLA/RTS. Po spełnieniu progu nie zeruje timera.
Podobna bramka 0A:8051 zeruje go po spełnieniu progu. Nie są wymienne.

Ruch stanu 0 korzysta z 81CE i E393. Przy chodzeniu ustawia zwrot i wykonuje
X=1, Y=0; 8CC5 sprawdza wynik ruchu 36. Nieujemny wynik wybiera stan 1,
ustawia 047D bit40, czyści 0469 bit02 i zeruje klatkę/timer. Wynik ujemny
pozostawia normalną ścieżkę chodzenia. W fixture z wyłączonym terenem
(0473 bit80=0) wynik jest 36=0, a więc po pierwszym kroku następuje spadanie.
To nie dowód ciągłego chodzenia po prawdziwym podłożu.

W stanie 5 moduły przemieszczeń kolejnych klatek to X=[0,2,3,4,5,6,7,8,8]
i Y=[8,6,4,2,0,2,4,6,8]. W klatce 4 czyszczony jest bit02 kierunku pionowego.
Dla fixture z początkowym 0469=C3 suma wynosi X+43, Y+0. Po końcu wybierany
jest stan 1 i czyszczony 047D bit40. Pomocnicza 8281 dla 36 bit40 wybiera
stan 41 i ustawia 047D bit40, a dla ujemnego 36 wybiera stan 42 i go czyści;
resetuje klatkę i timer. Nie nadano tym stanom nazw opartych wyłącznie na wyglądzie.

## Cel AI i asymetryczne przedziały ataku

D4..D7 stanowi `EnemyTargetPositionSnapshot`: Ylow/Yhigh/Xlow/Xhigh.
Wcześniej rozpoznany ogon 08:ABA8 kopiuje C9..CC, z wyjątkiem warunku
06BD=0B oraz 0593≠0. Warunek dotyczy **0593**, nie licznika 0596 slotu 3.
Powiązanie efektu 0B z Twin Power nie dowodzi, że każda procedura AI czyta
wprost pozycję graficznego sobowtóra. Pełne pochodzenie celu pozostaje otwarte.
Grupa 14 wykonuje ten ogon i nowego konsumenta E393 jako test integracyjny,
bez powtórzenia wcześniejszego pełnego pipeline'u.

0F:E393 oblicza różnice przeciwnik−cel i przez EB63 tworzy maskę 3F.
Klasyfikator korzysta ze znaku wysokiego bajtu różnicy oraz jej bajtów 22/23;
selektor 1 dotyczy X, selektor 3 dotyczy Y. Wyniki poniżej są dla signed16:

| Różnica X, dziesiętnie | Indeks | Maska z E3E2 |
|---|---:|---|
| < −40 | 7 | 88 |
| −40..−33 | 6 | 88 |
| −32..−25 | 5 | 08 |
| −24..−1 | 4 | 40 |
| 0..23 | 3 | 80 |
| 24..31 | 2 | 04 |
| 32..39 | 1 | 44 |
| ≥ 40 | 0 | 44 |

| Różnica Y, dziesiętnie | Indeks | Maska z E3EA |
|---|---:|---|
| < −32 | 7 | 22 |
| −32..−17 | 6 | 22 |
| −16..−2 | 5 | 02 |
| −1 | 4 | 10 |
| 0 | 3 | 20 |
| 1..7 | 2 | 01 |
| 8..15 | 1 | 11 |
| ≥ 16 | 0 | 11 |

Maski są łączone OR. Sześć tablic parametrów po pięć bajtów leży w EBA9..EBC7.
Przetestowano konteksty 1 i 3,
nie wszystkie pięć kontekstów wywołań klasyfikatora.

Rodzaj 00 atakuje lokalnie tylko dla X w **−32..−25 lub 24..31**;
nie jest to symetryczne abs(X)=24..31. Ta decyzja nie sprawdza Y.
0B:81BE zawiera stany `02 03 02 04 02 03 02 02 05 02 03 02 03 02 04 02`.
Indeks to `(97 + slot2C) & 0F`; procedura nie aktualizuje 97. Stan 5 dodatkowo
ustawia 047D bit40 i 0469 bit02. Nie wyznaczono rzeczywistych prawdopodobieństw.
846B może aktualizować zwrot według maski 3F&0C, jeśli pozwala 0469 bit04.

## Zwykła śmierć i kolejka trafienia

0B:80D5..812A przy wejściu w stan śmierci (040F różne od selektora 2F=6)
wykonuje jednorazowe skutki. Bit10 w 047D wyłącza **zarówno drop, jak i score**.
W przeciwnym razie C78E → 0E:DFCB tworzy drop, a 045F jest przekazywane przez
C746 do wcześniej rozpoznanej procedury score D8B5. Pełna pula obiektów nie
blokuje naliczenia score. Niskie trzy bity 045F kodują pozycję cyfry, wysoki
nibble — ilość; 21 w fixture daje 20 punktów. Bit40 w 0487 niezależnie wyłącza dźwięk 51.

Procedura ustawia stan 6, resetuje klatkę/timer i przechodzi przez osiem klatek.
Dla normalnego wejścia po resecie ósme wywołanie czyści 0469, 0473 i 047D.
Nie rozszerzono tego czasu na dowolne początkowe timery, np. zawinięcie FF.
Jeżeli zakolejkowane trafienie jest śmiertelne, E2F9 najpierw widzi stare HP>0,
wybiera selektor trafienia 7 i odejmuje obrażenia. Śmierć zaczyna się w następnym
wywołaniu. Generowanie dropu nie jest przyznaniem EXP; nadal wymagana jest kolekcja.

## Trzy powiązane wybory i osobna bramka 1-UP

Zwykły generator 0E:DFCB ma wyjątek: gdy `(DA&03)==0 && (D9&FC)==0`,
tworzy pojedynczy typ 6A przez E01B. Jest to bramka 1-UP, a nie czwarty losowany drop.
Poza nią początek wynosi `s=(D8>>1)&31`; kolejne indeksy to s, s+10 i s+20
modulo 32. Wartości 10 i 20 są dziesiętne. Zwykła tabela leży w DF7B,
specjalna w DF9B; specjalny generator 0E:DF37 nie wykonuje bramki 1-UP.

Generator nie wywołuje aktualizacji 97 i nie tworzy trzech niezależnych losowań.
D8 jest osobnym licznikiem bajtowym, D9/DA osobnym licznikiem 16-bitowym:
nie opisujemy ich jako jednego licznika 24-bitowego. Nie przeliczono bramki
na sekundy ani nie uznano częstości wpisów za rzeczywistą częstość w rozgrywce.

| Selektor | Typ | Wcześniej potwierdzony efekt zebrania | Wpisy zwykłe | Wpisy specjalne |
|---:|---|---|---:|---:|
| 0 | 46 | EXP +10 | 5 | 6 |
| 1 | 48 | EXP +30 | 5 | 5 |
| 2 | 4B | EXP +50 | 4 | 5 |
| 3 | 43 | MP +5 | 5 | 6 |
| 4 | 44 | MP +10 | 5 | 5 |
| 5 | 4C | score +100 | 6 | 5 |
| 6 | 41 | HP +16 surowych jednostek | 1 | 0 |
| 7 | 69 | obrażenia 4 surowe jednostki | 1 | 0 |

Te liczności opisują po 32 bajty tabel, nie zmierzone prawdopodobieństwa.
DFBB zawiera osiem wskaźników adres−1 do ustawienia typów.

## Dwa odmienne kontrakty tworzenia obiektów

0F:E01B..E08D obejmuje wejścia ustawiające typ oraz wspólny spawner dropu.
Wcześniejszy alokator E0ED wybiera wolny slot od N−1 w dół do 1, z wyłączeniem 0.
Kopiuje X przeciwnika oraz 16-bitowe Y−16; zapisuje typ 056B, flagi z 24-bajtowej
tablicy FEDE, vx0543=0, vy0557=F9 (−7), licznik0593=0 i timer05A7=7.
Pierwszy i drugi udany obiekt trójki otrzymują vx odpowiednio −1 i +1, vy=FA (−6).
Trzeci pozostaje z vx0/vy−7. Pierwsza nieudana alokacja kończy trójkę; carry
sygnalizuje niepowodzenie. Indeks X przeciwnika jest zachowany.

0F:E08D..E0D5 to odmienny spawner nagrody końcowej. Wybór z tablicy E0D5 jest
indeksowany parą typu: niezero **wymusza slot 1, nawet aktywny**, zero używa alokatora.
Kopiuje XY bez odejmowania 16 od Y, zapisuje typ, flagi FEDE|40 i zeruje vx/vy.
**Nie resetuje 0593 ani 05A7**. X zostaje indeksem typu, więc wywołujący odtwarza 2C.
Wszystkie 24 profile oraz zachowanie sentinelów 77/88 w liczniku/timerze objęto testami.

### Jedna instrukcja w dwóch bankach fizycznych

`PRG0E:DFFF: 99 43 05` to jedna instrukcja `STA $0543,Y`. Opcode 99 leży
w ostatnim bajcie PRG0E, a operandy 43/05 w PRG0F:E000/E001. Oba okna są stałe.
Eksport źródeł zapisuje fizyczne fragmenty `.byte` w odpowiednich bankach,
natomiast indeks instrukcji liczy całość raz. E000/E001 nie stały się fałszywymi
wejściami procedur. Audyt sprawdza tę konkretną granicę i pełne pokrycie bajtów;
pełny build potwierdza zachowanie ROM-u.

## Konstruktor śmierci specjalnej oraz ograniczony zakres rodzaju 50

0E:D9D7 wybiera najniższy slot z wyzerowanym 0469 bit80 w zakresie
0..06F8−1. Przy pełnej puli stan Z pochodzi z CPY, przy znalezieniu wolnego
zwraca A=1/Z=0. Konstruktor korzysta z Z, nie z rzekomego numeru slotu w A.
Przypadku 06F8=0 nie zaliczono.

0A:8061..8136 używa wolnego slotu lub bieżącego 2C przy pełnej puli.
Zeruje 0419, 042D, 0423, 040F, 0473; ustawia 0437=stary_kind−50,
kind=5B, 0469=90 i kopiuje score045F. Alternatywne wejście 8098 zmienia kind na 60.
Ten kod **nie inicjalizuje pozycji nowego slotu ani 047D**.
80A1 zapisuje wspólną kotwicę 0189 (Y) i 018B (X), przyciętą do przedziałów
kameraY+30..+B0 i kameraX+30..+D0 hex. Testy obejmują dodatnie współrzędne
przy kamerze zero, nie wszystkie przypadki zawinięcia 16-bitowego.

Dispatcher rodzaju 50 w 0A:816E używa A=0/Y=4 i siedmiu wskaźników 817E..818C.
Normalne ciała stanów 0..3 pozostają nieprzejrzane. Śmierć 4 prowadzi do 82C5,
trafienie 5 do C7A3, zatrzymanie 6 do RTS. 82C5 tworzy 5B, kolejkuje dźwięk D2
i dezaktywuje stary slot, jeśli nowy jest inny. Gdy znajdzie inny aktywny kind50,
zmienia nowy obiekt na 60 i ustawia 047D bit08, tłumiąc sygnał zakończenia.
Nie przypisano rodzaju 50 do nazwanego bossa na podstawie samego numeru.

## Cykl obiektów 5B i 60

5B ma własny dispatcher 0A:89FA dla stanów 0/1; nie używa bramki HP,
ponieważ 0437 przechowuje tutaj podtyp. Stan 0 (8A12) nalicza score tylko,
gdy OR klatki0419 i cyklu042D jest zerem. Osiem klatek przez 16 cykli daje
**128 wybranych wywołań AI**. 8AA9 jest wywoływane tylko dla nieparzystych klatek;
w cyklu zero daje cztery próby trójek, czyli maksymalnie 12 prób utworzenia dropu.

Po 128 wywołaniach 8A5D ustawia 49=2, X=kameraX+D0 oraz Y=kameraY+offset.
Tablica typów 8A91 dla 12 podtypów to
`54 50 5C 56 00 00 00 66 58 5E 00 00`;
tablica przesunięć Y w 8A9D to
`C0 C0 B0 C0 00 00 00 C0 B0 B0 00 00`.
Niezerowy typ uruchamia E08D, po czym odtwarzany jest indeks przeciwnika.
Stan zmienia się na 1. Procedura 8A43 czeka **100 kolejnych wywołań** przez 8051,
ustawia F8 bit20 tylko dla sceny 1B i czyści 0469/0473/047D.

60 w 0A:8B1A także nalicza score raz, ale uruchamia 8AA9 przy każdym wywołaniu.
Pierwszy cykl daje osiem prób trójek: maksymalnie 24 próby, nie gwarantowane
24 aktywne przedmioty. Pula N=20 mieści co najwyżej 19 w tych alokacjach;
testy obejmują dostępność 0, 3 i 19 slotów. Po 128 wywołaniach ustawiany jest
F8 bit80, chyba że 047D bit08 go blokuje; następuje dezaktywacja i wyzerowanie
070A/B. Nie używa końcowej tablicy nagród 5B.

## Rozrzut: wspólna kotwica, nakładające się pary i carry

0A:8AA9 odtwarza pozycję ze wspólnej kotwicy; tylko w cyklu042D=0 wywołuje DF37.
Kierunek pochodzi z 8B16 `[2,0,3,1]`, indeksowanego przez D8&3.
Indeks przesunięcia wynosi `((D8|024D)+97+carry)&31`.
**Carry nie jest zerowane**: w pierwszym cyklu może pochodzić z generatora dropu,
a w kolejnych z wejścia do procedury. 024D jest odrębnym wejściem pamięci.

33 bajty w 8AF5..8B16 tworzą 32 **nakładające się** pary:
Xmag=byte[i], Ymag=byte[i+1], nie 16 niezależnych słów. Niskie dwa bity 0469
określają kierunki. 0F:E44E wykonuje przesunięcia przez E478/E492 i E72D.
0473 bit80 włącza dalszą, nieprzejrzaną obsługę terenu E4AC; konstruktor ustawia
0473=0 w badanej ścieżce. Grupa 15 używa cyklu 1, aby oddzielnie sprawdzić
oba wejściowe carry bez wpływu generatora. Nie zastąpiono procedury terenu atrapą.

## Wykonane testy i jawne ograniczenia

| Grupa | Zakres | Zapisane przypadki |
|---:|---|---:|
| 1 | zależne trójki i ograniczenie puli | 2560 |
| 2 | bramka 1-UP | 224 |
| 3 | pola obiektów dropu | 90 |
| 4 | wymuszony slot nagrody | 72 |
| 5 | zwykła śmierć i jednorazowe skutki | 64 |
| 6 | śmiertelne zakolejkowane trafienie | 3 |
| 7 | przebiegi stanów rodzaju 00 | 105 |
| 8 | granice przedziałów odległości | 357 |
| 9 | wybór ataku rodzaju 00 | 96 |
| 10 | alokacja konstruktora i kotwica | 63 |
| 11 | śmierć rodzaju 50 z towarzyszem/bez | 4 |
| 12 | pełny lokalny cykl 5B: 128+100 wywołań | 120 |
| 13 | pełny lokalny cykl 60 | 24 |
| 14 | integracja snapshotu celu | 12 |
| 15 | carry i wszystkie pary rozrzutu | 256 |
| **Razem** | **15 grup PASS** | **4050** |

Zapisano 11437 wierszy trace. Liczba przypadków oznacza zapisane obserwacje,
nie liczbę wszystkich asercji lub wywołań: np. grupy 12/13 używają 20/6
fixture wielowywołaniowych. Wszystkie poprzednie zestawy zachowano, nie uruchamiano ich ponownie.

Pierwsze oczekiwanie w grupie 7 błędnie zakładało ciągłe chodzenie przy wyłączonym
terenie. Poprawiono oczekiwanie zgodnie z rzeczywistym warunkiem 36=0, powtórzono
tylko tę niezaliczoną grupę i wykonano nowe 8..15; zaliczone 1..6 zachowano.
Wstępny błąd inicjalizacji Disassembler w generatorze wystąpił przed zapisaniem
wyników i został poprawiony. Opis symetrycznego progu ataku skorygowano po
odczycie zapisanych testów granicznych; nie zmieniono obserwacji ani bajtów ROM-u.

NOT_TESTED/UNRESOLVED: pełny NES i timing, natywne importy MesenCE/Ghidra,
pełne E4AC i C773/C776, odświeżanie cache, żywe AI rodzaju 50 i pozostałych rodzajów,
pełna proweniencja celu Twin Power, osiągalność wszystkich syntetycznych stanów,
nazwy graficzne bossów, globalne prawdopodobieństwa dropów, geometria PNG↔ROM
oraz mapowanie 32 konfiguracji scen na osiem sektorów. Oryginały map i poradnika
pozostają niezmienione. Następny priorytet: pełne ścieżki terenu i producenci cache.
