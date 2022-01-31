from .internal.api.z_http_api import ZHttpAPI
from .internal.api.z_api_request import ZApiRequest
from .internal.api.z_api_response import ZApiResponse
from .internal.utils.objectification import *
from .internal.exceptions.other.unauthorized import Unauthorized
from .internal.websockets.z_websocket_listener import ZWebsocketListener
from .internal.api.z_media_api import ZMediaAPI
from .internal.exceptions.other.message_sending_error import MessageSendingError
from typing import Optional
from typing import Union
from aiofiles import open as async_open
from time import time
from types import FunctionType


class ZClient(ZHttpAPI):
    def __init__(self, device_id: Optional[str] = None, establish_websocket: bool = True) -> None:
        super().__init__()
        self._session = None
        self._websocket = None
        self._media_api = ZMediaAPI()
        self._is_websocket_required = establish_websocket
        if device_id:
            self._headers_template["rawDeviceId"] = device_id

    def get_current_session(self) -> Optional[Account]:
        return self._session

    def change_device_id(self, device_id: Optional[str] = None) -> None:
        if device_id:
            self._headers_template["rawDeviceId"] = device_id
        else:
            self._headers_template["rawDeviceId"] = self._device_id()

    async def login(self, email: str, password: str) -> Account:
        data = {
            "authType": 1,
            "email": email,
            "password": password
        }
        response = await self._post("/v1/auth/login", data)
        self._session = account(response.json)
        self._set_authorization_cookie(self._session.sId)
        if self._is_websocket_required:
            self._websocket = ZWebsocketListener(self)
        return self._session

    async def change_password(self, old_password: str, new_password: str) -> bool:
        data = {
            "newPassword": new_password,
            "oldPassword": old_password
        }
        response = await self._post("/v1/auth/change-password", data)
        return True

    async def get_recommended_circles(self, size: int = 30, page_token: Optional[str] = None) -> CircleList:
        url = "/v1/circles?type=recommend&size=" + str(size)
        if page_token:
            url += "&pageToken=" + page_token
        response = await self._get(url)
        return circle_list(response.json)

    async def get_my_circles(self, size: int = 30, page_token: Optional[str] = None) -> CircleList:
        url = f"/v1/circles?type=joined&categoryId=0&size={str(size)}"
        if page_token:
            url += "&pageToken=" + page_token
        response = await self._get(url)
        return circle_list(response.json)

    async def get_circle_chats(self,
                               circle_id: Optional[int] = None,
                               social_id: Optional[str] = None,
                               circle_link: Optional[str] = None,
                               size: int = 30,
                               page_token: Optional[str] = None) -> ChatList:
        circle_id = await self._circle_id(circle_id, social_id, circle_link)
        url = f"/v1/chat/threads?type=circle&objectId={str(circle_id)}&size={size}"
        if page_token:
            url += "&pageToken=" + page_token
        response = await self._get(url)
        return chat_list(response.json)

    async def circle_info(self, circle_id: int) -> Circle:
        response = await self._get(f"/v1/circles/{str(circle_id)}")
        return circle(response.json)

    async def link_info(self, link: str) -> LinkInfo:
        data = {
            "link": link
        }
        response = await self._post("/v1/links/path", data)
        return link_info(response.json)

    async def join_circle(
            self,
            circle_id: Optional[int] = None,
            social_id: Optional[str] = None,
            circle_link: Optional[str] = None) -> Circle:
        circle_id = await self._circle_id(circle_id, social_id, circle_link)
        response = await self._post(f"/v1/circles/{str(circle_id)}/members")
        return circle(response.json)

    async def leave_circle(
            self,
            circle_id: Optional[int] = None,
            social_id: Optional[str] = None,
            circle_link: Optional[str] = None) -> Circle:
        circle_id = await self._circle_id(circle_id, social_id, circle_link)
        response = await self._delete(f"/v1/circles/{str(circle_id)}/members")
        return circle(response.json)

    async def join_chat(
            self,
            thread_id: int
    ) -> ZApiResponse:
        return await self._post(f"/v1/chat/threads/{thread_id}/members")

    async def leave_chat(
            self,
            thread_id: int) -> ZApiResponse:
        return await self._delete(f"/v1/chat/threads/{thread_id}/members")

    async def send_message(self,
                           thread_id: int,
                           content: str,
                           message_type: int = 1,
                           reply_message_id: Optional[int] = None) -> dict:
        if not self._session:
            raise Unauthorized("You must be logged in to send this action")
        seq_id = int(time() * 1000)
        data = {
            "t": 1,
            "threadId": thread_id,
            "msg": {
                "type": message_type,
                "status": 1,
                "threadId": thread_id,
                "createdTime": int(time() * 1000),
                "uid": self._session.uid,
                "seqId": seq_id,
                "content": content,
                "messageId": message_type,
                "extensions": {
                    "replyMessageId": reply_message_id
                }
            }
        }
        if self._websocket:
            result = await self._websocket.send_json(data, MessageSendingError, seq_id)
        else:
            result = await ZWebsocketListener.send_and_disconnect(self, data, MessageSendingError, seq_id)
        return result

    async def request_security_validation(self, email: str) -> ZApiResponse:
        data = {
            "authType": 1,
            "purpose": 1,
            "email": email,
            "countryCode": "en"
        }
        return await self._post("/v1/auth/request-security-validation", data)

    async def get_chat_messages(self, thread_id: int, size: int = 30, page_token: Optional[str] = None):
        url = f"/v1/chat/threads/{str(thread_id)}/messages"
        url += "?size=" + str(size)
        if page_token:
            url += "&pageToken=" + page_token
        response = await self._get(url)
        return message_list(response.json)

    async def get_my_chats(self, start: int = 0, size: int = 30, chats_type: str = "all"):
        url = f"/v1/chat/joined-threads?start={str(start)}&size={str(size)}&type={chats_type}"
        response = await self._get(url)
        return old_chat_list(response.json)

    async def check_security_validation(self, email: str, code: str) -> bool:
        data = {
            "authType": 1,
            "email": email,
            "securityCode": code
        }
        await self._post("/v1/auth/check-security-validation", data)
        return True

    async def create_account(self,
                             email: str,
                             password: str,
                             security_code: str,
                             nickname: str,
                             tag_line: str,
                             icon_file_name: str,
                             card_background_file_name: str,
                             gender: int = 1,
                             birthday: str = "1900-01-01",
                             set_credentials: bool = False) -> Account:
        await self.check_security_validation(email, security_code)
        data = {
            "authType": 1,
            "purpose": 1,
            "email": email,
            "password": password,
            "phoneNumber": "+7 ",
            "securityCode": security_code,
            "invitationCode": "",
            "secret": "",
            "nickname": nickname,
            "tagLine": tag_line,
            "icon": (await self.upload(icon_file_name, 1)).raw_json,
            "nameCardBackground": (await self.upload(card_background_file_name, 11)).raw_json,
            "gender": gender,
            "birthday": birthday,
            "requestToBeReactivated": False,
            "countryCode": "en",
            "suggestedCountryCode": "EN"
        }
        response = await self._post("/v1/auth/register", data)
        new = account(response.json)
        if set_credentials:
            self._session = new
            self._set_authorization_cookie(self._session.sId)
            if self._is_websocket_required:
                self._websocket = ZWebsocketListener(self)
        return new

    async def get_circle_users(self,
                               circle_id: Optional[int] = None,
                               social_id: Optional[str] = None,
                               circle_link: Optional[str] = None,
                               search_type: str = "normal",
                               size: int = 30,
                               search_query_word: Optional[str] = None,
                               exclude_manager: bool = False,
                               page_token: Optional[str] = None) -> UserProfileList:
        circle_id = await self._circle_id(circle_id, social_id, circle_link)
        url = f"/v1/circles/{str(circle_id)}/members"
        url += "?type=" + search_type
        url += "&size=" + str(size)
        if search_query_word:
            url += "&word=" + search_query_word
        url += "&isExcludeManger=" + str(exclude_manager).lower()
        if page_token:
            url += "&pageToken=" + page_token
        response = await self._get(url)
        return user_list(response.json)

    async def get_circle_admins(self,
                                circle_id: Optional[int] = None,
                                social_id: Optional[str] = None,
                                circle_link: Optional[str] = None) -> UserProfileList:
        circle_id = await self._circle_id(circle_id, social_id, circle_link)
        response = await self._get(f"/v1/circles/{str(circle_id)}/management-team")
        return user_list(response.json)

    async def get_recommended_users(self) -> list[UserProfile]:
        response = await self._get("/v1/onboarding/recommend-users")
        return user_list_default(response.json)

    async def get_circle_active_users(self,
                                      circle_id: Optional[int] = None,
                                      social_id: Optional[str] = None,
                                      circle_link: Optional[str] = None,
                                      size: int = 30,
                                      page_token: Optional[str] = None) -> UserProfileList:
        circle_id = await self._circle_id(circle_id, social_id, circle_link)
        url = f"/v1/circles/{str(circle_id)}/active-members"
        url += "?size=" + str(size)
        if page_token:
            url += "&pageToken=" + page_token
        response = await self._get(url)
        return user_list(response.json)

    async def visit_profile(self, user_id: int) -> ZApiResponse:
        return await self._post(f"/v1/user/profile/{str(user_id)}/visit")

    async def start_chat(self,
                         invite_user_ids: Union[int, list],
                         message_content: str,
                         message_type: int = 1,
                         background_file_name: Optional[str] = None) -> Chat:
        background = (await self.get_default_chat_background()).raw_json if not background_file_name else (
            await self.upload(background_file_name, 1)).raw_json
        data = {
            "type": message_type,
            "status": 1,
            "background": background,
            "inviteMessageContent": message_content,
            "invitedUids": invite_user_ids if isinstance(invite_user_ids, list) else [invite_user_ids]
        }
        response = await self._post("/v1/chat/threads", data)
        return chat(response.json)

    async def verify_captcha(self, captcha_value: str) -> bool:
        data = {
            "captchaValue": captcha_value
        }
        response = await self._web_post("/api/f/v1/risk/verify-captcha", data)
        return response["success"]

    async def _circle_id(self,
                         circle_id: Optional[int] = None,
                         social_id: Optional[str] = None,
                         circle_link: Optional[str] = None
                         ) -> int:
        if circle_id:
            return circle_id
        if social_id:
            return (await self.link_info("https://www.projz.com/s/c/" + social_id)).object_id
        elif circle_link:
            return (await self.link_info(circle_link)).object_id
        if not circle_id:
            raise ValueError("This function cannot be called without arguments")

    async def get_default_chat_background(self) -> Media:
        return media({
            "mediaId": 1448528961146159000,
            "baseUrl": "http://sys.projz.com/4198/1448528961146159104-v1-r1125x2436-s0x0.png",
            "resourceList": [
                {
                    "width": 1125,
                    "height": 2436,
                    "thumbnail": False,
                    "duration": 0,
                    "url": "http://sys.projz.com/4198/1448528961146159104-v1-r1125x2436-s1125x2436.png"
                },
                {
                    "width": 695,
                    "height": 1508,
                    "thumbnail": False,
                    "duration": 0,
                    "url": "http://sys.projz.com/4198/1448528961146159104-v1-r1125x2436-s472x1024.png"
                },
                {
                    "width": 347,
                    "height": 754,
                    "thumbnail": False,
                    "duration": 0,
                    "url": "http://sys.projz.com/4198/1448528961146159104-v1-r1125x2436-s236x512.png"
                }
            ]
        })

    async def upload(self, file_name: str, target: int, duration: int = 0) -> Media:
        response = await self._media_api.upload_file(await async_open(file_name, "rb"), target, duration)
        return media(response.json)

    async def send_custom_request(self, request: ZApiRequest) -> ZApiResponse:
        return await self._send_custom(request)

    # - - - Decorators - - -

    def on_chat_message(self, handler: FunctionType):
        if not self._is_websocket_required:
            if self._session:
                self._websocket = ZWebsocketListener(self)
            self._is_websocket_required = True
        ZWebsocketListener.add(handler, "on_message")
