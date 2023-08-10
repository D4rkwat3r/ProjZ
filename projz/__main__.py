from argparse import ArgumentParser
from asyncio import get_event_loop
from asyncio import create_task
from asyncio import gather
from inspect import iscoroutinefunction
from sys import exit as sys_exit
from aiofiles import open as async_open
from os import remove
from . import *

parser = ArgumentParser(description="ProjZ.py library command line interface")
parser.add_argument("action", type=str, help="The action to be performed. "
                                             "You can view the list of possible actions by "
                                             "setting the value \"list-actions\"")
parser.add_argument("--login", type=str, dest="login", help="Email/Phone number of the account")
parser.add_argument("--password", type=str, dest="password", help="Password of the account")
parser.add_argument("--auth", type=str, dest="auth_type", help="Auth method: email or phone")
parser.add_argument("--link", type=str, dest="link", help="Link to the object to get information about")
parser.add_argument("--thread", type=str, dest="thread", help="Link to the chat to send message")
parser.add_argument("--message", type=str, dest="message", help="Text of the message to send")
parser.add_argument("--repeat", type=int, dest="repeat", help="The number of messages sent")
parser.add_argument("--circle", type=str, dest="circle", help="Link to the circle to join or leave")
parser.add_argument(
    "-fLH",
    "--flag-logging-http",
    action="store_true",
    dest="flag_http_logging",
    default=False,
    help="If True, the console will display information about the HTTP requests being sent."
)
parser.add_argument(
    "-fLW",
    "--flag-logging-websocket",
    action="store_true",
    dest="flag_ws_logging",
    default=False,
    help="If True, the console will display information about the websocket messages."
)
parser.add_argument(
    "-fSA",
    "--flag-save-auth",
    action="store_true",
    dest="flag_save_auth",
    default=False,
    help="If True, save the auth data to the cli-auth.json file"
)
cli_args = parser.parse_args()

client = Client(http_logging=cli_args.flag_http_logging, ws_logging=cli_args.flag_ws_logging)


def run_function(func: Callable, *args, **kwargs) -> Any:
    return get_event_loop().run_until_complete(func(*args, **kwargs))\
        if iscoroutinefunction(func) else func(*args, **kwargs)


