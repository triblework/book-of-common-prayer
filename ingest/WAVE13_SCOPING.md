# Wave 13 — the Psalter: source survey and scoping options

Status: **survey complete, rulings PENDING.** Written 2026-09-02 before any
build. Read with `AUDIT_METHOD.md` and spec §10.

---

## 1. Source survey

| Edition | Source | State |
|---|---|---|
| 1549 1552 1559 1604 | — | **NO allow-listed source.** justus has no psalter HTML for these; the 1559 index offers only `Psalter1634.pdf`, a 1634 printing (a page scan, not this edition). |
| 1662 | Church of England, 60 sub-pages under `.../book-common-prayer/psalter/` | **Clean.** `Psalm N.` heading, Latin incipit, verses numbered from 2 (verse 1 unnumbered, as printed), mediant already printed as ` : `. |
| 1637 1764 1929 | — | The Scottish index prints "The Psalter" with a note that it is Coverdale and "essentially identical to that in the US 1928 or the 1662 BCP's", but links no page. |
| 1789 1892 1928 | justus `1928/Psalms{1,2,3}.htm` | **One page carrying the 1928 text with earlier readings in a sidebar** — the Wave-10 two-column pattern exactly: `<td width="400">` is text, `<td width="200">` is apparatus. |
| 1979 | `bcpsalt1.txt` + `bcpsalt2.txt` | **Clean.** 150 psalms, ~2,506 verses. `<Psalm N>  =Latin incipit=`, numbered verses, `*` mediant, `/` marking a wrapped line. |

Sizes: 150 psalms and roughly 2,500 verses per edition, so a four-edition wave
is on the order of 10,000 authored lines — large but far more regular than the
tables of Wave 14.

---

## 2. Findings that shape the scoping

### 2.1 The American apparatus supports a GRADED rollback, not two independent texts

Counted across all three American pages: **227 apparatus cells**, whose edition
qualifiers are

| qualifier | count |
|---|---|
| `until 1928` | 213 |
| `1892` | 21 |
| `1789` / `1793` | 10 |
| `1845`, `1822`, `1871` (intermediate PRINTINGS, not prayer-book editions) | 8 |

So the page reliably attests **the pre-1928 reading**, and attests a further
handful of 1892-specific and 1789-specific readings. It does **not** contain a
complete delta set that would let 1789 and 1892 be reconstructed as two fully
independent texts. Deriving them as if it did would fabricate distinctions the
source does not attest, which the prime directive forbids. What IS attested is a
graded rollback: 1928 base → apply `until 1928` → 1892 → apply the notes naming
1892/1789 → 1789.

Deriving an edition from a page's own apparatus is established practice here
(Wave 10 derived 1552 and 1559 from the annotated 1549 propers page), provided
each delta is cited.

The notes naming 1845, 1822 and 1871 are intermediate printings between prayer
books and must be IGNORED, not applied — applying them would produce a text no
prayer-book edition ever printed.

### 2.2 There is no source for the Psalter before 1662

The Coverdale psalter was in the book from 1549, but no allow-listed source
gives us 1549/1552/1559/1604 text. Because nothing before 1662 can hold the
file, the Psalter would **first appear in the graph at `v1662`**. That is a
graph artefact, not history, and would read as "1662 added the Psalter" unless
NOTICE.md says otherwise in plain terms. This is the Wave-14 lesson again:
absence in the built history is a claim, and an unsourceable presence has to be
stated in prose because the graph cannot express it.

### 2.3 `1789/Psalter_1789.htm` is not the Psalter

It is the **Selections of Psalms** — a distinctively American feature, numbered
selections appointed for use instead of the day's psalms. A separate thing,
worth its own file if it is in scope.

### 2.4 Two tables here would close a Wave-14 recorded gap

`1892/Psalms_1892.htm` and `1789/Psalter1789&1892.htm` are **Tables of Proper
Psalms on Certain Days**. Wave 14 recorded a gap for exactly this table (it
stopped the 1789 Psalter-rubric slice before it). Transcribing them here would
close that gap.

### 2.5 The mediant is printed differently in every line of the tradition

The 1928 page states it plainly: 1928 uses an **asterisk**, 1892 the **musical
colon**, and "prior to that no breath-marks were used". The CoE 1662 pages print
` : ` and the 1979 e-text prints `*`. Spec §4 already rules that the pointing is
typography, not text, and normalizes it to ` : `. Applied here that means 1789
would be given a mediant it did not print. The alternative — preserving each
edition's mark — makes 1789 differ from 1892 on **every single verse** for a
purely typographic reason, drowning the real textual changes.

---

## 3. The scoping options

### (a) File shape

- **A1 — three files of fifty** (`psalter/psalms-1-50.md`, `51-100`, `101-150`),
  `## Psalm N` anchors within. Matches the American source's own division; each
  file lands near 900 lines. **RECOMMENDED**, and explicitly sanctioned by spec
  §10 ("split per fifty psalms if file size matters").
- A2 — one file `psalter/psalter.md`, ~2,600 lines per edition. The spec's other
  option; diffs are identical either way, but the file is unwieldy to browse.
- A3 — one file per psalm, 150 × editions. Gives the cleanest per-psalm diff but
  explodes the tree to 600+ files and breaks the "one file per service" idiom.

### (b) Which editions, and how far to trust the apparatus

- **B1 — 1662, 1789, 1892, 1928, 1979**, with 1892 derived from the 1928 base by
  applying the `until 1928` apparatus and 1789 derived from 1892 by applying the
  notes that name 1892/1789. Every delta cited; intermediate printings ignored
  and recorded. **RECOMMENDED** — it uses exactly what the source attests and
  nothing more.
- B2 — 1662, one pre-1928 American text at 1789 (1892 inherits it unchanged),
  1928, 1979. Simpler and still honest, but it suppresses the 21 apparatus notes
  that do name 1892, asserting an identity the source contradicts.
- B3 — 1662, 1928, 1979 only; 1789/1892 inherit. **Rejected**: they would carry
  the ENGLISH text, a false claim, since the American psalter had already
  diverged.

In all options 1549–1604 and the Scottish line carry a recorded gap (§2.2).

### (c) The mediant

- **C1 — normalize every edition to ` : `**, and state in NOTICE.md that 1789
  printed no breath-mark, 1892 a musical colon and 1928 an asterisk.
  **RECOMMENDED**: it follows the existing spec §4 rule, and it keeps the
  edition-to-edition diffs about words rather than about pointing.
- C2 — preserve each edition's printed mark. More literal, but every verse of
  1789 then differs from 1892 typographically and the real changes are lost in
  the noise.

### (d) Optional extras (say yes or no)

- `psalter/selections.md` — the 1789 Selections of Psalms (§2.3).
- `tables/proper-psalms.md` — the Tables of Proper Psalms, closing the Wave-14
  recorded gap (§2.4).
