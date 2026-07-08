"""
Terminal demo of the NLP parsing pipeline (Screenshot 4.3).
Run: python show_nlp.py
"""
import spacy
from ai import parse_natural_language, calculate_priority

print('\n' + '═'*64)
print('  TaskMind · NLP Parsing Pipeline Demo')
print('  spaCy en_core_web_sm + custom Matcher rules')
print('═'*64)

nlp = spacy.load('en_core_web_sm')
print(f"\n  spaCy model loaded  : en_core_web_sm")
print(f"  Pipeline components : {nlp.pipe_names}")
print(f"  Language            : {nlp.lang}  |  Vocab size: {len(nlp.vocab):,}")

TESTS = [
    "Submit quarterly report by Friday 5pm, high priority, 2 hours",
    "Call dentist tomorrow at 2:30pm, 15 minutes",
    "Read AI paper next week, low priority, 3 hours",
    "Fix production bug ASAP",
    "Plan team offsite next Monday, no rush, 4 hours",
    "Buy groceries Saturday, 45 minutes",
]

print('\n' + '─'*64)
print(f"  {'Input text':<45} {'Title':<25}")
print('─'*64)

for text in TESTS:
    r = parse_natural_language(text)
    score, label = calculate_priority(r['importance'], r['due_date'], r['effort_minutes'])

    imp_map = {3: 'High', 2: 'Medium', 1: 'Low'}
    short = (text[:42] + '…') if len(text) > 43 else text

    print(f"\n  Input  : {text}")
    print(f"  ┌─ Title      : {r['title']}")
    print(f"  ├─ Due date   : {r['due_date'] or '—'}")
    print(f"  ├─ Due time   : {r['due_time'] or '—'}")
    print(f"  ├─ Importance : {imp_map[r['importance']]} ({r['importance']})")
    print(f"  ├─ Effort     : {r['effort_minutes']} min")
    print(f"  └─ Priority   : {label} ({int(score*100)}%)")

print('\n' + '═'*64 + '\n')
