import requests
import json
import os

# ==================== ส่วนที่ต้องแก้ไขหลังดักจับเซิร์ฟเวอร์จริงได้ ====================
# เปลี่ยนเป็น URL Config/API หลังบ้านของ AppCreator24 ที่คุณดักจับได้ตอนเปิดแอป
API_URL = "https://html5.appcreator24.com/srv/get_config.php"  

# ใช้ข้อมูลระบุตัวตน (Headers) ของแอปพลิเคชันจริงที่คุณอัปโหลดมา
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; AppCreator24)",
    "X-Requested-With": "com.appcreator24.app4086696",  # แพ็กเกจไอดีของแอปตัวนี้
    "Content-Type": "application/x-www-form-urlencoded"
}

# ข้อมูลที่ส่งไปขอรายการช่องทั้งหมด (Payload)
PAYLOAD = {
    "idapp": "4086696",
    "action": "get_full_list"
}
# ==============================================================================

def fetch_rtmp_streams():
    print("🤖 กำลังปลอมตัวเป็นแอปเพื่อขอลิงก์ RTMP จากเซิร์ฟเวอร์...")
    try:
        # เปิดใช้งาน 3 บรรทัดล่างนี้เมื่อได้ลิงก์ API_URL จริงจากการดักจับทราฟฟิก
        # response = requests.post(API_URL, headers=HEADERS, data=PAYLOAD, timeout=15)
        # response_data = response.json()
        # return response_data.get('streams', [])

        # -----------------------------------------------------------------
        # ส่วนจำลองข้อมูลสตรีม RTMP (คุณสามารถลบส่วนนี้ออกเมื่อต่อ API จริงสำเร็จ)
        # ตัวอย่างนี้แสดงให้เห็นว่า .w3u สามารถใส่ลิงก์ rtmp:// หรือ .flv ได้โดยตรง
        mock_rtmp_data = [
            {
                "title": "ช่องสตรีมสด RTMP 1", 
                "stream_url": "rtmp://example.com/live/stream1", 
                "logo": "https://example.com/logo1.png"
            },
            {
                "title": "ช่องสตรีมสด FLV 2", 
                "stream_url": "http://example.com/live/stream2.flv", 
                "logo": "https://example.com/logo2.png"
            }
        ]
        return mock_rtmp_data
        # -----------------------------------------------------------------

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์: {e}")
        return []

def generate_w3u_playlist(stream_list):
    print("📝 กำลังแปลงข้อมูลสตรีมสดเป็นรูปแบบ StreamHub.w3u (Wiseplay Format)...")
    
    # โครงสร้างพื้นฐานของไฟล์ .w3u สำหรับแอปเครื่องเล่น
    w3u_structure = {
        "name": "StreamHub RTMP Live",
        "author": "GitHub Automation",
        "image": "https://wiseplay.tv/img/logo.png",
        "stations": []
    }
    
    # วนลูปอ่านค่าดึงสตรีมและแปลงเข้าโครงสร้าง Wiseplay
    for stream in stream_list:
        # ดึงค่า URL (ตรวจสอบให้ตรงกับคีย์ที่ระบบจริงส่งกลับมา เช่น 'stream_url' หรือ 'url')
        url = stream.get("stream_url", "")
        name = stream.get("title", "Unknown Channel")
        image = stream.get("logo", "")
        
        # คัดกรองเฉพาะช่องที่มี URL สตรีมส่งมา
        if url:
            station = {
                "name": name,
                "image": image,
                "url": url  # ใส่ rtmp://... หรือ .flv ได้โดยตรงเลย Wiseplay รองรับ
            }
            w3u_structure["stations"].append(station)
            
    # บันทึกไฟล์ออกมาในโฟลเดอร์หลักของโปรเจกต์
    output_filename = "StreamHub.w3u"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(w3u_structure, f, ensure_ascii=False, indent=4)
        
    print(f"✅ บันทึกไฟล์สำเร็จ! ได้รับทั้งหมด {len(w3u_structure['stations'])} ช่อง")

if __name__ == "__main__":
    streams = fetch_rtmp_streams()
    if streams:
        generate_w3u_playlist(streams)
    else:
        print("⚠️ ไม่พบข้อมูลสตรีมที่ดึงมาได้")
