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
  print(f"Object id: {info.object_id}, object type: {info.object_type}")

if __name__ == "__main__":
  get_event_loop().run_until_complete(main())
```

### Example - login and post blog
```python3
import projz
from asyncio import get_event_loop
from aiofiles import open as async_open

client = projz.Client()


async def main():
    result = await client.login("your email", "your password")
    print(f"Logged in to account with nickname {result.user_profile.nickname}")
    circle_link_info = await client.get_link_info(input("Circle link: "))
    await client.post_blog(
        "Blog title",
        "Blog content",
        content_rich_format=pzlib2.model.RichFormatBuilder().h1(0, 4).build(),
        cover=await client.upload_file(await async_open("cover-file.png", "rb"), projz.enum.UploadTarget.FOREGROUND),
        background=await client.upload_file(await async_open("bg-file.png", "rb"), projz.enum.UploadTarget.BACKGROUND),
        circle_list=[circle_link_info.object_id]
    )


if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
```
