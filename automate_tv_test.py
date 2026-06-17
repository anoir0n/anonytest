import json
import urllib.request

JSON_URL = "https://tv.laoid.net/world-cup/config.json"
OUTPUT_W3U_FILE = "tv-test_auto.w3u"
OUTPUT_M3U_FILE = "tv-test_auto.m3u8"  # แก้ไขจาก .m3u เป็น .m3u8 เรียบร้อยครับ

# ใช้ค่า User-Agent เดิมของ LaoTV เพื่อให้ระบบปลายทางไม่บล็อกการเล่นสตรีม
USER_AGENT = "LaoTV/1.0 (Linux; Android 12; LA; com.laotv.app) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

# IP ของประเทศลาว (Lao IP Address) เพื่อหลอกระบบ Geo-block ให้เสมือนดูอยู่ในลาว
LAO_IP = "115.84.112.1" 

# เปลี่ยน Referer และ Origin เป็น URL จริงตามที่กำหนด
REFERER_URL = "https://tv.laoid.net/world-cup"

def fetch_and_convert():
    try:
        print(f"กำลังดึงข้อมูลจาก {JSON_URL}...")
        req = urllib.request.Request(JSON_URL, headers={'User-Agent': USER_AGENT})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
        
        # เตรียมโครงสร้างสำหรับ .w3u (Wiseplay)
        w3u_data = {
          "name": "TV-Test Automated Playlist (Lao IP Proxy)",
          "author": "TV-Test Auto Generator",
          "stations": []
        }
        
        # เตรียมโครงสร้างสำหรับ .m3u8 (IPTV ทั่วไป)
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
                # --- จัดการข้อมูลสำหรับ .w3u ---
                station = {
                    "name": channel_name,
                    "url": stream_url,
                    "httpHeaders": {
                        "User-Agent": USER_AGENT,
                        "Referer": REFERER_URL,
                        "Origin": REFERER_URL,
                        "X-Forwarded-For": LAO_IP,
                        "X-Real-IP": LAO_IP
                    }
                }
                w3u_data["stations"].append(station)

                # --- จัดการข้อมูลสำหรับ .m3u8 ---
                m3u_lines.append(f'#EXTINF:-1 tvg-name="{channel_name}",{channel_name}')
                
                # แนบ Option Header สำหรับเครื่องเล่นที่รองรับมาตรฐาน #EXTVLCOPT (เช่น VLC, Perfect Player)
                m3u_lines.append(f'#EXTVLCOPT:http-user-agent={USER_AGENT}')
                m3u_lines.append(f'#EXTVLCOPT:http-referrer={REFERER_URL}')
                m3u_lines.append(f'#EXTVLCOPT:http-origin={REFERER_URL}')
                m3u_lines.append(f'#EXTVLCOPT:http-header=X-Forwarded-For: {LAO_IP}')
                m3u_lines.append(f'#EXTVLCOPT:http-header=X-Real-IP: {LAO_IP}')
                
                # แนบ Option Header ท้าย URL สำหรับเครื่องเล่นรุ่นใหม่ (เช่น TiviMate, OTT Navigator)
                appended_url = f"{stream_url}|User-Agent={USER_AGENT}&X-Forwarded-For={LAO_IP}&X-Real-IP={LAO_IP}&Referer={REFERER_URL}"
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
