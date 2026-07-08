from flask import Blueprint, request, jsonify, session
from functools import wraps
from ai import parse_natural_language, calculate_priority, get_do_next, task_to_dict
from models import Task

ai_bp = Blueprint('ai', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@ai_bp.route('/api/parse', methods=['POST'])
@login_required
def api_parse():
    """NLP endpoint: parse free-form text into structured task fields."""
    text   = request.json.get('text', '')
    parsed = parse_natural_language(text)
    score, label = calculate_priority(
        parsed['importance'],
        parsed['due_date'],
        parsed['effort_minutes'],
    )
    parsed['priority_score'] = score
    parsed['priority_label'] = label
    parsed['priority_pct']   = int(score * 100)
    return jsonify(parsed)


@ai_bp.route('/api/priority', methods=['POST'])
@login_required
def api_priority():
    """Compute priority score for given attributes (used by frontend live preview)."""
    data = request.json
    score, label = calculate_priority(
        int(data.get('importance', 2)),
        data.get('due_date'),
        int(data.get('effort_minutes', 30)),
    )
    return jsonify({'priority_score': score, 'priority_label': label,
                    'priority_pct': int(score * 100)})


@ai_bp.route('/api/recommendation', methods=['GET'])
@login_required
def api_recommendation():
    """Return the Do Next recommendation with full R_score breakdown."""
    result = get_do_next(session['user_id'])
    if not result:
        return jsonify({'task': None})
    task, pct = result
    return jsonify({'task': task_to_dict(task), 'match_pct': int(pct * 100)})
