"""
ComplaintDesk — Caleb University
Flask REST API backend
"""

import os, sqlite3, secrets, string
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, session, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'complaintdesk.db')
SCHEMA   = os.path.join(BASE_DIR, 'schema.sql')

app = Flask(__name__, static_folder='..', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-caleb-complaintdesk-2024')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE']   = False   # True in production with HTTPS

CORS(app, supports_credentials=True, origins=['http://127.0.0.1:5000',
                                               'http://localhost:5000'])

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop('db', None)
    if db:
        db.close()

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rv  = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def mutate(sql, args=()):
    db  = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_list(rows):
    return [dict(r) for r in rows]

def init_db():
    if not os.path.exists(DB_PATH):
        db = sqlite3.connect(DB_PATH)
        with open(SCHEMA) as f:
            db.executescript(f.read())
        # Fix seeded passwords — werkzeug hash the real ones
        _pw_admin   = generate_password_hash('Admin@1234')
        _pw_staff   = generate_password_hash('Staff@1234')
        _pw_student = generate_password_hash('Student@1234')
        db.execute("UPDATE users SET password=? WHERE email='administrator@caleb.edu.ng'",   (_pw_admin,))
        db.execute("UPDATE users SET password=? WHERE email='c.okafor@caleb.edu.ng'",        (_pw_staff,))
        db.execute("UPDATE users SET password=? WHERE email='a.nwosu@student.caleb.edu.ng'", (_pw_student,))
        db.commit()
        db.close()
        print('✓ Database initialised')

def gen_ref():
    letters = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(4))
    digits  = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f'CD-{letters}-{digits}'

# ---------------------------------------------------------------------------
# Auth decorator
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            if session.get('role') not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# ---------------------------------------------------------------------------
# Serve static HTML
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return app.send_static_file(filename)

# ===========================================================================
# AUTH
# ===========================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    d = request.get_json(silent=True) or {}
    name  = (d.get('name')  or '').strip()
    email = (d.get('email') or '').strip().lower()
    pw    = d.get('password', '')
    role  = d.get('role', 'student')
    dept  = (d.get('department') or '').strip()

    if not all([name, email, pw]):
        return jsonify({'error': 'Name, email and password are required'}), 400
    if role not in ('student', 'staff'):
        role = 'student'
    if len(pw) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    existing = query('SELECT id FROM users WHERE email=?', (email,), one=True)
    if existing:
        return jsonify({'error': 'An account with this email already exists'}), 409

    matric = d.get('matric_no', '').strip() or None
    staff_id = d.get('staff_id', '').strip() or None
    pw_hash = generate_password_hash(pw)
    uid = mutate(
        'INSERT INTO users (name,email,password,role,department,matric_no,staff_id) VALUES (?,?,?,?,?,?,?)',
        (name, email, pw_hash, role, dept, matric, staff_id)
    )
    return jsonify({'message': 'Account created successfully', 'user_id': uid}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    d     = request.get_json(silent=True) or {}
    email = (d.get('email') or '').strip().lower()
    pw    = d.get('password', '')
    role  = d.get('role', '')

    user = query('SELECT * FROM users WHERE email=?', (email,), one=True)
    if not user or not check_password_hash(user['password'], pw):
        return jsonify({'error': 'Invalid email or password'}), 401
    if not user['is_active']:
        return jsonify({'error': 'Your account has been suspended'}), 403
    if role and user['role'] != role:
        return jsonify({'error': f'This account is registered as {user["role"]}, not {role}'}), 403

    session.clear()
    session['user_id'] = user['id']
    session['role']    = user['role']
    session['name']    = user['name']

    redirect_map = {'student': '03-user-dashboard.html',
                    'staff':   'staff-dashboard.html',
                    'admin':   '07-admin-dashboard.html'}

    return jsonify({
        'message':  'Login successful',
        'user': {
            'id':         user['id'],
            'name':       user['name'],
            'email':      user['email'],
            'role':       user['role'],
            'department': user['department'],
            'matric_no':  user['matric_no'],
            'staff_id':   user['staff_id'],
        },
        'redirect': redirect_map.get(user['role'], '03-user-dashboard.html')
    })


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})


