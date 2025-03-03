# ProjZ
A simple asynchronous library for interaction with Project Z

# ❗ Outdated. I am not responsible for the functionality of the library at the moment. If the API hasn't changed much after the rebranding, this should work. 

## Installation
 ```commandline
 pip install projz.py
 ```

### Example - login and get object id from link
```python3
import projz
from asyncio import get_event_loop

client = projz.Client()


async def main():
    result = await client.login_email("your email", "your password")
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
    result = await client.login_email("your email", "your password")
    print(f"Logged in to account with nickname {result.user_profile.nickname}")
    circle_link_info = await client.get_link_info(input("Circle link: "))
    await client.post_blog(
        "Blog title",
        "Blog content",
        content_rich_format=projz.RichFormatBuilder().h1(0, 4).build(),
        cover=await client.upload_file(await async_open("cover-file.png", "rb"), projz.EUploadTarget.FOREGROUND),
        background=await client.upload_file(await async_open("bg-file.png", "rb"), projz.EUploadTarget.BACKGROUND),
        circle_list=[circle_link_info.object_id]
    )


if __name__ == "__main__":
    get_event_loop().run_until_complete(main())
```

### Example - receive messages
```python3
import projz
from asyncio import get_event_loop

client = projz.Client()


@client.on_message()
async def handle_echo(message: projz.ChatMessage):
    if message.content is not None:
        await client.send_message(message.thread_id, content=message.content)


# You can specify the command prefix in the arguments of the decorator or Client. 
# The slash / is set by default.


@client.on_command("off")  # = on_message("/off")
async def handle_off(message: projz.ChatMessage):
    await client.change_chat_online_status(message.thread_id, is_online=False)


async def main():
    await client.login_email("your email", "your password")
    print("Waiting for the messages...")


if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
```
## Addition: Using CLI functions
### Print available functions
```commandline
python -m projz list-actions
```
### Login to an account with email and print info about it
```commandline
python -m projz login --auth email --login yourlogin --password yourpassword
```
### Or with phone number
```commandline
python -m projz login --auth phone --login yourlogin --password yourpassword
```
### Get information about the link
```commandline
python -m projz link-info --auth email --login yourlogin --password yourpassword --info yourlink
```
### Send messages to the chat
```commandline
python -m projz send-message --auth email --login yourlogin --password yourpassword --thread chatlink --repeat 150
```
### Join to the circle
```commandline
python -m projz join-circle --auth email --login yourlogin --password yourpassword --circle circlelink
```
### Leave from the circle
```commandline
python -m projz leave-circle --auth email --login yourlogin --password yourpassword --circle circlelink
```
### Listen for the chat messages
```commandline
python -m projz listen --auth email --login yourlogin --password yourpassword
```
