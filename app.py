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
# เพิ่มการจำกัดขนาดไฟล์
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
app.config['MAX_FILE_SIZE'] = int(os.getenv('MAX_FILE_SIZE', 25 * 1024 * 1024))  # 25MB per file

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
    content = db.Column(db.Text)  # จำกัดความยาว 500 ตัวอักษร
    image_path = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับรูปภาพ
    external_link = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับลิงก์ภายนอก
    link_type = db.Column(db.String(50))  # ประเภทลิงก์
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    department = db.relationship('Department', backref=db.backref('knowledge', lazy=True))

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)  # จำกัดความยาว 300 ตัวอักษร
    image_path = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับรูปภาพ
    external_link = db.Column(db.String(500))  # เพิ่มฟิลด์สำหรับลิงก์ภายนอก
    link_type = db.Column(db.String(50))  # ประเภทลิงก์
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

@app.route('/admin/guidelines/edit/<int:guideline_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_guideline(guideline_id):
    guideline = db.session.get(Guideline, guideline_id)
    if guideline is None:
        abort(404)
    
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        description = request.form['description']
        upload_type = request.form['upload_type']
        
        guideline.department_id = department_id
        guideline.title = title
        guideline.description = description
        
        if upload_type == 'file':
            file = request.files['file']
            if file and file.filename:
                # ตรวจสอบขนาดไฟล์
                file.seek(0, 2)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > app.config['MAX_FILE_SIZE']:
                    flash(f'ไฟล์มีขนาดใหญ่เกินไป (สูงสุด {app.config["MAX_FILE_SIZE"] // (1024*1024)} MB)', 'error')
                    return redirect(url_for('admin_edit_guideline', guideline_id=guideline_id))
                
                # ลบไฟล์เก่าถ้ามี
                if guideline.file_path and os.path.exists(guideline.file_path):
                    os.remove(guideline.file_path)
                
                filename = secure_filename(file.filename)
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'guidelines', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                file_path = os.path.join(dept_folder, filename)
                file.save(file_path)
                
                guideline.file_path = file_path
                guideline.file_size = file_size
                guideline.external_link = None
                guideline.link_type = None
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                # ลบไฟล์เก่าถ้ามี
                if guideline.file_path and os.path.exists(guideline.file_path):
                    os.remove(guideline.file_path)
                
                guideline.external_link = external_link
                guideline.link_type = link_type
                guideline.file_path = None
                guideline.file_size = None
        
        db.session.commit()
        flash('แก้ไข guideline สำเร็จ', 'success')
        return redirect(url_for('admin_guidelines'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/edit_guideline.html', guideline=guideline, departments=departments)

@app.route('/admin/guidelines/delete/<int:guideline_id>', methods=['POST'])
@login_required
def admin_delete_guideline(guideline_id):
    guideline = db.session.get(Guideline, guideline_id)
    if guideline is None:
        abort(404)
    
    # ลบไฟล์ถ้ามี
    if guideline.file_path and os.path.exists(guideline.file_path):
        os.remove(guideline.file_path)
    
    db.session.delete(guideline)
    db.session.commit()
    flash('ลบ guideline สำเร็จ', 'success')
    return redirect(url_for('admin_guidelines'))

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
                # ตรวจสอบขนาดไฟล์
                file.seek(0, 2)  # ไปที่ท้ายไฟล์
                file_size = file.tell()
                file.seek(0)  # กลับไปที่ต้นไฟล์
                
                if file_size > app.config['MAX_FILE_SIZE']:
                    flash(f'ไฟล์มีขนาดใหญ่เกินไป (สูงสุด {app.config["MAX_FILE_SIZE"] // (1024*1024)} MB)', 'error')
                    return redirect(url_for('admin_upload_guideline'))
                
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
                    file_size=file_size,
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

@app.route('/storage/<path:filename>')
def serve_storage(filename):
    """Serve files from storage folder"""
    # ใช้ path โดยตรงจาก storage folder
    storage_path = os.path.join('storage', filename)
    if os.path.exists(storage_path):
        return send_file(storage_path)
    else:
        abort(404)

@app.route('/admin/activities')
@login_required
def admin_activities():
    activities = db.session.query(Activity).join(Department).all()
    return render_template('admin/activities.html', activities=activities)

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = db.session.query(Contact).join(Department).all()
    departments = db.session.query(Department).all()
    return render_template('admin/contacts.html', contacts=contacts, departments=departments)

@app.route('/admin/contacts/add', methods=['GET', 'POST'])
@login_required
def admin_add_contact():
    if request.method == 'POST':
        department_id = request.form['department_id']
        line_id = request.form['line_id']
        email = request.form['email']
        phone = request.form['phone']
        other_contact = request.form['other_contact']
        
        # ตรวจสอบว่ามีข้อมูลอย่างน้อย 1 อย่าง
        if not any([line_id, email, phone, other_contact]):
            flash('กรุณาใส่ข้อมูลการติดต่ออย่างน้อย 1 อย่าง', 'error')
            return redirect(url_for('admin_add_contact'))
        
        contact = Contact(
            department_id=department_id,
            line_id=line_id if line_id else None,
            email=email if email else None,
            phone=phone if phone else None,
            other_contact=other_contact if other_contact else None
        )
        
        db.session.add(contact)
        db.session.commit()
        flash('เพิ่มข้อมูลการติดต่อสำเร็จ', 'success')
        return redirect(url_for('admin_contacts'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/add_contact.html', departments=departments)

@app.route('/admin/contacts/edit/<int:contact_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        abort(404)
    
    if request.method == 'POST':
        department_id = request.form['department_id']
        line_id = request.form['line_id']
        email = request.form['email']
        phone = request.form['phone']
        other_contact = request.form['other_contact']
        
        # ตรวจสอบว่ามีข้อมูลอย่างน้อย 1 อย่าง
        if not any([line_id, email, phone, other_contact]):
            flash('กรุณาใส่ข้อมูลการติดต่ออย่างน้อย 1 อย่าง', 'error')
            return redirect(url_for('admin_edit_contact', contact_id=contact_id))
        
        contact.department_id = department_id
        contact.line_id = line_id if line_id else None
        contact.email = email if email else None
        contact.phone = phone if phone else None
        contact.other_contact = other_contact if other_contact else None
        
        db.session.commit()
        flash('แก้ไขข้อมูลการติดต่อสำเร็จ', 'success')
        return redirect(url_for('admin_contacts'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/edit_contact.html', contact=contact, departments=departments)

@app.route('/admin/contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
def admin_delete_contact(contact_id):
    contact = db.session.get(Contact, contact_id)
    if contact is None:
        abort(404)
    
    db.session.delete(contact)
    db.session.commit()
    flash('ลบข้อมูลการติดต่อสำเร็จ', 'success')
    return redirect(url_for('admin_contacts'))

@app.route('/admin/departments/edit/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def edit_department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    
    if request.method == 'POST':
        dept.name = request.form['name']
        dept.code = request.form['code']
        dept.description = request.form['description']
        dept.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        flash('แก้ไขข้อมูลหน่วยงานสำเร็จ', 'success')
        return redirect(url_for('admin_departments'))
    
    return render_template('admin/edit_department.html', department=dept)

@app.route('/admin/departments/delete/<int:dept_id>', methods=['POST'])
@login_required
def delete_department(dept_id):
    dept = db.session.get(Department, dept_id)
    if dept is None:
        abort(404)
    
    # ลบข้อมูลที่เกี่ยวข้องทั้งหมด
    db.session.query(Guideline).filter_by(department_id=dept_id).delete()
    db.session.query(Knowledge).filter_by(department_id=dept_id).delete()
    db.session.query(Activity).filter_by(department_id=dept_id).delete()
    db.session.query(Contact).filter_by(department_id=dept_id).delete()
    
    # ลบหน่วยงาน
    db.session.delete(dept)
    db.session.commit()
    
    flash('ลบหน่วยงานและข้อมูลที่เกี่ยวข้องสำเร็จ', 'success')
    return redirect(url_for('admin_departments'))

# ==================== KNOWLEDGE MANAGEMENT ====================
@app.route('/admin/knowledge/add', methods=['GET', 'POST'])
@login_required
def admin_add_knowledge():
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        content = request.form['content']
        upload_type = request.form['upload_type']
        
        # จำกัดความยาวเนื้อหา (500 ตัวอักษร)
        if len(content) > 500:
            flash('เนื้อหามีความยาวเกิน 500 ตัวอักษร', 'error')
            return redirect(url_for('admin_add_knowledge'))
        
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'knowledge', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                
                knowledge = Knowledge(
                    department_id=department_id,
                    title=title,
                    content=content,
                    image_path=image_path,
                    external_link=None,
                    link_type=None
                )
            else:
                flash('กรุณาเลือกรูปภาพ', 'error')
                return redirect(url_for('admin_add_knowledge'))
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                knowledge = Knowledge(
                    department_id=department_id,
                    title=title,
                    content=content,
                    image_path=None,
                    external_link=external_link,
                    link_type=link_type
                )
            else:
                flash('กรุณาใส่ลิงก์', 'error')
                return redirect(url_for('admin_add_knowledge'))
        else:
            # เฉพาะเนื้อหา
            knowledge = Knowledge(
                department_id=department_id,
                title=title,
                content=content,
                image_path=None,
                external_link=None,
                link_type=None
            )
        
        db.session.add(knowledge)
        db.session.commit()
        flash('เพิ่มบทความความรู้สำเร็จ', 'success')
        return redirect(url_for('admin_knowledge'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/add_knowledge.html', departments=departments)

@app.route('/admin/knowledge/edit/<int:knowledge_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_knowledge(knowledge_id):
    knowledge = db.session.get(Knowledge, knowledge_id)
    if knowledge is None:
        abort(404)
    
    if request.method == 'POST':
        knowledge.title = request.form['title']
        content = request.form['content']
        
        # จำกัดความยาวเนื้อหา
        if len(content) > 500:
            flash('เนื้อหามีความยาวเกิน 500 ตัวอักษร', 'error')
            return redirect(url_for('admin_edit_knowledge', knowledge_id=knowledge_id))
        
        knowledge.content = content
        knowledge.updated_at = datetime.now(timezone.utc)
        
        # อัปเดตรูปภาพหรือลิงก์
        upload_type = request.form['upload_type']
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, knowledge.department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'knowledge', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                knowledge.image_path = image_path
                knowledge.external_link = None
                knowledge.link_type = None
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            if external_link:
                knowledge.external_link = external_link
                knowledge.link_type = link_type
                knowledge.image_path = None
        
        db.session.commit()
        flash('แก้ไขบทความความรู้สำเร็จ', 'success')
        return redirect(url_for('admin_knowledge'))
    
    return render_template('admin/edit_knowledge.html', knowledge=knowledge)

@app.route('/admin/knowledge/delete/<int:knowledge_id>', methods=['POST'])
@login_required
def admin_delete_knowledge(knowledge_id):
    knowledge = db.session.get(Knowledge, knowledge_id)
    if knowledge is None:
        abort(404)
    
    # ลบรูปภาพถ้ามี
    if knowledge.image_path and os.path.exists(knowledge.image_path):
        os.remove(knowledge.image_path)
    
    db.session.delete(knowledge)
    db.session.commit()
    flash('ลบบทความความรู้สำเร็จ', 'success')
    return redirect(url_for('admin_knowledge'))

# ==================== ACTIVITY MANAGEMENT ====================
@app.route('/admin/activity/add', methods=['GET', 'POST'])
@login_required
def admin_add_activity():
    if request.method == 'POST':
        department_id = request.form['department_id']
        title = request.form['title']
        description = request.form['description']
        activity_date = request.form['activity_date']
        upload_type = request.form['upload_type']
        
        # จำกัดความยาวคำอธิบาย (300 ตัวอักษร)
        if len(description) > 300:
            flash('คำอธิบายมีความยาวเกิน 300 ตัวอักษร', 'error')
            return redirect(url_for('admin_add_activity'))
        
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'activities', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                
                activity = Activity(
                    department_id=department_id,
                    title=title,
                    description=description,
                    activity_date=datetime.strptime(activity_date, '%Y-%m-%d').date(),
                    image_path=image_path,
                    external_link=None,
                    link_type=None
                )
            else:
                flash('กรุณาเลือกรูปภาพ', 'error')
                return redirect(url_for('admin_add_activity'))
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            
            if external_link:
                activity = Activity(
                    department_id=department_id,
                    title=title,
                    description=description,
                    activity_date=datetime.strptime(activity_date, '%Y-%m-%d').date(),
                    image_path=None,
                    external_link=external_link,
                    link_type=link_type
                )
            else:
                flash('กรุณาใส่ลิงก์', 'error')
                return redirect(url_for('admin_add_activity'))
        else:
            # เฉพาะข้อมูลพื้นฐาน
            activity = Activity(
                department_id=department_id,
                title=title,
                description=description,
                activity_date=datetime.strptime(activity_date, '%Y-%m-%d').date(),
                image_path=None,
                external_link=None,
                link_type=None
            )
        
        db.session.add(activity)
        db.session.commit()
        flash('เพิ่มกิจกรรมสำเร็จ', 'success')
        return redirect(url_for('admin_activities'))
    
    departments = db.session.query(Department).all()
    return render_template('admin/add_activity.html', departments=departments)

@app.route('/admin/activity/edit/<int:activity_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_activity(activity_id):
    activity = db.session.get(Activity, activity_id)
    if activity is None:
        abort(404)
    
    if request.method == 'POST':
        activity.title = request.form['title']
        description = request.form['description']
        activity_date = request.form['activity_date']
        
        # จำกัดความยาวคำอธิบาย
        if len(description) > 300:
            flash('คำอธิบายมีความยาวเกิน 300 ตัวอักษร', 'error')
            return redirect(url_for('admin_edit_activity', activity_id=activity_id))
        
        activity.description = description
        activity.activity_date = datetime.strptime(activity_date, '%Y-%m-%d').date()
        
        # อัปเดตรูปภาพหรือลิงก์
        upload_type = request.form['upload_type']
        if upload_type == 'image':
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                dept = db.session.get(Department, activity.department_id)
                dept_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'activities', dept.code.lower())
                os.makedirs(dept_folder, exist_ok=True)
                
                image_path = os.path.join(dept_folder, filename)
                image.save(image_path)
                activity.image_path = image_path
                activity.external_link = None
                activity.link_type = None
        elif upload_type == 'link':
            external_link = request.form['external_link']
            link_type = request.form['link_type']
            if external_link:
                activity.external_link = external_link
                activity.link_type = link_type
                activity.image_path = None
        
        db.session.commit()
        flash('แก้ไขกิจกรรมสำเร็จ', 'success')
        return redirect(url_for('admin_activities'))
    
    return render_template('admin/edit_activity.html', activity=activity)

@app.route('/admin/activity/delete/<int:activity_id>', methods=['POST'])
@login_required
def admin_delete_activity(activity_id):
    activity = db.session.get(Activity, activity_id)
    if activity is None:
        abort(404)
    
    # ลบรูปภาพถ้ามี
    if activity.image_path and os.path.exists(activity.image_path):
        os.remove(activity.image_path)
    
    db.session.delete(activity)
    db.session.commit()
    flash('ลบกิจกรรมสำเร็จ', 'success')
    return redirect(url_for('admin_activities'))

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
                Department(name='หน่วยความดันโลหิตสูง', code='HTN', description='หน่วยดูแลผู้ป่วยโรคความดันโลหิตสูง'),
                Department(name='หน่วยภาวะติดเชื้อในกระแสเลือด', code='SEPSIS', description='หน่วยดูแลผู้ป่วยภาวะติดเชื้อในกระแสเลือด'),
                Department(name='หน่วยโรคข้อและรูมาติสซั่ม', code='RHEUMATO', description='หน่วยดูแลผู้ป่วยโรคข้อและรูมาติสซั่ม'),
                Department(name='หน่วยโรคอ้วน', code='OBESITY', description='หน่วยดูแลผู้ป่วยโรคอ้วน')
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
