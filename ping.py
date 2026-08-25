import os
import time
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime

FILE_NAME = "url.txt"

def get_url():
    # Kiểm tra xem file url.txt có tồn tại không
    if not os.path.exists(FILE_NAME):
        print(f"❌ Lỗi: Không tìm thấy file '{FILE_NAME}'. Vui lòng tạo file và nhập URL vào.")
        return None
    
    # Đọc file và loại bỏ khoảng trắng/xuống dòng thừa
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        url = f.read().strip()
        
    if not url:
        print(f"❌ Lỗi: File '{FILE_NAME}' trống. Vui lòng nhập URL vào file.")
        return None
        
    # Tự động thêm https:// nếu bạn quên nhập
    if not url.startswith("http"):
        url = "https://" + url
        
    return url

def keep_alive():
    url = get_url()
    if not url:
        return
        
    print(f"🚀 Bắt đầu gửi yêu cầu liên tục tới: {url} (mỗi 60 giây)")
    print("⚠️ Nhấn Ctrl+C để dừng chương trình.\n")
    print("-" * 50)
    
    while True:
        try:
            # Tạo Request với User-Agent giả lập để tránh bị máy chủ chặn
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'KeepAlive-Script/1.0'}
            )
            
            # Gửi GET request. timeout=10s để code không bị kẹt nếu mạng chậm
            urllib.request.urlopen(req, timeout=10)
            
            # In ra thông báo thành công cùng thời gian hiện tại
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] ✅ Đã gửi GET request thành công.")
            
        except HTTPError as e:
            # Máy chủ Render CÓ nhận được yêu cầu nhưng trả về lỗi (VD: 404, 500)
            # Việc này VẪN ĐƯỢC TÍNH là đã ping thành công (máy chủ đã thức)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] ⚠️ Đã ping. Máy chủ trả về mã lỗi: {e.code}")
            
        except URLError as e:
            # Các lỗi liên quan đến đường truyền mạng (VD: rớt mạng, mất mạng, timeout)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] ❌ Lỗi kết nối: {e.reason}")
            
        except Exception as e:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] ❌ Lỗi không xác định: {e}")
            
        # Tạm dừng 60 giây (1 phút) trước khi lặp lại vòng tiếp theo
        time.sleep(60)

if __name__ == "__main__":
    keep_alive()