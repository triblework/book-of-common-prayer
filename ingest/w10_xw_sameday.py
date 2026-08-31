import sys, re, os, difflib; sys.path.insert(0,'ingest')
import w10_1979
def norm(t): return " ".join(re.sub(r"[^a-z ]"," ",t.lower()).split())
hist={}
d="editions/1928/collects-epistles-gospels"
for fn in sorted(os.listdir(d)):
    b=open(os.path.join(d,fn),encoding="utf-8").read()
    m=re.search(r"## The Collect\n\n(.+?)(?:\n\n(?:##|>)|\Z)", b, re.S)
    if m: hist[fn[:-3]]=norm(m.group(1))
# 1979 occasion -> the SAME DAY in the historic calendar (10a: unambiguous)
SAMEDAY=[("First Sunday of Advent","advent-1"),
 ("Second Sunday of Advent","advent-2"),("Third Sunday of Advent","advent-3"),
 ("The Nativity of Our Lord:  Christmas Day","christmas-day"),
 ("First Sunday after Christmas Day","christmas-1"),
 ("The Holy Name","circumcision"),
 ("Second Sunday after Christmas Day","christmas-2"),
 ("The Epiphany","epiphany"),
 ("First Sunday after the Epiphany:  The Baptism of our Lord","epiphany-1"),
 ("Second Sunday after the Epiphany","epiphany-2"),
 ("Third Sunday after the Epiphany","epiphany-3"),
 ("Fourth Sunday after the Epiphany","epiphany-4"),
 ("Fifth Sunday after the Epiphany","epiphany-5"),
 ("Sixth Sunday after the Epiphany","epiphany-6"),
 ("Seventh Sunday after the Epiphany",None),
 ("Last Sunday after the Epiphany",None)]
sec=sys.argv[1]; data=w10_1979.load(sec)
def open12(t): return " ".join(norm(t).split()[:12])
print(f"{'1979 occasion':<42}{'slug':<14}{'full':<7}{'open':<7} verdict")
for name,slug in SAMEDAY:
    if name not in data: print(f"{name[:41]:<42}{str(slug):<14}  -- MISSING from e-text --"); continue
    if slug is None:
        best=max(((s,difflib.SequenceMatcher(None,norm(c),h).ratio())
                  for c in data[name]['collects'] for s,h in hist.items()),key=lambda kv:kv[1])
        print(f"{name[:41]:<42}{'(no same day)':<14}{best[1]:<7.2f}{'':<7} new? best={best[0]}")
        continue
    h=hist[slug]
    full=max(difflib.SequenceMatcher(None,norm(c),h).ratio() for c in data[name]['collects'])
    op=max(difflib.SequenceMatcher(None,open12(c),open12(h)).ratio() for c in data[name]['collects'])
    v = "CONTINUES" if (full>=.55 or op>=.70) else ("REPLACED" if full<.40 and op<.50 else "review")
    print(f"{name[:41]:<42}{slug:<14}{full:<7.2f}{op:<7.2f} {v}")
