from .api import RequestManager
from .api.headers import IHeadersProvider
from .api.headers import HeadersProvider
from .model import *
from .enum import *
from .websocket import WebsocketListener
from typing import Union
from typing import Callable
from typing import Any
from aiohttp import MultipartWriter
from typing import Optional
from aiofiles.threadpool.binary import AsyncBufferedReader
from random import randint
from sys import maxsize
from urllib.parse import urlparse
from magic import from_buffer
from mnemonic import Mnemonic
from bip32utils import BIP32Key

CircleReference = Union[Circle, str, int]


class Client(RequestManager):
    def __init__(
        self,
        commands_prefix: str = "/",
        provider: Optional[IHeadersProvider] = None,
        http_logging: bool = False,
        ws_logging: bool = False,
        *args,
        **kwargs
    ):
        super().__init__(provider or HeadersProvider(), logging=http_logging, *args, **kwargs)
        self.websocket = WebsocketListener(self, logging=ws_logging)
        self.commands_prefix = commands_prefix
        self.account = None
        self.user_profile = None

    async def _logout(self):
        self.provider.remove_sid()
        await self.websocket.disconnect()
        self.user_profile, self.account = None, None

    async def _auth(self, resp: AuthResult):
        if self.provider.get_sid(): await self._logout()
        self.provider.set_sid(resp.sid)
        self.account = resp.account
        self.user_profile = resp.user_profile
        await self.websocket.connect()

    async def _resolve_circle_reference(self, ref: CircleReference) -> int:
        if isinstance(ref, Circle):
            return ref.circle_id
        elif isinstance(ref, int) or ref.isdigit():
            return ref
        if "projz.com/s/c/" in ref:
            return (await self.get_link_info(ref)).object_id
        return (await self.get_link_info(f"https://www.projz.com/s/c/{ref}")).object_id

    async def _login(
        self,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        password: Optional[str] = None,
        secret: Optional[str] = None
    ) -> AuthResult:
        data = {"password": password} if password is not None else {}
        if email is not None:
            data["email"] = email
            data["authType"] = EAuthType.EMAIL.value
        elif phone_number is not None:
            data["phoneNumber"] = phone_number
            data["authType"] = EAuthType.PHONE_NUMBER.value
        elif secret is not None:
            data["secret"] = secret
            data["authType"] = EAuthType.SECRET.value
            data["purpose"] = EAuthPurpose.RENEW_SID.value
        resp = AuthResult.from_dict(await self.post_json("/v1/auth/login", data))
        await self._auth(resp)
        return resp

    async def login_email(self, email: str, password: str) -> AuthResult:
        """
        Login to account using a email
        :param email: email address
        :param password: account password
        :return: model.AuthResult
        """
        return await self._login(email=email, password=password, phone_number=None)

    async def login_phone_number(self, phone_number: str, password: str) -> AuthResult:
        """
        Login to account using a phone number
        :param phone_number: phone number
        :param password: account password
        :return: model.AuthResult
        """
        return await self._login(phone_number=phone_number, password=password, email=None)

    async def login_secret(self, secret: str) -> AuthResult:
        """
        Login to account using a secret token that acts as a refresh token.
        :param secret: secret token
        :return: model.AuthResult
        """
        return await self._login(secret=secret)

    async def logout(self) -> None:
        """
        Send logout request and remove sid
        :return:
        """
        await self.post_empty("/v1/auth/logout")
        await self._logout()

    async def _request_security_validation(
        self,
        email: Optional[str],
        phone_number: Optional[str],
        purpose: Union[EAuthPurpose, int] = EAuthPurpose.LOGIN
    ) -> None:
        data = {
            "purpose": purpose.value if isinstance(purpose, EAuthPurpose) else purpose,
            "countryCode": self.country_code
        }
        if email is not None:
            data["authType"] = EAuthType.EMAIL.value
            data["email"] = email
        elif phone_number is not None:
            data["authType"] = EAuthType.PHONE_NUMBER.value
            data["phoneNumber"] = phone_number
        await self.post_json("/v1/auth/request-security-validation", data)

    async def request_email_validation(self, email: str, purpose: Union[EAuthPurpose, int] = EAuthPurpose.LOGIN) -> None:
        """
        Send verification code to email
        :param email: email address
        :param purpose: AuthPurpose.LOGIN, AuthPurpose.CHANGE_EMAIL, custom value...
        :return:
        """
        return await self._request_security_validation(email=email, purpose=purpose, phone_number=None)

    async def request_phone_validation(self, phone_number: str, purpose: Union[EAuthPurpose, int] = EAuthPurpose.LOGIN) -> None:
        """
        Send verification code to phone number
        :param phone_number: phone number
        :param purpose: AuthPurpose.LOGIN, AuthPurpose.CHANGE_PHONE, custom value...
        :return:
        """
        return await self._request_security_validation(phone_number=phone_number, purpose=purpose, email=None



    # FORK INVITE HOST CHAT
    async def invite_host_chat(self, chat_id, user_id):
        """
        Send host a user
        param: chat_id Chat Id
        param: user_id Id from user
        """
        return await self.post_empty(f'/v1/chat/threads/{chat_id}/invite-host/{user_id}')

    async def change_password(self, old: str, new: str) -> None:
        """
        Change account password
        :param old: old password
        :param new: new passworod
        :return:
        """
        await self.post_json("/v1/auth/change-password", {"oldPassword": old, "newPassword": new})

    async def _check_security_validation(self, email: Optional[str], phone_number: Optional[str], code: str) -> None:
        data = {"securityCode": code}
        if email is not None:
            data["authType"] = EAuthType.EMAIL.value
            data["email"] = email
        elif phone_number is not None:
            data["authType"] = EAuthType.PHONE_NUMBER.value
            data["phoneNumber"] = phone_number
        await self.post_json("/v1/auth/check-security-validation", data)

    async def check_email_validation(self, email: str, code: str) -> None:
        """
        Check verification code sent to email
        :param email: email address
        :param code: verification code
        :return:
        """
        await self._check_security_validation(email=email, code=code, phone_number=None)

    async def check_phone_validation(self, phone_number: str, code: str) -> None:
        """
        Check verification code sent to phone number
        :param phone_number: phone number
        :param code: verification code
        :return:
        """
        await self._check_security_validation(phone_number=phone_number, code=code, email=None)

    async def _register(
        self,
        email: Optional[str],
        phone_number: Optional[str],
        password: str,
        nickname: str,
        tag_line: str,
        icon: Media,
        gender_type: EGender,
        birthday: str,
        code: str,
        name_card_background: Optional[Media] = None,
        invitation_code: Optional[str] = None,
        *,
        update_auth_credentials: bool = True
    ) -> AuthResult:
        raise NotImplementedError("[register] Not implemented -"
                                  "rawDeviceIdThree is required, "
                                  "but the correct algorithm for generating it is currently unknown.")
        # data = {
        #    "purpose": 1,
        #    "password": password,
        #    "securityCode": code,
        #    "invitationCode": invitation_code or "",
        #    "nickname": nickname,
        #    "tagLine": tag_line,
        #    "icon": icon.to_dict(),
        #    "nameCardBackground": name_card_background.to_dict() if name_card_background is not None else None,
        #    "gender": gender_type.value,
        #    "birthday": birthday,
        #    "requestToBeReactivated": False,
        #    "countryCode": self.country_code,
        #    "suggestedCountryCode": self.country_code.upper(),
        #    "ignoresDisabled": True,
        #    "rawDeviceIdThree": await self.provider.generate_device_id_three(
        #        "BU0gJ0gB5TFcCfN329Vx",
        #        "android",
        #        f"{randint(1, 12)}.{randint(1, 12)}.{randint(1, 12)}",
        #        "ASUS_Z02MQ",
        #        "default"
        #    )
        # }
        # if email is not None:
        #    data["authType"] = AuthType.EMAIL.value
        #    data["email"] = email
        # elif phone_number is not None:
        #    data["authType"] = AuthType.PHONE_NUMBER.value
        #    data["phoneNumber"] = phone_number
        # resp = await self.post_json("/v1/auth/register", data)
        # resp = AuthResult.from_dict(resp)
        # if update_auth_credentials: await self._auth(resp)
        # return AuthResult.from_dict(resp)

    async def register_email(
        self,
        email: str,
        password: str,
        nickname: str,
        tag_line: str,
        icon: Media,
        gender_type: EGender,
        birthday: str,
        code: str,
        name_card_background: Optional[Media] = None,
        invitation_code: Optional[str] = None,
        *,
        update_auth_credentials: bool = True
    ) -> AuthResult:
        """
        Create a new account with email
        :param email: email address
        :param password: account password
        :param nickname: profile nickname
        :param tag_line: profile tagline
        :param icon: icon image model.Media object
        :param gender_type: Gender.MALE | Gender.FEMALE | Gender.OTHER
        :param birthday: year-month-day
        :param code: verification code
        :param name_card_background: name card background model.Media object
        :param invitation_code: code of invitation
        :param update_auth_credentials: is it required to update client profile and sid
        :return: model.AuthResponse
        """
        return await self._register(
            email,
            None,
            password,
            nickname,
            tag_line,
            icon,
            gender_type,
            birthday,
            code,
            name_card_background,
            invitation_code,
            update_auth_credentials=update_auth_credentials
        )

    async def register_phone(
        self,
        phone_number: str,
        password: str,
        nickname: str,
        tag_line: str,
        icon: Media,
        gender_type: EGender,
        birthday: str,
        code: str,
        name_card_background: Optional[Media] = None,
        invitation_code: Optional[str] = None,
        *,
        update_auth_credentials: bool = True
    ) -> AuthResult:
        """
        Create a new account with phone number
        :param phone_number: phone number
        :param password: account password
        :param nickname: profile nickname
        :param tag_line: profile tagline
        :param icon: icon image model.Media object
        :param gender_type: Gender.MALE | Gender.FEMALE | Gender.OTHER
        :param birthday: year-month-day
        :param code: verification code
        :param name_card_background: name card background model.Media object
        :param invitation_code: code of invitation
        :param update_auth_credentials: is it required to update client profile and sid
        :return: model.AuthResponse
        """
        return await self._register(
            None,
            phone_number,
            password,
            nickname,
            tag_line,
            icon,
            gender_type,
            birthday,
            code,
            name_card_background,
            invitation_code,
            update_auth_credentials=update_auth_credentials
        )

    async def accept_chat_invitation(self, thread_id: int) -> None:
        """
        Accept invitation to the chat
        :param thread_id: id of the chat
        :return:
        """
        await self.post_empty(f"/v1/chat/threads/{thread_id}/accept-invitation")

    async def join_circle(self, reference: CircleReference) -> None:
        """
        Join to the circle
        :param reference: circle id | circle link | z id
        :return:
        """
        await self.post_empty(f"/v1/circles/{await self._resolve_circle_reference(reference)}/members")

    async def leave_circle(self, reference: CircleReference) -> None:
        """
        Leave from the chat
        :param reference: circle id | circle link | z id
        :return:
        """
        await self.delete(f"/v1/circles/{await self._resolve_circle_reference(reference)}/members")

    async def join_chat(self, thread_id: int) -> None:
        """
        Join to the chat
        :param thread_id: id of the chat
        :return:
        """
        await self.post_empty(f"/v1/chat/threads/{thread_id}/members")

    async def leave_chat(self, thread_id: int) -> None:
        """
        Leave from the chat
        :param thread_id: id of the chat
        :return:
        """
        await self.delete(f"/v1/chat/threads/{thread_id}/members")

    async def get_chat_message(self, thread_id: int, message_id: int) -> ChatMessage:
        """
        Get chat message by id
        :param thread_id: id of the chat
        :param message_id: id of the message
        :return: model.ChatMessage
        """
        return ChatMessage.from_dict(await self.get(f"/v1/chat/threads/{thread_id}/messages/{message_id}"))

    async def get_chat_messages(self, thread_id: int, size: int = 30, page_token: Optional[str] = None) -> PaginatedList[ChatMessage]:
        """
        Get list of last messages in the chat
        :param thread_id: id of the chat
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.ChatMessage]
        """
        resp = await self.get(f"/v1/chat/threads/{thread_id}/messages", {
            "size": size
        } if page_token is None else {
            "size": size,
            "pageToken": page_token
        })
        return PaginatedList(
            [ChatMessage.from_dict(message_json) for message_json in resp["list"]],
            resp.get("pagination")
        )

    async def send_message(self,
                           thread_id: int,
                           message_type: Union[EChatMessageType, int] = 1,
                           content: Optional[str] = None,
                           reply_to: Optional[int] = None,
                           message_rich_format: Optional[RichFormat] = None,
                           attached_media: Optional[Media] = None,
                           attached_audio: Optional[Media] = None,
                           poll_id: Optional[int] = None,
                           dice_id: Optional[int] = None,
                           *,
                           get_sent_message: bool = True) -> Optional[ChatMessage]:
        """
        Send message to the chat
        :param thread_id: id of the chat
        :param message_type: ChatMessageType enum field or int identifier
        :param content: text content of the message
        :param reply_to: reply message id
        :param message_rich_format: RichFormat object, can be created by RichFormatBuilder
        :param attached_media: attached to the message file model.Media object
        :param attached_audio: attached to the message audio model.Media object
        :param poll_id: attached to the message poll id
        :param dice_id: attached to the message dice id
        :param get_sent_message: If set to False, the request for information about the
        sent message will not be executed and the function will return None.
        :return:
        """
        if attached_media is not None and attached_audio is not None:
            raise ValueError("You can't send audio and media in one message")
        seq_id = randint(0, maxsize)
        data = {
            "type": message_type if isinstance(message_type, int) else message_type.value,
            "threadId": thread_id,
            "uid": self.user_profile.uid,
            "seqId": seq_id,
            "extensions": {}
        }
        if content is not None: data["content"] = content
        if reply_to is not None: data["extensions"]["replyMessageId"] = reply_to
        if message_rich_format is not None: data["richFormat"] = message_rich_format.to_dict()
        if attached_media is not None: data["media"] = attached_media.to_dict()
        if attached_audio is not None: data["media"] = attached_audio.to_dict()
        if poll_id is not None: data["extensions"]["pollId"] = poll_id
        if dice_id is not None: data["extensions"]["diceId"] = dice_id
        resp = await self.websocket.send_request(1, True, seq_id, **dict(threadId=thread_id, msg=data))
        if get_sent_message:
            return await self.get_chat_message(resp["threadId"], resp["messageId"])

    async def show_typing(self, thread_id: int) -> None:
        """
        Displays the text to the chat members that the account is "typing".
        :param thread_id: id of the chat
        :return:
        """
        await self.send_message(thread_id, EChatMessageType.TYPING, get_sent_message=False)

    async def get_block_users_info(self) -> BlockUsersInfo:
        return BlockUsersInfo.from_dict(await self.get("/v1/users/block-uids"))

    async def get_link_info(self, link: str) -> LinkInfo:
        """
        Get object info by link
        :param link: object link
        :return: model.LinkInfo
        """
        return LinkInfo.from_dict(await self.post_json("/v1/links/path", {"link": link}))

    async def parse_share_link(self, link: str) -> LinkInfo:
        """
        Web API alternative of get_link_info
        :param link: object link
        :return: model.LinkInfo
        """
        return LinkInfo.from_dict(
            await self.post_json("/v1/parse-share-link", {"link": urlparse(link).path}, web=True)
        )

    async def get_circle_info(self, circle_id: int) -> Circle:
        """
        Get circle info by id
        :param circle_id: id of the circle
        :return: model.Circle
        """
        return Circle.from_dict(await self.get(f"/v1/circles/{circle_id}"))

    async def get_chat_info(self, thread_id: int) -> Chat:
        """
        Get chat info by id
        :param thread_id: id of the chat
        :return:
        """
        return Chat.from_dict(await self.get(f"/v1/chat/threads/{thread_id}"))

    async def get_default_background_media_list(self) -> list[DefaultBackgroundMedia]:
        """
        Get default chat background list
        :return: list[model.DefaultBackgroundMedia]
        """
        return [
            DefaultBackgroundMedia.from_dict(media_json)
            for media_json in await self.get("/v1/media/default-background-media-info-list")
        ]

    async def start_chat(
        self,
        thread_type: EChatThreadType = EChatThreadType.ONE_ON_ONE,
        invite_message_content: Optional[str] = None,
        invited_user_ids: Union[str, list[str]] = None,
        circle_list: Optional[CircleReference] = None,
        title: Optional[str] = None,
        icon: Optional[Media] = None,
        background: Optional[Media] = None,
        tag_string_list: Optional[list[str]] = None,
        category_id: Optional[int] = None,
        language: Optional[str] = None
    ) -> Chat:
        """
        Create a new chat
        :param thread_type: ChatThreadType.ONE_ON_ONE | ChatThreadType.PRIVATE | ChatThreadType.PUBLIC
        :param invite_message_content: content of the auto-generated first message in the chat
        :param invited_user_ids: ids of users invited to the chat
        :param title: title of the chat
        :param icon: chat icon model.Media object
        :param background: chat background model.Media object
        :param tag_string_list: list if chat tags
        :param circle_list: circles to which the chat is attached
        :param category_id: id of the category to which the chat is attached
        :param language: language of the chat (default: en)
        :return: model.Chat
        """
        data = {
            "type": thread_type.value,
            "background": (background or (await self.get_default_background_media_list())[0].media).to_dict()
        }
        if invite_message_content is not None:
            data["inviteMessageContent"] = invite_message_content
        if invited_user_ids is not None:
            data["invitedUids"] = invited_user_ids if isinstance(invited_user_ids, list) else [invited_user_ids]
        if circle_list is not None:
            data["circleIdList"] = [await self._resolve_circle_reference(reference) for reference in circle_list]
        if title is not None: data["title"] = title
        if icon is not None: data["icon"] = icon.to_dict()
        if tag_string_list is not None: data["tagStrList"] = tag_string_list
        if category_id is not None: data["categoryId"] = category_id
        if language is not None: data["language"] = language
        return Chat.from_dict(await self.post_json("/v1/chat/threads", data))

    async def get_circle_active_members(self,
                                        reference: CircleReference,
                                        size: int = 30,
                                        page_token: Optional[str] = None) -> PaginatedList[User]:
        """
        Get active members in the circle
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.User]
        """
        resp = await self.get(
            f"/v1/circles/{await self._resolve_circle_reference(reference)}/active-members",
            {"size": size} if page_token is None else {"pageToken": page_token, "size": size}
        )
        return PaginatedList(
            [User.from_dict(user_json) for user_json in resp["list"]],
            resp.get("pagination")
        )

    async def get_chat_with_user(self, user_id: int) -> Chat:
        """
        Try to get a one-on-one chat with another user
        :param user_id: id of the user
        :return:
        """
        return Chat.from_dict(await self.get(f"/v1/chat/one-on-one-chat/{user_id}"))

    async def get_recommended_user_namecards(self, size: int = 100, gender_type: Union[EGender, int] = 0) -> list[User]:
        """
        Get recommended user namecards
        :param size: size of the list
        :param gender_type: Gender.MALE | Gender.FEMALE | Gender.OTHER | 0
        :return: list[model.User]
        """
        resp = await self.get("/v1/users/namecards", {
            "size": size,
            "gender": gender_type if isinstance(gender_type, int) else gender_type.value,
            "withoutExtraInfo": True
        })
        return [
            User.from_dict(user_json)
            for user_json in resp["list"]
        ]

    async def get_user_info(self, user_id: int) -> User:
        """
        Get user info by id
        :param user_id: id of the user
        :return: model.User
        """
        return User.from_dict(await self.get(f"/v1/users/profile/{user_id}"))

    async def delete_chat(self, chat_id: int) -> None:
        """
        Delete a chat
        :param chat_id: id of the chat
        :return:
        """
        await self.delete(f"/v1/chat/threads/{chat_id}")

    async def get_circle_chats(
        self,
        reference: CircleReference,
        size: int = 30,
        page_token: Optional[str] = None,
        query_type: Union[EPartyQueryType, int] = EPartyQueryType.ONLINE,
        *,
        with_pin: bool = False
    ) -> PaginatedList[Chat]:
        """
        Get public chats in the circle
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :param with_pin: include pinned chats
        :param query_type: PartyQueryType.ALL | PartyQueryType.ONLINE
        :return: PaginatedList[model.Chat]
        """
        resp = await self.get(f"/v1/chat/threads", {
            "type": "circle",
            "objectId": await self._resolve_circle_reference(reference),
            "size": size,
            "withPin": "false",
            "partyQueryType": query_type.value if isinstance(query_type, EPartyQueryType) else query_type
        } if page_token is None else {
            "type": "circle",
            "objectId": await self._resolve_circle_reference(reference),
            "size": size,
            "withPin": with_pin,
            "partyQueryType": query_type.value if isinstance(query_type, EPartyQueryType) else query_type,
            "pageToken": page_token
        })
        return PaginatedList(
            [Chat.from_dict(user_json) for user_json in resp["list"]],
            resp.get("pagination")
        )

    async def get_joined_chats(
        self,
        start: int = 0,
        size: int = 30,
        query_type: Union[EChatQueryType, int] = EChatQueryType.PRIVATE
    ) -> list[Chat]:
        """
        Get a list of chats that an account has joined
        :param start: offset of the list
        :param size: size of the list
        :param query_type: ChatQueryType enum field or type identifier (default: private)
        :return: list[Chat]
        """
        resp = await self.get("/v1/chat/joined-threads", {
            "type": query_type.value if isinstance(query_type, EChatQueryType) else query_type,
            "start": start,
            "size": size,
        })
        return [
            Chat.from_dict(chat_json)
            for chat_json in resp["list"]
        ]

    async def get_joined_parties(self, start: int = 0, size: int = 30) -> list[Party]:
        """
        Get a list of public chats that an account has joined
        :param start: offset of the list
        :param size: size of the list
        :return: list[Party]
        """
        resp = await self.get("/v1/chat/joined-parties", {
            "type": "parties",
            "start": start,
            "size": size
        })
        return [
            Party.from_dict(party_json)
            for party_json in resp["list"]
        ]

    async def get_qi_votes_info(self, object_id: int) -> QiVoteFullInfo:
        """
        Get qi votes info
        :param object_id: id of the object
        :return: model.QiVoteFullInfo
        """
        return QiVoteFullInfo.from_dict(await self.get("/v1/qivotes", {
            "objectId": object_id,
            "timezone": self.time_zone
        }))

    async def send_qi(self, object_id: int, target_type: Union[EObjectType, int] = 1, count: int = 1) -> QiVoteInfo:
        """
        Send qi to the specified object
        :param object_id: id of the target
        :param target_type: ObjectType enum field or type identifier (default: chat)
        :param count: qi count
        :return: model.QiVoteInfo
        """
        return QiVoteInfo.from_dict(await self.post_json("/v1/qivotes", {
            "objectType": target_type if isinstance(target_type, int) else target_type.value,
            "objectId": object_id,
            "votedCount": count,
            "timezone": self.time_zone
        }))

    async def get_chat_managers(self, chat_id: int, *, only_co_hosts: bool = False) -> list[User]:
        """
        Get chat admins
        :param chat_id: id of the chat
        :param only_co_hosts: include only co-hosts
        :return: list[model.User]
        """
        resp = await self.get(
            f"/v1/chat/threads/{chat_id}/management-team",
            {"onlyCoHosts": only_co_hosts}
        )
        return [
            User.from_dict(user_json)
            for user_json in resp["list"]
        ]

    async def get_chat_members(self,
                               chat_id: int,
                               size: int = 30,
                               query_word: str = "",
                               page_token: Optional[str] = None,
                               *,
                               only_active_members: bool = False,
                               exclude_managers: bool = False) -> PaginatedList[User]:
        """
        Get list of chat members
        :param chat_id: id of the chat
        :param size: size of the list
        :param only_active_members: include only active members
        :param exclude_managers: exclude management team
        :param query_word: search query
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.User]
        """
        resp = await self.get(f"/v1/chat/threads/{chat_id}/members", {
            "onlyActiveMember": only_active_members,
            "size": size,
            "isExcludeManger": exclude_managers,
            "queryWord": query_word
        } if page_token is None else {
            "onlyActiveMember": only_active_members,
            "size": size,
            "isExcludeManger": exclude_managers,
            "queryWord": query_word,
            "pageToken": page_token
        })
        return PaginatedList(
            [User.from_dict(user_json) for user_json in resp["list"]],
            resp.get("pagination")
        )

    async def get_circle_members(self,
                                 reference: CircleReference,
                                 size: int = 30,
                                 query_type: ECircleMembersQueryType = ECircleMembersQueryType.NORMAL,
                                 page_token: Optional[str] = None,
                                 *,
                                 exclude_managers: bool = False) -> PaginatedList[User]:
        """
        Get list of circle members
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :param query_type: CircleMembersQueryType.NORMAL | CircleMembersQueryType.BLOCKED
        :param exclude_managers: exclude management team
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.User]
        """
        resp = await self.get(f"/v1/circles/{await self._resolve_circle_reference(reference)}/members", {
            "type": query_type.value,
            "size": size,
            "isExcludeManger": exclude_managers
        } if page_token is None else {
            "type": query_type.value,
            "size": size,
            "isExcludeManger": exclude_managers,
            "pageToken": page_token
        })
        return PaginatedList(
            [User.from_dict(user_json) for user_json in resp["list"]],
            resp.get("pagination")
        )

    async def get_visible_member_titles(self, reference: CircleReference, size: int = 100) -> MemberTitlesInfo:
        """
        Get info about member title in specified circle
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :return: model.MemberTitlesInfo
        """
        return MemberTitlesInfo.from_dict(await self.get(f"/v1/circles/{await self._resolve_circle_reference(reference)}"
                                                         f"/visible-member-titles", {"size": size}))

    async def create_poll_with_icons(
        self,
        title: str,
        poll_items: list[tuple[str, Optional[Media]]]
    ) -> Poll:
        """
        Create and register a poll with icons
        :param title: title of the poll
        :param poll_items: list of poll item contents
        :return: model.Poll
        """
        poll_items = list(map(
            lambda x: (x[0], x[1].to_dict()) if isinstance(x[1], Media) else x,
            poll_items
        ))
        return Poll.from_dict(await self.post_json("/v1/polls", {
            "title": title,
            "pollItemList": [
                {"content": item[0]} if len(item) != 2 or item[1] is None else
                {"content": item[0], "icon": item[1]}
                for item in poll_items
            ]
        }))

    async def get_categories(self,
                             target_type: Union[EObjectType, int] = 5,
                             target_region: Union[EContentRegion, int] = 1) -> list[Category]:
        """
        Get available categories
        :param target_type: ObjectType enum field (ObjectType.CIRCLE, ObjectType.CHAT, etc.) or type identifier (default: circle)
        :param target_region: categories region - ContentRegion enum field or region identifier (default: English)
        :return: list[model.Category]
        """
        resp = await self.get("/v1/categories", {
            "objectType": target_type if isinstance(target_type, int) else target_type.value,
            "contentRegion": target_region if isinstance(target_region, int) else target_region.value
        })
        return [
            Category.from_dict(category_json)
            for category_json in resp["list"]
        ]

    async def get_circles(self,
                          filter_type: Union[ECircleFilterType, str],
                          size: int = 30,
                          category_id: int = 0,
                          page_token: Optional[str] = None) -> PaginatedList[Circle]:
        """
        Get circles attached to specified category
        :param filter_type: CircleFilterType enum field or filter identifier
        :param size: size of the list
        :param category_id: id of the category, 0 for all categories
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Circle]
        """
        resp = await self.get("/v1/circles", {
            "type": filter_type.value if isinstance(filter_type, ECircleFilterType) else filter_type,
            "size": size,
            "categoryId": category_id
        } if page_token is None else {
            "type": filter_type.value if isinstance(filter_type, ECircleFilterType) else filter_type,
            "size": size,
            "categoryId": category_id,
            "pageToken": page_token
        })
        return PaginatedList(
            [Circle.from_dict(circle_json) for circle_json in resp["list"]],
            resp.get("pagination")
        )

    async def visit_profile(self, user_id: int) -> None:
        """
        Visit user profile
        :param user_id: id of the user
        :return:
        """
        await self.post_empty(f"/v1/users/profile/{user_id}/visit")

    async def get_blog_info(self, blog_id: int) -> Blog:
        """
        Get blog info by blog id
        :param blog_id: id of the blog
        :return: model.Blog
        """
        return Blog.from_dict(await self.get(f"/v1/blogs/{blog_id}"))

    async def post_blog(self,
                        title: str,
                        content: str,
                        content_rich_format: Optional[RichFormat] = None,
                        media_list: Optional[list[Media]] = None,
                        background: Optional[Media] = None,
                        cover: Optional[Media] = None,
                        circle_list: Optional[list[int]] = None,
                        background_color: Optional[str] = None) -> Blog:
        """
        :param title: title of the blog
        :param content: content of the blog
        :param content_rich_format: RichFormat object, can be created by RichFormatBuilder
        :param media_list: list of model.Media objects in the blog
        :param background: blog background model.Media object
        :param cover: blog cover model.Media object
        :param circle_list: circles to which the blog is attached
        :param background_color: background color of the blog
        :return: model.Blog
        """
        circles = [await self._resolve_circle_reference(reference) for reference in circle_list] if circle_list is not None else []
        data = {
            "type": 2,
            "title": title,
            "content": content,
            "mediaList": [media_obj.to_dict() for media_obj in media_list] if media_list is not None else [],
            "richFormat": content_rich_format.to_dict() if content_rich_format is not None else RichFormatBuilder().build().to_dict(),
            "circleIdList": circles,
            "folderAffiliationList": [{"circleId": circle_id} for circle_id in circles],
            "backgroundColor": background_color or "",
            "extensions": {}
        }
        if background is not None: data["background"] = background.to_dict()
        if cover is not None: data["cover"] = cover.to_dict()
        if background_color is not None: data["extensions"]["backgroundColor"] = background_color
        return Blog.from_dict(await self.post_json("/v1/blogs", data))

    async def delete_blog(self, blog_id: int) -> None:
        """
        Delete a blog
        :param blog_id: id of the blog
        :return:
        """
        await self.delete(f"/v1/blogs/{blog_id}")

    async def get_comment_info(self, comment_id: int) -> Comment:
        """
        Get comment info by id
        :param comment_id: id of the comment
        :return: model.Comment
        """
        return Comment.from_dict(await self.get(f"/v1/comments/{comment_id}"))

    async def delete_comment(self, comment_id: int) -> Comment:
        """
        Delete a comment
        :param comment_id: id of the comment
        :return: model.Comment
        """
        await self.delete(f"/v1/comments/{comment_id}")

    async def get_comments(self,
                           parent_type: Union[EObjectType, int],
                           parent_id: int,
                           size: int = 30,
                           reply_id: int = 0,
                           page_token: Optional[str] = None,
                           *,
                           only_pinned: bool = False) -> PaginatedList[Comment]:
        """
        Get list of the comments
        :param parent_type: ObjectType enum field or type identifier
        :param parent_id: id of the parent
        :param size: size of the list
        :param reply_id: include only replies to comment with id reply_id
        :param only_pinned: include only pinned comments
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Comment]
        """
        resp = await self.get("/v1/comments", {
            "parentType": parent_type if isinstance(parent_type, int) else parent_type.value,
            "parentId": parent_id,
            "size": size,
            "replyId": reply_id,
            "onlyPinned": int(only_pinned)
        } if page_token is None else {
            "parentType": parent_type if isinstance(parent_type, int) else parent_type.value,
            "parentId": parent_id,
            "size": size,
            "replyId": reply_id,
            "onlyPinned": int(only_pinned),
            "pageToken": page_token
        })
        return PaginatedList(
            [Comment.from_dict(comment_json) for comment_json in resp["list"]],
            resp.get("pagination")
        )

    async def comment(self,
                      parent_type: Union[EObjectType, int],
                      parent_id: int,
                      content: Optional[str] = None,
                      media_list: Optional[list[Media]] = None,
                      reply_to: Optional[int] = None) -> Comment:
        """
        Create a comment
        :param parent_type: ObjectType enum field or type identifier
        :param parent_id: id of the parent
        :param content: text content of the comment
        :param media_list: attachments of the comment
        :param reply_to: reply to the comment id
        :return: model.Comment
        """
        data = {
            "commentType": 1 if not media_list else 2,
            "parentType": parent_type if isinstance(parent_type, int) else parent_type.value,
            "parentId": parent_id,
            "mediaList": [media_obj.to_dict() for media_obj in media_list] if media_list is not None else []
        }
        if content is not None: data["content"] = content
        if reply_to is not None: data["replyId"] = reply_to
        return Comment.from_dict(await self.post_json("/v1/comments", data))

    async def create_poll(self, title: str, poll_items: list[str]) -> Poll:
        """
        Create and register a poll without icons
        :param title: title of the poll
        :param poll_items: list of poll item contents
        :return: model.Poll
        """
        return await self.create_poll_with_icons(title, [(item, None) for item in poll_items])

    async def get_user_tasks(self) -> list[UserTask]:
        return [
            UserTask.from_dict(task_json)
            for task_json in (await self.get("/v2/user-tasks"))["list"]
        ]

    async def accept_gift(self, gift_id: int) -> None:
        """
        Accept a gift from user or from system
        :param gift_id: id of the gift
        :return:
        """
        await self.post_empty(f"/biz/v1/gift-boxes/{gift_id}/claim")

    async def complete_user_task(self, task_type: Union[EUserTaskType, int]):
        """
        Mark user task as completed and get coins
        :param task_type: UserTaskType enum field or custom int value
        :return:
        """
        await self.get_user_tasks()
        resp = await self.post_json("/v1/user-tasks/claim-reward", {
            "type": task_type.value if isinstance(task_type, EUserTaskType) else task_type
        })
        await self.accept_gift(resp["giftBox"]["boxId"])

    async def send_gift(
        self,
        user_id: int,
        count: int,
        payment_password: str,
        title: str,
        sending_currency_type: ECurrencyType
    ) -> GiftBox:
        """
        Send gift to user
        :param user_id: target user id
        :param count: count of coins/diamonds/merch
        :param payment_password: password needed to perform operation
        :param title: attached message
        :param sending_currency_type: CurrencyType enum value
        :return: model.GiftBox
        """
        resp = await self.post_json("/biz/v1/gift-boxes", {
            "toObjectId": user_id,
            "toObjectType": EObjectType.USER.value,
            "amount": str(count) + ("0" * 18),
            "paymentPassword": payment_password,
            "currencyType": sending_currency_type.value,
            "title": title
        })
        return GiftBox.from_dict(resp)

    async def get_transfer_orders(self, size: int = 30, page_token: Optional[str] = None) -> PaginatedList[TransferOrder]:
        """
        Get a list of incoming currency transfers
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.TransferOrder]
        """
        resp = await self.get("/biz/v2/transfer-orders", {
            "size": size
        } if page_token is None else {
            "size": size,
            "pageToken": page_token
        })
        return PaginatedList(
            [TransferOrder.from_dict(order_json) for order_json in resp["list"]],
            resp.get("pagination")
        )

    async def activate_wallet(self, payment_password: str, security_code: str) -> str:
        """
        Activate a wallet
        :param payment_password: password for performing payment operations
        :param security_code: validation code
        :return: recovery phrase
        """
        await self.get_wallet_info()
        
        mnemonic = Mnemonic(language="english")
        recovery_phrase = mnemonic.generate(strength=128)
        await self.post_json("/biz/v1/wallet/0/activate", {
            "paymentPassword": payment_password,
            "securityCode": security_code,
            "identity": self.account.email or self.account.phone_number,
            "authType": EAuthType.EMAIL.value if self.account.email is not None else EAuthType.PHONE_NUMBER.value,
            "recoveryPhrasePublicKey": BIP32Key.fromEntropy(mnemonic.to_seed(recovery_phrase)).PublicKey().hex()
        })
        return recovery_phrase

    async def get_wallet_info(self) -> Optional[Wallet]:
        """
        Get info about user's wallet
        :return: model.Wallet
        """
        resp = await self.get("/biz/v1/wallet")
        if len(resp) == 0: return None
        return Wallet.from_dict(resp)

    async def get_dices(self) -> list[Dice]:
        """
        Get list of currently available dices
        :return list[model.Dice]
        """
        return [
            Dice.from_dict(dice_json)
            for dice_json in (await self.get("/v1/dices"))["diceList"]
        ]

    async def get_invitation_code(self) -> MultiInvitationCodeInfo:
        """
        Get info about new user invitation code
        :return: model.MultiInvitationCodeInfo
        """
        return MultiInvitationCodeInfo.from_dict(await self.get("/v1/users/multi-invitation-code"))

    async def follow(self, user_id: int) -> None:
        """
        Follow user profile
        :param user_id: target user id
        :return:
        """
        await self.post_empty(f"/v1/users/membership/{user_id}")

    async def unfollow(self, user_id: int) -> None:
        """
        Unfollow user profile
        :param user_id: target user id
        :return:
        """
        await self.delete(f"/v1/users/membership/{user_id}")

    async def get_blocked_items(
        self,
        reference: CircleReference,
        items_type: Union[EObjectType, int],
        size: int = 30,
        page_token: Optional[str] = None
    ) -> PaginatedList[BlockedItemWrapper]:
        """
        Get blocked items in the circle
        :param reference: circle id | circle link | z id
        :param items_type: ObjectType enum field or type identifier
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[BlockedItemWrapper]
        """
        resp = await self.get(f"/v1/circles/{await self._resolve_circle_reference(reference)}/blocked-items", {
            "objectType": items_type.value if isinstance(items_type, EObjectType) else items_type,
            "size": size
        } if page_token is None else {
            "objectType": items_type.value if isinstance(items_type, EObjectType) else items_type,
            "size": size,
            "page_token": page_token
        })
        return PaginatedList(
            [BlockedItemWrapper.from_dict(item_json) for item_json in resp["list"]],
            resp.get("pagination")
        )

    async def get_blocked_blogs(
        self,
        reference: CircleReference,
        size: int = 30,
        page_token: Optional[str] = None
    ) -> PaginatedList[Blog]:
        """
        Get blogs blocked in the selected circle
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[Blog]
        """
        wrappers = await self.get_blocked_items(reference, EObjectType.BLOG, size, page_token)
        return PaginatedList(
            list(map(
                lambda x: x.blog,
                filter(lambda x: x.blog is not None, wrappers)
            )),
            next_page_token=wrappers.next_page_token
        )

    async def get_blocked_chats(
        self,
        reference: CircleReference,
        size: int = 30,
        page_token: Optional[str] = None
    ) -> PaginatedList[Chat]:
        """
        Get chats blocked in the selected circle
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[Chat]
        """
        wrappers = await self.get_blocked_items(reference, EObjectType.CHAT, size, page_token)
        return PaginatedList(
            list(map(
                lambda x: x.chat,
                filter(lambda x: x.chat is not None, wrappers)
            )),
            next_page_token=wrappers.next_page_token
        )

    async def block_item(self, reference: CircleReference, item_id: int, item_type: Union[EObjectType, int]) -> None:
        """
        Block item in the selected circle
        :param reference: circle id | circle link | z id
        :param item_id: id of the item
        :param item_type: ObjectType enum field or type identifier
        :return:
        """
        await self.post_json(f"/v1/circles/{await self._resolve_circle_reference(reference)}/blocked-items", {
            "objectId": item_id,
            "objectType": item_type.value if isinstance(item_type, EObjectType) else item_type
        })

    async def unblock_item(self, reference: CircleReference, item_id: int) -> None:
        """
        Unblock item in the selected circle
        :param reference: circle id | circle link | z id
        :param item_id: id of the item
        :return:
        """
        await self.delete(f"/v1/circles/{await self._resolve_circle_reference(reference)}/blocked-items/{item_id}")

    async def change_chat_online_status(self, chat_id: int, *, is_online: bool) -> None:
        """
        Enable or disable the chat
        :param chat_id: id of the chat
        :param is_online: True | False
        :return:
        """
        await self.post_json(f"/v1/chat/threads/{chat_id}/party-online-status", {
            "partyOnlineStatus": 1 if is_online else 2
        })

    async def remove_circle_member(
        self,
        reference: CircleReference,
        member_id: int,
        *,
        block_member: bool,
        remove_content: bool
    ) -> None:
        """
        Kick or ban circle member
        :param reference: circle id | circle link | z id
        :param member_id: id of the member
        :param block_member: is it required to ban member
        :param remove_content: is it required to remove all content posted by member
        :return:
        """
        await self.post_json(f"/v1/circles/{await self._resolve_circle_reference(reference)}/members/{member_id}", {
            "type": "block" if block_member else "remove",
            "removeContent": remove_content
        })

    async def kick_circle_member(
        self,
        reference: CircleReference,
        member_id: int,
        *,
        remove_content: bool = False
    ) -> None:
        """
        Kick circle member
        :param reference: circle id | circle link | z id
        :param member_id: id of the member
        :param remove_content: is it required to remove all content posted by member
        :return:
        """
        await self.remove_circle_member(reference, member_id, block_member=False, remove_content=remove_content)

    async def ban_circle_member(
        self,
        reference: CircleReference,
        member_id: int,
        *,
        remove_content: bool = False
    ) -> None:
        """
        Ban circle member
        :param reference: circle id | circle link | z id
        :param member_id: id of the member
        :param remove_content: is it required to remove all content posted by member
        :return:
        """
        await self.remove_circle_member(reference, member_id, block_member=True, remove_content=remove_content)

    async def unban_circle_member(self, reference: CircleReference, member_id: int) -> None:
        """
        Unban circle member
        :param reference: circle id | circle link | z id
        :param member_id: id of the member
        :return:
        """
        await self.post_json(f"/v1/circles/{await self._resolve_circle_reference(reference)}/members/{member_id}", {
            "type": "unblock"
        })

    async def remove_chat_member(
        self,
        chat_id: int,
        member_id: int,
        *,
        block_member: bool,
        remove_content: bool
    ) -> None:
        """
        Kick or ban chat member
        :param chat_id: id of the chat
        :param member_id: id of the member
        :param block_member: is it required to ban member
        :param remove_content: is it required to remove all content sent by member
        :return:
        """
        await self.delete(f"/v1/chat/threads/{chat_id}/members/{member_id}", {
            "block": block_member,
            "removeContent": remove_content
        })

    async def kick_chat_member(self, chat_id: int, member_id: int, *, remove_content: bool = False) -> None:
        """
        Kick chat member
        :param chat_id: id of the chat
        :param member_id: id of the member
        :param remove_content: is it required to remove all content posted by member
        :return:
        """
        await self.remove_chat_member(chat_id, member_id, block_member=False, remove_content=remove_content)

    async def ban_chat_member(self, chat_id: int, member_id: int, *, remove_content: bool = False) -> None:
        """
        Ban chat member
        :param chat_id: id of the chat
        :param member_id: id of the member
        :param remove_content: is it required to remove all content posted by member
        :return:
        """
        await self.remove_chat_member(chat_id, member_id, block_member=True, remove_content=remove_content)

    async def invite_to_chat(self, chat_id: int, invited_users: Union[str, list[str]]) -> None:
        """
        Invite a new user to the chat
        :param chat_id: id of the chat
        :param invited_users: id(s) of the user(s)
        :return:
        """
        await self.post_json(f"/v1/chat/threads/{chat_id}/members-invite", {
            "invitedUids": [invited_users] if isinstance(invited_users, str) else invited_users
        })

    async def delete_chat_message(self, chat_id: int, message_id: int) -> None:
        """
        Delete a message from the chat
        :param chat_id: id of the chat
        :param message_id: id of the message
        :return:
        """
        await self.delete(f"/v1/chat/threads/{chat_id}/messages/{message_id}")

    async def upload_file(self,
                          file: Union[bytes, AsyncBufferedReader],
                          target: Union[EUploadTarget, int],
                          duration: int = 0,
                          *,
                          raw_output: bool = False) -> Union[dict, Media]:
        """
        Upload a file to the Project Z server
        :param file: file object returned by aiofiles.open or raw in-memory byte buffer
        :param target: UploadTarget enum field or int identifier
        :param duration: audio duration in milliseconds or 0
        :param raw_output: is it required to return dictionary object instead of model.Media
        :return: dict | model.Media
        """
        file_content = await file.read() if isinstance(file, AsyncBufferedReader) else file
        target = target if isinstance(target, int) else target.value
        writer = MultipartWriter()
        part = writer.append(file_content, {"Content-Type": from_buffer(file_content, mime=True)})
        part.set_content_disposition(
            "form-data",
            name="media",
            filename=file.name if isinstance(file, AsyncBufferedReader) else "file"
        )
        resp = await self.post(f"/v1/media/upload?target={target}&duration={duration}",
                               writer,
                               content_type=f"multipart/form-data; boundary={writer.boundary}")
        return resp if raw_output else Media.from_dict(resp)

    def on_message(self, text: Optional[str] = None):
        """
        A high-level decorator for registering message handlers with a specific text.
        :param text: text of the messages
        :return:
        """
        def decorator(handler: Callable[[ChatMessage], Any]):
            self.register_chat_message_handler(handler, lambda x: (x.content == text) if text is not None else True)

        return decorator

    def on_command(self, text: str, prefix: Optional[str] = None):
        """
        A high-level decorator for registering message handlers with a commands with a specific text.
        The command differs from the message in that it has a prefix.
        :param text: text of the messages
        :param prefix: The prefix of the command. By default, the prefix passed to the Client arguments is used.
        :return:
        """
        return self.on_message(f"{prefix or self.commands_prefix}{text}")

    def register_chat_message_handler(
        self,
        handler: Callable[[ChatMessage], Any],
        content_filter: Callable[[ChatMessage], bool] = lambda _: True,
        content_transform: Callable[[ChatMessage], Any] = lambda x: x
    ) -> None:
        """
        Register handler to receive new message events from the server
        :param handler: function(model.ChatMessage) -> Any
        :param content_filter: function(model.ChatMessage) -> bool
        :param content_transform: function(model.ChatMessage) -> Any
        :return:
        """
        self.websocket.subscribe(handler, lambda x: isinstance(x, ChatMessage) and content_filter(x), content_transform)
