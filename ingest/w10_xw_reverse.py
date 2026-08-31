import sys, re, os, difflib; sys.path.insert(0,'ingest')
import w10_1979
def norm(t): return " ".join(re.sub(r"[^a-z ]"," ",t.lower()).split())
def op12(t): return " ".join(norm(t).split()[:12])
hist={}
d="editions/1928/collects-epistles-gospels"
for fn in sorted(os.listdir(d)):
    b=open(os.path.join(d,fn),encoding="utf-8").read()
    m=re.search(r"## The Collect\n\n(.+?)(?:\n\n(?:##|>)|\Z)", b, re.S)
    if m: hist[fn[:-3]]=m.group(1)
trad=w10_1979.load("Traditional")
print("historic slug -> where its collect survives in the 1979 Traditional set")
for slug,h in sorted(hist.items()):
    best=(None,0,0)
    for name,v in trad.items():
        for c in v["collects"]:
            f=difflib.SequenceMatcher(None,norm(c),norm(h)).ratio()
            o=difflib.SequenceMatcher(None,op12(c),op12(h)).ratio()
            if max(f,o)>max(best[1],best[2]): best=(name,f,o)
    tag = "SURVIVES" if (best[1]>=.55 or best[2]>=.70) else "no match"
    print(f"  {slug:<14} {tag:<9} {best[1]:.2f}/{best[2]:.2f}  {str(best[0])[:44]}")
