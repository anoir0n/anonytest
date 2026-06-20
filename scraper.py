import os
import time
import re
from playwright.sync_api import sync_playwright

# 🌟 สามารถใส่ผสมกันได้ทั้งลิงก์หน้าเว็บหนังปกติ และลิงก์ API/Player ตรงแบบที่คุณส่งมา
MOVIE_SOURCES = [
    {
        "title": "Per Aspera Ad Astra (2026)",
        "url": "https://www.037hddmovie.com/2026/06/19/per-aspera-ad-astra-2026-ฝ่าห้วงฝันสู่ดวงดาว/"
    },
    {
        "title": "LeoPlayer Stream Test",
        "url": "https://www.leoplayer7.com/api/analogy/mediahls3/ItCIv_Sgzn?expires=98733615&token=01b55a2beb23f756e7b2625f4ddf30e8&signature=aeezni61qf55zrg3slcywvw0kv4qpams73rfz25qo7xuxlyy9f"
    }
]

def get_m3u8_link(url):
    found_link = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            ignore_https_errors=True
        )
        
        # 🛡️ ขั้นตอนเผื่อไว้พิเศษ: ตรวจสอบว่าเป็นลิงก์ประเภท Player API ตรง (เช่น leoplayer) หรือไม่
        if "api/" in url or "leoplayer" in url or "player" in url:
            try:
                print(f"🔎 ตรวจพบลิงก์รูปแบบ API: กำลังใช้วิธีดึงข้อมูลตรงความเร็วสูง...")
                page = context.new_page()
                response = page.request.get(url)
                response_text = response.text()
                
                # ใช้ Regex สแกนหาลิงก์ตระกูล .m3u8 ที่อยู่ในเนื้อหาหรือ JSON
                m3u8_matches = re.findall(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', response_text)
                if m3u8_matches:
                    for match in m3u8_matches:
                        # ล้างค่าเครื่องหมายสแลชที่อาจติดมาจาก JSON (เช่น \/)
                        clean_url = match.replace("\\", "")
                        if "master" in clean_url or "playlist" in clean_url:
                            found_link = clean_url
                            break
                    if not found_link:
                        found_link = m3u8_matches[0].replace("\\", "")
                
                context.close()
                browser.close()
                
                if found_link:
                    return found_link
            except Exception as api_err:
                print(f"⚠️ วิธีดึงตรงผ่าน API ติดขัด: {api_err} -> จะสลับไปใช้ระบบจำลองเบราว์เซอร์ปกติสำรองให้")

        # --- 🌐 ระบบจำลองเบราว์เซอร์ปกติ (สำหรับหน้าเว็บทั่วไป หรือกรณีดึงตรงไม่ผ่าน) ---
        page = context.new_page()
        
        def handle_request(request):
            nonlocal found_link
            req_url = request.url
            if ".m3u8" in req_url:
                if "master" in req_url or "playlist" in req_url:
                    found_link = req_url
                elif "hls" in req_url or "stream" in req_url:
                    if not found_link or ("master" not in found_link and "playlist" not in found_link):
                        found_link = req_url
                elif not found_link:
                    found_link = req_url

        page.on("request", handle_request)
        
        try:
            page.goto(url, timeout=45000, wait_until="commit")
            
            # ระบบตรวจเช็คแล้วออกทันที (Early Exit) เพื่อความรวดเร็ว
            for _ in range(15):
                if found_link and ("master" in found_link or "playlist" in found_link):
                    break
                time.sleep(1)
                
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลดเว็บ {url}: {e}")
        finally:
            context.close()
            browser.close()
            
    return found_link

def generate_m3u():
    m3u_content = "#EXTM3U\n"
    
    for movie in MOVIE_SOURCES:
        print(f"\n========================================")
        print(f"กำลังดำเนินการค้นหา: {movie['title']}")
        m3u8_url = get_m3u8_link(movie['url'])
        
        if m3u8_url:
            print(f"🎯 เจอลิงก์สตรีมมิ่งสำเร็จ: {m3u8_url}")
            m3u_content += f'#EXTINF:-1 tvg-name="{movie["title"]}" group-title="Movies",{movie["title"]}\n'
            m3u_content += f'{m3u8_url}\n'
        else:
            print(f"❌ ไม่พบลิงก์สตรีมมิ่งสำหรับ: {movie['title']}")
            
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print("\n========================================")
    print("สร้างไฟล์ playlist.m3u เวอร์ชันรองรับ API & Web เรียบร้อยแล้ว!")

if __name__ == "__main__":
    generate_m3u()
