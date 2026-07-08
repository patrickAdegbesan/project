from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta, date
import json
import math
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'taskmind-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmind.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Try to load spaCy
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False

# ── Models ──────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text, default='')
    due_date = db.Column(db.Date, nullable=True)
    due_time = db.Column(db.String(10), nullable=True)
    priority_label = db.Column(db.String(20), default='Medium')  # High / Medium / Low
    priority_score = db.Column(db.Float, default=0.5)
    importance = db.Column(db.Integer, default=2)  # 1/2/3
    effort_minutes = db.Column(db.Integer, default=30)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_demo = db.Column(db.Boolean, default=False)

# ── NLP Parsing ─────────────────────────────────────────────────────────────

def parse_natural_language(text):
    """Extract task fields from free-form text."""
    result = {
        'title': text,
        'due_date': None,
        'due_time': None,
        'importance': 2,
        'effort_minutes': 30,
        'priority_label': 'Medium',
    }

    today = date.today()
    lower = text.lower()

    # --- Priority hints ---
    if any(w in lower for w in ['urgent', 'asap', 'high priority', 'important', 'critical']):
        result['importance'] = 3
    elif any(w in lower for w in ['low priority', 'whenever', 'no rush', 'eventually']):
        result['importance'] = 1

    # --- Effort hints ---
    effort_match = re.search(r'(\d+)\s*(?:hour|hr|h)s?\b', lower)
    if effort_match:
        result['effort_minutes'] = int(effort_match.group(1)) * 60
    else:
        effort_match = re.search(r'(\d+)\s*(?:min|minute)s?\b', lower)
        if effort_match:
            result['effort_minutes'] = int(effort_match.group(1))

    # --- Time extraction ---
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)', lower)
    if time_match:
        hr = int(time_match.group(1))
        mn = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3)
        if period == 'pm' and hr != 12:
            hr += 12
        elif period == 'am' and hr == 12:
            hr = 0
        result['due_time'] = f"{hr:02d}:{mn:02d}"

    # --- Date extraction (regex-based) ---
    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    today_wd = today.weekday()  # 0=Mon

    if 'today' in lower:
        result['due_date'] = today.isoformat()
    elif 'tomorrow' in lower:
        result['due_date'] = (today + timedelta(days=1)).isoformat()
    elif 'next week' in lower:
        result['due_date'] = (today + timedelta(days=7)).isoformat()
    elif 'next monday' in lower:
        days_ahead = (0 - today_wd + 7) % 7 or 7
        result['due_date'] = (today + timedelta(days=days_ahead)).isoformat()
    elif 'next friday' in lower:
        days_ahead = (4 - today_wd + 7) % 7 or 7
        result['due_date'] = (today + timedelta(days=days_ahead)).isoformat()
    else:
        for i, wd in enumerate(weekdays):
            if wd in lower:
                days_ahead = (i - today_wd + 7) % 7 or 7
                result['due_date'] = (today + timedelta(days=days_ahead)).isoformat()
                break

    # --- spaCy DATE entities override ---
    if SPACY_AVAILABLE:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'DATE' and not result['due_date']:
                # basic spaCy fallback — keep regex result if already found
                pass

    # Clean title: remove time/date phrases
    title = text
    for pattern in [
        r'\bby\s+(tomorrow|today|friday|monday|tuesday|wednesday|thursday|saturday|sunday|next\s+\w+)\b',
        r'\b(tomorrow|today)\b',
        r'\bnext\s+(week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
        r'\d{1,2}(?::\d{2})?\s*(?:am|pm)\b',
        r'\b\d+\s*(?:hour|hr|h|min|minute)s?\b',
        r'\b(high|low)\s+priority\b',
        r'\burgent\b', r'\basap\b', r'\bcritical\b', r'\bimportant\b',
        r'\bno rush\b', r'\bwhenever\b', r'\beventually\b',
    ]:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    title = re.sub(r'[,\s]+,', ',', title)          # collapse ", , " → ","
    title = re.sub(r'\s+', ' ', title).strip().strip(',.').strip()
    if title:
        result['title'] = title

    return result

# ── Priority Calculation ─────────────────────────────────────────────────────

