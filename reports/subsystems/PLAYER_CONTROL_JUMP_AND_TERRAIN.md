# Stage 02E — sterowanie graczem, fazy skoku i odczyt terenu

Stan: 2026-10-21. Analiza oryginalnych bajtów KickMaster NTSC-U o SHA-256
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
Adresy są kwalifikowane bankiem. PRG08 jest rezydentne w oknie R7 przy A000,
PRG0E/0F są stałe przy C000/E000. Pełne offsety bankowe, PRG i plikowe znajdują się
w `analysis/reviewed_ranges.csv`, `reviewed_instructions.csv` i indeksach tabel.
Wartości stanów i masek w poniższych tabelach są szesnastkowe; liczby wywołań są dziesiętne.

## Zakres i dowody

Nowe G01–G49 obejmują 41 zakresów kodu i 8 danych: 1013 instrukcji, 2249 bajtów.
To rozwinięcie programu/RAM oraz pracy nad graczem z głównego planu. Nie zamyka całego
Stage03 ani kompletnej rekonstrukcji gry. Przejrzano lokalne procedury normalnej rodziny
stanów 00–B8; wywoływane procedury destrukcji terenu pozostają częściowo nierozpoznane.

Dowody STATIC: ręczny przegląd granic i przepływu instrukcji, tabele z oryginalnego ROM-u.
Dowody CPU_TEST: 14 nowych grup, 11868 przypadków, 34866 wierszy śladu. Instrukcje wykonuje
vendored py65 z istniejącym modelem MMC3/RAM. Nie patchowano ROM-u i nie zastępowano
wywoływanych procedur. Ustawienia RAM są jawne w skrypcie; nie są zapisem pełnej rozgrywki.
Wyniki wcześniejszych etapów zachowano, bez ponownego wykonywania ich zestawów CPU.

## Sterowanie i wybór ataków

Maski sterowania zachowane z wcześniejszego etapu: 80 A,40 B,08 góra,04 dół,02 lewo,01 prawo.
Nowe naciśnięcia są w `$1F`, przytrzymanie w `$20`, dwa poprzednie przytrzymania w `$0713/$0714`.
Parzysty kod `$CD` identyfikuje stan/fazę; bit0 zachowuje zwrot. Nazwy technik z instrukcji
nie zostały jeszcze przypisane przez porównanie wyglądu animacji i hitboxów.

| Procedura | Bank:CPU | Ustalony kontrakt |
|---|---|---|
| Stanie | 08:B81D | próbki podłoża, wyrównanie Y; nowe A ma pierwszeństwo przed B |
| Chód | 08:B8B5 | kierunek z OR bieżącej i dwóch poprzednich próbek; prawo wygrywa konflikt poziomy |
| Skok | 08:B912 | fizyka, zwrot, nowe B; D1=0 zwykle przywraca stanie |
| Przejście w powietrzu | 08:B92F | po wyborze ataku zwiększa CD o2; nie traktować jako identycznej ścieżki B912 |
| Spadanie | 08:B947 | próbki Y−5/+3, opadanie z indeksem fazy sprzed dekrementacji |
| Kucanie | 08:B9A4 | dół z bieżącej/historii; nowe B używa BCAE, omijając zamianę na A0 od poziomu2 |
| Wybór w powietrzu | 08:B972 | pełna tablica 16 masek; przeciwne/nieobsługiwane kombinacje wracają bez zmiany |

Przy staniu sam kierunek 01 wprowadza 02,02 wprowadza03,04 wprowadza10/11.
Pozostałe maski, w tym kombinacje ukośne, trafiają do wspólnego RTS. To nie jest reguła
wyboru ataku: przy nowym B dół ma pierwszeństwo przed górą, a poziomy kierunek nadal
wpływa na wybrane warianty.

