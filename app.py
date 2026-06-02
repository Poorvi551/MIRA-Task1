from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'health-app-secret-key-2024'

db = SQLAlchemy(app)

# ── Model ─────────────────────────────────────────────────────────────────────

class Patient(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    full_name   = db.Column(db.String(150), nullable=False)
    dob         = db.Column(db.Date, nullable=False)
    email       = db.Column(db.String(200), nullable=False, unique=True)
    glucose     = db.Column(db.Float, nullable=False)
    haemoglobin = db.Column(db.Float, nullable=False)
    cholesterol = db.Column(db.Float, nullable=False)
    remarks     = db.Column(db.Text, default='')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':          self.id,
            'full_name':   self.full_name,
            'dob':         self.dob.strftime('%Y-%m-%d'),
            'email':       self.email,
            'glucose':     self.glucose,
            'haemoglobin': self.haemoglobin,
            'cholesterol': self.cholesterol,
            'remarks':     self.remarks,
            'created_at':  self.created_at.strftime('%d %b %Y'),
        }

# ── Validation helpers ────────────────────────────────────────────────────────

def validate_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)

def validate_patient_data(data, is_update=False):
    errors = []

    if not data.get('full_name', '').strip():
        errors.append('Full name is required.')

    dob_str = data.get('dob', '')
    if not dob_str:
        errors.append('Date of birth is required.')
    else:
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            if dob >= date.today():
                errors.append('Date of birth cannot be today or a future date.')
        except ValueError:
            errors.append('Invalid date format. Use YYYY-MM-DD.')

    email = data.get('email', '').strip()
    if not email:
        errors.append('Email address is required.')
    elif not validate_email(email):
        errors.append('Invalid email address format.')

    for field in ['glucose', 'haemoglobin', 'cholesterol']:
        val = data.get(field, '')
        if val == '' or val is None:
            errors.append(f'{field.capitalize()} value is required.')
        else:
            try:
                fval = float(val)
                if fval < 0:
                    errors.append(f'{field.capitalize()} must be a positive number.')
            except (ValueError, TypeError):
                errors.append(f'{field.capitalize()} must be a numeric value.')

    return errors

# ── AI Remarks via Anthropic ──────────────────────────────────────────────────
genai.configure(api_key="your-anthropic-api-key")
def generate_ai_remarks(full_name, glucose, haemoglobin, cholesterol):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('index.html', patients=patients)

@app.route('/api/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return jsonify([p.to_dict() for p in patients])

@app.route('/api/patients/<int:pid>', methods=['GET'])
def get_patient(pid):
    p = Patient.query.get_or_404(pid)
    return jsonify(p.to_dict())

@app.route('/api/patients', methods=['POST'])
def create_patient():
    data = request.get_json()
    errors = validate_patient_data(data)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Check duplicate email
    if Patient.query.filter_by(email=data['email'].strip()).first():
        return jsonify({'success': False, 'errors': ['Email address already exists.']}), 400

    remarks = generate_ai_remarks(
        data['full_name'],
        float(data['glucose']),
        float(data['haemoglobin']),
        float(data['cholesterol'])
    )

    patient = Patient(
        full_name   = data['full_name'].strip(),
        dob         = datetime.strptime(data['dob'], '%Y-%m-%d').date(),
        email       = data['email'].strip(),
        glucose     = float(data['glucose']),
        haemoglobin = float(data['haemoglobin']),
        cholesterol = float(data['cholesterol']),
        remarks     = remarks
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify({'success': True, 'patient': patient.to_dict()}), 201

@app.route('/api/patients/<int:pid>', methods=['PUT'])
def update_patient(pid):
    p = Patient.query.get_or_404(pid)
    data = request.get_json()
    errors = validate_patient_data(data, is_update=True)
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400

    # Check duplicate email (excluding self)
    existing = Patient.query.filter_by(email=data['email'].strip()).first()
    if existing and existing.id != pid:
        return jsonify({'success': False, 'errors': ['Email address already used by another patient.']}), 400

    p.full_name   = data['full_name'].strip()
    p.dob         = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    p.email       = data['email'].strip()
    p.glucose     = float(data['glucose'])
    p.haemoglobin = float(data['haemoglobin'])
    p.cholesterol = float(data['cholesterol'])
    p.updated_at  = datetime.utcnow()

    # Re-generate AI remarks if blood values changed
    p.remarks = generate_ai_remarks(p.full_name, p.glucose, p.haemoglobin, p.cholesterol)

    db.session.commit()
    return jsonify({'success': True, 'patient': p.to_dict()})

@app.route('/api/patients/<int:pid>', methods=['DELETE'])
def delete_patient(pid):
    p = Patient.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Patient record deleted.'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
