import socket
import webbrowser
import logging
from time import sleep

logger = logging.getLogger(__name__)

def find_free_port(start_port):
    port = start_port
    while port < start_port + 100:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result != 0:
                return port
            else:
                port += 1
    return start_port


def open_browser(port):
    sleep(1.5)
    url = f"http://127.0.0.1:{port}"
    logger.info(f"🌍 Opening browser at {url}...")
    try:
        browser = webbrowser.get('chrome')
    except webbrowser.Error:
        try:
            browser = webbrowser.get(r'open -a /Applications/Google\ Chrome.app %s')
        except webbrowser.Error:
            browser = webbrowser
    browser.open(url)
