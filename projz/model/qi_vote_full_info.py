from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from .media import Media
from .qi_vote_info import QiVoteInfo


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class QiVoteFullInfo:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class VoteResources:
        enabled_icon: Optional[Media] = None
        waiting_icon: Optional[Media] = None
        disabled_icon: Optional[Media] = None
        number_background: Optional[Media] = None
        animation_icons: Optional[list[Media]] = None

    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class VoteConfig:
        daily_quota: Optional[int] = None
        first_quota: Optional[int] = None
        waiting_time: Optional[int] = None

    vote_info: Optional[QiVoteInfo] = None
    vote_resources: Optional[VoteResources] = None
    vote_config: Optional[VoteConfig] = None
