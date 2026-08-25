import re
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

# Thiết lập logging để theo dõi lỗi nếu có
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FILE_NAME = "data.txt"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lấy nội dung tin nhắn gửi đến
    text = update.message.text
    
    # Kiểm tra xem tin nhắn có chứa cả /USER và /BOT hay không
    if "/USER" in text and "/BOT" in text:
        try:
            # Dùng RegEx để bóc tách nội dung
            # re.DOTALL giúp dấu chấm (.) khớp với cả ký tự xuống dòng (\n)
            # Dù người dùng nhập /USER trước hay /BOT trước thì code vẫn hiểu được
            user_match = re.search(r'/USER\s+(.*?)(?=/BOT|$)', text, re.DOTALL | re.IGNORECASE)
            bot_match = re.search(r'/BOT\s+(.*?)(?=/USER|$)', text, re.DOTALL | re.IGNORECASE)
            
            if user_match and bot_match:
                # Lấy nội dung và xóa khoảng trắng/dấu xuống dòng thừa ở 2 đầu
                user_content = user_match.group(1).strip()
                bot_content = bot_match.group(1).strip()
                
                # Mở file và ghi thêm vào dòng cuối (mode "a" - append)
                # encoding="utf-8" cực kỳ quan trọng để Windows không bị lỗi tiếng Việt
                with open(FILE_NAME, "a", encoding="utf-8") as f:
                    f.write(f"User: {user_content}\n")
                    f.write(f"Bot: {bot_content}\n")
                    f.write("-" * 30 + "\n") # Dòng kẻ phân cách cho dễ nhìn
                
                # Phản hồi lại người dùng
                await update.message.reply_text("✅ Đã lưu dữ liệu thành công!")
            else:
                await update.message.reply_text("❌ Lỗi: Cú pháp không hợp lệ. Hãy kiểm tra lại.")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Có lỗi xảy ra khi ghi file: {e}")
            logging.error(f"File writing error: {e}")
    else:
        # Nếu gửi tin nhắn bình thường (không có /USER và /BOT), bot sẽ bỏ qua
        pass

def main():
    # Khởi tạo ứng dụng bot
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Thêm handler để bắt tất cả các tin nhắn văn bản (bao gồm cả command)
    # filters.TEXT | filters.COMMAND đảm bảo tin nhắn bắt đầu bằng / vẫn được nhận
    application.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, handle_message))
    
    # Chạy bot liên tục
    print("Bot đang chạy... Nhấn Ctrl+C để dừng.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()