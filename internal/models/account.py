from dataclasses import dataclass
from .user_profile import UserProfile


@dataclass
class Account:
    sId: str
    secret: str
    uid: str
    status: int
    email: str
    created_time: int
    device_id: str
    has_profile: bool
    has_password: bool
    current_device_id: str
    current_device_id_two: str
    registered_device_id: str
    registered_device_id_two: str
    registered_ip_v4: str
    last_login_ip_v4: str
    user_profile: UserProfile
