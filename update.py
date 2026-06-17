import requests
import re
import os

# ลิงก์หน้าเว็บที่คุณต้องการดึงข้อมูล
TARGET_URL = "https://fpic.cc/embed/u-M0e2MJ"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://fpic.cc/"
}

def get_m3u8_link():
    try:
        # 1. ส่งคำขอไปยังเว็บต้นทาง
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=15)
        html_content = response.text

        # 2. ใช้ Regex ค้นหาลิงก์ .m3u8 ที่ซ่อนอยู่ในซอร์สโค้ดหรือสคริปต์
        # รองรับทั้งแบบลิงก์ตรง และแบบที่ถูกแปลงสแลช (เช่น https:\/\/...)
        matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html_content)
        
        if matches:
            # นำลิงก์แรกที่เจอมาล้างค่าสแลชส่วนเกิน (ถ้ามี)
            clean_link = matches[0].replace(r'\/', '/')
            return clean_link
        
        # กรณีที่เว็บใช้ API แยก (ตัวเลือกสำรอง)
        # หากเช็คใน Network แล้วพบว่าดึงผ่าน API ให้เปลี่ยน TARGET_URL เป็นลิงก์ API นั้นแทน
        
        print("❌ ไม่พบลิงก์ .m3u8 ในหน้าเว็บ")
        return None

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return None

def create_m3u_file(m3u8_url):
    if not m3u8_url:
        return
    
    # รูปแบบไฟล์ M3U สำหรับเอาไปใส่ในแอปเล่นวิดีโอ
    m3u_content = f"#EXTM3U\n#EXTINF:-1, ช่องรายการอัตโนมัติ\n{m3u8_url}\n"
    
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print("✅ อัปเดตไฟล์ playlist.m3u เรียบร้อยแล้ว!")

if __name__ == "__main__":
    link = get_m3u8_link()
    if link:
        print(f"🔗 ลิงก์ที่สแกนได้: {link}")
        create_m3u_file(link)
