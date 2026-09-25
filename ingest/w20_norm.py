"""w20_norm.py -- comparison key for two OCR reads of one Kalendar cell.

Used ONLY to decide whether two machine reads agree; never to produce text.
Folds the confusions Vision makes on this type (Cyrillic look-alikes, case,
spacing around stops, a trailing stop) and nothing that could hide a real
difference in a reading."""
import re

LOOK = str.maketrans({'х': 'x', 'Х': 'x', 'і': 'i', 'І': 'i', 'ї': 'i', 'ü': 'ii',
                      'ï': 'i', 'í': 'i', 'Í': 'i', 'т': 't', 'г': 'r', 'К': 'k',
                      'к': 'k', 'в': 'l', 'А': 'a', 'а': 'a', 'В': 'b', 'С': 'c',
                      'с': 'c', 'Е': 'e', 'е': 'e', 'М': 'm', 'Н': 'h', 'О': 'o',
                      'о': 'o', 'Р': 'p', 'р': 'p', 'у': 'y', 'б': '6', 'з': '3',
                      '·': ''})


def key(s):
    s = (s or '').translate(LOOK).lower()
    s = re.sub(r'\s*([.:,])\s*', r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s.rstrip('.,:; ')
