import os
import logging

log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

ztn_log_path = os.path.abspath(os.path.join(log_dir, 'ztn_momo.log'))

app_logger = logging.getLogger('ztn_momo')
app_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(ztn_log_path)
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
file_handler.setFormatter(formatter)
app_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
app_logger.addHandler(console_handler)

app_logger.info("✅ Logging to ztn_momo.log initialized.")
