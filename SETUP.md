# 🔧 การตั้งค่าโปรเจกต์

## 📋 ขั้นตอนการติดตั้ง

### 1. **สร้างไฟล์ .env**
```bash
# คัดลอกไฟล์ตัวอย่าง
cp env.example .env

# แก้ไขไฟล์ .env ด้วยข้อมูลจริง
nano .env  # หรือใช้ editor ที่ชอบ
```

### 2. **ตั้งค่าในไฟล์ .env**
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Security - เปลี่ยนเป็นค่าที่ปลอดภัย
SECRET_KEY=your-super-secret-key-here-12345
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-password
ADMIN_EMAIL=your-email@domain.com

# Database
DATABASE_URL=sqlite:///hospital.db

# Upload Settings
UPLOAD_FOLDER=storage/uploads
MAX_CONTENT_LENGTH=52428800

# Server Settings
HOST=0.0.0.0
PORT=5001
```

### 3. **ติดตั้ง Dependencies**
```bash
# สร้าง virtual environment
python -m venv .venv

# เปิดใช้งาน
source .venv/bin/activate  # macOS/Linux
# หรือ
.venv\Scripts\activate     # Windows

# ติดตั้ง packages
pip install -r requirements.txt
```

### 4. **รันแอปพลิเคชัน**
```bash
python app.py
```

## 🔐 ความปลอดภัย

### **SECRET_KEY**
- ใช้ค่าที่ซับซ้อนและยาว
- ตัวอย่าง: `SECRET_KEY=my-super-secret-key-2025-xyz-123`

### **ADMIN_PASSWORD**
- ใช้รหัสผ่านที่แข็งแกร่ง
- อย่างน้อย 8 ตัวอักษร
- รวมตัวพิมพ์ใหญ่, ตัวพิมพ์เล็ก, ตัวเลข, สัญลักษณ์

### **การตั้งค่า Production**
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key
HOST=127.0.0.1  # หรือ IP ที่ปลอดภัย
```

## ⚠️ ข้อควรระวัง

1. **อย่าอัปโหลดไฟล์ .env ไปยัง GitHub**
2. **เปลี่ยนรหัสผ่านเริ่มต้นทันที**
3. **ใช้ HTTPS ใน production**
4. **สำรองข้อมูลเป็นประจำ**

## 🆘 การแก้ไขปัญหา

### **ปัญหา: ModuleNotFoundError: No module named 'dotenv'**
```bash
pip install python-dotenv
```

### **ปัญหา: .env file not found**
```bash
# ตรวจสอบว่าอยู่ในโฟลเดอร์ที่ถูกต้อง
ls -la | grep .env
```

### **ปัญหา: Permission denied**
```bash
# เปลี่ยนสิทธิ์ไฟล์
chmod 600 .env
```
