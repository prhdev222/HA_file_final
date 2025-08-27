from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime, timezone
import mimetypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///hospital.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'storage/uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB max file size

# สร้างโฟลเดอร์ storage ถ้ายังไม่มี
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'guidelines'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'temp'), exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Models
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class Guideline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500))  # เปลี่ยนเป็น nullable=True
    file_size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    description = db.Column(db.Text)
    external_link = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับ external link
    link_type = db.Column(db.String(50))  # ประเภทลิงก์ เช่น Google Drive, OneDrive, Website
    department = db.relationship('Department', backref=db.backref('guidelines', lazy=True))

class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    department = db.relationship('Department', backref=db.backref('knowledge', lazy=True))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    activity_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    department = db.relationship('Department', backref=db.backref('activities', lazy=True))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    line_id = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    other_contact = db.Column(db.Text)
    department = db.relationship('Department', backref=db.backref('contacts', lazy=True))

class AdminUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))

# Routes
@app.route('/')
def home():
    departments = db.session.query(Department).all()
    return render_template('home.html', departments=departments)

@app.route('/department/<int:dept_id>')
def department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    return render_template('department.html', department=dept)

@app.route('/download/<int:guideline_id>')
def download_guideline(guideline_id):
    guideline = db.session.get(Guideline, guideline_id)
    if guideline is None:
        abort(404)
    
    # ถ้ามี external link ให้ redirect ไปที่ลิงก์นั้น
    if guideline.external_link:
        return redirect(guideline.external_link)
    
    # ถ้ามีไฟล์ให้ดาวน์โหลด
    if guideline.file_path and os.path.exists(guideline.file_path):
        return send_file(guideline.file_path, as_attachment=True)
    
    flash('ไฟล์ไม่พบ', 'error')
    return redirect(url_for('department', dept_id=guideline.department_id))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.session.query(AdminUser).filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    stats = {
        'departments': db.session.query(Department).count(),
        'guidelines': db.session.query(Guideline).count(),
        'knowledge': db.session.query(Knowledge).count(),
        'activities': db.session.query(Activity).count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/departments')
@login_required
def admin_departments():
    departments = db.session.query(Department).all()
    return render_template('admin/departments.html', departments=departments)

@app.route('/admin/guidelines')
@login_required
def admin_guidelines():
    guidelines = db.session.query(Guideline).join(Department).all()
    return render_template('admin/guidelines.html', guidelines=guidelines)

@app.route('/admin/upload_guideline', methods=['GET', 'POST'])
@login_required
def upload_guideline():
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        description = request.form['description']
        upload_type = request.form['upload_type']  # 'file' หรือ 'link'
        
        if upload_type == 'file':
            file = request.files['file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'guidelines', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                file_path = os.path.join(dept_folder, filename)
                file.save(file_path)
                
                guideline = Guideline(
                    department_id=department_id,
                    title=title,
                    file_path=file_path,
                    file_size=os.path.getsize(file_path),
                    description=description,
                    external_link=None,
                    link_type=None
                )
                db.session.add(guideline)
                db.session.commit()
                
                flash('อัปโหลดไฟล์สำเร็จ', 'success')
                return redirect(url_for('admin_guidelines'))
            else:
                flash('กรุณาเลือกไฟล์', 'error')
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                guideline = Guideline(
                    department_id=department_id,
                    title=title,
                    file_path=None,
                    file_size=None,
                    description=description,
                    external_link=external_link,
                    link_type=link_type
                )
                db.session.add(guideline)
                db.session.commit()
                
                flash('เพิ่มลิงก์ภายนอกสำเร็จ', 'success')
                return redirect(url_for('admin_guidelines'))
            else:
                flash('กรุณาใส่ลิงก์', 'error')
    
    departments = db.session.query(Department).all()
    return render_template('admin/upload_guideline.html', departments=departments)

@app.route('/admin/knowledge')
@login_required
def admin_knowledge():
    knowledge = db.session.query(Knowledge).join(Department).all()
    return render_template('admin/knowledge.html', knowledge=knowledge)

@app.route('/admin/activities')
@login_required
def admin_activities():
    activities = db.session.query(Activity).join(Department).all()
    return render_template('admin/activities.html', activities=activities)

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = db.session.query(Contact).join(Department).all()
    return render_template('admin/contacts.html', contacts=contacts)

def init_db():
    with app.app_context():
        db.create_all()
        
        # สร้างข้อมูลเริ่มต้น
        if db.session.query(Department).count() == 0:
            departments = [
                Department(name='หน่วยเบาหวาน', code='DM', description='หน่วยดูแลผู้ป่วยเบาหวาน'),
                Department(name='หน่วยปอดอุดกั้นเรื้อรัง', code='COPD', description='หน่วยดูแลผู้ป่วยโรคปอดอุดกั้นเรื้อรัง'),
                Department(name='หน่วยเลือดออกทางเดินอาหารส่วนต้น', code='UGIB', description='หน่วยดูแลผู้ป่วยเลือดออกทางเดินอาหารส่วนต้น'),
                Department(name='หน่วยไตเรื้อรัง', code='CKD', description='หน่วยดูแลผู้ป่วยไตเรื้อรัง'),
                Department(name='หน่วยหัวใจขาดเลือด', code='STEMI_NSTEMI', description='หน่วยดูแลผู้ป่วยหัวใจขาดเลือด'),
                Department(name='หน่วยโรคหลอดเลือดสมอง', code='STROKE', description='หน่วยดูแลผู้ป่วยโรคหลอดเลือดสมอง'),
                Department(name='หน่วยวัณโรค', code='TB', description='หน่วยดูแลผู้ป่วยวัณโรค'),
                Department(name='หน่วยเคมีบำบัด', code='CHEMO', description='หน่วยดูแลผู้ป่วยที่ได้รับเคมีบำบัด'),
                Department(name='หน่วยความดันโลหิตสูง', code='HTN', description='หน่วยดูแลผู้ป่วยโรคความดันโลหิตสูง')
            ]
            
            for dept in departments:
                db.session.add(dept)
            
            # สร้างแอดมินเริ่มต้นจาก environment variables
            admin_username = os.getenv('ADMIN_USERNAME', 'admin')
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin_email = os.getenv('ADMIN_EMAIL', 'admin@hospital.local')
            
            admin = AdminUser(
                username=admin_username,
                password_hash=generate_password_hash(admin_password),
                email=admin_email
            )
            db.session.add(admin)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    
    # ใช้ environment variables สำหรับ host และ port
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
