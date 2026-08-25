import os
import re
import json
import base64
import logging
import threading
import urllib.request
from urllib.error import HTTPError
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Thiết lập logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Cấu hình thông tin Repo GitHub của bạn
GITHUB_REPO = "duonggg-10/MinhThy_GetData"
GITHUB_FILE_PATH = "data.txt"
GITHUB_BRANCH = "main"

# ----------------- HÀM GHI DỮ LIỆU LÊN GITHUB -----------------
def append_to_github(new_text: str):
    """Lấy nội dung cũ trên GitHub, ghép nội dung mới và commit đè lên"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}?ref={GITHUB_BRANCH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Telegram-Bot-App"
    }

    sha = None
    old_content = ""

    # 1. Đọc nội dung file hiện tại trên GitHub (để lấy SHA và nội dung cũ)
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            sha = data.get("sha")
            # GitHub mã hóa nội dung bằng Base64
            encoded_content = data.get("content", "")
            old_content = base64.b64decode(encoded_content).decode('utf-8')
    except HTTPError as e:
        if e.code == 404:
            # File chưa tồn tại trên repo -> sẽ tạo file mới
            old_content = ""
        else:
            raise Exception(f"Lỗi đọc GitHub (Mã {e.code}): {e.read().decode('utf-8')}")

    # 2. Ghép nội dung mới vào cuối file cũ
    updated_content = old_content + new_text
    base64_content = base64.b64encode(updated_content.encode('utf-8')).decode('utf-8')

    # 3. Gửi PUT request để tạo Commit mới lên GitHub
    put_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    payload = {
        "message": "Update data.txt via Telegram Bot",
        "content": base64_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha  # Bắt buộc phải có sha nếu file đã tồn tại

    req_put = urllib.request.Request(
        put_url,
        data=json.dumps(payload).encode('utf-8'),
        headers={**headers, "Content-Type": "application/json"},
        method="PUT"
    )
    with urllib.request.urlopen(req_put) as resp:
        if resp.status not in (200, 201):
            raise Exception(f"Không thể commit lên GitHub. Mã: {resp.status}")

# ----------------- TẠO WEB SERVER ĐỂ RENDER NHẬN PORT -----------------
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    logging.info(f"Keep-Alive Server is listening on port {port}")
    server.serve_forever()
# ----------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text and "/USER" in text and "/BOT" in text:
        try:
            user_match = re.search(r'/USER\s+(.*?)(?=/BOT|$)', text, re.DOTALL | re.IGNORECASE)
            bot_match = re.search(r'/BOT\s+(.*?)(?=/USER|$)', text, re.DOTALL | re.IGNORECASE)
            
            if user_match and bot_match:
                user_content = user_match.group(1).strip()
                bot_content = bot_match.group(1).strip()
                
                # Tạo đoạn text cần ghi
                entry = f"User: {user_content}\nBot: {bot_content}\n" + ("-" * 30) + "\n"
                
                # Ghi trực tiếp lên GitHub
                append_to_github(entry)
                
                await update.message.reply_text("✅ Đã commit và lưu dữ liệu lên GitHub thành công!")
            else:
                await update.message.reply_text("❌ Lỗi: Cú pháp không hợp lệ. Hãy kiểm tra lại.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Có lỗi xảy ra khi lưu lên GitHub: {e}")
            logging.error(f"GitHub Error: {e}")

def main():
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN chưa được cài đặt!")
        return
    if not GITHUB_TOKEN:
        logging.error("❌ GITHUB_TOKEN chưa được cài đặt!")
        return

    # Chạy Web server ngầm
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # Khởi tạo Telegram Bot
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, handle_message))
    
    logging.info("Bot đang chạy Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
