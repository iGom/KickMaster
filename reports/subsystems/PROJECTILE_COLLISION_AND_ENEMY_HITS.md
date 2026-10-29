# Stage 02D — pociski, kolizje i rozliczanie trafień

Data: 2026-10-21. Badanie niezależne, oparte na oryginalnych bajtach ROM-u o SHA-256
`00ad4a0c6612319bb9f918ca36d6e93b4e5d996716c0570a3ec92bd60533881b`.
To kontynuacja lokalnych ustaleń Stage 02C, nie zamknięcie całego systemu walki.
Nazwy czarów zachowują wcześniejsze przyporządkowanie źródłowe; nowe twierdzenia poniżej
wynikają z kodu i opisanych prób CPU, a nie z poradnika lub osobistych notatek użytkownika.

Adresy są szesnastkowe i mają kwalifikator banku. Liczby bez oznaczenia „hex” są dziesiętne.
Mapowanie badanych ścieżek: MMC3 PRG mode 0; PRG06 przez R6 w oknie $8000,
PRG08/09 przez R7 w $A000, PRG0E w $C000, PRG0F w $E000.
Wszystkie zakresy, offsety bankowe/PRG/plikowe i instrukcje są w
`analysis/reviewed_ranges.csv` oraz `analysis/reviewed_instructions.csv`.

## 1. Kolejka trafienia i rzeczywiste HP

PRG08:$A230 wykrywa kolizję magicznego pocisku z przeciwnikiem. PRG09:$BD1B,
rozpoznana w 02C, wpisuje żądania trafień kolumnowego efektu. Obie ścieżki pozostawiają
surowe obrażenia w `$0441,X` i ustawiają bit 20 hex w `$0469,X`.

PRG0F:$E2F9 wybiera lokalną ścieżkę stanu:

| Kolejność | Warunek | Wynik |
|---|---|---|
| 1 | HP równe zero i wejściowe Y różne od zera | selektor Y, bez nowego odejmowania |
| 2 | bit 20 hex w `$0469,X` | selektor Y+1, wywołanie `$E32A` |
| 3 | bit 10 hex w `$0473,X` | selektor Y+2 |
| 4 | żaden z powyższych | inkrementacja `$0423,X`, selektor z `$040F,X` |

Selektor trafia do `$2F`, a jego podwojona wartość do Y. Próby obejmują wejściowe Y=0/2/5.
Przepełnienie inkrementacji dla Y bliskiego FF hex ma osobne odgałęzienia; powyższa tabela
nie stanowi ogólnego modelu dla całej przestrzeni 256 wartości ani pełnego dispatchu AI.

PRG0F:$E32A wykonuje `HP = max(HP − queued_damage, 0)` na **8-bitowych surowych HP**
w `$0437,X`, tylko jeśli `$0469,X` ma bit 40 hex. Dokładna równość także daje zero.
Następnie zeruje `$0455,X`, usuwa bit akceptacji 40 hex, ustawia bit reakcji 80 hex
w `$047D,X`, zgłasza dźwięk 55 hex i przywraca X z `$2C`.
Sam konsument nie sprawdza bitu oczekującego trafienia 20 hex: sprawdza go zewnętrzne `$E2F9`.
Nie zeruje też ani `$0441,X`, ani bitu 20 hex. Ponowne wejście przed przywróceniem
bitu 40 hex nie odejmuje HP po raz drugi.

**Istotny alias:** `$0437+9 = $0440`. Ten sam adres jest zerowany przed przebiegiem
przeciwników w PRG0E:$D6F0 i kopiowany po nim do `$06BC`. Producent wartości wewnątrz
nieprzeanalizowanego `$D759` pozostaje otwarty. Dziesięć indeksów w lokalnych próbach
nie dowodzi istnienia dziesięciu niezależnych, równocześnie żywych przeciwników.
Nie przypisano tej wartości jednostki „kratka HP” ani kompletnej semantyki paska bossa.

## 2. Reakcja po trafieniu

PRG0F:$E35B inkrementuje `$0423,X`. Przy nieparzystym wyniku inkrementuje `$0455,X`,
a następnie zeruje `$0423,X`. Przy `$0455,X = 0A` hex usuwa pending 20 hex,
przywraca acceptance 40 hex, czyści reaction 80 hex i zeruje licznik reakcji.
Z początkowych dwóch zer zajmuje to **10 wywołań procedury**, nie 20.
Początkowy nieparzysty licznik fazy dodaje jedno pominięte wywołanie.

W pozostałych aktywnych krokach wykonywany jest PRG0F:$E3FE. Trzy tabele
PRG0F:$E436–$E44D wybierają kierunek i moduły przesunięcia. W sprawdzonym wariancie
bez korekcji terenowej wynik dla niskich trzech bitów `$047D,X` wynosi:

