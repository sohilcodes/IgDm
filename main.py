import os
import time
import random
import json
from instagrapi import Client

# ===== ENV =====
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
PROXY = os.getenv("IG_PROXY")

cl = Client()

# ===== PROXY =====
if PROXY:
    cl.set_proxy(PROXY)
    print("🌐 Proxy Enabled")

# ===== SESSION =====
if os.path.exists("session.json"):
    cl.load_settings("session.json")

cl.login(USERNAME, PASSWORD)
cl.dump_settings("session.json")

print("✅ Login Successful")

# ===== TARGET (India / UP Audience) =====
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

Agar aap apna page grow karna chahte ho toh:
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

# ===== SAFE CALL =====
def safe_call(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("⚠️ Error:", e)
            sleep_time = random.randint(300, 600)
            print(f"⏸️ Sleeping {sleep_time}s (anti-429)")
            time.sleep(sleep_time)

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
            followers = safe_call(cl.user_followers, uid, amount=5)

            for user in followers.values():
                send_dm(user)

        except Exception as e:
            print("Target Error:", e)

# ===== MAIN LOOP =====
while True:
    process_targets()
    print("🛑 Cycle Done → Sleep 20 min")
    time.sleep(1200)
