# ===============================================================================
# bot/main.py
# ==============================================================================
import time

print("Bot container has started.")
print("This is a placeholder script to test the infrastructure.")
print(f"It will print a message every 30 seconds.")
print("-" * 20)

loop_count = 0
while True:
    loop_count += 1
    print(f"Bot is alive. Loop #{loop_count}")
    time.sleep(30)
