class XP:
    def __init__(self, total_xp: int):
        self.total = total_xp

        # Find level by incrementing until XP would exceed total_xp
        self.level = 0
        while self.xp_to_reach_level(self.level + 1) <= self.total:
            self.level += 1

        self.xp_current_level = self.xp_to_reach_level(self.level)
        self.xp_next_level    = self.xp_to_reach_level(self.level + 1)
        self.xp_current_level = self.total - self.xp_current_level

    @staticmethod
    def xp_to_reach_level(level: int) -> int:
        return 100 * level * (level + 1) * (2 * level + 1) // 6

    def __repr__(self):
        return (f"XP(total={self.total}, level={self.level}, current={self.xp_current_level}/{self.xp_next_level})")
