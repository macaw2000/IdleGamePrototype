class Character:
    def __init__(self):
        self.health = 100
        self.strength = 10
        self.level = 1

    def level_up(self):
        self.level += 1
        self.strength += 5
        self.health += 20
