"""
Terminal demo of the calculate_priority function (Screenshot 4.4).
Run: python show_priority.py
"""
import math
from datetime import date, timedelta
from ai import calculate_priority

TODAY = date.today()

def d(offset):
    return TODAY + timedelta(days=offset)

EXAMPLES = [
    dict(title="Team meeting prep (OVERDUE)",  importance=3, due_date=d(-1),  effort=30),
    dict(title="Submit quarterly report",       importance=3, due_date=d(1),   effort=120),
    dict(title="Fix production bug ASAP",       importance=3, due_date=d(0),   effort=60),
    dict(title="Review project proposal",       importance=3, due_date=d(2),   effort=60),
    dict(title="Buy groceries",                 importance=2, due_date=d(3),   effort=45),
    dict(title="Call dentist",                  importance=2, due_date=d(11),  effort=15),
    dict(title="Read AI paper",                 importance=1, due_date=d(10),  effort=180),
    dict(title="Explore new ML libraries",      importance=1, due_date=d(30),  effort=120),
]

print('\n' + '═'*72)
print('  TaskMind · Priority Calculation (Enhanced Eisenhower Matrix)')
print('  P_score = (I × 0.35) + (U × 0.30) + (D_f × 0.25) + (E_f × 0.10)')
print('═'*72)
print(f"\n  {'Task':<38} {'I':>3} {'days':>5} {'U':>5} {'D_f':>5} {'E_f':>5} {'Score':>6}  {'Label'}")
print('  ' + '─'*68)

for ex in EXAMPLES:
    imp  = ex['importance']
    due  = ex['due_date']
    eff  = ex['effort']
    days = max(0, (due - TODAY).days)

    I   = imp
    U   = 1 / (1 + days)
    D_f = math.exp(-days / 3)
    E_f = 1 / (1 + eff / 60)

    score, label = calculate_priority(imp, due, eff)
    pct = int(score * 100)

    bar = {'High': '🔴', 'Medium': '🟠', 'Low': '⚪'}[label]
    t   = (ex['title'][:36] + '…') if len(ex['title']) > 37 else ex['title']
    print(f"  {t:<38} {I:>3}  {days:>4}  {U:>5.2f}  {D_f:>5.2f}  {E_f:>5.2f}  {pct:>4}%  {bar} {label}")

print('\n  Formula components:')
print('    I   = Importance (3=High, 2=Medium, 1=Low)         weight 0.35')
print('    U   = 1/(1+days)  — urgency                        weight 0.30')
print('    D_f = e^(-days/3) — exponential deadline decay     weight 0.25')
print('    E_f = 1/(1+effort/60) — quick-win boost            weight 0.10')
print('    Normalized against theoretical max ≈ 1.70')
print('    High > 70%  |  Medium 40–70%  |  Low < 40%')
print('\n' + '═'*72 + '\n')