def print_error(func: Callable):
    def wrapper(*args, **kwargs) -> Any:
        try:
            return run_function(func, *args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")

    return wrapper


def with_auth(get_auth_response: bool):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            saved_auth_data = await read_auth_file()

            result: AuthResult
            if saved_auth_data is not None:
                try:
                    result = await login(secret_str=saved_auth_data.secret)
                except projz.error.ApiException:
                    remove_auth_file()
                    return await wrapper(*args, **kwargs)
            else:
                if cli_args.login is None or cli_args.password is None or cli_args.auth_type is None:
                    print("Error: A file with the valid auth data is not found, "
                          "please specify login, password and auth type.")
                    return
                result = await login(cli_args.auth_type, cli_args.login, cli_args.password)

            if cli_args.flag_save_auth:
                await write_auth_file(result)

            if get_auth_response:
                args = (result,) + args

            return await func(*args, **kwargs)
        return wrapper

    return decorator


def with_args(*needed_cli_args):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            function_args = []
            for arg in needed_cli_args:
                matching_cli_arg = cli_args.__dict__.get(arg)
                if matching_cli_arg is None:
                    print(f"Error: The required argument \"{arg}\" is not specified")
                    return
                function_args.append(matching_cli_arg)
            args += tuple(function_args)

            return run_function(func, *args, **kwargs)
        return wrapper

    return decorator


async def login(
    auth_type_str: Optional[str] = None,
    login_str: Optional[str] = None,
    password_str: Optional[str] = None,
    secret_str: Optional[str] = None
) -> AuthResult:
    if auth_type_str == "email":
        return await client.login_email(login_str, password_str)
    elif auth_type_str == "phone":
        return await client.login_phone_number(login_str, password_str)
    else:
        return await client.login_secret(secret_str)


async def write_auth_file(auth: AuthResult):
    async with async_open("cli-auth.json", "w") as file:
        await file.write(auth.to_json(indent=4))


async def read_auth_file() -> AuthResult:
    try:
        file = await async_open("cli-auth.json", "r")
        data = AuthResult.from_json(await file.read())
        await file.close()
        return data
    except Exception as e:
        return None


def remove_auth_file():
    remove("cli-auth.json")


async def safe_send_chat_message(chat_id: int, message_content: str) -> bool:
    try:
        await client.send_message(chat_id, content=message_content)
    except:
        return False
    return True


def action_list_actions():
    for i, key in enumerate(action_mapping, start=1):
        print(f"{i}. {key} - {action_mapping[key][1]}")


def action_clear_auth():
    remove_auth_file()
    print("[+] Cleared successfully.")


@print_error
@with_auth(get_auth_response=True)
async def action_login(auth: AuthResult):
    print(f"[+] Session ID: {auth.sid}")
    print(f"[+] Refresh token (secret): {auth.secret}")
    print("[+] Account:")
    print(f"    -- Email: {auth.account.email or '-'}")
    print(f"    -- Phone number: {auth.account.phone_number or '-'}")
    print(f"    -- Registration time: {auth.account.created_time or '-'}")
    print(f"    -- Registered IPv4: {auth.account.registered_ipv4 or '-'}")
    print(f"    -- Last login IPv4: {auth.account.last_login_ipv4 or '-'}")
    print("[+] User Profile: ")
    print(f"    -- User ID: {auth.user_profile.uid}")
    print(f"    -- Nickname: {auth.user_profile.nickname}")
    print(f"    -- Tagline: {auth.user_profile.tagline or '-'}")
    print(f"    -- Bio: {auth.user_profile.bio or '-'}")
    if auth.user_profile.icon is not None:
        print("    -- Icon resources:")
        for resource in auth.user_profile.icon.resource_list:
            print(f"        -- URL: {resource.url}; width: {resource.width}; height: {resource.height}")
    if auth.user_profile.name_card_background is not None:
        print("    -- Name card background resources:")
        for resource in auth.user_profile.name_card_background.resource_list:
            print(f"        -- URL: {resource.url}; width: {resource.width}; height: {resource.height}")


@print_error
@with_args("link")
@with_auth(get_auth_response=False)
async def action_link_info(link: str):
    info = await client.get_link_info(link)
    print(f"[+] Path: {info.path or '-'}")
    print(f"[+] Object ID: {info.object_id or '-'}")
    print(f"[+] Object type: {info.object_type or '-'}")
    print(f"[+] Share link: {info.share_link or '-'}")
    print(f"[+] Parent type: {info.parent_type or '-'}")


@print_error
@with_args("thread", "message", "repeat")
@with_auth(get_auth_response=False)
async def action_send_message(chat_link: str, message_content: str, repeat: int):
    chat_id = (await client.get_link_info(chat_link)).object_id
    results = await gather(*[create_task(safe_send_chat_message(chat_id, message_content)) for _ in range(repeat)])
    sent = list(filter(lambda x: x, results))

    print(f"[{'+' if any(results) else '-'}] Sent: {len(sent)}/{len(results)}")


@print_error
@with_args("circle")
@with_auth(get_auth_response=False)
async def action_join_circle(circle_link: str):
    await client.join_circle(circle_link)
    print(f"[+] Joined successfully.")


@print_error
@with_args("circle")
@with_auth(get_auth_response=False)
async def action_leave_circle(circle_link: str):
    await client.leave_circle(circle_link)
    print(f"[+] Left successfully.")


@print_error
@with_auth(get_auth_response=False)
async def action_listen():
    client.register_chat_message_handler(
        lambda x: print(f"{x.author.nickname}: {x.content}"),
        lambda x: x.content is not None and x.author is not None
    )
    print(f"[+] Waiting for the messages...")

action_mapping = {
    "list-actions": [action_list_actions, "Print a list of all possible actions."],
    "clear-auth": [action_clear_auth, "Remove auth file."],
    "login": [action_login, "Login to the account and print account information."],
    "link-info": [action_link_info, "Get information about the object by the link."],
    "send-message": [action_send_message, "Send message to the chat."],
    "join-circle": [action_join_circle, "Join to the circle by the link."],
    "leave-circle": [action_leave_circle, "Leave from the circle by the link."],
    "listen": [action_listen, "Listen for the chat messages."]
}


def main():
    if cli_args.action not in action_mapping:
        print("Unknown action.")
        return

    fn = action_mapping[cli_args.action][0]

    run_function(fn)
    if cli_args.action == "listen":
        try:
            get_event_loop().run_forever()
        except KeyboardInterrupt:
            print("Interrupted.")
            sys_exit(0)


if __name__ == "__main__":
    main()