| Wejście selektora | Warunek poziomu/kierunku | Wybrany parzysty stan |
|---|---|---|
| 08:BC56, zwykły | poziom0–3 /4–5 /6–7 | 1E /2C /7E |
| 08:BC34, poziomy w powietrzu | poziom≥5 i zgodny zwrot | A0, D1=80 |
| 08:BC34, pozostałe | niższy poziom lub przeciwny zwrot | zwykły wariant z BC56 |
| 08:BC81, dół w powietrzu | poziom0 /≥1 | 0E /1C, D1=00 |
| 08:BC99, dół na ziemi | poziom0–1 /≥2 | 12 przy podłożu /A0, D1=00 w drugiej gałęzi |
| 08:BCBE, góra | poziom7 | 42 |
| 08:BCBE, góra | poziom3–6 i dowolny bit poziomy | 5C |
| 08:BCBE, pozostałe | — | AC |

Oddzielne wejścia BC67 i BCCF pomijają odpowiednio zamianę poziomu6 i7. Ich lokalne
kontrakty są sprawdzone, lecz pełny wykaz wywołujących ścieżek pozostaje otwarty.
Bezpośrednie BC34 dopuszcza również brak bitu poziomego; normalna tablica B972 kieruje
maskę00 do BC56. Nie należy utożsamiać kontraktu wejścia z jego normalną osiągalnością.

`player_direction_dispatch.csv` zapisuje 32 pary z dwóch tablic split-pointer;
`player_air_attack_selection.csv` zawiera wszystkie 256 kombinacji poziomu, kierunku i zwrotu.

## Liczniki i przebiegi animacji

Normalny chód 02/04/06/08 trwa po 8 wywołań na fazę. Instrukcja SBC przy B8FA odejmuje07,
ale nie poprzedza jej SEC: carry pochodzi z dawnego bitu7 CD, równego0 dla normalnego chodu.
To daje efektywne porównanie z8. Nie rozszerzamy tego wniosku na syntetyczne CD z bitem80.

| Początkowy stan | Procedura | Wywołania/fazę | Fazy / koniec | Łącznie wywołań |
|---|---|---:|---|---:|
|12|08:B9D4|3|12..1A →10|15|
|1E|08:BA38|4|1E..2A →00|28|
|2C|08:BA42|4|2C..40 →00|44|
|42|08:BA4C|1|sekwencja BA63, koniec przy indeksie32|32|
|5C|08:BA84|3|5C..7C →00|51|
|7E|08:BA8E|3|7E..9E →00|51|
|A0|08:BA98|6|A0..AA →0A przy wolnej przestrzeni nad głową|36|
|AC|08:BB21|3|AC..B6 →00|18|

Wpis B8 również wskazuje BB21, lecz zwykły przebieg od AC nie wyświetla go jako kolejnej
fazy: próg końca jest wyłączny. Dlatego nie wynika z tablicy siedem faz po trzy wywołania.
Sekwencja42 jest osobną tablicą; D3&A0 może zamrozić jej licznik, choć fizyka nadal się wykona.
Wariant A0 używa kroków 2,3,3,3,3,2 piksele/fazę; bez przeszkód i obcięcia daje96 pikseli
przez36 wywołań. Test utrzymywał kamerę przy graczu, więc nie dowodzi działania scrollingu.
Nie przeliczono tych liczników na sekundy ani klatki NES.

## Skok i ruch

`$D1` jest fazą z bitami sterującymi, nie zwykłą prędkością ze znakiem.
Start BC17 ustawia stan0A, D1=E7 i natychmiast przesuwa gracza o3 piksele w górę.
BCEF rozdziela wznoszenie bitem40. W ujemnej fazie kontynuuje krok3, jeśli A jest
przytrzymane lub któryś z dwóch najmłodszych bitów historii `$21` jest ustawiony.
Zwolnienie ustawia40 i w tym wywołaniu nie zmienia Y; następne wywołania korzystają z tabeli.

