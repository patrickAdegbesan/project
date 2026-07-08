"""
TaskMind AI module — NLP parsing, priority calculation, and recommendation engine.
Imported by both app.py (monolith) and the blueprints (refactored structure).
"""
import math
import re
from datetime import date, datetime, timedelta

# ── spaCy setup ──────────────────────────────────────────────────────────────

try:
    import spacy
    from spacy.matcher import Matcher
    nlp = spacy.load('en_core_web_sm')
    SPACY_AVAILABLE = True

    # Matcher patterns for priority keywords
    _matcher = Matcher(nlp.vocab)
    _matcher.add('HIGH_PRIORITY', [
        [{'LOWER': {'IN': ['urgent', 'asap', 'critical', 'immediately']}}],
        [{'LOWER': 'high'}, {'LOWER': 'priority'}],
        [{'LOWER': 'top'}, {'LOWER': 'priority'}],
    ])
    _matcher.add('LOW_PRIORITY', [
        [{'LOWER': {'IN': ['eventually', 'someday', 'whenever']}}],
        [{'LOWER': 'low'}, {'LOWER': 'priority'}],
        [{'LOWER': 'no'}, {'LOWER': 'rush'}],
        [{'LOWER': 'not'}, {'LOWER': 'urgent'}],
    ])

except Exception:
    SPACY_AVAILABLE = False
    _matcher = None
    nlp = None


# ── NLP parsing ───────────────────────────────────────────────────────────────

def _extract_title_spacy(doc):
    """
    Use dependency parsing to find the root verb + direct object as task name.
    Falls back to full text if no clear root is found.
    """
    root = None
    for token in doc:
        if token.dep_ == 'ROOT':
            root = token
            break
    if not root:
        return doc.text.strip()

    # Collect the root verb + its subtree (subject, object, modifiers)
    # but exclude time/date named entities
    date_ent_spans = {t.i for ent in doc.ents if ent.label_ in ('DATE', 'TIME') for t in ent}
    keep = [
        t for t in root.subtree
        if t.i not in date_ent_spans and t.pos_ not in ('PUNCT',)
    ]
    if keep:
        title = doc[keep[0].i : keep[-1].i + 1].text.strip()
        return title if len(title) > 2 else doc.text.strip()
    return doc.text.strip()


def _parse_time(text):
    """Extract HH:MM from text using regex (handles 5pm, 14:30, 2:30 PM)."""
    m = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text, re.IGNORECASE)
    if m:
        hr = int(m.group(1))
        mn = int(m.group(2)) if m.group(2) else 0
        period = m.group(3).lower()
        if period == 'pm' and hr != 12:
            hr += 12
        elif period == 'am' and hr == 12:
            hr = 0
        return f'{hr:02d}:{mn:02d}'
    m24 = re.search(r'\b([01]?\d|2[0-3]):([0-5]\d)\b', text)
    if m24:
        return f'{int(m24.group(1)):02d}:{m24.group(2)}'
    return None


def _parse_date(text, lower):
    """
    Extract due date from text.
    Stage 1: relative keywords (today, tomorrow, next week, weekday names).
    Stage 2: spaCy DATE entities for absolute dates (e.g. "June 25").
    """
    today  = date.today()
    today_wd = today.weekday()
    weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

    if 'today'        in lower: return today.isoformat()
    if 'tomorrow'     in lower: return (today + timedelta(days=1)).isoformat()
    if 'next week'    in lower: return (today + timedelta(days=7)).isoformat()
    if 'next monday'  in lower:
        days = (0 - today_wd + 7) % 7 or 7
        return (today + timedelta(days=days)).isoformat()
    if 'next friday'  in lower:
        days = (4 - today_wd + 7) % 7 or 7
        return (today + timedelta(days=days)).isoformat()

    for i, wd in enumerate(weekdays):
        if re.search(rf'\b{wd}\b', lower):
            days = (i - today_wd + 7) % 7 or 7
            return (today + timedelta(days=days)).isoformat()

    # Stage 2: spaCy named entity DATE
    if SPACY_AVAILABLE and nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                try:
                    from dateutil import parser as dparser
                    parsed = dparser.parse(ent.text, default=datetime(today.year, today.month, today.day))
                    if parsed.date() >= today:
                        return parsed.date().isoformat()
                except Exception:
                    pass

    return None


def _parse_effort(lower):
    """Extract effort in minutes from text."""
    m = re.search(r'(\d+)\s*(?:hour|hr|h)s?\b', lower)
    if m:
        return int(m.group(1)) * 60
    m = re.search(r'(\d+)\s*(?:min|minute)s?\b', lower)
    if m:
        return int(m.group(1))
    return 30  # default


def _parse_importance(text, lower):
    """
    Use spaCy Matcher for priority detection when available,
    otherwise fall back to simple keyword search.
    """
    if SPACY_AVAILABLE and _matcher and nlp:
        doc = nlp(text)
        matches = _matcher(doc)
        labels = {nlp.vocab.strings[mid] for mid, _, _ in matches}
        if 'HIGH_PRIORITY' in labels:
            return 3
        if 'LOW_PRIORITY' in labels:
            return 1
    else:
        if any(w in lower for w in ['urgent','asap','high priority','critical','immediately','top priority']):
            return 3
        if any(w in lower for w in ['low priority','whenever','no rush','eventually','someday','not urgent']):
            return 1
    return 2


