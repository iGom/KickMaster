# KickMaster NTSC-U — Stage 02F

Raport z 2026-10-22. Ukończono ograniczony etap analizy kopnięć, kontaktu z ciałem
przeciwnika, jego dodatkowego obszaru ataku oraz wejść dispatchu AI i agregatu HP.
Pełna rekonstrukcja gry pozostaje w toku. Nie korzystano z osobnych badań użytkownika.

## Wyniki

- Rozdzielono trzy ścieżki kolizji i ich dane. Kopnięcie kolejkuje obrażenia dla pierwszego
  nakładającego się przeciwnika; zerowe obrażenia tego profilu kończą skan.
- Odtworzono 101 profili ataku. Nie ma lokalnego mnożnika poziomu. Zerowe składniki geometrii
  nie zawsze wyłączają kolizję. Końce ataku poza stroną kamery są zastępowane początkiem kamery.
- Rozpoznano czterobajtowy rekord klatki przeciwnika: obrażenia i kształt ciała oraz obrażenia
  i kształt dodatkowego ataku. Dodatkowy obszar nie sprawdza wysokiego bajtu X.
- Ustalono 99 wskaźników rodzajów kolizji, lecz tylko 64 zwykłe i 29 specjalnych wpisów AI.
  Nie uznano luki 40..45 hex za poprawne rodzaje na podstawie progu schedulera.
- Prześledzono wybór fazy AI/renderowania i obliczanie agregatu HP ograniczonego do AF hex.
  Slot 9 aliasuje akumulator; znaczenie ekranowe i liczba niezależnych slotów pozostają otwarte.
- Sprawdzono argumenty i bramki prób terenu do granic C773/C776. Ich pełnych skutków nie zaliczono.

Szczegóły banków, wzorów i ograniczeń: `reports/subsystems/MELEE_CONTACT_AND_ENEMY_DISPATCH.md`.
Oryginalny poradnik, maps.zip i osiem PNG zachowano bez zmiany bajtów i rozdzielczości.
Nie przeprowadzono jeszcze porównania PNG z geometrią ROM-u ani mapowania 32 scen na osiem sektorów.

## Wznowienie i zachowane wyniki

Na początku02F ponownie odczytano02E ZIP i sześć osobnych plików. SHA-256 ZIP-u:
`1ae70fe401ac890e7e083e1c2ec4d5763e3ac314bf4b4ae698ccb1107f55759c`.
Rozmiar4361394 bajty; CRC, pełny manifest251 plików, ekstrakcja i porównania hashy:PASS.
Dowód: `manifests/stage02E_resume_verification.json`. Nie powtarzano starych CPU/buildów
ani nie przesyłano ponownie poprawnych archiwów. Domknięte02B/02C/02D pozostają zachowane.

## Stan rekonstrukcji

| Miara | Po02E | Po02F |
|---|---:|---:|
| Zakresy kodu |231|243|
| Zakresy danych |92|115|
| Instrukcje |5624|6021|
| Bajty PRG z przejrzaną lokalną semantyką |15194|17674|
| Udział128KiB PRG |11,592102%|13,484192%|
| Role RAM |133|133|
| Symbole |456|491|
| Wpisy dispatchu pośredniego |256|349|
| Krawędzie grafu wywołań/tablic |563|653|

NoweH01..H35:12 zakresów kodu,23 danych,397 instrukcji i2480 bajtów.
Dziewięć ról RAM doprecyzowano. Kompletny build262160 bajtów jest zgodny z oryginałem;
17690 bajtów jawnego źródła zawiera16-bajtowy nagłówek,244470 pochodzi z zależnych od ROM-u
fragmentów incbin. Zgodność binarna nie jest równoznaczna z pełnym zrozumieniem programu.

## Testy i ograniczenia

Wykonano12 nowych grup,27126 przypadków i zapisano5223 wiersze trace. Wszystkie grupy:PASS.
Bez patchowania ROM-u i bez zastępowania wywoływanych procedur. Geometrię i wyniki
porównywano z niezależnymi wzorami oraz rzeczywistymi tabelami ROM-u. Zestawy wcześniejszych
etapów jedynie odczytano jako zachowane dowody; nie uruchomiono ich ponownie.

CPU_TEST obejmuje kontrakty w kontrolowanej pamięci. Testy AI kończą się przed pierwszą
instrukcją docelowej procedury; testy schedulera przed AI/renderowaniem, a testy terenu
przed C773 lub pierwszym C776. Nie zaliczają pełnego AI, bossów, mutacji terenu, grafiki,
ani osiągalności wszystkich syntetycznych kombinacji w rozgrywce. Druga próba stóp +6/+2
jest potwierdzona statycznie, a nie dynamicznie. A2C3 z licznikiem zero nie testowano.

Audyt zakresów, instrukcji, offsetów, eksportów, bieżących danych i oryginalnych materiałów:PASS.
Native NES, natywne importy MesenCE/Ghidra, timing NMI/IRQ:NOT_TESTED.
Nie napotkano niezaliczonej nowej grupy CPU; poprawiono opis warunku bankowania R6/R7
w generatorze i indeksie, bez powtórzenia ukończonej analizy.

## Checkpoint i następna praca

Planowana nazwa: `kickmaster-ntscu-checkpoint-stage02F.zip`.
Ten raport wewnętrzny jest migawką sprzed pakowania. SHA, integralność nowego ZIP-u,
czysty build z archiwum oraz zapis i ponowny odczyt: **PENDING w tej migawce**.
Wyników późniejszych kontroli szukaj w osobnych `stage02F.*.json` i finalnym
`KickMaster_STAGE02F_REPORT.md`; nie wnioskuj PASS z samego istnienia tego raportu.

Stage02G: rzeczywiste cele AI i ich stany/klatki, reakcja na trafienie/śmierć oraz nagrody;
pełny kontrakt C773/C776 i odświeżanie cache; następnie geometria, kamera i porównanie map.
Dalsza kolejność i polecenia znajdują się w RESUME.md. Żaden wcześniejszy ukończony test
nie wymaga automatycznego powtórzenia po przywróceniu środowiska.
