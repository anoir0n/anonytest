import requests
import json
import os

# ==================== ส่วนที่ต้องแก้ไขตามแอปของคุณ ====================
# เปลี่ยนเป็น URL API หลังบ้านของ AppCreator24 ที่คุณดักจับได้
API_URL = "https://html5.appcreator24.com/srv/get_links.php"

# ปลอมตัวเป็นแอปพลิเคชันโดยใส่ Headers ที่ก๊อปปี้มาจากแอปจริง
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; AppCreator24)",
    "X-Requested-With": "com.appcreator24.app4086696",  # ID ของแอปตัวนี้
    "Content-Type": "application/x-www-form-urlencoded"
}

# ข้อมูลที่แอปส่งไปขอลิงก์ (Payload)
PAYLOAD = {
    "idapp": "4086696",
    "action": "get_streams"
}
# ==================================================================

def fetch_m3u8_links():
    print("กำลังส่งคำขอแบบปลอมตัวเป็นแอป...")
    try:
        # ในการใช้งานจริง ให้เปิดคอมเมนต์ 3 บรรทัดล่างนี้เพื่อต่อกับเซิร์ฟเวอร์จริง
        # response = requests.post(API_URL, headers=HEADERS, data=PAYLOAD, timeout=10)
        # result = response.json() 
        # return result['channels']

        # --- ส่วนจำลองข้อมูล (คุณสามารถลบส่วนนี้ออกเมื่อต่อ API จริงสำเร็จ) ---
        mock_extracted_channels = [
            {"name": "Live ช่อง 1", "url": "https://example.com/live/stream1/playlist.m3u8", "image": "https://example.com/logo1.png"},
            {"name": "Live ช่อง 2", "url": "https://example.com/live/stream2/playlist.m3u8", "image": "https://example.com/logo2.png"}
        ]
        return mock_extracted_channels
        # -----------------------------------------------------------------

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}")
        return []

def convert_to_w3u(channels):
    print("กำลังแปลงข้อมูลเป็นรูปแบบ StreamHub.w3u (Wiseplay Format)...")
    
    # โครงสร้างพื้นฐานของไฟล์ .w3u
    w3u_structure = {
        "name": "StreamHub Playlist",
        "author": "GitHub Automation",
        "image": "https://wiseplay.tv/img/logo.png",
        "stations": []
    }
    
    # วนลูปนำลิงก์ m3u8 ใส่เข้าไป
    for ch in channels:
        station = {
            "name": ch["name"],
            "image": ch.get("image", ""),
            "url": ch["url"]
        }
        w3u_structure["stations"].append(station)
        
    # บันทึกออกเป็นไฟล์ StreamHub.w3uตามที่ต้องการ
    with open("StreamHub.w3u", "w", encoding="utf-8") as f:
        json.dump(w3u_structure, f, ensure_ascii=False, indent=4)
        
    print("สร้างไฟล์ StreamHub.w3u เรียบร้อยแล้ว!")

if __name__ == "__main__":
    extracted_data = fetch_m3u8_links()
    if extracted_data:
        convert_to_w3u(extracted_data)
    else:
        print("ไม่พบข้อมูลช่องรายการ")
