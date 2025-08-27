#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite Database Reader for Hospital Management System
ใช้สำหรับอ่านและวิเคราะห์ฐานข้อมูล hospital.db
"""

import sqlite3
import os
from datetime import datetime

def connect_db():
    """เชื่อมต่อฐานข้อมูล"""
    db_path = 'instance/hospital.db'
    if not os.path.exists(db_path):
        print(f"❌ ไม่พบไฟล์ฐานข้อมูล: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # ทำให้ผลลัพธ์เป็น dictionary-like
        return conn
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูล: {e}")
        return None

def show_table_info(conn, table_name):
    """แสดงข้อมูลในตาราง"""
    try:
        cursor = conn.cursor()
        
        # ดูโครงสร้างตาราง
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n📋 โครงสร้างตาราง: {table_name}")
        print("-" * 50)
        for col in columns:
            print(f"  {col['name']} ({col['type']}) - {'NOT NULL' if col['notnull'] else 'NULL'}")
        
        # ดูจำนวนข้อมูล
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']
        print(f"\n📊 จำนวนข้อมูล: {count} รายการ")
        
        # ดูข้อมูลทั้งหมด
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            print(f"\n📝 ข้อมูลในตาราง {table_name}:")
            print("-" * 50)
            
            for i, row in enumerate(rows, 1):
                print(f"\n  รายการที่ {i}:")
                for col in columns:
                    value = row[col['name']]
                    if value is None:
                        value = "NULL"
                    elif isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"    {col['name']}: {value}")
        
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่านตาราง {table_name}: {e}")

def show_departments_summary(conn):
    """แสดงสรุปข้อมูลหน่วยงาน"""
    try:
        cursor = conn.cursor()
        
        # นับจำนวนข้อมูลในแต่ละตารางที่เกี่ยวข้อง
        tables = ['guideline', 'knowledge', 'activity', 'contact']
        
        print("\n🏥 สรุปข้อมูลหน่วยงาน")
        print("=" * 60)
        
        cursor.execute("SELECT * FROM department ORDER BY id")
        departments = cursor.fetchall()
        
        for dept in departments:
            print(f"\n📋 {dept['name']} (ID: {dept['id']}, Code: {dept['code']})")
            print(f"   คำอธิบาย: {dept['description']}")
            print(f"   วันที่สร้าง: {dept['created_at']}")
            print(f"   วันที่อัปเดต: {dept['updated_at']}")
            
            # นับข้อมูลที่เกี่ยวข้อง
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table} WHERE department_id = ?", (dept['id'],))
                count = cursor.fetchone()['count']
                print(f"   {table.capitalize()}: {count} รายการ")
        
    except sqlite3.Error as e:
        print(f"❌ เกิดข้อผิดพลาดในการอ่านสรุปข้อมูล: {e}")

def main():
    """ฟังก์ชันหลัก"""
    print("🏥 SQLite Database Reader for Hospital Management System")
    print("=" * 60)
    
    # เชื่อมต่อฐานข้อมูล
    conn = connect_db()
    if not conn:
        return
    
    try:
        # แสดงข้อมูลในแต่ละตาราง
        tables = ['department', 'admin_user', 'guideline', 'knowledge', 'activity', 'contact']
        
        for table in tables:
            show_table_info(conn, table)
        
        # แสดงสรุปข้อมูลหน่วยงาน
        show_departments_summary(conn)
        
    finally:
        conn.close()
        print("\n✅ ปิดการเชื่อมต่อฐานข้อมูลแล้ว")

if __name__ == "__main__":
    main()