| Kierunek | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ΔX na krok | 0 | +2 | +2 | +2 | 0 | −2 | −2 | −2 |
| ΔY na krok | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Dziewięć kroków przesunięcia poprzedza dziesiąte wywołanie przywracające akceptację.
Próby wykonały oryginalne pomocnicze procedury pozycji i commit, bez zastępników;
bit 80 hex `$0473,X` był wyzerowany, a scratch `$36=0`.
Odrębna gałąź korekcji terenowej i kompletny cykl AI wroga nie są tu zweryfikowane.

## 3. Kolizja magicznego pocisku

PRG08:$A230 zaczyna od limitu zależnego od `$06BD`. Tabela PRG08:$A8E6 ma 13 bajtów:

| Wybrany efekt | Wartość | Badane globalne sloty pocisków |
|---|---:|---|
| 03 hex — Lightning | 1 | 1, 0 |
| 05/06 hex — Bouncing Bulb / Pulse Wave | 2 | 2, 1, 0 |
| 0C hex — wyłączony efekt | 1 | 1, 0 |
| pozostałe indeksy | 0 | przejście do odrębnej ścieżki kontaktu `$A2C3` |

Wartość niezerowa jest **najwyższym indeksem**, a nie liczbą slotów. Zero nie oznacza
„badaj tylko slot 0”. Lightning tworzy trzy obiekty, lecz **slot 2 nie jest badany przez tę
konkretną ścieżkę kolizji**. Nie dowodzi to braku innych zastosowań lub kolizji tego obiektu.

Przeciwnicy są skanowani od `$06F8−1` w dół. Wymagane są `$0469,X >= C0` hex,
zerowe dwa najmłodsze bity `$0473,X` i poprawne granice z `$A354`.
Pocisk musi mieć aktywny bit 80 hex oraz typ mniejszy niż 40 hex.
Po trafieniu kod:

1. usuwa pocisk, jeśli jego bit 10 hex jest wyzerowany;
2. ustawia kierunek reakcji 7/1/0 dla ujemnej/dodatniej/zerowej prędkości X;
3. kolejkuje obrażenia i bit pending;
4. przechodzi do kolejnego przeciwnika — najwyżej jedno nowe trafienie na przeciwnika w przebiegu.

Pocisk z bitem 10 hex może trafić kolejnych przeciwników w tym samym przebiegu.
Zużywany pocisk trafia tylko pierwszego nakładającego się przeciwnika według malejących indeksów.
Próba dwóch przeciwników potwierdziła tę kolejność. Zdarzenie zerowego damage zakończyłoby
skan pocisków dla danego przeciwnika; wszystkie 32 odczytane wartości damage są niezerowe.

### Profile i granice

PRG06 zawiera pięć tabel po 32 bajty: `$84BC` offset Y, `$84DC` rozmiar Y,
`$84FC/$851C` dwa poziome zasięgi, `$853C` surowe obrażenia.
Indeks to `type >> 1`; nieparzysty typ zamienia poziome strony.
Pełne wartości: `projectile_collision_profiles.csv`.

PRG08:$A54D stosuje ścisłe porównania przedziałów z arytmetyką modulo 256;
poziome końce ogranicza do strony kamery. Próby objęły wszystkie 64 bajty typów,
siedem pozycji względem kamery i granice przedziałów. Dotyczy to środka pocisku w stronie
kamery; nie jest to dowód wszystkich przypadków poza ekranem ani ich osiągalności.

PRG08:$A4EC korzysta z czterech 101-bajtowych tabel gracza w PRG06:
`$8000`, `$8065`, `$80CA`, `$812F`, indeksowanych przez `$CD >> 1`.
Carry clear oznacza nakładanie. Zapisano 101 profili i zbadano 202 lokalne wartości stanu
z obydwoma kierunkami; bramki poprzedzające kolizję mogą wykluczać niektóre z nich w grze.

PRG08:$A354 i `$A404` odczytują geometrię wrogów/pocisków przez wskaźniki w R6=06.
Integracje użyły rzeczywistego enemy kind0/frame0 oraz enemy-projectile kind0/state0.
Dla pierwszego próbny profil ma wysokość32 i poziome zasięgi12/12; drugi daje damage7,
shape2, offset Y=FC hex, wysokość8 i zasięgi4/4. Pełny katalog poprawnych kombinacji
kind/state/frame pozostaje otwarty. Żadne wywołanie kolizji lub HP nie było zastąpione atrapą.

## 4. Budżet Force Shield

