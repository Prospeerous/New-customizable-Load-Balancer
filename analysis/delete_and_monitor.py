import requests
import time

RM_URL = "http://localhost:5000/rm"
REP_URL = "http://localhost:5000/rep"

SERVER_TO_DELETE = "server2"  # 🔁 Change this to any server name like 'server3'

def delete_server(server_name):
    print(f"🧨 Requesting deletion of {server_name}...")

    res = requests.delete(RM_URL, json={
        "n": 1,
        "hostnames": [server_name]
    })

    if res.status_code != 200:
        print("❌ Server deletion failed.")
        print(res.text)
        return False

    print("✅ Server deletion successful.")
    return True

def monitor_replacement(original_server):
    print("🔍 Waiting for replacement...")

    known_replicas = set()
    while True:
        try:
            res = requests.get(REP_URL)
            data = res.json()
            replicas = data["message"]["replicas"]
            current_set = set(replicas)

            # Show progress
            if current_set != known_replicas:
                known_replicas = current_set
                print(f"👀 Current replicas: {replicas}")

            # Check if a new server has appeared
            numeric_ids = [int(r.replace("server", "")) for r in replicas if r.startswith("server") and r.replace("server", "").isdigit()]
            if len(numeric_ids) > 0 and f"{original_server}" not in replicas:
                max_id = max(numeric_ids)
                if f"server{max_id}" not in replicas:
                    continue
                if f"server{max_id}" != original_server and len(replicas) == 3:
                    print(f"✅ Replacement detected: {f'server{max_id}'}")
                    break

        except Exception as e:
            print("⚠️ Error polling /rep:", str(e))
        time.sleep(2)

def main():
    if delete_server(SERVER_TO_DELETE):
        monitor_replacement(SERVER_TO_DELETE)

if __name__ == "__main__":
    main()