# Strip phrases used to clean up the title
_STRIP_PATTERNS = [
    r'\bby\s+(?:tomorrow|today|friday|monday|tuesday|wednesday|thursday|saturday|sunday|next\s+\w+)\b',
    r'\bnext\s+(?:week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(?:tomorrow|today)\b',
    r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\d{1,2}(?::\d{2})?\s*(?:am|pm)\b',
    r'\b\d+\s*(?:hour|hr|h|min|minute)s?\b',
    r'\b(?:high|top|low)\s+priority\b',
    r'\b(?:urgent|asap|critical|immediately|eventually|someday|whenever)\b',
    r'\bno\s+rush\b', r'\bnot\s+urgent\b',
]


def parse_natural_language(text):
    """
    Eight-stage NLP pipeline:
      1. Tokenise through spaCy
      2. Extract due date  (relative keywords → spaCy DATE entities)
      3. Extract due time  (regex patterns)
      4. Extract importance (spaCy Matcher → keyword fallback)
      5. Extract effort    (regex duration patterns)
      6. Extract title     (dependency parse root subtree → regex strip fallback)
      7. Clean title       (strip extracted phrases)
      8. Return structured dict
    """
    lower = text.lower()

    due_date    = _parse_date(text, lower)
    due_time    = _parse_time(lower)
    importance  = _parse_importance(text, lower)
    effort_mins = _parse_effort(lower)

    # Title: prefer spaCy dependency parse
    if SPACY_AVAILABLE and nlp:
        doc   = nlp(text)
        title = _extract_title_spacy(doc)
    else:
        title = text

    # Strip recognised phrases from title
    for pattern in _STRIP_PATTERNS:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    title = re.sub(r'[,\s]+,', ',', title)
    title = re.sub(r'\s+', ' ', title).strip().strip(',.').strip()
    if not title:
        title = text.strip()

    return {
        'title':          title,
        'due_date':       due_date,
        'due_time':       due_time,
        'importance':     importance,
        'effort_minutes': effort_mins,
    }


# ── Priority calculation ──────────────────────────────────────────────────────

def calculate_priority(importance, due_date, effort_minutes):
    """
    Enhanced Eisenhower Matrix formula:
      P_score = (I × 0.35) + (U × 0.30) + (D_f × 0.25) + (E_f × 0.10)

    I   = Importance (3/2/1)
    U   = 1 / (1 + days_to_deadline)          — urgency
    D_f = e^(−days / 3)                        — exponential deadline decay
    E_f = 1 / (1 + effort_minutes / 60)        — effort factor (quick-win boost)
    """
    today = date.today()
    if due_date:
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        days = max(0, (due_date - today).days)
    else:
        days = 14

    I   = importance
    U   = 1 / (1 + days)
    D_f = math.exp(-days / 3)
    E_f = 1 / (1 + effort_minutes / 60)

    score      = (I * 0.35) + (U * 0.30) + (D_f * 0.25) + (E_f * 0.10)
    normalized = min(score / 1.70, 1.0)

    if normalized > 0.70:  label = 'High'
    elif normalized >= 0.40: label = 'Medium'
    else:                    label = 'Low'

    return round(normalized, 4), label


# ── Personal match profile ────────────────────────────────────────────────────

def get_personal_match_profile(user_id):
    from models import Task
    completed = Task.query.filter(
        Task.user_id == user_id,
        Task.completed == True,
        Task.completed_at != None,
    ).all()

    if not completed:
        return {'peak_hour': 10, 'peak_dow': 0, 'preferred_effort_band': 'medium'}

    hour_counts    = [0] * 24
    dow_counts     = [0] * 7
    effort_buckets = {'short': 0, 'medium': 0, 'long': 0}

    for t in completed:
        hour_counts[t.completed_at.hour] += 1
        dow_counts[t.completed_at.weekday()] += 1
        if   t.effort_minutes < 45:   effort_buckets['short']  += 1
        elif t.effort_minutes <= 120:  effort_buckets['medium'] += 1
        else:                          effort_buckets['long']   += 1

    return {
        'peak_hour':             hour_counts.index(max(hour_counts)),
        'peak_dow':              dow_counts.index(max(dow_counts)),
        'preferred_effort_band': max(effort_buckets, key=effort_buckets.get),
    }


def score_personal_match(task, profile):
    task_hour  = int(task.due_time.split(':')[0]) if task.due_time else profile['peak_hour']
    hour_score = max(0, 1 - abs(task_hour - profile['peak_hour']) / 12)

    if task.due_date:
        day_diff  = abs(task.due_date.weekday() - profile['peak_dow'])
        day_diff  = min(day_diff, 7 - day_diff)
        day_score = max(0, 1 - day_diff / 3.5)
    else:
        day_score = 0.5

    band = ('short' if task.effort_minutes < 45
            else 'medium' if task.effort_minutes <= 120
            else 'long')
    effort_score = 1.0 if band == profile['preferred_effort_band'] else 0.4

    return round((hour_score + day_score + effort_score) / 3, 4)


