# ProjZ
A simple asynchronous library for interaction with Project Z

### Example - login and get object id from link
```python3
import projz
from asyncio import get_event_loop

client = projz.Client()


async def main():
  result = await client.login("your email", "your password")
  print(f"Logged in to account with nickname {result.user_profile.nickname}")
  info = await client.get_link_info("link here")
  print(f"Object id: {info.object_id}, object type: {info.object_type}

if __name__ == "__main__":
  get_event_loop().run_until_complete(main())
```
