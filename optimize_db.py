#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Optimization Script for Hospital Management System
ใช้สำหรับเพิ่มประสิทธิภาพฐานข้อมูล SQLite
"""

import sqlite3
import os
import time
from datetime import datetime

def connect_db():
    """เชื่อมต่อฐานข้อมูล"""
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
        return None

def create_indexes(conn):
    """สร้างดัชนีเพื่อเพิ่มประสิทธิภาพ"""
    try:
        cursor = conn.cursor()
        
        print("🔧 กำลังสร้างดัชนีเพื่อเพิ่มประสิทธิภาพ...")
        
        # ดัชนีสำหรับตาราง department
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_department_code ON department(code)",
            "CREATE INDEX IF NOT EXISTS idx_department_name ON department(name)",
            "CREATE INDEX IF NOT EXISTS idx_department_created ON department(created_at)",
            
            # ดัชนีสำหรับตาราง guideline
            "CREATE INDEX IF NOT EXISTS idx_guideline_dept ON guideline(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_guideline_title ON guideline(title)",
            "CREATE INDEX IF NOT EXISTS idx_guideline_upload ON guideline(upload_date)",
            "CREATE INDEX IF NOT EXISTS idx_guideline_external ON guideline(external_link)",
            
            # ดัชนีสำหรับตาราง knowledge
            "CREATE INDEX IF NOT EXISTS idx_knowledge_dept ON knowledge(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_title ON knowledge(title)",
            "CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge(created_at)",
            
            # ดัชนีสำหรับตาราง activity
            "CREATE INDEX IF NOT EXISTS idx_activity_dept ON activity(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_activity_date ON activity(activity_date)",
            "CREATE INDEX IF NOT EXISTS idx_activity_created ON activity(created_at)",
            
            # ดัชนีสำหรับตาราง contact
            "CREATE INDEX IF NOT EXISTS idx_contact_dept ON contact(department_id)",
            "CREATE INDEX IF NOT EXISTS idx_contact_email ON contact(email)",
            "CREATE INDEX IF NOT EXISTS idx_contact_phone ON contact(phone)",
            
            # ดัชนีสำหรับตาราง admin_user
            "CREATE INDEX IF NOT EXISTS idx_admin_username ON admin_user(username)",
            "CREATE INDEX IF NOT EXISTS idx_admin_email ON admin_user(email)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"  ✅ สร้างดัชนี: {index_sql.split('idx_')[1].split(' ON ')[0]}")
        
        conn.commit()
        print("✅ สร้างดัชนีเสร็จสิ้น")
        
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้างดัชนี: {e}")

def analyze_database(conn):
    """วิเคราะห์ฐานข้อมูล"""
    try:
        cursor = conn.cursor()
        
        print("\n📊 การวิเคราะห์ฐานข้อมูล")
        print("=" * 50)
        
        # ดูขนาดไฟล์
        db_path = 'instance/hospital.db'
        file_size = os.path.getsize(db_path)
        file_size_mb = file_size / (1024 * 1024)
        print(f"📁 ขนาดไฟล์ฐานข้อมูล: {file_size_mb:.2f} MB")
        
        # ดูจำนวนข้อมูลในแต่ละตาราง
        tables = ['department', 'admin_user', 'guideline', 'knowledge', 'activity', 'contact']
        
        total_records = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            total_records += count
            print(f"📋 {table.capitalize()}: {count:,} รายการ")
        
        print(f"\n📈 จำนวนข้อมูลทั้งหมด: {total_records:,} รายการ")
        
        # ประมาณการขนาดในอนาคต
        if total_records > 0:
            avg_record_size = file_size / total_records
            print(f"📏 ขนาดเฉลี่ยต่อรายการ: {avg_record_size:.2f} bytes")
            
            # คำนวณขนาดในอนาคต
            future_sizes = [10000, 100000, 1000000, 10000000]
            print(f"\n🔮 การประมาณการขนาดในอนาคต:")
            for future_count in future_sizes:
                future_size_mb = (future_count * avg_record_size) / (1024 * 1024)
                print(f"  {future_count:,} รายการ: {future_size_mb:.2f} MB")
        
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการวิเคราะห์: {e}")

def performance_test(conn):
    """ทดสอบประสิทธิภาพ"""
    try:
        cursor = conn.cursor()
        
        print("\n⚡ ทดสอบประสิทธิภาพ")
        print("=" * 50)
        
        # ทดสอบการค้นหาแบบไม่มีดัชนี
        print("🔍 ทดสอบการค้นหาแบบไม่มีดัชนี...")
        start_time = time.time()
        cursor.execute("SELECT * FROM department WHERE code = 'DM'")
        result = cursor.fetchone()
        no_index_time = time.time() - start_time
        print(f"  ⏱️  เวลา: {no_index_time:.6f} วินาที")
        
        # ทดสอบการค้นหาแบบมีดัชนี
        print("🔍 ทดสอบการค้นหาแบบมีดัชนี...")
        start_time = time.time()
        cursor.execute("SELECT * FROM department WHERE code = 'DM'")
        result = cursor.fetchone()
        with_index_time = time.time() - start_time
        print(f"  ⏱️  เวลา: {with_index_time:.6f} วินาที")
        
        # ทดสอบการค้นหาข้อมูลที่เกี่ยวข้อง
        print("🔍 ทดสอบการค้นหาข้อมูลที่เกี่ยวข้อง...")
        start_time = time.time()
        cursor.execute("""
            SELECT d.name, COUNT(g.id) as guideline_count
            FROM department d
            LEFT JOIN guideline g ON d.id = g.department_id
            GROUP BY d.id
            ORDER BY guideline_count DESC
        """)
        results = cursor.fetchall()
        join_time = time.time() - start_time
        print(f"  ⏱️  เวลา: {join_time:.6f} วินาที")
        print(f"  📊 ผลลัพธ์: {len(results)} รายการ")
        
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการทดสอบประสิทธิภาพ: {e}")

def maintenance_tips():
    """คำแนะนำการบำรุงรักษา"""
    print("\n💡 คำแนะนำการบำรุงรักษาฐานข้อมูล")
    print("=" * 50)
    
    tips = [
        "🔧 สร้างดัชนีสำหรับคอลัมน์ที่ใช้ค้นหาบ่อย",
        "🗑️ ลบข้อมูลเก่าที่ไม่ใช้แล้ว",
        "📅 แบ่งข้อมูลตามช่วงเวลา (Partitioning)",
        "💾 สำรองข้อมูลเป็นประจำ",
        "📊 วิเคราะห์ประสิทธิภาพเป็นระยะ",
        "🔄 ใช้ VACUUM เพื่อจัดระเบียบฐานข้อมูล",
        "📝 จำกัดขนาดไฟล์ที่อัปโหลด",
        "⚡ ใช้การเชื่อมต่อแบบ Read-Only สำหรับการอ่าน"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"  {i}. {tip}")

def main():
    """ฟังก์ชันหลัก"""
    print("🏥 Database Optimization Script for Hospital Management System")
    print("=" * 70)
    
    # เชื่อมต่อฐานข้อมูล
    conn = connect_db()
    if not conn:
        return
    
    try:
        # สร้างดัชนี
        create_indexes(conn)
        
        # วิเคราะห์ฐานข้อมูล
        analyze_database(conn)
        
        # ทดสอบประสิทธิภาพ
        performance_test(conn)
        
        # คำแนะนำการบำรุงรักษา
        maintenance_tips()
        
    finally:
        conn.close()
        print("\n✅ ปิดการเชื่อมต่อฐานข้อมูลแล้ว")

if __name__ == "__main__":
    main()
