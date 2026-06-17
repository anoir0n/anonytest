import requests
import re
import json

url = "https://fpic.cc/embed/u-M0e2MJ?autoplay=1"

# ปรับ Header ให้เหมือนเบราว์เซอร์มนุษย์มากขึ้น เพื่อลดโอกาสโดนบล็อก
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://fpic.cc/",
    "Connection": "keep-alive"
}

def get_live_m3u8():
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html_content = response.text
        
        # ค้นหาลิงก์ .m3u8
        match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html_content)
        
        if match:
            m3u8_url = match.group(1).replace("\\/", "/")
            return m3u8_url
        else:
            match_alt = re.search(r'["\']([^"\']+\.m3u8[^"\']*)["\']', html_content)
            if match_alt:
                link = match_alt.group(1).replace("\\/", "/")
                if link.startswith("//"): return "https:" + link
                if link.startswith("/"): return "https://fpic.cc" + link
                return link
            return None
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

live_url = get_live_m3u8()

# หากดึงไม่สำเร็จ จะสร้างลิงก์ Placeholder ป้องกัน Git หาไฟล์ไม่เจอ
if not live_url:
    print("⚠️ ไม่สามารถดึง Token ล่าสุดได้ ระบบจะสร้างไฟล์ตัวอย่างรอไว้ก่อนเพื่อป้องกันระบบล่ม")
    live_url = "https://example.com/stream_expired.m3u8"

# 1. เขียนและบันทึกไฟล์ playlist.m3u
m3u_content = f"""#EXTM3U
#EXTINF:-1 tvg-id="FpicLive" tvg-name="Fpic Live" group-title="Channels",Fpic Live Stream
{live_url}
"""
with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_content.strip() + "\n")
print("อัปเดตไฟล์ playlist.m3u เรียบร้อย")

# 2. เขียนและบันทึกไฟล์ playlist.w3u
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
