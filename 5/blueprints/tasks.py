from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from models import db, Task, TaskHistory
from ai import calculate_priority, get_do_next, task_to_dict, seed_demo_tasks
from datetime import date, datetime, timedelta
from functools import wraps
import json

tasks_bp = Blueprint('tasks', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def current_user():
    from models import User
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


# ── Pages ────────────────────────────────────────────────────────────────────

@tasks_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('tasks.dashboard'))
    return redirect(url_for('auth.login'))


@tasks_bp.route('/dashboard')
@login_required
def dashboard():
    user  = current_user()
    today = date.today()
    all_tasks = Task.query.filter_by(user_id=user.id).order_by(Task.created_at.desc()).all()

    total     = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.completed)
    pending   = sum(1 for t in all_tasks if not t.completed)
    overdue   = sum(1 for t in all_tasks if t.due_date and t.due_date < today and not t.completed)

    do_next_result = get_do_next(user.id)
    do_next, do_next_pct = (None, 0)
    if do_next_result:
        do_next_task, raw_pct = do_next_result
        do_next     = task_to_dict(do_next_task)
        do_next_pct = int(raw_pct * 100)

    chart_labels, chart_data = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%a'))
        chart_data.append(sum(
            1 for t in all_tasks
            if t.completed and t.completed_at and t.completed_at.date() == d
        ))

    return render_template('dashboard.html',
        user=user,
        tasks=[task_to_dict(t) for t in all_tasks],
        total=total, completed=completed, pending=pending, overdue=overdue,
        do_next=do_next, do_next_pct=do_next_pct,
        chart_labels=json.dumps(chart_labels),
        chart_data=json.dumps(chart_data),
    )


@tasks_bp.route('/profile')
@login_required
def profile():
    from models import User
    user  = current_user()
    today = date.today()
    all_tasks = Task.query.filter_by(user_id=user.id).all()
    total     = len(all_tasks)
    completed = [t for t in all_tasks if t.completed]
    completion_rate = round(len(completed) / total * 100) if total else 0
    avg_effort = round(sum(t.effort_minutes for t in completed) / len(completed)) if completed else 0

    week_start      = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)
    this_week = sum(1 for t in completed if t.completed_at and t.completed_at.date() >= week_start)
    last_week = sum(1 for t in completed if t.completed_at and last_week_start <= t.completed_at.date() < week_start)

    day_counts = [0] * 7
    for t in completed:
        if t.completed_at:
            day_counts[t.completed_at.weekday()] += 1
    days_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    most_productive_day = days_names[day_counts.index(max(day_counts))] if any(day_counts) else 'N/A'

    return render_template('profile.html', user=user,
        total=total, completion_rate=completion_rate,
        avg_effort=avg_effort, this_week=this_week, last_week=last_week,
        most_productive_day=most_productive_day,
        completed_count=len(completed))


# ── CRUD API ─────────────────────────────────────────────────────────────────

@tasks_bp.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    data = request.json
    due_date = None
    if data.get('due_date'):
        try:
            due_date = date.fromisoformat(data['due_date'])
        except ValueError:
            pass
    importance     = int(data.get('importance', 2))
    effort_minutes = int(data.get('effort_minutes', 30))
    score, label   = calculate_priority(importance, due_date, effort_minutes)
    task = Task(
        user_id        = session['user_id'],
        title          = data['title'],
        description    = data.get('description', ''),
        due_date       = due_date,
        due_time       = data.get('due_time') or None,
        importance     = importance,
        effort_minutes = effort_minutes,
        priority_score = score,
        priority_label = label,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'task': task_to_dict(task)})


@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    data = request.json
    if 'completed'      in data:
        task.completed   = data['completed']
        task.completed_at = datetime.utcnow() if data['completed'] else None
    if 'title'          in data: task.title          = data['title']
    if 'description'    in data: task.description    = data['description']
    if 'due_time'       in data: task.due_time        = data['due_time'] or None
    if 'importance'     in data: task.importance      = int(data['importance'])
    if 'effort_minutes' in data: task.effort_minutes  = int(data['effort_minutes'])
    if 'due_date'       in data:
        task.due_date = date.fromisoformat(data['due_date']) if data['due_date'] else None

    score, label = calculate_priority(task.importance, task.due_date, task.effort_minutes)
    task.priority_score = score
    task.priority_label = label
    db.session.commit()

    today = date.today()
    overdue_tasks = Task.query.filter_by(user_id=session['user_id'], completed=False).filter(
        Task.due_date < today).all()
    suggestions = []
    if task.completed and overdue_tasks:
        for ot in overdue_tasks[:2]:
            suggestions.append({'id': ot.id, 'title': ot.title,
                                 'suggested_date': (today + timedelta(days=1)).isoformat()})

    return jsonify({'success': True, 'task': task_to_dict(task),
                    'reschedule_suggestions': suggestions})


@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})


@tasks_bp.route('/api/tasks/<int:task_id>/reschedule', methods=['POST'])
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
