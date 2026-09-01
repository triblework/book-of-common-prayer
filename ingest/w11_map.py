#!/usr/bin/env python3
"""Wave 11 — explicit (section, title) -> slug map.

EXPLICIT ON PURPOSE. Fuzzy title matching would quietly misfile a prayer, and
"For Rain" is printed TWICE in every book -- once as a prayer, once as a
thanksgiving -- so the section is part of the key. The builder ABORTS on an
unmapped title rather than dropping it (AUDIT_METHOD: turn a silent loss into a
loud stop).
"""
import re

def norm(t: str) -> str:
    t = t.lower().strip()
    t = t.replace('’', "'").replace('‘', "'")
    t = re.sub(r'[^a-z0-9 ]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

SECTION_HEADS = {
    'prayers', 'thanksgivings', 'collects', 'prayers and thanksgivings',
    'upon several occasions', 'prayers and thanksgivings upon several occasions',
}

# section 'p' = Prayers, 't' = Thanksgivings, 'c' = the 1928 Collects block
MAP = {
 # --- occasional prayers, the 1552 core -------------------------------------
 ('p', 'for rain'): 'for-rain',
 ('p', 'for fair weather'): 'for-fair-weather',
 ('p', 'in the time of dearth and famine i'): 'in-time-of-dearth-and-famine',
 ('p', 'in the time of dearth and famine ii'): 'in-time-of-dearth-and-famine-2',
 ('p', 'in time of dearth and famine'): 'in-time-of-dearth-and-famine',
 ('p', 'in the time of war and tumults'): 'in-time-of-war-and-tumults',
 ('p', 'in time of war and tumults'): 'in-time-of-war-and-tumults',
 ('p', 'in the time of any common plague of sickness'): 'in-time-of-plague',
 ('p', 'in time of great sickness and mortality'): 'in-time-of-plague',
 ('p', 'a prayer that may be said after any of the former'): 'prayer-after-the-former',
 # --- 1662 additions ---------------------------------------------------------
 ('p', 'a prayer for the high court of parliament to be read during their session'):
     'for-the-high-court-of-parliament',
 ('p', 'a collect or prayer for all conditions of men to be used at such times '
       'when the litany is not appointed to be said'): 'for-all-conditions-of-men',
 ('p', 'a prayer for all conditions of men'): 'for-all-conditions-of-men',
 # --- American -------------------------------------------------------------
 ('p', 'for those who are to be admitted into holy orders'):
     'for-those-to-be-admitted-into-holy-orders',
 ('p', 'for a sick person'): 'for-a-sick-person',
 ('p', 'for a sick child'): 'for-a-sick-child',
 ('p', 'for a person or persons going to sea'): 'for-a-person-going-to-sea',
 ('p', 'for a person under affliction'): 'for-a-person-under-affliction',
 ('p', 'for malefactors after condemnation'): 'for-malefactors-after-condemnation',
 ('p', 'a prayer to be used at the meetings of convention'): 'for-the-convention',
 ('p', 'a prayer for congress'): 'for-congress',
 ('p', 'for a state legislature'): 'for-a-state-legislature',
 ('p', 'for courts of justice'): 'for-courts-of-justice',
 ('p', 'for our country'): 'for-our-country',
 ('p', 'for the church'): 'for-the-church',
 ('p', 'for the unity of god s people'): 'for-unity',
 ('p', 'for missions'): 'for-missions',
 ('p', 'for the increase of the ministry'): 'for-the-increase-of-the-ministry',
 ('p', 'for fruitful seasons'): 'for-fruitful-seasons',
 ('p', 'in time of calamity'): 'in-time-of-calamity',
 ('p', 'for the army'): 'for-the-army',
 ('p', 'for the navy'): 'for-the-navy',
 ('p', 'memorial days'): 'memorial-days',
 ('p', 'for schools colleges and universities'): 'for-schools-colleges-universities',
 ('p', 'for religious education'): 'for-religious-education',
 ('p', 'for children'): 'for-children',
 ('p', 'for those about to be confirmed'): 'for-those-about-to-be-confirmed',
 ('p', 'for christian service'): 'for-christian-service',
 ('p', 'for social justice'): 'for-social-justice',
 ('p', 'for every man in his work'): 'for-every-man-in-his-work',
 ('p', 'for the family of nations'): 'for-the-family-of-nations',
 ('p', 'for prisoners'): 'for-prisoners',
 ('p', 'a bidding prayer'): 'a-bidding-prayer',
 # --- thanksgivings ---------------------------------------------------------
 ('t', 'a general thanksgiving'): 'thanksgiving-general',
 ('t', 'a thanksgiving to almighty god for the fruits of the earth and all the '
       'other blessings of his merciful providence'): 'thanksgiving-for-fruits-of-the-earth',
 ('t', 'for rain'): 'thanksgiving-for-rain',
 ('t', 'for fair weather'): 'thanksgiving-for-fair-weather',
 ('t', 'for plenty'): 'thanksgiving-for-plenty',
 ('t', 'for peace and deliverance from our enemies'):
     'thanksgiving-for-peace-and-deliverance',
 ('t', 'for restoring publick peace at home'): 'thanksgiving-for-restoring-publick-peace',
 ('t', 'for restoring public peace at home'): 'thanksgiving-for-restoring-publick-peace',
 ('t', 'for deliverance from the plague or other common sickness'):
     'thanksgiving-for-deliverance-from-plague',
 ('t', 'for deliverance from great sickness and mortality'):
     'thanksgiving-for-deliverance-from-plague',
 ('t', 'the thanksgiving of women after childbirth'): 'thanksgiving-women-after-childbirth',
 ('t', 'the thanksgiving of women after child birth'): 'thanksgiving-women-after-childbirth',
 ('t', 'for a recovery from sickness'): 'thanksgiving-for-recovery-from-sickness',
 ('t', 'for recovery from sickness'): 'thanksgiving-for-recovery-from-sickness',
 ('t', 'for a child s recovery from sickness'): 'thanksgiving-for-childs-recovery',
 ('t', 'for a safe return from sea'): 'thanksgiving-for-safe-return-from-sea',
 ('t', 'for a safe return from a journey'): 'thanksgiving-for-safe-return-from-sea',
}

# Titles printed as a bare "Or this." -- a second form of the PRECEDING slug.
SECOND_FORM = {'or this'}

# The CoE marks this rubric up as a heading; it belongs to the prayer before it.
RUBRIC_AS_TITLE = {
    'this to be said when any desire the prayers of the congregation',
    'this to be said when any that have been prayed for desire to return praise',
}

# The Ember-weeks pair share one printed title; disambiguated by order.
EMBER = 'in the ember weeks to be said every day for those that are to be admitted into holy orders'

# 1928 Collects: printed untitled under one shared rubric, so keyed by order.
COLLECTS_1928 = [
    'collect-peace-i-leave-with-you',
    'collect-assist-us-mercifully',
    'collect-grant-we-beseech-thee',
    'collect-direct-us-o-lord',
    'collect-fountain-of-all-wisdom',
    'collect-promised-to-hear-petitions',
]
