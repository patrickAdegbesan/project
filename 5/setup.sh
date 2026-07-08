#!/bin/bash
# TaskMind setup script

echo "Installing Python dependencies..."
pip install flask flask-sqlalchemy flask-bcrypt python-dateutil spacy scikit-learn numpy

echo "Downloading spaCy language model..."
python -m spacy download en_core_web_sm

echo "Done! Run the app with: python app.py"
echo "Then open: http://localhost:5000"
echo ""
echo "Demo account: username=demo  password=demo123"
echo "(will be auto-created on first register)"