Tabela B80A ma 13 bajtów: `03 03 03 03 02 02 02 02 01 01 01 01 00`.
Wznoszenie zwiększa fazę przed odczytem; opadanie zmniejsza fazę, ale odczytuje stary indeks.
Osiągnięcie zera kroku lub sufitu daje D1=0C. Opadanie zaczyna więc od zerowego kroku,
potem czterech kroków1, czterech2 i kroków3. Indeksy13–63 nie są uznane za poprawny
normalny stan tylko dlatego, że pole jest maskowane przez3F.

W próbach bez sufitu, podłoża i ograniczenia ekranu minimalna suma ruchu w górę wyniosła
24 piksele, maksymalna99, licząc początkowe3. Są to wyniki ograniczonego modelu wywołań
z kontrolowaną historią przycisku. Przy przepełnieniu ujemnej fazy do00 kod ustawia40
i wykonuje krok z indeksu0 przed ponownym testowaniem przytrzymania w następnych wywołaniach.
Kontakt sufitu sprawdza bit02; lądowanie sprawdza bit01 i wyrównuje dolny bajt Y do końca
16-pikselowej komórki, po czym zeruje D1.

Ruch poziomy ADFD korzysta z historii i prędkości1. Próbki ściany są przy X±9 oraz
Y−28,−14,0. Bity03 blokują ruch. CE04 na nieparzystym D8 pomija translację, lecz nadal
ustawia znacznik CE40. Zatem CE40 nie jest dowodem rzeczywistego przesunięcia w danym wywołaniu.
Statycznie rozpoznano obcięcie pozycji względem ekranu: lewa20, prawa235, górna31,
a dolna≥206 przechodzi do wcześniejszej procedury terminalnego upadku B007.
Testy potwierdzają lokalne ściany, spowolnienie i poziome granice. Pełne granice kamery,
jej napełnianie buforów i wszystkie tryby przewijania wymagają dalszej integracji.

## Dwa źródła terenu i ważna różnica zwracanych wartości

| Usługa / procedura | Rola |
|---|---|
|0E:C75B →D9E8|bezpośrednia próbka ze współrzędnych bazowych26..29|
|0E:DA07|próbka z podpisanymi offsetami X w A i Y w Y oraz wyborem źródła|
|0E:DAC2 /DAE6|bezpośredni odczyt cache po dodaniu offsetów|
|0E:DD5F|wybór cache, ROM lub obszaru poza domeną|
|0E:DA3D|odczyt atrybutu z danych strony/metatila sceny|
|0F:F50D|obliczenie wskaźnika strony z B9 i BB|
|0E:C767 →DB02|klasyfikacja próbki dla gracza, dotąd analizowana tylko z ograniczonymi zależnościami|
|0E:C773 →DBB7|próbkowanie z możliwą modyfikacją terenu; pełne skutki nadal otwarte|

Cache zaczyna się przy `$05B8`. Po przeliczeniu liniowego Y na strony po240 pikseli:
`index = ((Y mod 240) & F0) | ((X & FF) >> 4)`.
To 16 kolumn i15 używanych rzędów komórek po16 pikseli. Sam odczyt nie uwzględnia strony X;
poprawność zależy od klasyfikatora i producentów cache. Nie wolno traktować bufora jako
całej niezmiennej mapy. Nie odtworzono jeszcze jego uzupełniania podczas scrollingu.

DD5F sprawdza32 flagi scen przy DDB9. Niezerowe flagi dla indeksów dziesiętnych
7,11,14,18,19,22,23,24,25 wymuszają cache. W pozostałych przypadkach porównuje strony
współrzędnych i kamery. Dla poziomego trybu DB04 względne X≥248 wybiera ROM.
Fragment DD92–DD9B nie ma dojścia z przejrzanego wejścia DD5F: poprzedzające BCS/BCC
wyczerpują oba wyniki. Nie przypisano mu aktywnej roli tylko na podstawie instrukcji.

