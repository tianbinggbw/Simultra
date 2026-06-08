"""
说话人管理器
管理会议中的发言人和用户分配关系
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

class SpeakerManager:
    """说话人管理器"""

    def __init__(self):
        # 发言人到名称的映射
        self._speaker_names: Dict[str, str] = {}
        # 用户分配的发言人
        self._user_assignments: Dict[str, str] = {}  # user_id -> speaker_id
        # 发言统计
        self._speaker_stats: Dict[str, Dict[str, Any]] = {}

    def register_speaker(self, speaker_id: str) -> str:
        """
        注册新发言人

        Args:
            speaker_id: 发言人ID

        Returns:
            分配的默认名称
        """
        if speaker_id not in self._speaker_names:
            # 自动分配名称
            count = len(self._speaker_names) + 1
            default_name = f"Speaker_{count}"
            self._speaker_names[speaker_id] = default_name

            # 初始化统计
            self._speaker_stats[speaker_id] = {
                "name": default_name,
                "first_seen": datetime.now().isoformat(),
                "utterance_count": 0,
                "total_duration": 0.0
            }

        return self._speaker_names[speaker_id]

    def set_name(self, speaker_id: str, name: str):
        """
        设置发言人名称

        Args:
            speaker_id: 发言人ID
            name: 新的名称
        """
        self._speaker_names[speaker_id] = name
        if speaker_id in self._speaker_stats:
            self._speaker_stats[speaker_id]["name"] = name

    def get_name(self, speaker_id: str) -> str:
        """获取发言人名称"""
        return self._speaker_names.get(speaker_id, f"Speaker_{speaker_id}")

    def get_speakers(self) -> List[Dict[str, Any]]:
        """获取所有发言人列表"""
        return [
            {
                "speaker_id": sid,
                "name": self._speaker_names.get(sid, f"Speaker_{sid}"),
                "utterance_count": stats.get("utterance_count", 0),
                "first_seen": stats.get("first_seen")
            }
            for sid, stats in self._speaker_stats.items()
        ]

    def update_stats(self, speaker_id: str, duration: float = 0.0):
        """更新发言人统计"""
        if speaker_id in self._speaker_stats:
            self._speaker_stats[speaker_id]["utterance_count"] += 1
            self._speaker_stats[speaker_id]["total_duration"] += duration

    def assign_user(self, user_id: str, speaker_id: str):
        """
        分配用户到发言人

        Args:
            user_id: 用户ID
            speaker_id: 发言人ID
        """
        self._user_assignments[user_id] = speaker_id

    def get_user_speaker(self, user_id: str) -> Optional[str]:
        """获取用户分配的发言人"""
        return self._user_assignments.get(user_id)

    def get_user_assignments(self) -> Dict[str, str]:
        """获取所有用户分配"""
        return self._user_assignments.copy()

    def get_speaker_for_user(self, user_id: str, users: List[Dict[str, Any]]) -> Optional[str]:
        """
        根据用户选择返回推荐发言人

        Args:
            user_id: 当前用户ID
            users: 用户列表

        Returns:
            推荐发言人ID
        """
        # 如果用户已有分配，保持不变
        if user_id in self._user_assignments:
            return self._user_assignments[user_id]

        # 否则返回最近发言的人
        if self._speaker_stats:
            most_active = max(
                self._speaker_stats.items(),
                key=lambda x: x[1].get("utterance_count", 0)
            )
            return most_active[0]

        return None

    def clear(self):
        """清除所有数据"""
        self._speaker_names.clear()
        self._user_assignments.clear()
        self._speaker_stats.clear()