# 🏥 ระบบจัดการไฟล์แผนกอายุรกรรม โรงพยาบาลสงฆ์

ระบบจัดการไฟล์และข้อมูลสำหรับแผนกอายุรกรรม พัฒนาด้วย Flask และ SQLAlchemy เพื่อจัดการข้อมูลหน่วยงานต่างๆ ในโรงพยาบาล

## ✨ ฟีเจอร์หลัก

### �� **จัดการหน่วยงาน (12 หน่วย)**
- **DM** - หน่วยเบาหวาน
- **COPD** - หน่วยโรคปอดอุดกั้นเรื้อรัง  
- **UGIB** - หน่วยเลือดออกในทางเดินอาหารส่วนบน
- **CKD** - หน่วยโรคไตเรื้อรัง
- **STEMI/NSTEMI** - หน่วยกล้ามเนื้อหัวใจขาดเลือด
- **STROKE** - หน่วยโรคหลอดเลือดสมอง
- **TB** - หน่วยวัณโรค
- **CHEMO** - หน่วยเคมีบำบัด
- **HTN** - หน่วยความดันโลหิตสูง
- **SEPSIS** - หน่วยภาวะติดเชื้อในกระแสเลือด
- **RHEUMATO** - หน่วยโรคข้อและรูมาติสซั่ม
- **OBESITY** - หน่วยโรคอ้วน

### 📁 **จัดการไฟล์และข้อมูล**
- **Guidelines**: อัปโหลดไฟล์และลิงก์ภายนอก (รองรับ PDF, DOC, DOCX, TXT)
- **ความรู้ (Knowledge)**: จัดการข้อมูลความรู้ทางการแพทย์ พร้อมรูปภาพและลิงก์ภายนอก
- **กิจกรรม (Activities)**: จัดการกิจกรรมและงานของหน่วยงาน พร้อมรูปภาพและลิงก์ภายนอก
- **ข้อมูลติดต่อ (Contacts)**: จัดการข้อมูลการติดต่อของแต่ละหน่วย (Line ID, อีเมล, เบอร์โทร)

### 🔐 **ระบบแอดมิน**
- ระบบล็อกอินสำหรับผู้ดูแลระบบ
- แดชบอร์ดแสดงสถิติและข้อมูลสรุป
- จัดการหน่วยงาน (เพิ่ม/แก้ไข/ลบ)
- จัดการ Guidelines (อัปโหลด/แก้ไข/ลบ)
- จัดการความรู้ (เพิ่ม/แก้ไข/ลบ)
- จัดการกิจกรรม (เพิ่ม/แก้ไข/ลบ)
- จัดการข้อมูลติดต่อ (เพิ่ม/แก้ไข/ลบ)

### 🖼️ **การจัดการรูปภาพและลิงก์**
- รองรับการอัปโหลดรูปภาพสำหรับ Knowledge และ Activities
- รองรับลิงก์ภายนอก (Website, YouTube, Facebook, Line, อื่นๆ)
- แสดงรูปภาพแบบ thumbnail และคลิกดูใหญ่
- จำกัดขนาดเนื้อหา (Knowledge: 500 ตัวอักษร, Activities: 300 ตัวอักษร)

## 🛠️ เทคโนโลยีที่ใช้

- **Backend**: Python Flask 3.1.2
- **Database**: SQLite + SQLAlchemy 3.0.5
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login 0.6.3
- **File Management**: Local file system + External links
- **Image Processing**: Local storage with optimization
- **Security**: Secure filename handling, file size limits

## 📋 ความต้องการของระบบ

- **Python**: 3.8+ (แนะนำ 3.12)
- **Memory**: ขั้นต่ำ 512MB RAM
- **Storage**: ขั้นต่ำ 1GB สำหรับไฟล์และฐานข้อมูล
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

## 🚀 การติดตั้ง

### 1. **Clone Repository**
```bash
git clone https://github.com/prhdev222/HA_file_final.git
cd HA_file_final
```

### 2. **สร้าง Virtual Environment**
```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. **ติดตั้ง Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **ตั้งค่า Environment Variables**
สร้างไฟล์ `.env` ในโฟลเดอร์หลัก:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=sqlite:///hospital.db
UPLOAD_FOLDER=storage/uploads
MAX_CONTENT_LENGTH=5242880
MAX_FILE_SIZE=5242880
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@hospital.local
HOST=0.0.0.0
PORT=5001
FLASK_DEBUG=true
```

### 5. **รันแอปพลิเคชัน**
```bash
python app.py
```

แอปพลิเคชันจะทำงานที่ `http://localhost:5001`

## 📁 โครงสร้างโปรเจกต์

