import os
import time
from playwright.sync_api import sync_playwright

# 🌟 ใส่รายชื่อหน้าเว็บหนังที่ต้องการดึงลิงก์ตรงนี้ (สามารถเพิ่มหรือเปลี่ยนลิงก์ได้เรื่อยๆ)
MOVIE_SOURCES = [
    {
        "title": "Per Aspera Ad Astra (2026)",
        "url": "https://www.037hddmovie.com/2026/06/19/per-aspera-ad-astra-2026-ฝ่าห้วงฝันสู่ดวงดาว/"
    }
]

def get_m3u8_link(url):
    found_link = None
    
    with sync_playwright() as p:
        # เปิดเบราว์เซอร์จำลองแบบไร้หน้าต่าง (Headless Mode)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # ฟังก์ชันดักฟังเครือข่าย (Network Interception)
        def handle_request(request):
            nonlocal found_link
            # ดักจับเฉพาะคำขอที่มีนามสกุล .m3u8 เท่านั้น
            if ".m3u8" in request.url:
                # เจาะจงเลือกเฉพาะลิงก์ที่มีคำว่า 'master' หรือระบุสตรีมหลัก (ถ้ามี)
                if "master" in request.url or "playlist" in request.url:
                    found_link = request.url
                # หากไม่มีคำเฉพาะด้านบน แต่เจอ .m3u8 ตัวแรก ให้เก็บไว้เป็นตัวสำรองก่อน
                elif not found_link:
                    found_link = request.url

        # สั่งให้ระบบเริ่มดักฟังทุกครั้งที่มีคำขอเครือข่ายเกิดขึ้นในหน้าเว็บ
        page.on("request", handle_request)
        
        try:
            page.goto(url, timeout=30000)
            # รอให้ระบบเครื่องเล่นวิดีโอบนเว็บโหลดสคริปต์และพ่นคำขอ m3u8 ออกมา (ประมาณ 10-12 วินาที)
            page.wait_for_timeout(12000) 
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดเว็บ {url}: {e}")
        finally:
            browser.close()
            
    return found_link

def generate_m3u():
    # สร้างโครงสร้างไฟล์สำหรับ Playlist M3U
    m3u_content = "#EXTM3U\n"
    
    for movie in MOVIE_SOURCES:
        print(f"กำลังค้นหาลิงก์ .m3u8 สำหรับ: {movie['title']}")
        m3u8_url = get_m3u8_link(movie['url'])
        
        if m3u8_url:
            print(f"🎯 เจอลิงก์ m3u8: {m3u8_url}")
            # จัดฟอร์แมตมาตรฐาน IPTV
            m3u_content += f'#EXTINF:-1 tvg-name="{movie["title"]}" group-title="Movies",{movie["title"]}\n'
            m3u_content += f'{m3u8_url}\n'
        else:
            print(f"❌ ไม่พบลิงก์ .m3u8 สำหรับ: {movie['title']}")
            
    # บันทึกผลลัพธ์ลงไฟล์ playlist.m3u
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print("สร้างไฟล์ playlist.m3u (เฉพาะ m3u8) สำเร็จแล้ว!")

if __name__ == "__main__":
    generate_m3u()
