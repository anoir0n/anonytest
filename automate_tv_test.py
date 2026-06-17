import json
import urllib.request

JSON_URL = "https://tv.laoid.net/world-cup/config.json"
OUTPUT_W3U_FILE = "tv-test_auto.w3u"
OUTPUT_M3U_FILE = "tv-test_auto.m3u8"  # เปลี่ยนนามสกุลเป็น .m3u8 ตามต้องการ

# ใช้ค่า User-Agent เดิมของ LaoTV
USER_AGENT = "LaoTV/1.0 (Linux; Android 12; LA; com.laotv.app) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

# สุ่มหรือระบุ IP ของประเทศลาว (Lao IP Address) เพื่อหลอกระบบ Geo-block
LAO_IP = "115.84.112.1" 

def fetch_and_convert():
    try:
        print(f"กำลังดึงข้อมูลจาก {JSON_URL}...")
        req = urllib.request.Request(JSON_URL, headers={'User-Agent': USER_AGENT})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
        
        w3u_data = {
          "name": "TV-Test Automated Playlist (Lao IP Proxy)",
          "author": "TV-Test Auto Generator",
          "stations": []
        }
        
        # จัดเตรียมรูปแบบ M3U8 มาตรฐาน
        m3u_lines = ["#EXTM3U"]
        
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ['channels', 'stations', 'data', 'links']:
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            if not items: 
                for val in data.values():
                    if isinstance(val, list):
                        items = val
                        break

        if not items:
            print("ไม่พบข้อมูลแบบรายการ")
            return

        for item in items:
            if not isinstance(item, dict):
                continue
            channel_name = item.get('ChannelName', item.get('name', item.get('title', 'Unknown Channel')))
            stream_url = ""
            links = item.get('Links')
            
            if isinstance(links, list) and len(links) > 0:
                stream_url = links[0].get('Url', '')
            else:
                stream_url = item.get('Url', item.get('url', item.get('link', '')))
            
            if stream_url:
                # --- จัดการข้อมูลสำหรับ .w3u (Wiseplay) ---
                station = {
                    "name": channel_name,
                    "url": stream_url,
                    "httpHeaders": {
                        "User-Agent": USER_AGENT,
                        "Referer": "http://localhost/",
                        "Origin": "http://localhost/",
                        "X-Forwarded-For": LAO_IP,
                        "X-Real-IP": LAO_IP
                    }
                }
                w3u_data["stations"].append(station)

                # --- จัดการข้อมูลสำหรับ .m3u8 (IPTV ทั่วไป) ---
                # ใส่รายละเอียด Header แบบฝังในบรรทัดเพื่อความเข้ากันได้สูงกับแอป เช่น OTT Navigator, Perfect Player, TiviMate
                m3u_lines.append(f'#EXTINF:-1 tvg-name="{channel_name}",{channel_name}')
                
                # มาตรฐาน VLC / IPTV Player options
                m3u_lines.append(f'#EXTVLCOPT:http-user-agent={USER_AGENT}')
                m3u_lines.append('#EXTVLCOPT:http-referrer=http://localhost/')
                m3u_lines.append('#EXTVLCOPT:http-origin=http://localhost/')
                m3u_lines.append(f'#EXTVLCOPT:http-header=X-Forwarded-For: {LAO_IP}')
                m3u_lines.append(f'#EXTVLCOPT:http-header=X-Real-IP: {LAO_IP}')
                
                # เพิ่มรูปแบบจัดส่ง Header ท้าย URL (ช่วยให้บางแอปที่ไม่อ่าน #EXTVLCOPT ทำงานได้)
                # โดยเฉพาะแอปยุคใหม่จะชอบโครงสร้างแบบ URL|User-Agent=...
                appended_url = f"{stream_url}|User-Agent={USER_AGENT}&X-Forwarded-For={LAO_IP}&X-Real-IP={LAO_IP}&Referer=http://localhost/"
                m3u_lines.append(appended_url)
        
        # บันทึกไฟล์ .w3u
        with open(OUTPUT_W3U_FILE, 'w', encoding='utf-8') as f:
            json.dump(w3u_data, f, ensure_ascii=False, indent=2)
            
        # บันทึกไฟล์ .m3u8
        with open(OUTPUT_M3U_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(m3u_lines))
            
        print(f"สร้างไฟล์สำเร็จ! ทั้งแบบ .w3u และ .m3u8 รวม {len(w3u_data['stations'])} ช่อง")

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    fetch_and_convert()