Odczyt ROM używa B9 jako tablicy identyfikatorów stron, BB jako bazy stron po64 bajty,
a C1 jako tablicy czterech atrybutów na metatil. W poziomej konfiguracji:

1. `page_id = ROM[B9 + floor(X/256)]`.
2. `metatile = ROM[BB + 64*page_id + 8*floor((Y mod240)/32) + floor((X mod256)/32)]`.
3. `attribute = ROM[C1 + 4*metatile + 2*floor((Y mod32)/16) + floor((X mod32)/16)]`.

Powyższy wzór kroku3 dotyczy poziomej próbki w pierwszej stronie Y; ogólnie używa się
znormalizowanego Y modulo240 również przy wyborze kwadrantu. Kod przełącza R6 na03B9,
a po odczycie przywraca poprzedni bank i X. B9 może w innych scenach wskazywać inny
rezydentny zakres; nie narzucono wszystkim wskaźnikom banku02.

**DA3D zwraca rzeczywisty atrybut w A/3D, lecz pozostawia3C=03.** D9E8/C75B zachowuje A.
Natomiast DB02 po powrocie klasyfikuje3C i ostatecznie zwraca3C; dla tej ścieżki zwraca03,
nie rzeczywisty atrybut. Po odczycie cache A i3C są jednakowe. Integracyjne próby obu usług
potwierdzają tę różnicę. Rozdzielamy zaobserwowany kontrakt od nieustalonego zamiaru autorów.

## Próbki z rzeczywistych danych sceny00

`analysis/scene00_terrain_samples.csv` zawiera3840 próbek: 16 wpisów stron ×16 kolumn ×15 rzędów.
Użyto rzeczywistych wskaźników sceny00: B9=02:846D, BB=02:847D, C1=02:8FCB.
Identyfikatory stron to00..0E oraz ponownie0E. Sprawdzono każdy wynik kodu DA3D z niezależnym
odczytem opisanej struktury, wraz z przywróceniem R6 i X.

To nie dowodzi długości poziomu4096 pikseli: szesnasty wpis powtarza stronę0E, a granice
rozgrywki i przejścia wymagają osobnego ustalenia. Nie przypisano sceny00 do konkretnej mapy
sprays ani nie uznano zgodności geometrii na podstawie samego wymiaru PNG.
Oryginalne mapy i poradnik są nadal dostępne bez zmian; nie wykonano skalowania ani cropów.
Pełne porównanie geometrii, transformacja współrzędnych i32 sceny→8 sektorów pozostają otwarte.

## Reprodukcja, ograniczenia i następne kroki

Nowy skrypt: `python3 scripts/cpu_stage02e.py inputs/original.nes`.
`--groups 14` uruchamia tylko wskazaną grupę, zachowując pozostałe wyniki z partial JSON.
Nie uruchamiać ponownie zaliczonych grup bez konkretnej potrzeby. Testy kontrolowane nie
obejmują natywnego NES, pełnych NMI/IRQ, interakcji z AI, hitboxów ataków ani ich obrażeń.
Nie importowano eksportów do natywnego MesenCE/Ghidra; status NOT_TESTED pozostaje jawny.

Dziennik nieudanych prób: `analysis/stage02E_development_notes.json`. Rejestracja duplikatu
C37 została zatrzymana przed zapisem tabel. Pierwsza próba grupy14 miała błędną inicjalizację A
przed ACF7; po udokumentowanej korekcie powtórzono tylko tę grupę, zachowując grupy1–13.

Kolejne zadania: rzeczywisty kontakt/atak w08:A2C3, komplet definicji wrogów i ich
hitboxów, C773/destrukcja i producenci cache. Do dalszej pracy nad geometrią używać obecnych
wskaźników i próbek; rozszerzać na32 sceny wraz z ustaleniem granic, a następnie porównywać
z oryginalnymi mapami. Nie rozpoczynać Stage00A od nowa.

## Nowe zakresy przejrzane

