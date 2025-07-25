class Reward:
    def __init__(self, reason: str, *, experience: int = 0, coins: int = 0):
        self.reason = reason
        self.experience = experience
        self.coins = coins

    def __add__(self, other):
        if isinstance(other, Reward):
            return Reward(
                reason=f"{self.reason}\n{other.reason}",
                experience=self.experience + other.experience,
                coins=self.coins + other.coins
            )
        raise TypeError("Can only add another Reward instance")

    def is_empty(self):
        return all([
            self.experience == 0,
            self.coins == 0,
        ])

    def __repr__(self):
        return f"Reward(reason={self.reason}, experience={self.experience}, coins={self.coins})"