# 🏥 ระบบจัดการไฟล์แผนกอายุรกรรม โรงพยาบาลสงฆ์

ระบบจัดการไฟล์และข้อมูลสำหรับแผนกอายุรกรรม พัฒนาด้วย Flask และ SQLAlchemy เพื่อจัดการข้อมูลหน่วยงานต่างๆ ในโรงพยาบาล

## ✨ ฟีเจอร์หลัก

### 🏢 **จัดการหน่วยงาน (9 หน่วย)**
- **DM** - หน่วยเบาหวาน
- **COPD** - หน่วยโรคปอดอุดกั้นเรื้อรัง  
- **UGIB** - หน่วยเลือดออกในทางเดินอาหารส่วนบน
- **CKD** - หน่วยโรคไตเรื้อรัง
- **STEMI/NSTEMI** - หน่วยกล้ามเนื้อหัวใจขาดเลือด
- **STROKE** - หน่วยโรคหลอดเลือดสมอง
- **TB** - หน่วยวัณโรค
- **CHEMO** - หน่วยเคมีบำบัด
- **HTN** - หน่วยความดันโลหิตสูง

### 📁 **จัดการไฟล์และข้อมูล**
- **Guidelines**: อัปโหลดไฟล์และลิงก์ภายนอก
- **ความรู้**: จัดการข้อมูลความรู้ทางการแพทย์
- **กิจกรรม**: จัดการกิจกรรมและงานของหน่วยงาน
- **ข้อมูลติดต่อ**: จัดการข้อมูลการติดต่อของแต่ละหน่วย

### 🔐 **ระบบแอดมิน**
- ระบบล็อกอินสำหรับผู้ดูแลระบบ
- แดชบอร์ดแสดงสถิติและข้อมูลสรุป
- จัดการผู้ใช้และสิทธิ์การเข้าถึง

## 🛠️ เทคโนโลยีที่ใช้

- **Backend**: Python Flask
- **Database**: SQLite + SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login
- **File Management**: Local file system + External links

## 📋 ความต้องการของระบบ

- Python 3.8+
- pip หรือ package manager อื่นๆ
- Virtual environment (แนะนำ)

## 🚀 การติดตั้ง

### 1. **Clone Repository**
```bash
git clone https://github.com/prhdev222/HA_file.git
cd HA_file
```

### 2. **สร้าง Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# หรือ
.venv\Scripts\activate     # Windows
```

### 3. **ติดตั้ง Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **รันแอปพลิเคชัน**
```bash
python app.py
```

แอปพลิเคชันจะทำงานที่ `http://localhost:5001`

## 📁 โครงสร้างโปรเจกต์

```
HA_file/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── home.html         # Homepage
│   ├── department.html   # Department page
│   └── admin/            # Admin templates
├── static/               # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   └── images/           # Images and icons
└── storage/              # File storage
    └── uploads/          # Uploaded files
        └── guidelines/    # Department guidelines
```

## 🔧 การตั้งค่า

### **Environment Variables**
สร้างไฟล์ `.env` ในโฟลเดอร์หลัก:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=storage/uploads
```

### **Database**
ฐานข้อมูล SQLite จะถูกสร้างอัตโนมัติเมื่อรันแอปพลิเคชันครั้งแรก

## 👥 ผู้พัฒนา

**© 2025 Directed by Uradev**  
แผนกอายุรกรรม โรงพยาบาลสงฆ์

**วันที่อัปเดต**: 26/08/2025  
**เวอร์ชัน**: 1.0.0

## 📄 License

โปรเจกต์นี้พัฒนาเพื่อใช้ภายในโรงพยาบาลสงฆ์

## 🤝 การสนับสนุน

หากมีปัญหาหรือต้องการความช่วยเหลือ กรุณาติดต่อทีมพัฒนา

---

⭐ **Star โปรเจกต์นี้หากมีประโยชน์** ⭐