| ID | Bank:CPU | Koniec wyłączny | Rodzaj | Nazwa |
|---|---|---|---|---|
|G01|08:AD44|AD61|code|AdvancePlayerAttackPhase|
|G02|08:AD82|AD98|code|SamplePlayerOffsetTerrain|
|G03|08:AD98|ADCF|code|SampleTwoPlayerTerrainPoints|
|G04|08:ADFD|AE14|code|SelectHorizontalPlayerMotion|
|G05|08:AE14|AEB1|code|MovePlayerLeft|
|G06|08:AEB1|AF47|code|MovePlayerRight|
|G07|08:AF47|AF5A|code|SelectFreeVerticalPlayerMotion|
|G08|08:AF5A|AFBC|code|MovePlayerUp|
|G09|08:AFBC|B007|code|MovePlayerDown|
|G10|08:B016|B01F|code|MarkDownwardPlayerMotion|
|G11|08:B80A|B817|data|PlayerJumpStepMagnitudes|
|G12|08:B817|B81D|data|PlayerForwardAttackStepMagnitudes|
|G13|08:B81D|B881|code|UpdateStandingPlayer|
|G14|08:B881|B8A1|data|StandingDirectionSplitPointers|
|G15|08:B8A1|B8B5|code|EnterWalkOrCrouchPlayer|
|G16|08:B8B5|B912|code|UpdateWalkingPlayer|
|G17|08:B912|B92F|code|UpdateJumpingPlayer|
|G18|08:B92F|B947|code|AdvancePlayerAirTransition|
|G19|08:B947|B972|code|UpdateFallingPlayer|
|G20|08:B972|B984|code|SelectAirbornePlayerAttack|
|G21|08:B984|B9A4|data|AirborneAttackSplitPointers|
|G22|08:B9A4|B9D4|code|UpdateCrouchingPlayer|
|G23|08:B9D4|B9F8|code|UpdateCrouchingAttack|
|G24|08:B9F8|BA38|code|UpdateDownwardAttack|
|G25|08:BA38|BA42|code|UpdateAttack1E|
|G26|08:BA42|BA4C|code|UpdateAttack2C|
|G27|08:BA4C|BA63|code|UpdateAttack42|
|G28|08:BA63|BA84|data|PlayerAttack42Sequence|
|G29|08:BA84|BA8E|code|UpdateAttack5C|
|G30|08:BA8E|BA98|code|UpdateAttack7E|
|G31|08:BA98|BB21|code|UpdateForwardAttack|
|G32|08:BB21|BB2B|code|UpdateAttackAC|
|G33|08:BC12|BC34|code|EnterIdleJumpOrFall|
|G34|08:BC34|BC56|code|SelectForwardAttackTier|
|G35|08:BC56|BC81|code|SelectNormalAttackTier|
|G36|08:BC81|BC99|code|SelectDownwardAttackTier|
|G37|08:BC99|BCBE|code|SelectGroundDownAttackTier|
|G38|08:BCBE|BCEF|code|SelectUpwardAttackTier|
|G39|08:BCEF|BD56|code|IntegratePlayerJumpPhase|
|G40|0E:D9E8|DA07|code|SampleTerrainAtBase|
|G41|0E:DA07|DA3D|code|SampleTerrainAtSignedOffset|
|G42|0E:DA3D|DAB3|code|LookupTerrainFromSceneRom|
|G43|0E:DAB3|DAC2|code|SampleCachedTerrainAtBase|
|G44|0E:DAC2|DB02|code|SampleCachedTerrainAtSignedOffset|
|G45|0E:DD5F|DDB9|code|SelectTerrainCacheOrRom|
|G46|0E:DDB9|DDD9|data|SceneTerrainCacheBypassFlags|
|G47|0F:F50D|F520|code|ResolveSceneMetatilePagePointer|
|G48|0F:F520|F540|data|ScenePageOffsetLow|
|G49|0F:F540|F560|data|ScenePageOffsetHigh|
