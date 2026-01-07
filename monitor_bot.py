import time

def monitor_log():
    while True:
        with open("data/learning_database.json", "r") as f:
            print(f.read())
        time.sleep(10)
