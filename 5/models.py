from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import sqlalchemy.event as sa_event

db = SQLAlchemy()
bcrypt = Bcrypt()


# ── Association table ────────────────────────────────────────────────────────

task_tags = db.Table(
    'task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('tag_id',  db.Integer, db.ForeignKey('tag.id'),  primary_key=True),
)


# ── User ─────────────────────────────────────────────────────────────────────

class User(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks   = db.relationship('Task',        backref='user', lazy=True, cascade='all, delete-orphan')
    history = db.relationship('TaskHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, plaintext):
        self.password = bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def check_password(self, plaintext):
        return bcrypt.check_password_hash(self.password, plaintext)


# ── Tag ──────────────────────────────────────────────────────────────────────

class Tag(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name    = db.Column(db.String(50), nullable=False)
    color   = db.Column(db.String(7), default='#1565C0')   # hex colour

    __table_args__ = (db.UniqueConstraint('user_id', 'name'),)


# ── Task ─────────────────────────────────────────────────────────────────────

class Task(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title          = db.Column(db.String(300), nullable=False)
    description    = db.Column(db.Text, default='')
    due_date       = db.Column(db.Date,    nullable=True)
    due_time       = db.Column(db.String(10), nullable=True)
    priority_label = db.Column(db.String(20), default='Medium')
    priority_score = db.Column(db.Float,   default=0.5)
    importance     = db.Column(db.Integer, default=2)
    effort_minutes = db.Column(db.Integer, default=30)
    completed      = db.Column(db.Boolean, default=False)
    completed_at   = db.Column(db.DateTime, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    is_demo        = db.Column(db.Boolean, default=False)

    tags = db.relationship('Tag', secondary=task_tags, backref='tasks', lazy=True)


# ── TaskHistory ───────────────────────────────────────────────────────────────

class TaskHistory(db.Model):
    """
    Audit log for every create / update / complete / reschedule event.
    Populated automatically by SQLAlchemy event listeners below.
    Also used as training data for the reschedule ML model:
      - rows with event_type='reschedule' form the training set
      - completed_by_suggested (bool) is the binary target variable
    """
    id                    = db.Column(db.Integer, primary_key=True)
    user_id               = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id               = db.Column(db.Integer, db.ForeignKey('task.id', ondelete='SET NULL'), nullable=True)
    event_type            = db.Column(db.String(20), nullable=False)   # create | update | complete | reschedule
    task_title            = db.Column(db.String(300))
    previous_due_date     = db.Column(db.Date,    nullable=True)
    new_due_date          = db.Column(db.Date,    nullable=True)
    priority_label        = db.Column(db.String(20))
    priority_score        = db.Column(db.Float,   nullable=True)
    effort_minutes        = db.Column(db.Integer, nullable=True)
    days_overdue          = db.Column(db.Integer, nullable=True)       # for reschedule events
    completed_by_suggested = db.Column(db.Boolean, nullable=True)      # ML target: was it done by new_due_date?
    timestamp             = db.Column(db.DateTime, default=datetime.utcnow)


# ── SQLAlchemy event listeners ────────────────────────────────────────────────

def _log(task, event_type, **kwargs):
    """Write a TaskHistory row without touching the session stack."""
    from datetime import date
    today = date.today()
    days_overdue = None
    if task.due_date and task.due_date < today and not task.completed:
        days_overdue = (today - task.due_date).days

    entry = TaskHistory(
        user_id        = task.user_id,
        task_id        = task.id,
        event_type     = event_type,
        task_title     = task.title,
        previous_due_date = kwargs.get('previous_due_date'),
        new_due_date   = task.due_date,
        priority_label = task.priority_label,
        priority_score = task.priority_score,
        effort_minutes = task.effort_minutes,
        days_overdue   = days_overdue,
    )
    db.session.add(entry)


@sa_event.listens_for(Task, 'after_insert')
def after_task_insert(mapper, connection, target):
    _log(target, 'create')


@sa_event.listens_for(Task, 'after_update')
def after_task_update(mapper, connection, target):
    history = db.inspect(target).attrs
    if history.completed.history.has_changes() and target.completed:
        _log(target, 'complete')
    elif history.due_date.history.has_changes():
        prev = history.due_date.history.deleted
        _log(target, 'reschedule',
             previous_due_date=prev[0] if prev else None)
    else:
        _log(target, 'update')
