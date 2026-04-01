import os
import time
import random
from instagrapi import Client

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

cl = Client()

# SESSION LOAD (safe login)
if os.path.exists("session.json"):
    cl.load_settings("session.json")

try:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("session.json")
    print("Login Successful ✅")
except Exception as e:
    print("Login Error:", e)
    exit()

# ===== SETTINGS =====
target = "targetpage"   # yaha target page daal
limit = 20              # daily DM limit

messages = [
"""Hey 👋  
Aapka page dekha 🔥  

Growth chahte ho?  
1k followers = ₹30  
1k likes = ₹12  
1k views = ₹2  

Demo available 👍"""
]

replies = {
    "price": "💰 Prices:\n1k followers = ₹30\n1k likes = ₹12\n1k views = ₹2\nDemo ₹5–₹10 👍",
    "interested": "🔥 Great! Batao kya chahiye? Followers / Likes / Views?",
    "demo": "👍 Demo available hai sirf ₹5–₹10 me",
    "hi": "Hey 👋 Kaise help kar sakta hoon?"
}

# ===== SEND DM =====
try:
    user_id = cl.user_id_from_username(target)
    followers = cl.user_followers(user_id, amount=limit)

    for user in followers.values():
        try:
            cl.direct_send(random.choice(messages), [user.pk])
            print("Sent:", user.username)

            delay = random.randint(40, 80)
            print(f"Waiting {delay}s")
            time.sleep(delay)

        except Exception as e:
            print("DM Error:", e)

    print("DM Sending Done ✅")

except Exception as e:
    print("Fetch Error:", e)

# ===== AUTO REPLY =====
replied_users = set()

while True:
    try:
        threads = cl.direct_threads(amount=10)

        for thread in threads:
            for msg in thread.messages:
                uid = msg.user_id

                if uid in replied_users:
                    continue

                text = msg.text.lower() if msg.text else ""

                for key in replies:
                    if key in text:
                        cl.direct_send(replies[key], [uid])
                        replied_users.add(uid)
                        print("Replied:", uid)
                        time.sleep(10)
                        break

        time.sleep(20)

    except Exception as e:
        print("Loop Error:", e)
        time.sleep(30)