@app.route('/api/auth/me')
@login_required
def me():
    user = query('SELECT id,name,email,role,department,matric_no,staff_id,phone,created_at FROM users WHERE id=?',
                 (session['user_id'],), one=True)
    return jsonify(row_to_dict(user))


@app.route('/api/auth/change-password', methods=['POST'])
@login_required
def change_password():
    d       = request.get_json(silent=True) or {}
    current = d.get('current_password', '')
    new_pw  = d.get('new_password', '')
    if len(new_pw) < 8:
        return jsonify({'error': 'New password must be at least 8 characters'}), 400
    user = query('SELECT password FROM users WHERE id=?', (session['user_id'],), one=True)
    if not check_password_hash(user['password'], current):
        return jsonify({'error': 'Current password is incorrect'}), 400
    mutate('UPDATE users SET password=? WHERE id=?',
           (generate_password_hash(new_pw), session['user_id']))
    return jsonify({'message': 'Password updated successfully'})


@app.route('/api/auth/update-profile', methods=['POST'])
@login_required
def update_profile():
    d    = request.get_json(silent=True) or {}
    name = (d.get('name') or '').strip()
    phone = (d.get('phone') or '').strip()
    dept  = (d.get('department') or '').strip()
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    mutate('UPDATE users SET name=?,phone=?,department=? WHERE id=?',
           (name, phone, dept, session['user_id']))
    session['name'] = name
    return jsonify({'message': 'Profile updated'})


# ===========================================================================
# CATEGORIES (public)
# ===========================================================================

@app.route('/api/categories')
def get_categories():
    cats = query('SELECT id,name,department FROM categories WHERE is_active=1 ORDER BY name')
    return jsonify(rows_to_list(cats))


# ===========================================================================
# COMPLAINTS — Student / Staff views
# ===========================================================================