# ── Do Next recommendation ────────────────────────────────────────────────────

def get_do_next(user_id, verbose=False):
    """
    R_score = (P_score × 0.4) + (U_norm × 0.3) + (M_personal × 0.3)
    Returns (best_task, match_pct) or None.
    """
    from models import Task
    today = date.today()
    tasks = Task.query.filter_by(user_id=user_id, completed=False).all()
    if not tasks:
        return None

    profile  = get_personal_match_profile(user_id)
    best     = None
    best_r   = -1
    best_bd  = {}

    if verbose:
        dn = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        print('\n' + '═'*64)
        print('  TaskMind · Do Next Recommendation Engine')
        print('═'*64)
        print(f"  Peak productive hour : {profile['peak_hour']:02d}:00")
        print(f"  Most productive day  : {dn[profile['peak_dow']]}")
        print(f"  Preferred effort     : {profile['preferred_effort_band']}")
        print('─'*64)
        print(f"  {'Task':<36} {'P':>5} {'U':>5} {'M':>5} {'R':>6}")
        print('─'*64)

    for t in tasks:
        days       = max(0, (t.due_date - today).days) if t.due_date else 14
        U_norm     = round(1 / (1 + days), 4)
        M_personal = score_personal_match(t, profile)
        R          = round(t.priority_score * 0.4 + U_norm * 0.3 + M_personal * 0.3, 4)

        if verbose:
            s = (t.title[:34] + '…') if len(t.title) > 35 else t.title
            print(f"  {s:<36} {t.priority_score:>5.2f} {U_norm:>5.2f} {M_personal:>5.2f} {R:>6.3f}"
                  + (' ◀' if R > best_r else ''))

        if R > best_r:
            best_r  = R
            best    = t
            best_bd = {'P': t.priority_score, 'U': U_norm, 'M': M_personal, 'R': R}

    if verbose and best:
        print('─'*64)
        print(f"\n  ✦ Recommended: {best.title}")
        print(f"    P × 0.4 : {best_bd['P']:.2f} → {best_bd['P']*0.4:.3f}")
        print(f"    U × 0.3 : {best_bd['U']:.2f} → {best_bd['U']*0.3:.3f}")
        print(f"    M × 0.3 : {best_bd['M']:.2f} → {best_bd['M']*0.3:.3f}")
        print(f"    R_score : {best_bd['R']:.4f}  ({int(best_r*100)}% match)")
        print('═'*64 + '\n')

    return best, round(best_r, 2)


# ── Helpers ───────────────────────────────────────────────────────────────────

def task_to_dict(t):
    today   = date.today()
    overdue = bool(t.due_date and t.due_date < today and not t.completed)
    days_left = (t.due_date - today).days if t.due_date else None
    return {
        'id':            t.id,
        'title':         t.title,
        'description':   t.description,
        'due_date':      t.due_date.isoformat() if t.due_date else None,
        'due_date_fmt':  t.due_date.strftime('%b %d, %Y') if t.due_date else 'No deadline',
        'due_time':      t.due_time or '',
        'priority_label': t.priority_label,
        'priority_score': t.priority_score,
        'priority_pct':  int(t.priority_score * 100),
        'importance':    t.importance,
        'effort_minutes': t.effort_minutes,
        'effort_fmt':    (f"{t.effort_minutes // 60}h {t.effort_minutes % 60}m"
                          if t.effort_minutes >= 60 else f"{t.effort_minutes}m"),
        'completed':     t.completed,
        'overdue':       overdue,
        'days_left':     days_left,
        'created_at':    t.created_at.isoformat(),
    }


def seed_demo_tasks(user_id):
    from models import Task, db
    today = date.today()
    demos = [
        dict(title='Submit quarterly report', due_date=today + timedelta(days=(4 - today.weekday()) % 7 or 7),
             due_time='17:00', importance=3, effort_minutes=120),
        dict(title='Review project proposal', due_date=today + timedelta(days=1),
             due_time='14:00', importance=3, effort_minutes=60),
        dict(title='Buy groceries', due_date=today + timedelta(days=(5 - today.weekday()) % 7 or 7),
             due_time=None, importance=2, effort_minutes=45),
        dict(title='Call dentist', due_date=today + timedelta(days=(0 - today.weekday() + 7) % 7 + 7),
             due_time=None, importance=2, effort_minutes=15),
        dict(title='Read AI paper', due_date=today + timedelta(days=10),
             due_time=None, importance=1, effort_minutes=180),
        dict(title='Team meeting prep', due_date=today - timedelta(days=1),
             due_time='09:00', importance=3, effort_minutes=30),
    ]
    for d in demos:
        score, label = calculate_priority(d['importance'], d['due_date'], d['effort_minutes'])
        db.session.add(Task(
            user_id=user_id, title=d['title'], due_date=d['due_date'],
            due_time=d['due_time'], importance=d['importance'],
            effort_minutes=d['effort_minutes'], priority_score=score,
            priority_label=label, is_demo=True,
        ))
    db.session.commit()
