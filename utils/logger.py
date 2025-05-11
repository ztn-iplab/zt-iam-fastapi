import logging

# ==========================
# 🔐 ZTN_MoMo Logging Setup
# ==========================
ztn_log_path = '/var/log/ztn_momo.log'

app_logger = logging.getLogger('ztn_momo')
app_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(ztn_log_path)
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s')
file_handler.setFormatter(formatter)
app_logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
app_logger.addHandler(console_handler)

# Test log to verify setup
app_logger.info("✅ Logging to ztn_momo.log initialized.")
app_logger.info("[ZTN_MOMO_TEST] Confirming visibility in Wazuh dashboard.")

