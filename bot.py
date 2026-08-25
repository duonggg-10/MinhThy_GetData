import os
import re
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Thiết lập logging chung cho ứng dụng
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ⚠️ QUAN TRỌNG: Tắt log INFO của thư viện httpx để KHÔNG in Token Bot ra màn hình log
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FILE_NAME = "data.txt"

# ----------------- TẠO WEB SERVER ĐỂ RENDER NHẬN PORT -----------------
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Phản hồi khi tool keep_alive hoặc Render kiểm tra
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        # Tắt in log rác mỗi lần ping để log server luôn sạch đẹp
        return

def run_dummy_server():
    # Render sẽ cấp biến môi trường PORT (mặc định nếu chạy local sẽ là 8080)
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    logging.info(f"Keep-Alive Server is listening on port {port}")
    server.serve_forever()
# ----------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lấy nội dung tin nhắn gửi đến
    text = update.message.text
    
    # Kiểm tra xem tin nhắn có chứa cả /USER và /BOT hay không
    if text and "/USER" in text and "/BOT" in text:
        try:
            # Dùng RegEx để bóc tách nội dung nhiều dòng
            user_match = re.search(r'/USER\s+(.*?)(?=/BOT|$)', text, re.DOTALL | re.IGNORECASE)
            bot_match = re.search(r'/BOT\s+(.*?)(?=/USER|$)', text, re.DOTALL | re.IGNORECASE)
            
            if user_match and bot_match:
                # Lấy nội dung và xóa khoảng trắng thừa ở 2 đầu
                user_content = user_match.group(1).strip()
                bot_content = bot_match.group(1).strip()
                
                # Mở file và ghi tiếp vào cuối file (mode "a")
                with open(FILE_NAME, "a", encoding="utf-8") as f:
                    f.write(f"User: {user_content}\n")
                    f.write(f"Bot: {bot_content}\n")
                    f.write("-" * 30 + "\n")
                
                # Phản hồi lại người dùng
                await update.message.reply_text("✅ Đã lưu dữ liệu thành công!")
            else:
                await update.message.reply_text("❌ Lỗi: Cú pháp không hợp lệ. Hãy kiểm tra lại.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Có lỗi xảy ra khi ghi file: {e}")
            logging.error(f"File writing error: {e}")

def main():
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN chưa được cài đặt trong Environment Variables / file .env!")
        return

    # 1. Chạy Web server ở một luồng riêng để Render quét thấy Port
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()

    # 2. Khởi tạo ứng dụng bot
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Thêm handler nhận text và command
    application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, handle_message))
    
    # 3. Chạy bot liên tục
    logging.info("Bot đang chạy Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