def calculate_priority(importance, due_date, effort_minutes):
    """Eisenhower Matrix Enhanced formula."""
    today = date.today()
    if due_date:
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        days = max(0, (due_date - today).days)
    else:
        days = 14  # no deadline → treat as 2 weeks out

    I = importance  # 1/2/3
    U = 1 / (1 + days)
    D_f = math.exp(-days / 3)
    E_f = 1 / (1 + effort_minutes / 60)

    score = (I * 0.35) + (U * 0.30) + (D_f * 0.25) + (E_f * 0.10)
    # Normalize: max possible ≈ 3*0.35 + 1*0.30 + 1*0.25 + 1*0.10 = 1.70
    normalized = min(score / 1.70, 1.0)

    if normalized > 0.70:
        label = 'High'
    elif normalized >= 0.40:
        label = 'Medium'
    else:
        label = 'Low'

    return round(normalized, 4), label

# ── Helpers ─────────────────────────────────────────────────────────────────

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


def seed_demo_tasks(user_id):
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
        task = Task(
            user_id=user_id,
            title=d['title'],
            due_date=d['due_date'],
            due_time=d['due_time'],
            importance=d['importance'],
            effort_minutes=d['effort_minutes'],
            priority_score=score,
            priority_label=label,
            is_demo=True,
        )
        db.session.add(task)
    db.session.commit()


def get_personal_match_profile(user_id):
    """
    Derive M_personal heuristics from the user's actual completion history.
    Returns a dict with:
      - peak_hour: the hour of day they complete most tasks
      - peak_dow:  the weekday (0=Mon) they complete most tasks
      - preferred_effort_band: 'short'(<45min), 'medium'(45-120), 'long'(>120)
    Falls back to neutral defaults when there is no history.
    """
    completed = Task.query.filter(
        Task.user_id == user_id,
        Task.completed == True,
        Task.completed_at != None
    ).all()

    if not completed:
        return {'peak_hour': 10, 'peak_dow': 0, 'preferred_effort_band': 'medium'}

    hour_counts = [0] * 24
    dow_counts  = [0] * 7
    effort_buckets = {'short': 0, 'medium': 0, 'long': 0}

    for t in completed:
        hour_counts[t.completed_at.hour] += 1
        dow_counts[t.completed_at.weekday()] += 1
        if t.effort_minutes < 45:
            effort_buckets['short'] += 1
        elif t.effort_minutes <= 120:
            effort_buckets['medium'] += 1
        else:
            effort_buckets['long'] += 1

    peak_hour = hour_counts.index(max(hour_counts))
    peak_dow  = dow_counts.index(max(dow_counts))
    preferred_effort_band = max(effort_buckets, key=effort_buckets.get)

    return {
        'peak_hour': peak_hour,
        'peak_dow': peak_dow,
        'preferred_effort_band': preferred_effort_band,
    }


def score_personal_match(task, profile):
    """
    Compute M_personal (0–1) for a task given a user's historical profile.
    Three sub-components, equal weight:
      1. Hour match   — task due time aligns with user's peak productive hour
      2. Day match    — task due date falls on user's most productive weekday
      3. Effort match — task effort matches the user's preferred effort band
    """
    # 1. Hour match
    task_hour = int(task.due_time.split(':')[0]) if task.due_time else profile['peak_hour']
    hour_diff = abs(task_hour - profile['peak_hour'])
    hour_score = max(0, 1 - hour_diff / 12)

    # 2. Day match
    if task.due_date:
        day_diff = abs(task.due_date.weekday() - profile['peak_dow'])
        day_diff = min(day_diff, 7 - day_diff)   # wrap around week
        day_score = max(0, 1 - day_diff / 3.5)
    else:
        day_score = 0.5

    # 3. Effort band match
    if task.effort_minutes < 45:
        band = 'short'
    elif task.effort_minutes <= 120:
        band = 'medium'
    else:
        band = 'long'
    effort_score = 1.0 if band == profile['preferred_effort_band'] else 0.4

    return round((hour_score + day_score + effort_score) / 3, 4)


