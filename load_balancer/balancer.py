from flask import Flask, request, jsonify
import os, random, subprocess, threading, time, requests
from consistent_hash import ConsistentHash
import docker

random.seed(42)  # For reproducibility

app = Flask(__name__)

client = docker.DockerClient(base_url='unix://var/run/docker.sock')

replicas = []
N = 3
HASH_RING = ConsistentHash(num_servers=N)

def start_initial_servers():
    for i in range(1, N + 1):
        name = f"server{i}"
        run_container(name)
        replicas.append(name)

def run_container(name):
    client.containers.run(
        "simple-server",
        detach=True,
        name=name,
        environment={"SERVER_ID": name},
        ports={},
        network="net1",
        hostname=name
    )

@app.route('/rep', methods=['GET'])
def get_replicas():
    return jsonify({
        "message": {
            "N": len(replicas),
            "replicas": replicas
        },
        "status": "successful"
    }), 200

@app.route('/add', methods=['POST'])
def add_servers():
    data = request.json
    count = data.get("n")
    names = data.get("hostnames", [])
    if len(names) > count:
        return jsonify({
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }), 400

    for i in range(count):
        name = names[i] if i < len(names) else f"S{random.randint(1000,9999)}"
        run_container(name)
        replicas.append(name)
    return get_replicas()

@app.route('/rm', methods=['DELETE'])
def remove_servers():
    data = request.json
    count = data.get("n")
    names = data.get("hostnames", [])
    if len(names) > count:
        return jsonify({
            "message": "<Error> Length of hostname list is more than removable instances",
            "status": "failure"
        }), 400

    to_remove = names + random.sample([r for r in replicas if r not in names], count - len(names))
    for name in to_remove:
        try:
            container = client.containers.get(name)
            container.stop()
            container.remove()
            replicas.remove(name)
        except:
            pass
    return get_replicas()

@app.route('/<path:endpoint>', methods=['GET'])
def route_request(endpoint):
    req_id = random.randint(100000, 999999)
    try:
        server = HASH_RING.get_server_for_request(req_id)
        url = f"http://{server}:5000/{endpoint}"
        r = requests.get(url)
        return jsonify(r.json()), 200
    except Exception as e:
        return jsonify({
            "message": f"<Error> '{endpoint}' endpoint does not exist in server replicas",
            "status": "failure"
        }), 400

# 🧠 Background thread to monitor heartbeat of replicas
def monitor_heartbeats():
    while True:
        time.sleep(5)
        failed = []
        for server in replicas.copy():
            try:
                res = requests.get(f"http://{server}:5000/heartbeat", timeout=2)
                if res.status_code != 200:
                    raise Exception("Heartbeat failed")
            except:
                print(f"❌ Heartbeat failed for {server}")
                failed.append(server)

        for server in failed:
            # Remove failed container
            try:
                container = client.containers.get(server)
                container.remove(force=True)
            except:
                pass
            replicas.remove(server)

            # Spawn new one
            existing_ids = [int(r.replace("server", "")) for r in replicas if r.startswith("server") and r.replace("server", "").isdigit()]
            next_id = max(existing_ids, default=3) + 1
            new_name = f"server{next_id}"
            run_container(new_name)
            replicas.append(new_name)
            print(f"✅ Replaced {server} with {new_name}")

# Start heartbeat monitor as background thread
threading.Thread(target=monitor_heartbeats, daemon=True).start()

if __name__ == '__main__':
    start_initial_servers()
    app.run(host='0.0.0.0', port=5000)
