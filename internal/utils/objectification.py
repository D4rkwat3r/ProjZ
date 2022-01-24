from ..models.account import Account
from ..models.resource import Resource
from ..models.media import Media
from ..models.circle import Circle
from ..models.circle_list import CircleList
from ..models.pagination import Pagination
from ..models.link_info import LinkInfo
from ..models.user_profile import UserProfile
from ..models.user_mood import UserMood
from ..models.user_profile_extensions import UserProfileExtensions
from ..models.message import Message
from ..models.user_profile_list import UserProfileList
from ..models.chat import Chat
from ..models.chat_list import ChatList
from ..models.message_list import MessageList
from ..models.old_chat_list import OldChatList

none_type = type(None)

primitives = [
    str,
    int,
    float,
    bool,
    none_type
]


def user_mood(source: dict) -> UserMood:
    return UserMood(
        source.get("type"),
        bool(source.get("onlineStatus"))
    )


def user_profile_extensions(source: dict) -> UserProfileExtensions:
    return UserProfileExtensions(
        source.get("openDaysInRow"),
        source.get("maxOpenDaysInRow"),
        source.get("appRated"),
        source.get("stickerClaimedMask"),
        source.get("socialInviteCount"),
        source.get("lastOpenDate"),
        source.get("chatBubbleColor"),
        source.get("previewBlogIds"),
        source.get("genderModified"),
        source.get("ignoreReviewMode")
    )


def user_profile(source: dict) -> UserProfile:
    return UserProfile(
        source.get("uid"),
        source.get("nickname"),
        source.get("socialId"),
        bool(source.get("socialIdModified")),
        source.get("gender"),
        source.get("status"),
        media(source.get("icon")) if source.get("icon") else None,
        source.get("chatInvitationStatus"),
        user_profile_extensions(source.get("extensions")) if source.get("extensions") else None,
        bool(source.get("onlineStatus")),
        source.get("createdTime"),
        source.get("contentRegion"),
        source.get("contentRegionName"),
        user_mood(source.get("userMood")) if source.get("userMood") else None,
        bool(source.get("showsSchool")),
        source.get("lastActiveTime"),
        source.get("showsLocation"),
        source.get("nameCardEnabled"),
        source.get("matchEnabled"),
        media(source.get("nameCardBackground")) if source.get("nameCardBackground") else None,
        media(source.get("background")) if source.get("background") else None,
        source.get("tagline"),
        source.get("zodiacType"),
        source.get("language"),
        bool(source.get("pushEnabled")),
        source.get("showsJoinedCircles"),
        source.get("birthday"),
        source.get("fansCount"),
        source.get("followingCount"),
        source.get("friendsCount"),
        source.get("commentsCount"),
        source.get("commentPermissionType"),
        source.get("thirdPartyUid")
    )


def account(source: dict) -> Account:
    return Account(
        source.get("sId"),
        source.get("secret"),
        source.get("account").get("uid"),
        source["account"].get("status"),
        source["account"].get("email"),
        source["account"].get("createdTime"),
        source["account"].get("deviceId"),
        bool(source["account"].get("hasProfile")),
        bool(source["account"].get("hasPassword")),
        source["account"].get("currentDeviceId"),
        source["account"].get("currentDeviceId2"),
        source["account"].get("registeredDeviceId"),
        source["account"].get("registeredDeviceId2"),
        source["account"].get("registeredIpv4"),
        source["account"].get("lastLoginIpv4"),
        user_profile(source["userProfile"])
    )


def resource(source: dict) -> Resource:
    return Resource(
        source["width"],
        source["height"],
        source["url"],
        bool(source.get("thumbnail"))
    )


def media(source: dict) -> Media:
    resources = list()
    for res in source["resourceList"]:
        resources.append(
            resource(res)
        )
    return Media(
        source["mediaId"],
        source["baseUrl"],
        resources,
        source
    )


def pagination(source: dict) -> Pagination:
    return Pagination(
        source.get("nextPageToken"),
        source.get("total")
    )


def circle(source: dict) -> Circle:
    return Circle(
        source["circleId"],
        source.get("categoryId"),
        source.get("conceptId"),
        source["socialId"],
        bool(source["socialIdModified"]),
        source["createdTime"],
        source["updatedTime"],
        source["status"],
        source["verifiedStatus"],
        source["name"],
        source["tagline"],
        source["language"],
        source["contentRegion"],
        source["membersCount"],
        source.get("dailyActiveUser"),
        source.get("dailyNewPostCount"),
        source["visibility"],
        media(source["icon"]),
        source
    )


def circle_list(source: dict) -> CircleList[Circle]:
    circles = CircleList(pagination(source["pagination"]))
    for c in source["list"]:
        circles.append(
            circle(c)
        )
    return circles


def link_info(source: dict) -> LinkInfo:
    return LinkInfo(
        source["path"],
        source["objectId"],
        source["objectType"],
        source["shareLink"]
    )


def message(source: dict) -> Message:
    return Message(
        source.get("threadId"),
        source.get("messageId"),
        source.get("uid"),
        source.get("createdTime"),
        source.get("type"),
        source.get("asSummary"),
        source.get("content"),
        user_profile(source.get("author")) if source.get("author") else None
    )


def user_list_default(source: dict, internal: bool = False) -> list[UserProfile]:
    users = []
    if internal:
        for one_user in source:
            users.append(user_profile(one_user))
        return users
    for one_user in source["userList"]:
        users.append(user_profile(one_user))
    return users


def user_list(source: dict) -> UserProfileList[UserProfile]:
    users = UserProfileList(pagination(source["pagination"]))
    for one_user in source["list"]:
        users.append(user_profile(one_user))
    return users


def old_chat_list(source: dict) -> OldChatList[Chat]:
    chats = OldChatList(source["isEnd"])
    for one_chat in source["list"]:
        chats.append(chat(one_chat))
    return chats


def message_list(source: dict) -> MessageList[MessageList]:
    messages = MessageList(pagination(source["pagination"]))
    for one_message in source["list"]:
        messages.append(message(one_message))
    return messages


def chat_list(source: dict) -> ChatList[Chat]:
    chats = ChatList(pagination(source["pagination"]))
    for one_chat in source["list"]:
        chats.append(chat(one_chat))
    return chats


def chat(source: dict) -> Chat:
    return Chat(
        source.get("threadId"),
        source.get("status"),
        source.get("type"),
        source.get("host_uid"),
        source.get("title"),
        media(source.get("icon")) if source.get("icon") else None,
        source.get("content"),
        source.get("latestMessageId"),
        source.get("membersCount"),
        source.get("allMembersCount"),
        media(source.get("background")) if source.get("background") else None,
        source.get("contentRegion"),
        source.get("welcomeMessage"),
        source.get("createdTime"),
        user_list_default(source.get("membersSummary"), True) if source.get("membersSummary") else None,
        source.get("language"),
        source.get("visibility"),
        source.get("rolesCount"),
        message(source.get("latestMessage")) if source.get("latestMessage") else None,
        user_profile(source.get("host")) if source.get("host") else None,
        source.get("qiVotedCount"),
        source.get("usingRoleCount"),
        source.get("talkingMemberCount"),
        source.get("roleplayerCount")
    )
