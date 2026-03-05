from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
# zusätzliche Sicherheitsbibliotheken
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server.db'
# sichere Session-Cookies
app.config.update({
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Strict',
})

db = SQLAlchemy(app)

# Rate limiting konfigurieren
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200 per day","50 per hour"])


# ============ DATENBANKMODELLE ============
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class PageContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============ AUTHENTIFIZIERUNG ============
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ============ ROUTEN - ÖFFENTLICH ============
@app.route('/')
def index():
    content = PageContent.query.first()
    if not content:
        content = PageContent(title='Willkommen', content='Hallo! Dieser Server ist online.')
        db.session.add(content)
        db.session.commit()
    return render_template('index.html', content=content)

@app.route('/api/status')
def api_status():
    """API für Geräte-Status"""
    return jsonify({
        'status': 'online',
        'server_name': 'Mein Ubuntu Server',
        'timestamp': datetime.now().isoformat(),
        'message': 'Server läuft'
    })

# ============ ROUTEN - ADMIN ============
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            if request.is_json:
                return jsonify({'success': True})
            return redirect(url_for('admin_panel'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Ungültige Anmeldedaten'}), 401
            return render_template('admin_login.html', error='Ungültige Anmeldedaten')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/panel')
@login_required
def admin_panel():
    content = PageContent.query.first()
    return render_template('admin_panel.html', content=content)

@app.route('/admin/api/update-content', methods=['POST'])
@login_required
def update_content():
    data = request.get_json()
    content = PageContent.query.first()
    
    if not content:
        content = PageContent()
        db.session.add(content)
    
    content.title = data.get('title', content.title)
    content.content = data.get('content', content.content)
    content.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Inhalte aktualisiert'})

# ============ FEHLERBEHANDLUNG ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Seite nicht gefunden'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Serverfehler'}), 500

# ============ INITIALISIERUNG ============
def init_db():
    with app.app_context():
        db.create_all()
        # Admin-Benutzer erstellen (Passwort: admin123)
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                password=generate_password_hash('admin123')  # ÄNDERN SIE DIESES PASSWORT!
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin-Benutzer erstellt: admin / admin123")

if __name__ == '__main__':
    init_db()
    # Für Produktion: Gunicorn verwenden, nicht debug=True
    app.run(host='0.0.0.0', port=5000, debug=False)
