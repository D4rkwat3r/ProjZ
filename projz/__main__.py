from argparse import ArgumentParser
from asyncio import get_event_loop
from asyncio import create_task
from asyncio import gather
from inspect import iscoroutinefunction
from sys import exit as sys_exit
from . import *

parser = ArgumentParser(description="ProjZ.py library command line interface")
parser.add_argument("action", type=str, help="The action to be performed. "
                                             "You can view the list of possible actions by "
                                             "setting the value \"list-action\"")
parser.add_argument("-l", "--login", type=str, dest="login", help="Email/Phone number of the account")
parser.add_argument("-p", "--password", type=str, dest="password", help="Password of the account")
parser.add_argument("-a", "--auth", type=str, dest="auth_type", help="Auth method: email or phone")
parser.add_argument("-i", "--info", type=str, dest="info", help="Link to the object to get information about")
parser.add_argument("-t", "--thread", type=str, dest="thread", help="Link to the chat to send message")
parser.add_argument("-m", "--message", type=str, dest="message", help="Text of the message to send")
parser.add_argument("-r", "--repeat", type=int, dest="repeat", help="The number of messages sent.")
parser.add_argument("-c", "--circle", type=str, dest="circle", help="Link to the circle to join or leave")
parser.add_argument("-s", "--solve", type=str, dest="solve", help="The solution of the captcha sent "
                                                                  "to the mail or to the phone. "
                                                                  "Needed to verify or register an account")
cli_args = parser.parse_args()

client = Client()


def print_error(func: Callable):
    def wrapper(*args, **kwargs) -> Any:
        try:
            return get_event_loop().run_until_complete(func(*args, **kwargs)) if iscoroutinefunction(func) \
                else func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")

    return wrapper


def authenticated(func):
    def wrapper(*args, **kwargs):
        if cli_args.login is None or cli_args.password is None or cli_args.auth_type is None:
            print("Specify login, password and auth type.")
            return
        return get_event_loop().run_until_complete(func(*args, **kwargs)) if iscoroutinefunction(func) \
            else func(*args, **kwargs)
    return wrapper


async def login() -> AuthResult:
    return await (
        client.login_email if cli_args.auth_type == "email"
        else client.login_phone_number
    )(cli_args.login, cli_args.password)


async def safe_send_chat_message(chat_id: int) -> bool:
    try:
        await client.send_message(chat_id, content=cli_args.message)
    except:
        return False
    return True


def action_list_actions():
    for i, key in enumerate(action_mapping, start=1):
        print(f"{i}. {key} - {action_mapping[key][1]}")


@print_error
@authenticated
async def action_login():
    auth = await login()
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
@authenticated
async def action_link_info():
    if cli_args.info is None:
        print("Specify --info.")
        return
    await login()
    info = await client.get_link_info(cli_args.info)
    print(f"[+] Path: {info.path or '-'}")
    print(f"[+] Object ID: {info.object_id or '-'}")
    print(f"[+] Object type: {info.object_type or '-'}")
    print(f"[+] Share link: {info.share_link or '-'}")
    print(f"[+] Parent type: {info.parent_type or '-'}")


@print_error
@authenticated
async def action_send_message():
    if cli_args.thread is None or cli_args.message is None or cli_args.repeat is None:
        print("Specify --thread, --message and --repeat.")
        return
    if cli_args.repeat == 0:
        print("Illegal argument (repeat=0).")
        return
    await login()

    chat_id = (await client.get_link_info(cli_args.thread)).object_id
    results = await gather(*[create_task(safe_send_chat_message(chat_id)) for _ in range(cli_args.repeat)])
    sent = list(filter(lambda x: x, results))

    print(f"[{'+' if any(results) else '-'}] Sent: {len(sent)}/{len(results)}")


@print_error
@authenticated
async def action_join_circle():
    if cli_args.circle is None:
        print("Specify --circle.")
        return
    await login()

    await client.join_circle(cli_args.circle)
    print(f"[+] Joined successfully.")


@print_error
@authenticated
async def action_leave_circle():
    if cli_args.circle is None:
        print("Specify --circle.")
        return
    await login()

    await client.leave_circle(cli_args.circle)
    print(f"[+] Left successfully.")


@print_error
@authenticated
async def action_listen():
    await login()

    client.register_chat_message_handler(
        lambda x: print(f"{x.author.nickname}: {x.content}"),
        lambda x: x.content is not None and x.author is not None
    )
    print(f"[+] Waiting for the messages...")

action_mapping = {
    "list-actions": [action_list_actions, "Print a list of all possible actions."],
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
    loop = get_event_loop()

    loop.run_until_complete(fn()) if iscoroutinefunction(fn) else fn()
    if cli_args.action == "listen":
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Interrupted.")
            sys_exit(0)


if __name__ == "__main__":
    main()