PRG08:$A305 skanuje dziesięć pól pocisków wroga od indeksu9 do0. Akceptuje flagi
z bitem 80 hex i bez 40 hex, niezerowy damage oraz kolizję z graczem.
**Najpierw usuwa pocisk**, potem rozstrzyga tarczę i obrażenia.

Jeśli `$06BD=0A` hex, dekrementuje `$05A7` i pochłania trafienie, dopóki wynik ma
wyzerowany bit znaku. Prawidłowy seed 0A hex z aktywacji tarczy pochłania więc
**10 takich przecięć**. Jedenaste zmienia licznik z0 na FF hex i wywołuje oryginalne
uszkodzenie gracza przez PRG08:$C76D → PRG0E:$DDD9. Następna aktualizacja kontrolera
PRG09:$B964 wraca do typu gotowości 84 hex.

Warunek w tej procedurze sprawdza wybrany indeks, nie aktualny typ aktywnego obiektu.
Przecięcie podczas niewrażliwości gracza również może zużyć budżet; późniejsza bramka
`$D2` blokuje samo odejmowanie HP. Próby wartości127/128/255 były **syntetycznymi
granicami bajtu**, nie wykazanym sposobem osiągnięcia nieskończonej tarczy.
Nie przenosimy tej ochrony na kontakt z ciałem przeciwnika, teren ani inne niebadane ścieżki.
Gałąź `$03D9` odwijająca dodatkową ramkę stosu pozostaje poza tymi próbami.

## 5. Licznik Earthquake

Producent PRG0E:$D7E7, zachowany z 02C, ustawia `$03DC=1` i oznacza wybrane
z pierwszych ośmiu wpisów `$0473`. Konsument PRG0E:$D7AD:

| Wartość na wejściu | Działanie |
|---|---|
| 0 | brak działania |
| 1…EF hex z wyjątkiem D2 hex | inkrementacja |
| D2 hex | dodanie bitu 40 hex wpisom z bitem 10 hex, następnie inkrementacja |
| F0 hex | wyzerowanie licznika i usunięcie bitów 10/40 hex z pierwszych ośmiu wpisów |

Od seedu1 trwa to **240 wywołań konsumenta**. Dodatkowa flaga pojawia się przy
wywołaniu210; wywołanie240 usuwa oba bity, także we wpisach pierwotnie pominiętych przez
producenta. Wpisy8/9 pozostają bez zmian. PRG0E:$D6F0 woła konsumenta tylko przy
nieparzystym `$D8`. Nie przeliczono tego na sekundy ani pełne klatki gry.

Bit 10 hex rzeczywiście wybiera alternatywną ścieżkę przez `$E2F9`. Ustalenie pełnego
„ogłuszenia” każdego gatunku wroga/bossa wymaga jeszcze ich procedur stanu.

## 6. Sterowniki pocisków

Tabela PRG09:$AB87–$ABC6 zawiera 32 pary wskaźników dla typów00–3F hex.
`projectile_object_dispatch.csv` zachowuje wszystkie wpisy, a graf otrzymał32 krawędzie tabeli.

| Rodzina | Sterownik | Ustalenie lokalne |
|---|---|---|
| Pulse Wave | PRG09:$B55C | co trzecie wywołanie zwiększa typ o2; typ0A/0B hex kończy wzrost i trafia do RTS |
| Bouncing Bulb | PRG09:$B571 | przełącza bit1 typu; osobno bada przyszłe X/Y i neguje odpowiednią prędkość dla wyniku z niskimi bitami |
| Lightning | PRG09:$B5EF–$B65D | zmiana typu o krok +2/−2, liczniki pętli i kopiowanie 16-bitowej pozycji ze slotu3 |

Pulse dochodzi do końcowego profilu po15 wywołaniach własnego sterownika.
Próby pełnej pętli PRG09:$BE90, z flagami90 hex i początkowym `$D9=1`, wykazały
aktualizację co drugi przebieg: końcowy profil na przebiegu29, krok X równy ±8 tylko
podczas faktycznej aktualizacji. Obie orientacje śledzono przez48 przebiegów.
Odczytane damage to3; rosnące rozmiary Y zapisano w CSV. Nie jest to zmierzona prędkość na sekundę.

Bouncing typ10/12 hex naprzemiennie wybiera damage3/2. Próbki przyszłego terenu przechodzą
przez oryginalne `$C773`, a bieżącego punktu przez `$C75B`. Niskie dwa bity bieżącej próbki
dezaktywują pocisk; bit3 może ustawić atrybut20 hex. Typ bez bitu10 hex dostaje także
flagę pozwalającą trafiać kolejnych wrogów. Testy użyły komórek cache RAM 00–03/08 hex,
sceny0 i położeń wewnętrznych oraz prędkości ±16. To kontrolowane wejścia do rzeczywistych
procedur; nie pełna rekonstrukcja formatu map, destrukcji terenu ani kolizji poza ekranem.

