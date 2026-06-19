import requests
import json
import re

# ==================== ตั้งค่าการเชื่อมต่อเลียนแบบแอป ====================
# เซิร์ฟเวอร์หลักของ AppCreator24 (ปรับเปลี่ยนโดเมนได้ถ้าดักจับพบตัวอื่น เช่น srv1.appcreator24.com)
API_URL = "https://html5.appcreator24.com/srv/get_config.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; AppCreator24)",
    "X-Requested-With": "com.appcreator24.app4086696",  # แพ็กเกจไอดีแอปของคุณ
    "Content-Type": "application/x-www-form-urlencoded"
}

PAYLOAD = {
    "idapp": "4086696",  # ไอดีแอปของคุณ
    "v": "1",
    "lang": "th"
}
# ====================================================================

def find_streams_recursively(data, found_stations=None):
    """ฟังก์ชันอัจฉริยะสแกนหาลิงก์สตรีมสดและชื่อช่องในข้อมูล JSON ทั้งหมด"""
    if found_stations is None:
        found_stations = []

    if isinstance(data, dict):
        # พยายามจับคู่ชื่อช่องกับลิงก์สตรีมสดที่อยู่ใน Object เดียวกัน
        name = data.get("title") or data.get("name") or data.get("titulo")
        url = data.get("url") or data.get("stream") or data.get("link") or data.get("url_stream")
        image = data.get("logo") or data.get("image") or data.get("img") or ""

        # ตรวจสอบว่าลิงก์เป็นโปรโตคอลสตรีมมิงหรือไม่ (RTMP, FLV, M3U8, TS, MP4)
        if url and isinstance(url, str):
            is_stream = (
                url.startswith("rtmp://") or 
                url.startswith("rtmps://") or 
                any(ext in url.lower() for ext in [".flv", ".m3u8", ".ts", "live"])
            )
            if is_stream:
                channel_name = name if name else f"ช่องสตรีมสด {len(found_stations) + 1}"
                found_stations.append({
                    "name": str(channel_name).strip(),
                    "image": str(image).strip(),
                    "url": str(url).strip()
                })
        
        # วนลูปค้นหาต่อในชั้นถัดไป
        for key, value in data.items():
            find_streams_recursively(value, found_stations)

    elif isinstance(data, list):
        for item in data:
            find_streams_recursively(item, found_stations)

    return found_stations

def fetch_all_live_streams():
    print("🤖 กำลังเลียนแบบแอปเพื่อเชื่อมต่อไปยังเซิร์ฟเวอร์หลังบ้าน...")
    try:
        response = requests.post(API_URL, headers=HEADERS, data=PAYLOAD, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ เซิร์ฟเวอร์ปฏิเสธคำขอ (Status Code: {response.status_code})")
            return []

        # พยายามอ่านค่าเป็น JSON
        try:
            response_data = response.json()
            print("📝 เชื่อมต่อสำเร็จ! กำลังค้นหารายการสตรีมทั้งหมดภายในข้อมูล...")
            return find_streams_recursively(response_data)
        except json.JSONDecodeError:
            # กรณีเซิร์ฟเวอร์ส่งมาเป็นข้อความธรรมดา หรือ Format อื่น ให้ใช้ Regex สแกนหาลิงก์ตรงๆ
            print("⚠️ ข้อมูลไม่ได้เป็น JSON ตรงๆ กำลังใช้ระบบสแกนข้อความดิบ...")
            raw_text = response.text
            # ค้นหาลิงก์ rtmp หรือ http ที่เกี่ยวกับสตรีม
            urls = re.findall(r'(rtmp://[^\s"\']+|https?://[^\s"\']+(?:\.m3u8|\.flv|\.ts))', raw_text)
            
            stations = []
            for i, url in enumerate(set(urls)): # set เพื่อตัดลิงก์ซ้ำ
                stations.append({
                    "name": f"สตรีมสด ช่องที่ {i+1}",
                    "image": "",
                    "url": url
                })
            return stations

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในระบบเครือข่าย: {e}")
        return []

def save_to_w3u(stations):
    w3u_structure = {
        "name": "StreamHub Live All",
        "author": "GitHub Automation Emulator",
        "image": "https://wiseplay.tv/img/logo.png",
        "stations": stations
    }
    
    output_file = "StreamHub.w3u"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(w3u_structure, f, ensure_ascii=False, indent=4)
        
    print(f"✅ บันทึกไฟล์สำเร็จ! พบสตรีมทั้งหมดที่ใช้งานได้ {len(stations)} ช่อง")

if __name__ == "__main__":
    all_stations = fetch_all_live_streams()
    if all_stations:
        save_to_w3u(all_stations)
    else:
        print("⚠️ ไม่พบลิงก์สตรีมสดใดๆ ส่งกลับมาจากเซิร์ฟเวอร์ในรอบนี้")