@app.route('/api/complaints', methods=['GET'])
@login_required
def list_my_complaints():
    uid    = session['user_id']
    status = request.args.get('status')
    page   = max(1, int(request.args.get('page', 1)))
    limit  = 20
    offset = (page - 1) * limit

    where  = 'WHERE c.user_id=?'
    params = [uid]
    if status:
        where += ' AND c.status=?'
        params.append(status)

    total = query(f'SELECT COUNT(*) n FROM complaints c {where}', params, one=True)['n']
    rows  = query(f'''
        SELECT c.id, c.ref_no, c.title, c.priority, c.status, c.created_at, c.updated_at,
               cat.name category_name,
               (SELECT COUNT(*) FROM responses r WHERE r.complaint_id=c.id AND r.is_internal=0) response_count
        FROM complaints c
        LEFT JOIN categories cat ON cat.id=c.category_id
        {where}
        ORDER BY c.created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [limit, offset])

    return jsonify({'complaints': rows_to_list(rows), 'total': total, 'page': page})


@app.route('/api/complaints', methods=['POST'])
@login_required
def submit_complaint():
    d    = request.get_json(silent=True) or {}
    title = (d.get('title') or '').strip()
    desc  = (d.get('description') or '').strip()
    cat   = d.get('category_id')
    pri   = d.get('priority', 'medium')
    anon  = 1 if d.get('anonymous') else 0

    if not title or not desc:
        return jsonify({'error': 'Title and description are required'}), 400

    ref = gen_ref()
    while query('SELECT id FROM complaints WHERE ref_no=?', (ref,), one=True):
        ref = gen_ref()

    cid = mutate(
        '''INSERT INTO complaints (ref_no,title,description,category_id,priority,user_id,is_anonymous)
           VALUES (?,?,?,?,?,?,?)''',
        (ref, title, desc, cat, pri, session['user_id'], anon)
    )
    return jsonify({'message': 'Complaint submitted', 'ref_no': ref, 'id': cid}), 201


@app.route('/api/complaints/<int:cid>', methods=['GET'])
@login_required
def get_complaint(cid):
    uid  = session['user_id']
    role = session.get('role')

    if role == 'admin' or role == 'staff':
        c = query('''
            SELECT c.*, cat.name category_name,
                   u.name submitter_name, u.email submitter_email,
                   u.department submitter_dept, u.matric_no submitter_matric,
                   a.name assigned_name
            FROM complaints c
            LEFT JOIN categories cat ON cat.id=c.category_id
            LEFT JOIN users u ON u.id=c.user_id
            LEFT JOIN users a ON a.id=c.assigned_to
            WHERE c.id=?
        ''', (cid,), one=True)
    else:
        c = query('''
            SELECT c.*, cat.name category_name, a.name assigned_name
            FROM complaints c
            LEFT JOIN categories cat ON cat.id=c.category_id
            LEFT JOIN users a ON a.id=c.assigned_to
            WHERE c.id=? AND c.user_id=?
        ''', (cid, uid), one=True)

    if not c:
        return jsonify({'error': 'Complaint not found'}), 404

    # Increment view count on announcements — skip for complaints, just return responses
    internal_filter = '' if role in ('admin','staff') else 'AND r.is_internal=0'
    responses = query(f'''
        SELECT r.id, r.message, r.is_internal, r.created_at, u.name author_name, u.role author_role
        FROM responses r
        JOIN users u ON u.id=r.user_id
        WHERE r.complaint_id=? {internal_filter}
        ORDER BY r.created_at ASC
    ''', (cid,))

    data = row_to_dict(c)
    data['responses'] = rows_to_list(responses)
    return jsonify(data)


@app.route('/api/complaints/<int:cid>/respond', methods=['POST'])
@login_required
def add_response(cid):
    d        = request.get_json(silent=True) or {}
    message  = (d.get('message') or '').strip()
    internal = 1 if d.get('internal') else 0

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    role = session.get('role')
    uid  = session['user_id']

    c = query('SELECT id,user_id FROM complaints WHERE id=?', (cid,), one=True)
    if not c:
        return jsonify({'error': 'Complaint not found'}), 404

    if role == 'student' and c['user_id'] != uid:
        return jsonify({'error': 'Forbidden'}), 403

    mutate('INSERT INTO responses (complaint_id,user_id,message,is_internal) VALUES (?,?,?,?)',
           (cid, uid, message, internal))
    mutate("UPDATE complaints SET updated_at=datetime('now') WHERE id=?", (cid,))

    return jsonify({'message': 'Response added'})


# ===========================================================================
# ADMIN — Complaints
# ===========================================================================

@app.route('/api/admin/complaints', methods=['GET'])
@role_required('admin', 'staff')
def admin_list_complaints():
    status   = request.args.get('status')
    priority = request.args.get('priority')
    search   = request.args.get('q', '').strip()
    page     = max(1, int(request.args.get('page', 1)))
    limit    = int(request.args.get('limit', 20))
    offset   = (page - 1) * limit

    conditions = []
    params     = []

    if status:
        conditions.append('c.status=?')
        params.append(status)
    if priority:
        conditions.append('c.priority=?')
        params.append(priority)
    if search:
        conditions.append('(c.title LIKE ? OR c.ref_no LIKE ? OR u.name LIKE ?)')
        s = f'%{search}%'
        params.extend([s, s, s])

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''

    total = query(f'''
        SELECT COUNT(*) n FROM complaints c
        LEFT JOIN users u ON u.id=c.user_id
        {where}
    ''', params, one=True)['n']

    rows = query(f'''
        SELECT c.id, c.ref_no, c.title, c.priority, c.status, c.created_at, c.updated_at,
               cat.name category_name,
               CASE WHEN c.is_anonymous=1 THEN 'Anonymous' ELSE u.name END submitter_name,
               u.department submitter_dept,
               a.name assigned_name,
               (SELECT COUNT(*) FROM responses r WHERE r.complaint_id=c.id) response_count
        FROM complaints c
        LEFT JOIN categories cat ON cat.id=c.category_id
        LEFT JOIN users u ON u.id=c.user_id
        LEFT JOIN users a ON a.id=c.assigned_to
        {where}
        ORDER BY
          CASE c.priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 ELSE 4 END,
          c.created_at DESC
        LIMIT ? OFFSET ?
    ''', params + [limit, offset])

    return jsonify({'complaints': rows_to_list(rows), 'total': total, 'page': page})


@app.route('/api/admin/complaints/<int:cid>', methods=['PUT'])
@role_required('admin', 'staff')
def admin_update_complaint(cid):
    d       = request.get_json(silent=True) or {}
    status  = d.get('status')
    assign  = d.get('assigned_to')
    pri     = d.get('priority')

    c = query('SELECT id FROM complaints WHERE id=?', (cid,), one=True)
    if not c:
        return jsonify({'error': 'Not found'}), 404

    if status:
        resolved_clause = ", resolved_at=datetime('now')" if status == 'resolved' else ''
        mutate(f"UPDATE complaints SET status=?, updated_at=datetime('now'){resolved_clause} WHERE id=?",
               (status, cid))
    if assign is not None:
        mutate("UPDATE complaints SET assigned_to=?, updated_at=datetime('now') WHERE id=?",
               (assign or None, cid))
    if pri:
        mutate("UPDATE complaints SET priority=?, updated_at=datetime('now') WHERE id=?",
               (pri, cid))

    return jsonify({'message': 'Complaint updated'})


# ===========================================================================
# ADMIN — Stats / Dashboard
# ===========================================================================

@app.route('/api/admin/stats')
@role_required('admin', 'staff')
def admin_stats():
    total      = query('SELECT COUNT(*) n FROM complaints', one=True)['n']
    open_c     = query("SELECT COUNT(*) n FROM complaints WHERE status='open'", one=True)['n']
    in_prog    = query("SELECT COUNT(*) n FROM complaints WHERE status='in_progress'", one=True)['n']
    resolved   = query("SELECT COUNT(*) n FROM complaints WHERE status='resolved'", one=True)['n']
    urgent     = query("SELECT COUNT(*) n FROM complaints WHERE priority='urgent' AND status NOT IN ('resolved','closed')", one=True)['n']
    total_users= query('SELECT COUNT(*) n FROM users', one=True)['n']

    by_cat = query('''
        SELECT cat.name label, COUNT(*) value
        FROM complaints c
        JOIN categories cat ON cat.id=c.category_id
        GROUP BY cat.id ORDER BY value DESC LIMIT 8
    ''')

    by_day = query('''
        SELECT strftime('%Y-%m-%d', created_at) day, COUNT(*) count
        FROM complaints
        WHERE created_at >= date('now','-30 days')
        GROUP BY day ORDER BY day
    ''')

    recent = query('''
        SELECT c.id, c.ref_no, c.title, c.status, c.priority, c.created_at,
               CASE WHEN c.is_anonymous=1 THEN 'Anonymous' ELSE u.name END submitter_name
        FROM complaints c
        LEFT JOIN users u ON u.id=c.user_id
        ORDER BY c.created_at DESC LIMIT 5
    ''')

    return jsonify({
        'total':       total,
        'open':        open_c,
        'in_progress': in_prog,
        'resolved':    resolved,
        'urgent':      urgent,
        'total_users': total_users,
        'by_category': rows_to_list(by_cat),
        'by_day':      rows_to_list(by_day),
        'recent':      rows_to_list(recent),
    })


@app.route('/api/user/stats')
@login_required
def user_stats():
    uid   = session['user_id']
    total = query('SELECT COUNT(*) n FROM complaints WHERE user_id=?', (uid,), one=True)['n']
    open_ = query("SELECT COUNT(*) n FROM complaints WHERE user_id=? AND status='open'", (uid,), one=True)['n']
    prog  = query("SELECT COUNT(*) n FROM complaints WHERE user_id=? AND status='in_progress'", (uid,), one=True)['n']
    res   = query("SELECT COUNT(*) n FROM complaints WHERE user_id=? AND status='resolved'", (uid,), one=True)['n']
    return jsonify({'total': total, 'open': open_, 'in_progress': prog, 'resolved': res})


# ===========================================================================
# ADMIN — Users
# ===========================================================================

@app.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def admin_list_users():
    role   = request.args.get('role')
    search = request.args.get('q', '').strip()
    page   = max(1, int(request.args.get('page', 1)))
    limit  = 20
    offset = (page - 1) * limit

    conditions, params = [], []
    if role:
        conditions.append('role=?'); params.append(role)
    if search:
        conditions.append('(name LIKE ? OR email LIKE ? OR matric_no LIKE ? OR staff_id LIKE ?)')
        s = f'%{search}%'
        params.extend([s, s, s, s])

    where = ('WHERE ' + ' AND '.join(conditions)) if conditions else ''
    total = query(f'SELECT COUNT(*) n FROM users {where}', params, one=True)['n']
    rows  = query(f'''
        SELECT id, name, email, role, department, matric_no, staff_id, is_active, created_at,
               (SELECT COUNT(*) FROM complaints WHERE user_id=users.id) complaint_count
        FROM users {where}
        ORDER BY created_at DESC LIMIT ? OFFSET ?
    ''', params + [limit, offset])

    return jsonify({'users': rows_to_list(rows), 'total': total, 'page': page})


@app.route('/api/admin/users/<int:uid>', methods=['GET'])
@role_required('admin')
def admin_get_user(uid):
    user = query('''
        SELECT id,name,email,role,department,matric_no,staff_id,phone,is_active,created_at
        FROM users WHERE id=?
    ''', (uid,), one=True)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(row_to_dict(user))


@app.route('/api/admin/users/<int:uid>', methods=['PUT'])
@role_required('admin')
def admin_update_user(uid):
    d = request.get_json(silent=True) or {}
    if 'is_active' in d:
        mutate('UPDATE users SET is_active=? WHERE id=?', (1 if d['is_active'] else 0, uid))
    if 'role' in d and d['role'] in ('student','staff','admin'):
        mutate('UPDATE users SET role=? WHERE id=?', (d['role'], uid))
    return jsonify({'message': 'User updated'})


@app.route('/api/admin/users', methods=['POST'])
@role_required('admin')
def admin_create_user():
    d    = request.get_json(silent=True) or {}
    name = (d.get('name') or '').strip()
    email= (d.get('email') or '').strip().lower()
    role = d.get('role', 'student')
    dept = (d.get('department') or '').strip()
    pw   = d.get('password', 'ChangeMe@123')

    if not name or not email:
        return jsonify({'error': 'Name and email required'}), 400
    if query('SELECT id FROM users WHERE email=?', (email,), one=True):
        return jsonify({'error': 'Email already in use'}), 409

    uid = mutate(
        'INSERT INTO users (name,email,password,role,department,matric_no,staff_id) VALUES (?,?,?,?,?,?,?)',
        (name, email, generate_password_hash(pw), role, dept,
         d.get('matric_no'), d.get('staff_id'))
    )
    return jsonify({'message': 'User created', 'id': uid}), 201


# ===========================================================================
# ANNOUNCEMENTS
# ===========================================================================

@app.route('/api/announcements')
@login_required
def list_announcements():
    role = session.get('role')
    target_filter = "AND (target='all' OR target=?)" if role != 'admin' else ''
    params = [] if role == 'admin' else [role + 's']   # 'students' or 'staff'

    rows = query(f'''
        SELECT a.id, a.title, a.message, a.target, a.priority, a.is_pinned,
               a.view_count, a.created_at, a.expires_at, u.name author_name
        FROM announcements a
        JOIN users u ON u.id=a.author_id
        WHERE a.is_draft=0
        {target_filter}
        AND (a.expires_at IS NULL OR a.expires_at > datetime('now'))
        ORDER BY a.is_pinned DESC, a.created_at DESC
        LIMIT 20
    ''', params)

    return jsonify(rows_to_list(rows))


@app.route('/api/admin/announcements', methods=['GET'])
@role_required('admin')
def admin_list_announcements():
    rows = query('''
        SELECT a.*, u.name author_name
        FROM announcements a
        JOIN users u ON u.id=a.author_id
        ORDER BY a.is_pinned DESC, a.created_at DESC
    ''')
    return jsonify(rows_to_list(rows))


@app.route('/api/admin/announcements', methods=['POST'])
@role_required('admin')
def admin_create_announcement():
    d       = request.get_json(silent=True) or {}
    title   = (d.get('title')   or '').strip()
    message = (d.get('message') or '').strip()
    if not title or not message:
        return jsonify({'error': 'Title and message are required'}), 400

    aid = mutate('''
        INSERT INTO announcements (title,message,target,priority,is_pinned,is_draft,author_id,expires_at)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (
        title,
        message,
        d.get('target', 'all'),
        d.get('priority', 'normal'),
        1 if d.get('is_pinned') else 0,
        1 if d.get('is_draft')  else 0,
        session['user_id'],
        d.get('expires_at') or None
    ))
    return jsonify({'message': 'Announcement created', 'id': aid}), 201


