import os
import time
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime

FILE_NAME = "url.txt"
INTERVAL_SECONDS = 60  # Chu kỳ 60 giây (1 phút)

def read_target_url():
    """Đọc URL từ file, tự động thêm https:// nếu thiếu"""
    if not os.path.exists(FILE_NAME):
        return None
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            url = f.read().strip()
            if not url:
                return None
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            return url
    except Exception:
        return None

def ping_server():
    print("=" * 55)
    print("🚀 KEEP-ALIVE SCRIPT ĐÃ KHỞI ĐỘNG (Ping mỗi 60 giây)")
    print("⚠️  Nhấn Ctrl+C bất kỳ lúc nào để dừng.")
    print("=" * 55)

    while True:
        url = read_target_url()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not url:
            print(f"[{now}] ❌ Không tìm thấy hoặc file '{FILE_NAME}' đang trống! Đợi 1 phút...")
        else:
            try:
                # Tạo request với User-Agent chuẩn
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Render-KeepAlive/2.0'}
                )
                
                # Gửi GET request tới Render với timeout 15 giây
                with urllib.request.urlopen(req, timeout=15) as response:
                    # Đọc nội dung phản hồi từ Web server ngầm trong bot.py
                    body = response.read().decode('utf-8', errors='ignore').strip()
                    print(f"[{now}] ✅ Ping thành công (Mã {response.status}) -> Server: \"{body}\"")
                    
            except HTTPError as e:
                # Máy chủ đã nhận được ping nhưng báo mã trạng thái khác 200
                print(f"[{now}] ⚠️ Đã ping. Máy chủ phản hồi mã lỗi: {e.code}")
            except URLError as e:
                # Lỗi rớt mạng phía máy bạn hoặc mạng yếu
                print(f"[{now}] ❌ Lỗi kết nối mạng: {e.reason}")
            except Exception as e:
                # Các lỗi ngoại lệ khác
                print(f"[{now}] ❌ Lỗi không xác định: {e}")

        # Tạm nghỉ 60 giây trước khi ping lần tiếp theo
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    ping_server()