def get_do_next(user_id, verbose=False):
    """
    R_score = (P_score × 0.4) + (U_norm × 0.3) + (M_personal × 0.3)
    Returns (best_task, match_pct) or None.
    When verbose=True, prints a terminal breakdown of every candidate.
    """
    today = date.today()
    tasks = Task.query.filter_by(user_id=user_id, completed=False).all()
    if not tasks:
        return None

    profile = get_personal_match_profile(user_id)

    if verbose:
        days_names = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        print("\n" + "═"*64)
        print("  TaskMind · Do Next Recommendation Engine")
        print("═"*64)
        print(f"  User profile:")
        print(f"    Peak productive hour : {profile['peak_hour']:02d}:00")
        print(f"    Most productive day  : {days_names[profile['peak_dow']]}")
        print(f"    Preferred effort band: {profile['preferred_effort_band']}")
        print("─"*64)
        print(f"  {'Task':<36} {'P':>5} {'U':>5} {'M':>5} {'R':>6}")
        print("─"*64)

    best = None
    best_r = -1
    best_breakdown = {}

    for t in tasks:
        days = max(0, (t.due_date - today).days) if t.due_date else 14
        U_norm   = round(1 / (1 + days), 4)
        M_personal = score_personal_match(t, profile)
        R = round((t.priority_score * 0.4) + (U_norm * 0.3) + (M_personal * 0.3), 4)

        if verbose:
            title_str = (t.title[:34] + '…') if len(t.title) > 35 else t.title
            marker = ' ◀' if R > best_r else ''
            print(f"  {title_str:<36} {t.priority_score:>5.2f} {U_norm:>5.2f} {M_personal:>5.2f} {R:>6.3f}{marker}")

        if R > best_r:
            best_r = R
            best = t
            best_breakdown = {
                'P_score': t.priority_score,
                'U_norm': U_norm,
                'M_personal': M_personal,
                'R_score': R,
            }

    match_pct = round(best_r, 2)

    if verbose and best:
        print("─"*64)
        print(f"\n  ✦ Recommended: {best.title}")
        print(f"    Priority score (P × 0.4) : {best_breakdown['P_score']:.2f} → {best_breakdown['P_score']*0.4:.3f}")
        print(f"    Urgency score  (U × 0.3) : {best_breakdown['U_norm']:.2f} → {best_breakdown['U_norm']*0.3:.3f}")
        print(f"    Personal match (M × 0.3) : {best_breakdown['M_personal']:.2f} → {best_breakdown['M_personal']*0.3:.3f}")
        print(f"    ─────────────────────────────────────────")
        print(f"    R_score                  : {best_breakdown['R_score']:.4f}  ({int(match_pct*100)}% match)")
        print(f"\n  Factors: {best.priority_label.lower()} priority"
              f" + {'overdue' if best.due_date and best.due_date < today else str((best.due_date - today).days) + 'd to deadline' if best.due_date else 'no deadline'}"
              f" + {profile['preferred_effort_band']} task preference")
        print("═"*64 + "\n")

    return best, match_pct


def task_to_dict(t):
    today = date.today()
    overdue = bool(t.due_date and t.due_date < today and not t.completed)
    days_left = (t.due_date - today).days if t.due_date else None
    return {
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'due_date': t.due_date.isoformat() if t.due_date else None,
        'due_date_fmt': t.due_date.strftime('%b %d, %Y') if t.due_date else 'No deadline',
        'due_time': t.due_time or '',
        'priority_label': t.priority_label,
        'priority_score': t.priority_score,
        'priority_pct': int(t.priority_score * 100),
        'importance': t.importance,
        'effort_minutes': t.effort_minutes,
        'effort_fmt': f"{t.effort_minutes // 60}h {t.effort_minutes % 60}m" if t.effort_minutes >= 60 else f"{t.effort_minutes}m",
        'completed': t.completed,
        'overdue': overdue,
        'days_left': days_left,
        'created_at': t.created_at.isoformat(),
    }

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()
        seed_demo_tasks(user.id)
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    today = date.today()
    tasks = Task.query.filter_by(user_id=user.id).order_by(Task.created_at.desc()).all()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.completed)
    pending = sum(1 for t in tasks if not t.completed)
    overdue = sum(1 for t in tasks if t.due_date and t.due_date < today and not t.completed)

    do_next_result = get_do_next(user.id)
    do_next = None
    do_next_pct = 0
    if do_next_result:
        do_next_task, do_next_pct = do_next_result
        do_next = task_to_dict(do_next_task)
        do_next_pct = int(do_next_pct * 100)

    # Chart: tasks completed per day last 7 days
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%a'))
        count = sum(1 for t in tasks if t.completed and t.completed_at and t.completed_at.date() == d)
        chart_data.append(count)

    task_dicts = [task_to_dict(t) for t in tasks]

    return render_template('dashboard.html',
        user=user,
        tasks=task_dicts,
        total=total,
        completed=completed,
        pending=pending,
        overdue=overdue,
        do_next=do_next,
        do_next_pct=do_next_pct,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
    )


