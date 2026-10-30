# Aktualizacje instrukcji projektu — 2026-10-20

Główna specyfikacja w `project_specification.md` pozostaje zachowana w pierwotnej postaci.
Poniższe późniejsze instrukcje użytkownika obowiązują przy dalszej pracy.

- Zweryfikować istniejący checkpoint 02B o SHA-256
  `397afcb28be6c26ce6fa471b5270531162a4a62b61f810cc02d14681fd5ce07b`.
  Nie przesyłać go ponownie, jeżeli kopia jest poprawna; nie nadpisywać starszych checkpointów.
- Uzupełnić osobne `stage02B.verification.json`, `stage02B.reproducibility.json`
  i `stage02B.persistence.json`, wykonać zapis i ponowny odczyt. Nie oznaczać niewykonanych kontroli jako PASS.
  Użytkownik wyraził zgodę na alternatywny bezpośredni zapis, gdy standardowa metoda zawodzi.
- Zachować dostarczony pełny poradnik Wyrentha, `maps.zip` oraz osiem oryginalnych PNG sprays
  bez zmiany bajtów i rozdzielczości; uwzględniać je w kolejnych checkpointach.
  Ta wyraźna prośba o zachowanie własnych załączników zastępuje wcześniejsze ograniczenie
  kopiowania pełnego poradnika do checkpointu.
- Uaktualnić dostępność w indeksach źródeł i map. Nie powtarzać Stage00A wyłącznie z powodu załączników.
- Wykorzystać mapy w odpowiednich etapach do geometrii, scrollingu, przejść, obiektów,
  przeciwników i powiązania 32 konfiguracji scen z ośmioma sektorami. Zawsze porównywać z danymi ROM-u.
  Ewentualne fragmenty zachować w oryginalnej skali i opisać współrzędnymi względem oryginału.
- Zachować niezależność badań; nie powtarzać ukończonych analiz i testów bez konkretnego uzasadnienia.

Realizacja 02B: osobne potwierdzenia i odczyt w `manifests/stage02B_sidecars_readback.json`.
Źródła: `research/originals_manifest.csv`. Bieżący stan i następne zadania: `RESUME.md`.

Wznowienie02E (2026-10-21):02D ZIP i sześć osobnych plików odczytano ponownie; hashy, CRC, manifest228 plików i pełna ekstrakcja są poprawne. Zachowane dowody: manifests/stage02D_resume_verification.json. Bez powtarzania wcześniejszych CPU/buildów.

Wznowienie02F:02E ZIP i sześć sidecarów odczytano i porównano; CRC, manifest251 plików i pełna ekstrakcja PASS. Dowód: manifests/stage02E_resume_verification.json. Stage02F dodaje lokalne kontrakty walki i wejścia AI; nie powtarza Stage00A ani wcześniejszych CPU/buildów. Oryginały źródeł i status oczekującego porównania map pozostają zachowane.

Wznowienie02G (2026-10-22):02F ZIP i sześć osobnych plików odczytano ponownie i porównano z zapisanymi SHA-256. CRC, pełny manifest278 plików i pełna ekstrakcja PASS. Dowód: manifests/stage02F_resume_verification.json. Bez ponownego przesyłania poprawnych wcześniejszych checkpointów i bez powtarzania starych CPU/buildów.

Domknięcie dokumentacji02G (2026-10-29):zachowano wyniki15 nowych grup/4050 obserwacji oraz opis błędnego pierwszego oczekiwania w grupie7 i jego selektywnej korekty. Stage02G obejmuje AI rodzaju00, dropy i cykle śmierci5B/60; pełny teren i pozostałe AI pozostają otwarte. Oryginalne mapy i poradnik nadal są niezmienione. Wewnętrzny raport nie oznacza przyszłych kontroli archiwum/zapisu jako PASS; ich wyniki mają osobne potwierdzenia. Następny priorytet02H:pełne C773/C776, cache i teren, następnie geometria oraz porównanie map.
