import asyncio
from db.mongodb import get_database

async def show_users():
    try:
        db = get_database()
        users = await db.users.find().to_list(length=10)
        print("Available users:")
        for user in users:
            print(f"Email: {user.get('email')}, ID: {user.get('_id')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(show_users())