@app.route('/api/parse', methods=['POST'])
@login_required
def api_parse():
    text = request.json.get('text', '')
    parsed = parse_natural_language(text)
    score, label = calculate_priority(
        parsed['importance'],
        parsed['due_date'],
        parsed['effort_minutes']
    )
    parsed['priority_score'] = score
    parsed['priority_label'] = label
    parsed['priority_pct'] = int(score * 100)
    return jsonify(parsed)


@app.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    data = request.json
    user = current_user()
    due_date = None
    if data.get('due_date'):
        try:
            due_date = date.fromisoformat(data['due_date'])
        except ValueError:
            pass
    importance = int(data.get('importance', 2))
    effort_minutes = int(data.get('effort_minutes', 30))
    score, label = calculate_priority(importance, due_date, effort_minutes)
    task = Task(
        user_id=user.id,
        title=data['title'],
        description=data.get('description', ''),
        due_date=due_date,
        due_time=data.get('due_time') or None,
        importance=importance,
        effort_minutes=effort_minutes,
        priority_score=score,
        priority_label=label,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'task': task_to_dict(task)})


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    data = request.json
    if 'completed' in data:
        task.completed = data['completed']
        task.completed_at = datetime.utcnow() if data['completed'] else None
    if 'title' in data:
        task.title = data['title']
    if 'due_date' in data:
        task.due_date = date.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'due_time' in data:
        task.due_time = data['due_time'] or None
    if 'importance' in data:
        task.importance = int(data['importance'])
    if 'effort_minutes' in data:
        task.effort_minutes = int(data['effort_minutes'])
    if 'description' in data:
        task.description = data['description']
    score, label = calculate_priority(task.importance, task.due_date, task.effort_minutes)
    task.priority_score = score
    task.priority_label = label
    db.session.commit()

    # Check overdue tasks to suggest rescheduling
    today = date.today()
    overdue_tasks = Task.query.filter_by(user_id=session['user_id'], completed=False).filter(
        Task.due_date < today).all()
    suggestions = []
    if task.completed and overdue_tasks:
        for ot in overdue_tasks[:2]:
            suggestions.append({'id': ot.id, 'title': ot.title,
                                 'suggested_date': (today + timedelta(days=1)).isoformat()})

    return jsonify({'success': True, 'task': task_to_dict(task), 'reschedule_suggestions': suggestions})


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/tasks/<int:task_id>/reschedule', methods=['POST'])
@login_required
def api_reschedule(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    new_date_str = request.json.get('new_date')
    if new_date_str:
        task.due_date = date.fromisoformat(new_date_str)
        score, label = calculate_priority(task.importance, task.due_date, task.effort_minutes)
        task.priority_score = score
        task.priority_label = label
        db.session.commit()
    return jsonify({'success': True, 'task': task_to_dict(task)})


@app.route('/profile')
@login_required
def profile():
    user = current_user()
    today = date.today()
    tasks = Task.query.filter_by(user_id=user.id).all()
    total = len(tasks)
    completed = [t for t in tasks if t.completed]
    completion_rate = round(len(completed) / total * 100) if total else 0

    # Average effort of completed tasks
    avg_effort = round(sum(t.effort_minutes for t in completed) / len(completed)) if completed else 0

    # This week vs last week
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)
    this_week = sum(1 for t in completed if t.completed_at and t.completed_at.date() >= week_start)
    last_week = sum(1 for t in completed if t.completed_at and last_week_start <= t.completed_at.date() < week_start)

    # Most productive day
    day_counts = [0] * 7
    for t in completed:
        if t.completed_at:
            day_counts[t.completed_at.weekday()] += 1
    days_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    most_productive_day = days_names[day_counts.index(max(day_counts))] if any(day_counts) else 'N/A'

    return render_template('profile.html', user=user,
        total=total, completion_rate=completion_rate,
        avg_effort=avg_effort, this_week=this_week, last_week=last_week,
        most_productive_day=most_productive_day,
        completed_count=len(completed))


@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    user = current_user()
    current = request.form['current_password']
    new_pw = request.form['new_password']
    if bcrypt.check_password_hash(user.password, current):
        user.password = bcrypt.generate_password_hash(new_pw).decode('utf-8')
        db.session.commit()
        flash('Password changed successfully.', 'success')
    else:
        flash('Current password is incorrect.', 'danger')
    return redirect(url_for('profile'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