@app.route('/api/admin/announcements/<int:aid>', methods=['PUT'])
@role_required('admin')
def admin_update_announcement(aid):
    d = request.get_json(silent=True) or {}
    fields, vals = [], []
    for col in ('title','message','target','priority','is_pinned','is_draft','expires_at'):
        if col in d:
            fields.append(f'{col}=?')
            vals.append(1 if (col in ('is_pinned','is_draft') and d[col]) else d[col])
    if not fields:
        return jsonify({'error': 'Nothing to update'}), 400
    vals.append(aid)
    mutate(f'UPDATE announcements SET {", ".join(fields)} WHERE id=?', vals)
    return jsonify({'message': 'Announcement updated'})


@app.route('/api/admin/announcements/<int:aid>', methods=['DELETE'])
@role_required('admin')
def admin_delete_announcement(aid):
    mutate('DELETE FROM announcements WHERE id=?', (aid,))
    return jsonify({'message': 'Deleted'})


@app.route('/api/admin/announcements/<int:aid>/view', methods=['POST'])
def inc_announcement_view(aid):
    mutate('UPDATE announcements SET view_count=view_count+1 WHERE id=?', (aid,))
    return jsonify({'ok': True})


# ===========================================================================
# REPORTS
# ===========================================================================

@app.route('/api/admin/reports')
@role_required('admin', 'staff')
def admin_reports():
    period = request.args.get('period', '30')  # days

    by_status = query('''
        SELECT status label, COUNT(*) value FROM complaints GROUP BY status
    ''')
    by_priority = query('''
        SELECT priority label, COUNT(*) value FROM complaints GROUP BY priority
    ''')
    by_category = query('''
        SELECT cat.name label, COUNT(*) value
        FROM complaints c
        JOIN categories cat ON cat.id=c.category_id
        GROUP BY cat.id ORDER BY value DESC
    ''')
    by_dept = query('''
        SELECT COALESCE(u.department,'Unknown') label, COUNT(*) value
        FROM complaints c
        JOIN users u ON u.id=c.user_id
        GROUP BY u.department ORDER BY value DESC LIMIT 10
    ''')
    avg_resolution = query('''
        SELECT ROUND(AVG(
            (julianday(resolved_at) - julianday(created_at)) * 24
        ), 1) hours
        FROM complaints WHERE resolved_at IS NOT NULL
    ''', one=True)['hours']

    monthly = query(f'''
        SELECT strftime('%Y-%m', created_at) month, COUNT(*) submitted,
               SUM(CASE WHEN status='resolved' THEN 1 ELSE 0 END) resolved
        FROM complaints
        WHERE created_at >= date('now', '-{period} days')
        GROUP BY month ORDER BY month
    ''')

    return jsonify({
        'by_status':        rows_to_list(by_status),
        'by_priority':      rows_to_list(by_priority),
        'by_category':      rows_to_list(by_category),
        'by_department':    rows_to_list(by_dept),
        'avg_resolution_hours': avg_resolution,
        'monthly':          rows_to_list(monthly),
    })


# ===========================================================================
# ADMIN — Settings
# ===========================================================================

@app.route('/api/admin/settings', methods=['GET'])
@role_required('admin')
def get_settings():
    # In a real system these would come from a settings table
    return jsonify({
        'institution_name': 'Caleb University',
        'portal_name':      'ComplaintDesk',
        'support_email':    'support@caleb.edu.ng',
        'max_file_size_mb': 10,
        'allow_anonymous':  True,
        'auto_assign':      False,
        'resolution_days':  14,
        'notify_email':     True,
        'notify_sms':       False,
    })


@app.route('/api/admin/settings', methods=['POST'])
@role_required('admin')
def save_settings():
    # Settings would be persisted to a key-value table in production
    return jsonify({'message': 'Settings saved successfully'})


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == '__main__':
    init_db()
    print('\n  ComplaintDesk backend running at http://127.0.0.1:5000\n')
    print('  Default accounts:')
    print('    Admin:   administrator@caleb.edu.ng  /  Admin@1234')
    print('    Staff:   c.okafor@caleb.edu.ng       /  Staff@1234')
    print('    Student: a.nwosu@student.caleb.edu.ng /  Student@1234\n')
    app.run(debug=True, port=5000)
