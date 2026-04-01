import os
import time
import random
import json
from instagrapi import Client

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

cl = Client()

# ===== SESSION =====
if os.path.exists("session.json"):
    cl.load_settings("session.json")

cl.login(USERNAME, PASSWORD)
cl.dump_settings("session.json")

print("✅ Login Successful")

# ===== SETTINGS =====
targets = ["targetpage1", "targetpage2", "targetpage3"]  # rotation
daily_limit = 25

messages = [
"Hey 👋 Aapka content mast hai 🔥 Growth chahte ho? Followers ₹30/1k, Likes ₹12/1k, Views ₹2/1k. Demo available 👍",
"Hey 👋 Main SMM services deta hoon 🚀 Cheap + fast delivery. Interested ho toh batao 👍"
]

replies = {
    "price": "💰 1k followers ₹30\n1k likes ₹12\n1k views ₹2\nDemo ₹5–₹10 👍",
    "interested": "🔥 Batao kya chahiye? Followers / Likes / Views?",
    "demo": "👍 Demo ₹5–₹10 me available",
    "hi": "Hey 👋 Kaise help kar sakta hoon?"
}

# ===== STATE FILE (resume system) =====
STATE_FILE = "state.json"

if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
else:
    state = {"sent": 0, "replied": []}

# ===== SAFE REQUEST =====
def safe_call(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("⚠️ Error:", e)
            print("⏸️ Auto pause 5 min (anti-429)...")
            time.sleep(300)

# ===== HUMAN BEHAVIOR =====
def human_activity(user):
    try:
        safe_call(cl.user_info, user.pk)
        time.sleep(random.randint(3, 7))

        # kabhi kabhi like bhi karega
        if random.random() < 0.3:
            medias = safe_call(cl.user_medias, user.pk, amount=1)
            if medias:
                safe_call(cl.media_like, medias[0].id)
                print("❤️ Liked post")

        time.sleep(random.randint(5, 10))
    except:
        pass

# ===== DM FUNCTION =====
def send_dm(user):
    if state["sent"] >= daily_limit:
        print("🚫 Daily limit reached")
        return

    try:
        human_activity(user)

        msg = random.choice(messages)
        safe_call(cl.direct_send, msg, [user.pk])

        state["sent"] += 1
        print(f"📩 Sent to {user.username} ({state['sent']})")

        # save state
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

        delay = random.randint(80, 160)
        print(f"⏳ Sleeping {delay}s...")
        time.sleep(delay)

    except Exception as e:
        print("DM Error:", e)

# ===== TARGET ROTATION =====
def process_targets():
    for target in targets:
        print(f"\n🎯 Target: {target}")

        try:
            uid = safe_call(cl.user_id_from_username, target)
            followers = safe_call(cl.user_followers, uid, amount=10)

            for user in followers.values():
                send_dm(user)

        except Exception as e:
            print("Target Error:", e)

# ===== AUTO REPLY =====
def auto_reply():
    while True:
        try:
            threads = safe_call(cl.direct_threads, amount=10)

            for thread in threads:
                for msg in thread.messages:
                    uid = msg.user_id

                    if uid in state["replied"]:
                        continue

                    text = msg.text.lower() if msg.text else ""

                    for key in replies:
                        if key in text:
                            safe_call(cl.direct_send, replies[key], [uid])
                            state["replied"].append(uid)

                            print(f"🤖 Replied to {uid}")

                            # save state
                            with open(STATE_FILE, "w") as f:
                                json.dump(state, f)

                            time.sleep(10)
                            break

            time.sleep(25)

        except Exception as e:
            print("Reply Error:", e)
            time.sleep(120)

# ===== MAIN =====
while True:
    process_targets()

    print("🛑 Cycle complete → Taking long break (15 min)")
    time.sleep(900)

    auto_reply()
