"""
Terminal demo of the Do Next recommendation engine.
Run: python show_recommendation.py [username]
Prints the full R_score breakdown for all pending tasks.
"""
import sys
from app import app, db, User, get_do_next

username = sys.argv[1] if len(sys.argv) > 1 else 'demo'

with app.app_context():
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"User '{username}' not found.")
        sys.exit(1)
    get_do_next(user.id, verbose=True)
