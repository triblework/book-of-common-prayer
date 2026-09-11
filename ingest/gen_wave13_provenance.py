#!/usr/bin/env python3
"""Wave 13 — provenance records + verify_items for the Psalter.

One record per <service, edition> authored, and one per RECORDED GAP (the book
carries it, no allow-listed source gives this edition's own text, so it
inherits) -- stated so no reader mistakes inheritance for "reprinted unchanged".
"""
from __future__ import annotations
import re
from pathlib import Path

WT = Path(__file__).resolve().parent.parent
RETRIEVED = '2026-09-11'
VERIFIER = 'claude-opus-5 (scripted ingest; verse-run, cross-edition and change-log gates)'
J = 'http://justus.anglican.org/resources/bcp/'
COE = ('https://www.churchofengland.org/prayer-and-worship/'
       'worship-texts-and-resources/book-common-prayer/psalter/')
FILES = ['psalter/psalms-1-50', 'psalter/psalms-51-100', 'psalter/psalms-101-150']

NOTE = {
 '1662': (COE + 'psalms-1-5',
   'The Coverdale psalter as the Church of England serves it, from 60 sub-pages '
   'parsed on the page\'s own classes (vlitemheading / vllatinsub / vlpsalm / '
   'vlversenumber). Pages are ordered by the psalm and verse range their URL '
   'encodes; Psalm 17\'s verses 14-16 share one paragraph and are split at their '
   'number spans. The mediant is printed " : " as the book prints it.'),
 '1892': (J + '1892/Psalms.pdf',
   'The 1892 PDF\'s own letters, after a whitespace repair: pypdf\'s plain mode '
   'keeps letters in reading order but kerning splits words; layout mode spaces '
   'well but displaces drop capitals and reads straight across the two printed '
   'columns. A space is kept where both modes agree (layout re-ordered column '
   'by column), and the rest are settled by counted rules that never change a '
   'letter. Tested against an INDEPENDENT witness, the justus dated table of '
   'pre-1928 U.S. psalter changes: 51 of 55 applicable entries agree, including '
   '32 of the 35 changes it dates to 1892 itself. The mediant is the musical '
   'colon, normalized to " : ".'),
 '1928': (J + '1928/Psalms1.htm',
   'The width-400 text column of justus 1928/Psalms{1,2,3}.htm. The width-200 '
   'sidebar of earlier readings is NOT applied (no backward derivation), and the '
   '164 superscript marks pointing into it are removed as apparatus. The '
   'asterisk mediant is normalized to " : ". Eight psalms genuinely differ from '
   '1662 in verse count, each with evidence: 14 (Romans-3 interpolation '
   'removed), 19 (last two verses merged), 45 (opening re-translated), 58, 71, '
   '73, 104 (a long verse split in two), and 89 (see the 1662 VERIFY).'),
 '1979': (J + 'bcpsalt1.txt',
   'The 1979 translation from bcpsalt1.txt and bcpsalt2.txt, each file\'s FTP '
   'header stripped independently. 1979 prints verse 1\'s number and divides '
   'seven long psalms into Parts, both carried. The asterisk mediant is '
   'normalized to " : ".'),
}
EXTRA = {
 ('psalter/selections', '1789'): (J + '1789/Psalter_1789.htm',
   'The ten Selections of Psalms, "to be used instead of the Psalms for the Day", '
   'as citations.'),
 ('tables/proper-psalms', '1789'): (J + '1789/FrontMatter_1789.htm',
   'The Proper Psalms on Certain Days table printed within the 1789 Psalter '
   'rubric; closes the Wave-14 recorded gap.'),
 ('tables/proper-psalms', '1892'): (J + '1892/Psalms_1892.htm',
   'The 1892 Table of Proper Psalms on Certain Days, sixteen days, read left '
   'column then right (liturgical order).'),
}
GAPS = {
 ('1789', 'psalter/psalms-1-50'): 'psalter',
 ('1789', 'psalter/psalms-51-100'): 'psalter',
 ('1789', 'psalter/psalms-101-150'): 'psalter',
 ('1892', 'psalter/selections'): 'selections',
 ('1928', 'psalter/selections'): 'selections',
 ('1928', 'tables/proper-psalms'): 'proper',
}
GAPNOTE = {
 'psalter': ('RECORDED GAP. The 1789 book printed its own Psalter, but no '
             'allow-listed source gives it: justus\'s 1789 index points its '
             'Psalter link at the shared 1928 page, and the 1790 folio\'s text '
             'layer is unusable OCR of a long-s original. Deriving it backwards '
             'from 1928 or 1892 was REJECTED by the maintainer (an apparatus is '
             'only as complete as its editor, so silence is not evidence of no '
             'change). 1789 inherits 1662; this is not a claim that 1789 '
             'reprinted 1662 unchanged.'),
 'selections': ('RECORDED GAP. The book prints Selections of Psalms, but justus '
                'links this edition\'s Selections to the 1789 page (the "looks '
                'shared" trap), so this edition\'s own list is not sourced. It '
                'inherits the 1789 list.'),
 'proper': ('RECORDED GAP. 1928\'s tables are PDF-only and were not transcribed; '
            'it inherits the 1892 table.'),
}
VERIFY_RE = re.compile(r"<!--\s*VERIFY:\s*'([^']*)'(.*?)-->", re.S)


def q(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def record(ed, service, url, note, status='transcribed'):
    f = WT / 'editions' / ed / (service + '.md')
    items = []
    if f.exists() and status == 'transcribed':
        items = [(m.group(1), re.sub(r'\s+', ' ', m.group(2)).strip().lstrip(';').strip())
                 for m in VERIFY_RE.finditer(f.read_text(encoding='utf-8'))]
    rec = ['  - edition: %s' % ed, '    service: %s' % service,
           '    source_url: %s' % q(url), '    retrieved: %s' % RETRIEVED,
           '    status: %s' % status, '    depth: tier-1' if service.startswith('psalter/psalms') else '    depth: table',
           '    verifier: %s' % q(VERIFIER), '    note: %s' % q(note)]
    if items:
        rec.append('    verify_items:')
        for reading, text in items:
            rec += ['      - anchor: %s' % q(service.split('/')[-1]),
                    '        source_reading: %s' % q(reading),
                    '        note: %s' % q(text)]
    else:
        rec.append('    verify_items: []')
    return '\n'.join(rec), len(items)


def main():
    out, n_items = [], 0
    for ed, (url, note) in NOTE.items():
        for svc in FILES:
            r, k = record(ed, svc, url, note)
            out.append(r); n_items += k
    for (svc, ed), (url, note) in EXTRA.items():
        r, k = record(ed, svc, url, note)
        out.append(r); n_items += k
    for (ed, svc), kind in GAPS.items():
        r, _k = record(ed, svc, '(no allow-listed source for this edition)',
                       GAPNOTE[kind], status='inherited-unreviewed')
        out.append(r)
    p = WT / 'provenance.yaml'
    body = p.read_text(encoding='utf-8').rstrip('\n')
    body += ('\n\n  # --- Wave 13: the Psalter ---\n' + '\n'.join(out)
             + '\n  # --- end Wave 13 ---\n')
    p.write_text(body, encoding='utf-8')
    print("appended %d records (%d gaps), %d verify_items" % (len(out), len(GAPS), n_items))


if __name__ == '__main__':
    main()
