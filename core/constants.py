import os
import sys

APP_NAME = "Pygon"
APP_VERSION = "2.0.0"

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BIN_DIR = os.path.join(BASE_DIR, "bin")
WWW_DIR = os.path.join(BASE_DIR, "www")
VHOST_CONF_DIR = os.path.join(BIN_DIR, "apache", "conf", "vhosts")

# Ensure directories exist
for d in [BIN_DIR, WWW_DIR, VHOST_CONF_DIR]:
    os.makedirs(d, exist_ok=True)
