# ===============================================================================
# FILE: bot/main.py
# ==============================================================================
# A minimal Python script to confirm the bot container is running.
# This does NOT connect to Discord. It simply runs in a loop and prints to the logs.
import time

print("Bot container has started.")
print("This is a placeholder script to test the infrastructure.")
print(f"It will print a message every 30 seconds.")
print("-" * 20)

# You can check environment variables are loading correctly (optional)
# api_url = os.getenv("API_URL")
# print(f"API_URL from environment: {api_url}")

loop_count = 0
while True:
    loop_count += 1
    print(f"Bot is alive. Loop #{loop_count}")
    time.sleep(30)
