import requests
import re
import json

url = "https://fpic.cc/embed/u-M0e2MJ?autoplay=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://fpic.cc/"
}

def get_live_m3u8():
    try:
        response = requests.get(url, headers=headers, timeout=10)
        html_content = response.text
        
        # ค้นหาลิงก์ .m3u8 ใน JavaScript หรือ HTML ตัวเล่นวิดีโอ
        match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html_content)
        
        if match:
            # แปลงอักขระพิเศษสแลช (\/) ที่หลุดมาจาก JavaScript
            m3u8_url = match.group(1).replace("\\/", "/")
            return m3u8_url
        else:
            # ค้นหารูปแบบสำรองเผื่อสคริปต์เปลี่ยนโครงสร้าง
            match_alt = re.search(r'["\']([^"\']+\.m3u8[^"\']*)["\']', html_content)
            if match_alt:
                link = match_alt.group(1).replace("\\/", "/")
                if link.startswith("//"): return "https:" + link
                if link.startswith("/"): return "https://fpic.cc" + link
                return link
            print("ไม่พบลิงก์ m3u8 ในหน้าเว็บ")
            return None
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        return None

live_url = get_live_m3u8()

if live_url:
    print(f"ดึงลิงก์สดสำเร็จ: {live_url}")
    
    # 1. เขียนและบันทึกไฟล์ playlist.m3u ลง GitHub
    m3u_content = f"""#EXTM3U
#EXTINF:-1 tvg-id="FpicLive" tvg-name="Fpic Live" group-title="Channels",Fpic Live Stream
{live_url}
"""
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_content.strip() + "\n")
    print("อัปเดตไฟล์ playlist.m3u เรียบร้อย")

    # 2. เขียนและบันทึกไฟล์ playlist.w3u (Wiseplay JSON) ลง GitHub
    w3u_data = {
        "name": "Fpic Auto Playlist",
        "author": "GitHub Actions",
        "stations": [
            {
                "name": "Fpic Live Stream",
                "url": live_url,
                "image": ""
            }
        ]
    }
    with open("playlist.w3u", "w", encoding="utf-8") as f:
        json.dump(w3u_data, f, indent=4, ensure_ascii=False)
    print("อัปเดตไฟล์ playlist.w3u เรียบร้อย")
else:
    print("ระบบไม่สามารถดึง Token ได้ จะไม่มีการเขียนทับไฟล์เดิม")
