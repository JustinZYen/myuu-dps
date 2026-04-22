class DefaultResult:
    def __init__(self):
        self.damage = 0
        self.swap = False
        self.baton_pass = False

class DeadResult(DefaultResult):
    def __init__(self):
        super().__init__()
        self.swap = True

class BatonPassResult(DefaultResult):
    def __init__(self):
        super().__init__()
        self.swap = True
        self.baton_pass = True

class DamageResult(DefaultResult):
    def __init__(self, damage:float):
        super().__init__()
        self.damage = damage