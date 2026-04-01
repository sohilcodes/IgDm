import os
import time
import random
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from instagrapi import Client

# ===== ENV =====
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
PROXY = os.getenv("IG_PROXY")

cl = Client()

# ===== PROXY =====
if PROXY:
    try:
        cl.set_proxy(PROXY)
        print("🌐 Proxy Enabled")
    except:
        print("❌ Proxy Error")

# ===== SESSION =====
if os.path.exists("session.json"):
    cl.load_settings("session.json")

# ===== LOGIN =====
try:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("session.json")
    print("✅ Login Successful")
except Exception as e:
    print("❌ Login Error:", e)
    exit()

# ===== TARGET (REAL PAGES) =====
targets = [
    "indianreels",
    "contentcreatorindia",
    "hindimemes",
    "startupindia",
    "reelsindia",
    "lucknowcity",
    "kanpurdiaries",
    "delhi_memes"
]

daily_limit = 10

messages = [
"""Hey 👋  
Aapka content mast hai 🔥  

Agar growth chahte ho:
1k followers = ₹30  
1k likes = ₹12  
1k views = ₹2  

Demo available 👍"""
]

# ===== STATE =====
STATE_FILE = "state.json"

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {"sent": 0}

# ===== SAFE CALL (ANTI-429) =====
def safe_call(func, *args, **kwargs):
    retries = 0
    while retries < 5:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("⚠️ Error:", e)
            retries += 1
            sleep_time = random.randint(300, 600)
            print(f"⏸️ Sleeping {sleep_time}s (anti-429)")
            time.sleep(sleep_time)
    return None

# ===== HUMAN BEHAVIOR =====
def human_behavior(user):
    try:
        safe_call(cl.user_info, user.pk)
        time.sleep(random.randint(5, 10))

        if random.random() < 0.3:
            medias = safe_call(cl.user_medias, user.pk, amount=1)
            if medias:
                safe_call(cl.media_like, medias[0].id)
                print("❤️ Liked")

        time.sleep(random.randint(5, 10))
    except:
        pass

# ===== SEND DM =====
def send_dm(user):
    if state["sent"] >= daily_limit:
        print("🚫 Daily limit reached")
        return

    try:
        human_behavior(user)

        safe_call(cl.direct_send, random.choice(messages), [user.pk])

        state["sent"] += 1
        print(f"📩 Sent to {user.username} ({state['sent']})")

        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

        delay = random.randint(120, 240)
        print(f"⏳ Sleep {delay}s")
        time.sleep(delay)

    except Exception as e:
        print("DM Error:", e)

# ===== PROCESS TARGET =====
def process_targets():
    for target in targets:
        print(f"\n🎯 Target: {target}")

        try:
            uid = safe_call(cl.user_id_from_username, target)
            if not uid:
                continue

            followers = safe_call(cl.user_followers, uid, amount=5)

            if not followers:
                continue

            for user in followers.values():
                send_dm(user)

        except Exception as e:
            print("Target Error:", e)

# ===== BOT LOOP =====
def run_bot():
    while True:
        process_targets()
        print("🛑 Cycle Done → Sleep 20 min")
        time.sleep(1200)

# ===== SERVER (RENDER FIX) =====
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot Running ✅")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"🌐 Server running on port {port}")
    server.serve_forever()

# ===== START =====
threading.Thread(target=run_bot).start()
run_server()