Lightning: segment środkowy ze zwykłym seedem21 wygasa po92 lokalnych wywołaniach
dispatchu; boczne z seedem8 po91. Pozycja podąża za slotem3. Dla środka i dodatniego
N wynik to `4*N+8`; dla boków N≥2 wynik to `12*N−5`, w zbadanych przypadkach N=2/8/21.
Seed0 usuwa segment w pierwszym wywołaniu. **Syntetyczny boczny seed1 jest wyjątkiem**:
przy pierwszym zejściu licznika do zera krok nadal wynosi+2, więc licznik wraca przez FF hex;
wygaśnięcie następuje dopiero po3069 wywołaniach. Wykonano cały ten lokalny przebieg,
ale nie dowiedziono osiągalności seedu1 z normalnego spawnera. Nie jest to deklaracja błędu rozgrywki.

## 7. Dowody i ograniczenia wykonania

`cpu_stage02D.json`, `cpu_stage02D_vectors.csv` i `cpu_stage02D_trace.csv` zachowują
**16 grup, 26 832 wektory i 117 943 wiersze śladu**. Wektor oznacza w zależności od grupy
wariant wejścia lub krok sekwencji, nie zawsze niezależnie uruchomiony scenariusz.

| Grupa | Wektory | Przedmiot |
|---|---:|---|
| F_CPU01 | 5120 | wszystkie HP, dziesięć damage, indeksy0/9; brak ponownego odjęcia |
| F_CPU02 | 256 | wszystkie bajty flag akceptacji |
| F_CPU03 | 72 | priorytet death/hit/quake/normal |
| F_CPU04 | 10 | oryginalna kolejka kolumn → faktyczne HP |
| F_CPU05 | 96 | przywracanie akceptacji i rzeczywisty knockback |
| F_CPU06 | 240 | pełen lokalny przebieg quake |
| F_CPU07 | 1928 | liczniki0–240 i osiem wariantów flag |
| F_CPU08 | 53 | kolizje pocisków wroga, granice budżetu i pełny ciąg11 trafień |
| F_CPU09 | 3232 | granice profili gracza |
| F_CPU10 | 7168 | kierunki, kamera i granice profili pocisków |
| F_CPU11 | 384 | rzeczywista geometria → kolejka → HP |
| F_CPU12 | 2 | kolejność skanu i zachowanie/zużycie pocisku |
| F_CPU13 | 39 | ograniczenia slotów dla13 wybranych efektów |
| F_CPU14 | 96 | wzrost fali i pełna pętla ruchu |
| F_CPU15 | 960 | dwa odbijane kierunki i oryginalne samplery terenu |
| F_CPU16 | 7176 | kompletne lokalne cykle segmentów lightning |

Użyto py65, modelu MMC3 i uproszczonego PPU; bajty ROM-u nie były patchowane.
Nie ma zastępowanych callees. W F_CPU13 zerowy limit celowo zatrzymuje wykonanie przed
nieprzeanalizowanym kontaktem `$A2C3`; pozostałe warianty tej grupy dochodzą do powrotu.
Nie wykonano natywnego emulatora NES, pomiaru NMI/IRQ/PPU, odtwarzania wejścia ani importu GUI.

`stage02D_test_development.json` opisuje dwie poprawki oczekiwań nowych testów oraz
konkretną przyczynę powtórzenia wyłącznie F_CPU11–13: brak ich zapisów w odczytanym pliku
częściowym mimo wcześniejszego PASS w stdout. Wszystkie pozostałe zaliczone grupy wykorzystano
z zachowanych wyników. Zestawów01A/01B/02A/02B/02C nie uruchamiano ponownie.

## 8. Dalsze badania

Następne zadania to główne procedury gracza PRG08:$B81D/$B8B5 i fizyka `$BCEF`,
kontrakt próbkowania terenu, kontakt z przeciwnikiem, kompletna lista kind/state/frame,
AI i odporności bossów oraz targeting sobowtóra. Osobno pozostają pozostałe zapisy poziomu/HP,
producent `$01A5`, hasła i split-scroll. Lokalne zamknięcie powyższych konsumentów nie zamyka tych zadań.

Oryginalny poradnik Wyrentha, `maps.zip` i osiem PNG sprays pozostają niezmienione.
Etap geometrii ma porównać dane ROM-u z mapami, ustalić transformacje współrzędnych,
scrolling/przejścia/spawny i dopiero wtedy przypisać32 sceny do ośmiu sektorów.
W 02D nie wykonywano tego porównania i nie powtarzano Stage00A.
