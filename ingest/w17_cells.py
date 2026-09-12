"""The Psalter cells as {psalm: {verse: text}} -- the authoring source, read
back for the Wave-17 gates."""
import glob, re
import os
WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

def cells(ed='1892'):
    out = {}
    for f in sorted(glob.glob(WT + 'editions/%s/psalter/psalms-*.md' % ed)):
        ps = None
        for line in open(f, encoding='utf-8'):
            line = line.rstrip('\n')
            m = re.match(r'^## Psalm (\d+)', line)
            if m:
                ps = int(m.group(1)); out[ps] = {}; nxt = 1; continue
            if ps is None or not line.strip() or line.startswith(('>', '<!--', '#')):
                continue
            m = re.match(r'^(\d+) (.*)$', line)
            if m:
                out[ps][int(m.group(1))] = m.group(2)
            else:
                out[ps][1] = line          # verse 1 carries no number
    return out

if __name__ == '__main__':
    c = cells()
    print(len(c), 'psalms', sum(len(v) for v in c.values()), 'verses')
    print(c[1][1][:60]); print(c[150][max(c[150])][:60])
