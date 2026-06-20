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
        # เปิดเบราว์เซอร์จำลองแบบไร้หน้าต่าง
        browser = p.chromium.launch(headless=True)
        
        # 🛡️ เผื่อไว้ 1: ตั้งค่าจำลองสภาพแวดล้อมให้เหมือนมนุษย์ใช้งานจริง และข้ามระบบตรวจ SSL
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True # เผื่อเว็บหนังทำระบบ SSL หลังบ้านพัง สคริปต์จะยังไม่หลุดขัดข้อง
        )
        
        page = context.new_page()
        
        # ฟังก์ชันดักฟังเครือข่าย (Network Interception)
        def handle_request(request):
            nonlocal found_link
            req_url = request.url
            
            # ตรวจสอบคำขอที่เป็นตระกูลสตรีมมิ่ง .m3u8
            if ".m3u8" in req_url:
                # 🛡️ เผื่อไว้ 2: จัดลำดับความสำคัญของลิงก์ที่เจอ
                # ลำดับ 1: ลิงก์หลักที่มีทุกความละเอียด (มักมีคำว่า master หรือ playlist)
                if "master" in req_url or "playlist" in req_url:
                    found_link = req_url
                # ลำดับ 2: ถ้าไม่มีสองคำบน แต่มีลักษณะของ HLS Stream ให้เก็บไว้สำรอง
                elif "hls" in req_url or "stream" in req_url:
                    if not found_link or ("master" not in found_link and "playlist" not in found_link):
                        found_link = req_url
                # ลำดับ 3: เจอไฟล์ .m3u8 อะไรก็ตามจับไว้ก่อนกันพลาด
                elif not found_link:
                    found_link = req_url

        # สั่งเริ่มกระบวนการดักฟังเครือข่าย
        page.on("request", handle_request)
        
        try:
            # wait_until="commit" เพื่อให้เริ่มดักจับทันทีเมื่อหน้าเว็บเริ่มตอบรับ ไม่ต้องรอให้พวกโฆษณาโหลดเสร็จหมด
            page.goto(url, timeout=45000, wait_until="commit")
            
            # 🛡️ เผื่อไว้ 3 (Early Exit): ไม่ต้องรอให้ครบเวลาตายตัว 
            # ให้วนลูปตรวจเช็คทุกๆ 1 วินาที สูงสุด 15 วินาที ถ้าเจอลิงก์หลักแล้วให้ข้ามทันทีเพื่อเซฟเวลาบอท
            for _ in range(15):
                if found_link and ("master" in found_link or "playlist" in found_link):
                    break
                time.sleep(1)
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดเว็บ {url}: {e}")
        finally:
            # ปิดหน้าต่างเซสชันให้สะอาดเรียบร้อย
            context.close()
            browser.close()
            
    return found_link

def generate_m3u():
    m3u_content = "#EXTM3U\n"
    
    for movie in MOVIE_SOURCES:
        print(f"กำลังค้นหาลิงก์ .m3u8 สำหรับ: {movie['title']}")
        m3u8_url = get_m3u8_link(movie['url'])
        
        if m3u8_url:
            print(f"🎯 เจอลิงก์ m3u8: {m3u8_url}")
            m3u_content += f'#EXTINF:-1 tvg-name="{movie["title"]}" group-title="Movies",{movie["title"]}\n'
            m3u_content += f'{m3u8_url}\n'
        else:
            print(f"❌ ไม่พบลิงก์ .m3u8 สำหรับ: {movie['title']}")
            
    # บันทึกไฟล์ playlist.m3u
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print("สร้างไฟล์ playlist.m3u (เวอร์ชันเสถียรสูง) สำเร็จแล้ว!")

if __name__ == "__main__":
    generate_m3u()
