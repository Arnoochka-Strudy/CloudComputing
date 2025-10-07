import asyncpg
import asyncio
import json
from datetime import datetime

async def connect_with_retry(config, retries=3, delay=3):
    for i in range(retries):
        try:
            conn = await asyncpg.connect(
                host=config['host'],
                port=config['port'],
                database=config['name'],
                user=config['user'],
                password=config['pass']
            )
            print("Connected to database")
            return conn
        except Exception as e:
            print(f"Retry {i+1}/{retries}: {e}")
            await asyncio.sleep(delay)
    raise RuntimeError("Could not connect to database")

async def view_logs():
    with open("config.json") as f:
        config = json.load(f)

    conn = await connect_with_retry(config)

    while True:
        rows = await conn.fetch("SELECT * FROM tgdb_log ORDER BY datetime DESC LIMIT 100;")
        
        print("\n" + "="*80)
        print(f"Last {len(rows)} log entries ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        print("="*80)

        for row in rows:
            dt = row['datetime'].strftime("%Y-%m-%d %H:%M:%S")
            print(
                f"ID: {row['id']:>3} | "
                f"Time: {dt} | "
                f"User: {row['user_id']} ({row['username']}) | "
                f"Action: {row['action']}\n"
                f"Message: {row['message']}\n"
                + "-"*80
            )

        await asyncio.sleep(5)
        print("Sleeping 5 seconds...\n")

if __name__ == "__main__":
    asyncio.run(view_logs())
