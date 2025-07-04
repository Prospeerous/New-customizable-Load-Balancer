import asyncio
import aiohttp
from collections import Counter
import matplotlib.pyplot as plt

print("Starting load test...")

URL = "http://localhost:5000/home"
NUM_REQUESTS = 10000

# Dictionary to count server responses
counter = Counter()

async def fetch(session):
    async with session.get(URL) as response:
        try:
            data = await response.json()
            server = data["message"].split(":")[-1].strip()
            # print(f"✅ Response from {server}")
            counter[server] += 1
        except Exception as e:
            print("Error:", e)

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session) for _ in range(NUM_REQUESTS)]
        await asyncio.gather(*tasks)

    # Print and plot results
    print("\nRequest counts per server:")
    for server, count in counter.items():
        print(f"{server}: {count}")

    plt.bar(counter.keys(), counter.values())
    plt.title("Requests Handled per Server (N=3)")
    plt.xlabel("Server")
    plt.ylabel("Number of Requests")
    plt.show()

if __name__ == "__main__":
    asyncio.run(main())
