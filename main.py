import os
import time
import random
import json
from instagrapi import Client

# ===== ENV =====
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
PROXY = os.getenv("IG_PROXY")  # http://user:pass@ip:port

cl = Client()

# ===== PROXY SET =====
if PROXY:
    cl.set_proxy(PROXY)
    print("🌐 Proxy Enabled")

# ===== SESSION =====
if os.path.exists("session.json"):
    cl.load_settings("session.json")

# ===== SAFE LOGIN =====
try:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("session.json")
    print("✅ Login Successful")
except Exception as e:
    print("❌ Login Error:", e)
    exit()

# ===== WARMUP (VERY IMPORTANT 🔥) =====
def warmup():
    print("🔥 Warmup start...")
    try:
        cl.get_timeline_feed()
        time.sleep(random.randint(5, 10))

        cl.get_reels_tray_feed()
        time.sleep(random.randint(5, 10))

        print("✅ Warmup done")
    except Exception as e:
        print("Warmup Error:", e)

# ===== SAFE REQUEST =====
def safe_call(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("⚠️ Error:", e)
            print("⏸️ Sleeping 10 min (Anti-429)...")
            time.sleep(600)

# ===== STATE (RESUME SYSTEM) =====
STATE_FILE = "state.json"

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {"sent": 0}

# ===== SETTINGS =====
targets = ["targetpage1", "targetpage2"]
daily_limit = 10  # keep low for safety

messages = [
"Hey 👋 Aapka content mast hai 🔥 Growth chahte ho? Followers ₹30/1k, Likes ₹12/1k, Views ₹2/1k. Demo available 👍"
]

# ===== HUMAN BEHAVIOR =====
def human_behavior(user):
    try:
        safe_call(cl.user_info, user.pk)
        time.sleep(random.randint(5, 12))

        if random.random() < 0.4:
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
        print(f"⏳ Sleeping {delay}s")
        time.sleep(delay)

    except Exception as e:
        print("DM Error:", e)

# ===== MAIN PROCESS =====
def process():
    for target in targets:
        print(f"\n🎯 Target: {target}")

        try:
            uid = safe_call(cl.user_id_from_username, target)

            # fetch very small amount (safe)
            followers = safe_call(cl.user_followers, uid, amount=5)

            for user in followers.values():
                send_dm(user)

        except Exception as e:
            print("Target Error:", e)

# ===== MAIN LOOP =====
while True:
    warmup()
    process()

    print("🛑 Cycle complete → Sleeping 20 min")
    time.sleep(1200)
