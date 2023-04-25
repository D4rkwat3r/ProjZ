from .api import RequestManager
from .api.headers import ABCHeadersProvider
from .api.headers import RPCHeadersProvider
from .api.control import RPC
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

CircleReference = Union[Circle, str, int]


class Client(RequestManager):
    def __init__(
        self,
        provider: Optional[ABCHeadersProvider] = None,
        http_logging: bool = False,
        ws_logging: bool = False,
        *args,
        **kwargs
    ):
        super().__init__(provider or RPCHeadersProvider(), logging=http_logging, *args, **kwargs)
        self.websocket = WebsocketListener(self, logging=ws_logging)
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

    async def _login(self, email: Optional[str], phone_number: Optional[str], password: str) -> AuthResult:
        data = {"password": password}
        if email is not None:
            data["email"] = email
            data["authType"] = AuthType.EMAIL.value
        elif phone_number is not None:
            data["phoneNumber"] = phone_number
            data["authType"] = AuthType.PHONE_NUMBER.value
        resp = AuthResult.from_dict(await self.post_json("/v1/auth/login", data))
        await self._auth(resp)
        return resp

    async def login_email(self, email: str, password: str) -> AuthResult:
        """
        Login to account by email
        :param email: email address
        :param password: account password
        :return: model.AuthResponse
        """
        return await self._login(email=email, password=password, phone_number=None)
    
    async def login_phone_number(self, phone_number: str, password: str) -> AuthResult:
        """
        Login to account by phone number
        :param phone_number: phone number
        :param password: account password
        :return: model.AuthResponse
        """
        return await self._login(phone_number=phone_number, password=password, email=None)

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
        purpose: Union[AuthPurpose, int] = AuthPurpose.LOGIN
    ) -> None:
        data = {
            "purpose": purpose.value if isinstance(purpose, AuthPurpose) else purpose,
            "countryCode": self.country_code
        }
        if email is not None:
            data["authType"] = AuthType.EMAIL.value
            data["email"] = email
        elif phone_number is not None:
            data["authType"] = AuthType.PHONE_NUMBER.value
            data["phoneNumber"] = phone_number
        await self.post_json("/v1/auth/request-security-validation", data)

    async def request_email_validation(self, email: str, purpose: Union[AuthPurpose, int] = AuthPurpose.LOGIN) -> None:
        """
        Send verification code to email
        :param email: email address
        :param purpose: AuthPurpose.LOGIN, AuthPurpose.CHANGE_EMAIL, custom value...
        :return:
        """
        return await self._request_security_validation(email=email, purpose=purpose, phone_number=None)

    async def request_phone_validation(self, phone_number: str, purpose: Union[AuthPurpose, int] = AuthPurpose.LOGIN) -> None:
        """
        Send verification code to phone number
        :param phone_number: phone number
        :param purpose: AuthPurpose.LOGIN, AuthPurpose.CHANGE_PHONE, custom value...
        :return:
        """
        return await self._request_security_validation(phone_number=phone_number, purpose=purpose, email=None)

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
            data["authType"] = AuthType.EMAIL.value
            data["email"] = email
        elif phone_number is not None:
            data["authType"] = AuthType.PHONE_NUMBER.value
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
        gender_type: Gender,
        birthday: str,
        code: str,
        name_card_background: Optional[Media] = None,
        invitation_code: Optional[str] = None,
        update_auth_credentials: bool = True
    ) -> AuthResult:
        data = {
            "purpose": 1,
            "password": password,
            "securityCode": code,
            "invitationCode": invitation_code or "",
            "nickname": nickname,
            "tagLine": tag_line,
            "icon": icon.to_dict(),
            "nameCardBackground": name_card_background.to_dict() if name_card_background is not None else None,
            "gender": gender_type.value,
            "birthday": birthday,
            "requestToBeReactivated": False,
            "countryCode": self.country_code,
            "suggestedCountryCode": self.country_code.upper(),
            "ignoresDisabled": True,
            "rawDeviceIdThree": await self.provider.generate_device_id_three(
                "BU0gJ0gB5TFcCfN329Vx",
                "android",
                f"{randint(1, 12)}.{randint(1, 12)}.{randint(1, 12)}",
                "ASUS_Z09MN",
                "default"
            )
        }
        if email is not None:
            data["authType"] = AuthType.EMAIL.value
            data["email"] = email
        elif phone_number is not None:
            data["authType"] = AuthType.PHONE_NUMBER.value
            data["phoneNumber"] = phone_number
        resp = await self.post_json("/v1/auth/register", data)
        resp = AuthResult.from_dict(resp)
        if update_auth_credentials: await self._auth(resp)
        return AuthResult.from_dict(resp)

    async def register_email(
        self,
        email: str,
        password: str,
        nickname: str,
        tag_line: str,
        icon: Media,
        gender_type: Gender,
        birthday: str,
        code: str,
        name_card_background: Optional[Media] = None,
        invitation_code: Optional[str] = None,
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
            update_auth_credentials
        )

    async def register_phone(
        self,
        phone_number: str,
        password: str,
        nickname: str,
        tag_line: str,
        icon: Media,
        gender_type: Gender,
        birthday: str,
        code: str,
        name_card_background: Optional[Media] = None,
        invitation_code: Optional[str] = None,
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
            update_auth_credentials
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
                           message_type: Union[ChatMessageType, int] = 1,
                           content: Optional[str] = None,
                           reply_to: Optional[int] = None,
                           message_rich_format: Optional[RichFormat] = None,
                           attached_media: Optional[Media] = None,
                           attached_audio: Optional[Media] = None,
                           poll_id: Optional[int] = None,
                           dice_id: Optional[int] = None) -> ChatMessage:
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
        if reply_to is not None: data["extensions"]["replyMessage"] = reply_to
        if message_rich_format is not None: data["richFormat"] = message_rich_format.to_dict()
        if attached_media is not None: data["media"] = attached_media.to_dict()
        if attached_audio is not None: data["media"] = attached_audio.to_dict()
        if poll_id is not None: data["extensions"]["pollId"] = poll_id
        if dice_id is not None: data["extensions"]["diceId"] = dice_id
        resp = await self.websocket.send_request(1, True, seq_id, **dict(threadId=thread_id, msg=data))
        return await self.get_chat_message(resp["threadId"], resp["messageId"])

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
        thread_type: ChatThreadType = ChatThreadType.ONE_ON_ONE,
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

    async def get_recommended_user_namecards(self, size: int = 100, gender_type: Union[Gender, int] = 0) -> list[User]:
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

    async def get_circle_chats(self,
                               reference: CircleReference,
                               size: int = 30,
                               page_token: Optional[str] = None,
                               with_pin: bool = False) -> PaginatedList[Chat]:
        """
        Get control chats in the circle
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :param page_token: stored in PaginatedList.next_page_token
        :param with_pin: include pinned chats
        :return: PaginatedList[model.Chat]
        """
        resp = await self.get(f"/v1/chat/threads", {
            "type": "circle",
            "objectId": await self._resolve_circle_reference(reference),
            "size": size,
            "withPin": with_pin
        } if page_token is None else {
            "type": "circle",
            "objectId": await self._resolve_circle_reference(reference),
            "size": size,
            "withPin": with_pin,
            "pageToken": page_token
        })
        return PaginatedList(
            [Chat.from_dict(user_json) for user_json in resp["list"]],
            resp.get("pagination")
        )

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

    async def send_qi(self, object_id: int, target_type: Union[ObjectType, int] = 1, count: int = 1) -> QiVoteInfo:
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

    async def get_chat_managers(self, chat_id: int, only_co_hosts: bool = False) -> list[User]:
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
                               only_active_members: bool = False,
                               exclude_manager: bool = False,
                               query_word: str = "",
                               page_token: Optional[str] = None) -> PaginatedList[User]:
        """
        Get list of chat members
        :param chat_id: id of the chat
        :param size: size of the list
        :param only_active_members: include only active members
        :param exclude_manager: exclude management team
        :param query_word: search query
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.User]
        """
        resp = await self.get(f"/v1/chat/threads/{chat_id}/members", {
            "onlyActiveMember": only_active_members,
            "size": size,
            "isExcludeManger": exclude_manager,
            "queryWord": query_word
        } if page_token is None else {
            "onlyActiveMember": only_active_members,
            "size": size,
            "isExcludeManger": exclude_manager,
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
                                 members_type: str = "normal",
                                 exclude_manager: bool = False,
                                 page_token: Optional[str] = None) -> PaginatedList[User]:
        """
        Get list of circle members
        :param reference: circle id | circle link | z id
        :param size: size of the list
        :param members_type: members filter, default: normal
        :param exclude_manager: exclude management team
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.User]
        """
        resp = await self.get(f"/v1/circles/{await self._resolve_circle_reference(reference)}/members", {
            "type": members_type,
            "size": size,
            "isExcludeManger": exclude_manager
        } if page_token is None else {
            "type": members_type,
            "size": size,
            "isExcludeManger": exclude_manager,
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
        return Poll.from_dict(await self.post_json("/v1/polls", {
            "title": title,
            "pollItemList": [
                {"content": item[0]} if len(item) != 2 or item[1] is None else
                {"content": item[0], "icon": item[1]}
                for item in poll_items
            ]
        }))

    async def get_categories(self,
                             target_type: Union[ObjectType, int] = 5,
                             target_region: Union[ContentRegion, int] = 1) -> list[Category]:
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
                          filter_type: Union[CircleFilterType, str] = "recommend",
                          size: int = 30,
                          category_id: int = 0,
                          page_token: Optional[str] = None) -> PaginatedList[Circle]:
        """
        Get circles attached to specified category
        :param filter_type: CircleFilterType enum field or filter identifier (default: recommend)
        :param size: size of the list
        :param category_id: id of the category, 0 for all categories
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Circle]
        """
        resp = await self.get("/v1/circles", {
            "type": filter_type,
            "size": size,
            "categoryId": category_id
        } if page_token is None else {
            "type": filter_type,
            "size": size,
            "categoryId": category_id,
            "pageToken": page_token
        })
        return PaginatedList(
            [Circle.from_dict(circle_json) for circle_json in resp["list"]],
            resp.get("pagination")
        )

    async def get_latest_circles(self,
                                 size: int = 30,
                                 category_id: int = 0,
                                 page_token: Optional[str] = None) -> PaginatedList[Circle]:
        """
        Get circles with filter_type=latest
        :param size: size of the list
        :param category_id: id of the category, 0 for all categories
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Circle]
        """
        return await self.get_circles(CircleFilterType.LATEST, size, category_id, page_token)

    async def get_recommended_circles(self,
                                      size: int = 30,
                                      category_id: int = 0,
                                      page_token: Optional[str] = None) -> PaginatedList[Circle]:
        """
        Get circles with filter_type=recommend
        :param size: size of the list
        :param category_id: id of the category, 0 for all categories
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Circle]
        """
        return await self.get_circles(CircleFilterType.RECOMMEND, size, category_id, page_token)

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
                           parent_type: Union[ObjectType, int],
                           parent_id: int,
                           size: int = 30,
                           reply_id: int = 0,
                           only_pinned: bool = False,
                           page_token: Optional[str] = None) -> PaginatedList[Comment]:
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

    async def get_blog_comments(self,
                                parent_id: int,
                                size: int = 30,
                                reply_id: int = 0,
                                only_pinned: bool = False,
                                page_token: Optional[str] = None) -> PaginatedList[Comment]:
        """
        Get list of comments with parent_type=ObjectType.BLOG
        :param parent_id: id of the parent
        :param size: size of the list
        :param reply_id: include only replies to comment with id reply_id
        :param only_pinned: include only pinned comments
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Comment]
        """
        return await self.get_comments(ObjectType.BLOG, parent_id, size, reply_id, only_pinned, page_token)

    async def get_user_comments(self,
                                parent_id: int,
                                size: int = 30,
                                reply_id: int = 0,
                                only_pinned: bool = False,
                                page_token: Optional[str] = None) -> PaginatedList[Comment]:
        """
        Get list of comments with parent_type=ObjectType.USER
        :param parent_id: id of the parent
        :param size: size of the list
        :param reply_id: include only replies to comment with id reply_id
        :param only_pinned: include only pinned comments
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Comment]
        """
        return await self.get_comments(ObjectType.USER, parent_id, size, reply_id, only_pinned, page_token)

    async def comment(self,
                      parent_type: Union[ObjectType, int],
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

    async def comment_blog(self,
                           parent_id: int,
                           content: Optional[str] = None,
                           media_list: Optional[list[Media]] = None,
                           reply_to: Optional[int] = None) -> Comment:
        """
        Create a comment with parent_type=ObjectType.BLOG
        :param parent_id: id of the parent
        :param content: text content of the comment
        :param media_list: attachments of the comment
        :param reply_to: reply to the comment id
        :return: model.Comment
        """
        return await self.comment(ObjectType.BLOG, parent_id, content, media_list, reply_to)

    async def comment_profile(self,
                              parent_id: int,
                              content: Optional[str] = None,
                              media_list: Optional[list[Media]] = None,
                              reply_to: Optional[int] = None) -> Comment:
        """
        Create a comment with parent_type=ObjectType.USER
        :param parent_id: id of the parent
        :param content: text content of the comment
        :param media_list: attachments of the comment
        :param reply_to: reply to the comment id
        :return: model.Comment
        """
        return await self.comment(ObjectType.USER, parent_id, content, media_list, reply_to)

    async def get_popular_circles(self,
                                  size: int = 30,
                                  category_id: int = 0,
                                  page_token: Optional[str] = None) -> PaginatedList[Circle]:
        """
        Get circles with filter_type=popular
        :param size: size of the list
        :param category_id: id of the category, 0 for all categories
        :param page_token: stored in PaginatedList.next_page_token
        :return: PaginatedList[model.Circle]
        """
        return await self.get_circles(CircleFilterType.POPULAR, size, category_id, page_token)

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

    async def complete_user_task(self, task_type: Union[UserTaskType, int]):
        """
        Mark user task as completed and get coins
        :param task_type: UserTaskType enum field or custom int value
        :return:
        """
        await self.get_user_tasks()
        resp = await self.post_json("/v1/user-tasks/claim-reward", {
            "type": task_type.value if isinstance(task_type, UserTaskType) else task_type
        })
        await self.accept_gift(resp["giftBox"]["boxId"])

    async def send_gift(
        self,
        user_id: int,
        count: int,
        payment_password: str,
        title: str,
        sending_currency_type: CurrencyType
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
            "toObjectType": ObjectType.USER.value,
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
        mnemonic, key = await RPC.generate_wallet_recovery_data(128, "english")
        await self.post_json("/biz/v1/wallet/0/activate", {
            "paymentPassword": payment_password,
            "securityCode": security_code,
            "identity": self.account.email or self.account.phone_number,
            "authType": AuthType.EMAIL.value if self.account.email is not None else AuthType.PHONE_NUMBER.value,
            "recoveryPhrasePublicKey": key
        })
        return mnemonic

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

    async def upload_file(self,
                          file: Union[bytes, AsyncBufferedReader],
                          target: Union[UploadTarget, int],
                          duration: int = 0,
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
        self.websocket.subscribe(handler, lambda x: isinstance(x, ChatMessage) and content_filter, content_transform)
