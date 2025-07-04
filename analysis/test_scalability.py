import asyncio
import aiohttp
from collections import Counter
import matplotlib.pyplot as plt
import requests

NUM_REQUESTS = 10000
TEST_URL = "http://localhost:5000/home"
ADD_URL = "http://localhost:5000/add"
RM_URL = "http://localhost:5000/rm"

# Set a limit for concurrent requests
CONCURRENCY_LIMIT = 100

async def fetch(session, counter, sem):
    async with sem:
        for _ in range(3):  # Retry up to 3 times
            try:
                async with session.get(TEST_URL) as resp:
                    data = await resp.json()
                    server = data["message"].split(":")[-1].strip()
                    counter[server] += 1
                    break
            except:
                await asyncio.sleep(0.05)  # backoff and retry

async def run_test(n_servers):
    counter = Counter()

    # Reset and set exact N servers
    requests.delete(RM_URL, json={"n": 10, "hostnames": []})
    requests.post(ADD_URL, json={"n": n_servers, "hostnames": [f"server{i}" for i in range(1, n_servers + 1)]})

    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, counter, sem) for _ in range(NUM_REQUESTS)]
        await asyncio.gather(*tasks)

    avg = sum(counter.values()) / len(counter)
    print(f"N={n_servers}, Avg={avg:.2f}, Server Counts: {dict(counter)}")
    return n_servers, avg

async def main():
    results = []
    for n in range(2, 7):
        print(f"\n🔁 Testing with N={n} servers...")
        n_val, avg = await run_test(n)
        results.append((n_val, avg))

    # Plot results
    x_vals = [r[0] for r in results]
    y_vals = [r[1] for r in results]

    plt.plot(x_vals, y_vals, marker='o')
    plt.title("Average Load per Server vs Number of Servers")
    plt.xlabel("Number of Servers (N)")
    plt.ylabel("Average Requests per Server")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())