```
HA_file_final/
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── SETUP.md                 # Detailed setup guide
├── .gitignore               # Git ignore rules
├── env.example              # Environment variables template
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── home.html            # Homepage
│   ├── department.html      # Department page
│   └── admin/               # Admin templates
│       ├── dashboard.html   # Admin dashboard
│       ├── login.html       # Admin login
│       ├── guidelines.html  # Manage guidelines
│       ├── knowledge.html   # Manage knowledge
│       ├── activities.html  # Manage activities
│       ├── contacts.html    # Manage contacts
│       ├── departments.html # Manage departments
│       ├── upload_guideline.html # Upload guidelines
│       ├── edit_guideline.html   # Edit guidelines
│       ├── add_knowledge.html    # Add knowledge
│       ├── edit_knowledge.html   # Edit knowledge
│       ├── add_activity.html     # Add activity
│       ├── edit_activity.html    # Edit activity
│       ├── add_contact.html      # Add contact
│       └── edit_contact.html     # Edit contact
├── static/                  # Static files
│   ├── css/                 # Stylesheets
│   │   └── style.css        # Custom styles
│   ├── js/                  # JavaScript
│   │   └── main.js          # Main JavaScript
│   └── images/              # Images and icons
│       └── kidney.svg       # Kidney icon
├── storage/                 # File storage
│   └── uploads/             # Uploaded files
│       ├── guidelines/      # Department guidelines
│       │   ├── dm/          # Diabetes guidelines
│       │   ├── htn/         # Hypertension guidelines
│       │   ├── chemo/       # Chemotherapy guidelines
│       │   ├── sepsis/      # Sepsis guidelines
│       │   ├── rheumato/    # Rheumatology guidelines
│       │   └── obesity/     # Obesity guidelines
│       ├── knowledge/       # Knowledge images
│       ├── activities/      # Activity images
│       └── images/          # General images
├── instance/                # Instance folder (auto-created)
│   └── hospital.db         # SQLite database
└── scripts/                 # Utility scripts
    ├── read_db.py          # Database reader
    └── optimize_db.py      # Database optimizer
```

## 🔧 การตั้งค่า

### **Database Optimization**
รันสคริปต์เพื่อเพิ่มประสิทธิภาพฐานข้อมูล:
```bash
python optimize_db.py
```

### **Database Inspection**
ตรวจสอบข้อมูลในฐานข้อมูล:
```bash
python read_db.py
```

## 🔐 การเข้าสู่ระบบ

### **Default Admin Credentials**
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@hospital.local`

⚠️ **คำเตือน**: เปลี่ยนรหัสผ่านทันทีหลังการติดตั้งครั้งแรก

## 📊 ฟีเจอร์การจัดการ

### **Guidelines Management**
- อัปโหลดไฟล์ (PDF, DOC, DOCX, TXT) ขนาดสูงสุด 5MB
- เพิ่มลิงก์ภายนอกพร้อมประเภท
- แก้ไขและลบข้อมูล
- จัดการตามหน่วยงาน

### **Knowledge Management**
- เพิ่มความรู้พร้อมรูปภาพหรือลิงก์
- จำกัดเนื้อหา 500 ตัวอักษร
- รองรับรูปภาพและลิงก์ภายนอก
- จัดการตามหน่วยงาน

### **Activity Management**
- เพิ่มกิจกรรมพร้อมรูปภาพหรือลิงก์
- จำกัดคำอธิบาย 300 ตัวอักษร
- รองรับรูปภาพและลิงก์ภายนอก
- จัดการตามหน่วยงาน

### **Contact Management**
- จัดการข้อมูลการติดต่อของแต่ละหน่วย
- รองรับ Line ID, อีเมล, เบอร์โทร, ข้อมูลอื่นๆ
- ต้องมีข้อมูลติดต่ออย่างน้อย 1 อย่าง

## 🚀 การ Deploy

### **Development**
```bash
python app.py
```

### **Production (แนะนำ)**
```bash
# ใช้ Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app

# หรือใช้ Waitress (Windows)
pip install waitress
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

## 🔒 ความปลอดภัย

- ใช้ HTTPS ใน production
- เปลี่ยนรหัสผ่านเริ่มต้น
- จำกัดขนาดไฟล์ที่อัปโหลด
- ตรวจสอบประเภทไฟล์
- ใช้ environment variables สำหรับข้อมูลสำคัญ

## 📈 Performance

- ฐานข้อมูล SQLite พร้อมดัชนี
- การจัดการไฟล์แบบ local storage
- รองรับข้อมูลได้ถึง 10 ล้านรายการ
- ขนาดฐานข้อมูลประมาณ 78GB สำหรับ 10 ล้านรายการ

## 👥 ผู้พัฒนา

**© 2025 ทีมพัฒนาโรงพยาบาลสงฆ์**  
แผนกอายุรกรรม โรงพยาบาลสงฆ์

**วันที่อัปเดต**: 26/08/2025  
**เวอร์ชัน**: 1.0.0

## 📄 License

โปรเจกต์นี้พัฒนาเพื่อใช้ภายในโรงพยาบาลสงฆ์

## 🤝 การสนับสนุน

หากมีปัญหาหรือต้องการความช่วยเหลือ กรุณาติดต่อทีมพัฒนา

## 🔄 การอัปเดต

### **Version 1.0.0 (26/08/2025)**
- ✅ ระบบจัดการหน่วยงาน 12 หน่วย
- ✅ ระบบจัดการ Guidelines (ไฟล์ + ลิงก์)
- ✅ ระบบจัดการความรู้ (รูปภาพ + ลิงก์)
- ✅ ระบบจัดการกิจกรรม (รูปภาพ + ลิงก์)
- ✅ ระบบจัดการข้อมูลติดต่อ
- ✅ ระบบแอดมินครบถ้วน
- ✅ การจัดการรูปภาพและลิงก์ภายนอก
- ✅ ระบบฐานข้อมูลที่เหมาะสม
- ✅ การจัดการไฟล์ที่ปลอดภัย

---

⭐ **Star โปรเจกต์นี้หากมีประโยชน์** ⭐
