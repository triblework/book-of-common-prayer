#!/usr/bin/env python3
"""w10_1979.py — parse the 1979 collects e-text (Wave 10).

Authoring-only; NOT published. Text flows e-text -> script -> file; nothing is
emitted as model output.

bcpcolct.txt structure:
    <Collects:  Traditional>  ... <Collects:  Contemporary>
    <Occasion Name>  =December 25=      heading (the =...= is the calendar date)
    ...collect body...
    *or this*                           an alternative collect follows
    *Preface of Advent*                 the proper preface pointer (not a collect)

'=Amen.=' is the e-text's emphasis marking, normalized to 'Amen.' here.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "spines-w10", "1979_bcpcolct.txt")

HEAD = re.compile(r"^<(?P<name>[^>]+)>\s*(?P<rest>.*)$")
STAR = re.compile(r"^\*(?P<note>.*?)\*?\s*$")


def _clean(text):
    text = text.replace("=Amen.=", "Amen.")
    text = re.sub(r"=([^=]*)=", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def load(section):
    """section: 'Traditional' or 'Contemporary' -> {occasion: {...}} in order."""
    lines = open(SRC, encoding="utf-8").read().splitlines()
    starts = {}
    for i, ln in enumerate(lines):
        m = HEAD.match(ln)
        if m and m.group("name").strip().startswith("Collects:"):
            starts[m.group("name").split(":", 1)[1].strip()] = i
    if section not in starts:
        raise SystemExit(f"section not found: {section}")
    begin = starts[section]
    end = min([v for v in starts.values() if v > begin] + [len(lines)])

    out, cur, buf, alts, prefaces = {}, None, [], [], []
    # An italic direction opens with '*' but only its LAST line ends with '*';
    # its continuation lines look like ordinary text and would otherwise be
    # absorbed into the collect body.
    in_note = False

    def flush():
        if cur is None:
            return
        body = _clean(" ".join(buf))
        if body:
            alts.append(body)
        out[cur] = {"collects": [a for a in alts if a],
                    "prefaces": list(prefaces)}

    for ln in lines[begin + 1:end]:
        m = HEAD.match(ln)
        if m:
            name = m.group("name").strip()
            if name.lower().startswith("page"):
                continue
            flush()
            cur, buf, alts, prefaces = name, [], [], []
            in_note = False
            continue
        if cur is None:
            continue
        stripped = ln.strip()
        if not stripped:
            continue
        if in_note:
            if stripped.endswith("*"):
                in_note = False
            continue
        if stripped.startswith("*"):
            if not stripped.endswith("*") or stripped == "*":
                in_note = True
                continue
            note = STAR.match(stripped).group("note").strip()
            if note.lower().startswith("or this"):
                body = _clean(" ".join(buf))
                if body:
                    alts.append(body)
                buf = []
            elif note.lower().startswith("preface of"):
                prefaces.append(note)
            # other italic notes are rubrics/directions; kept out of the collect
            continue
        buf.append(stripped)
    flush()
    return out


if __name__ == "__main__":
    for sec in ("Traditional", "Contemporary"):
        data = load(sec)
        print(f"{sec}: {len(data)} occasions, "
              f"{sum(len(v['collects']) for v in data.values())} collects")
