import subprocess
import sys

# Chạy file ngầm không hiện cửa sổ terminal (trên Windows) hoặc tách tiến trình (Linux/Mac)
if sys.platform == "win32":
  # DETACHED_PROCESS hoặc CREATE_NO_WINDOW
  DETACHED_PROCESS = 0x00000008
  subprocess.Popen(
      ["python", "bot.py"], creationflags=DETACHED_PROCESS, close_fds=True
  )
  subprocess.Popen(
      ["python", "ping.py"], creationflags=DETACHED_PROCESS, close_fds=True
  )
else:
  # Trên Linux/macOS
  subprocess.Popen(["python3", "bot.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
  subprocess.Popen(["python3", "ping.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
