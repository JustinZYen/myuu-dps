PERFECT_ODDS = False

class Pokemon:
    def __init__(self):
        self._stats = {
            "hp"  : 1.0,
            "atk" : 1.0,
            "def" : 1.0,
            "spa" : 1.0,
            "spd" : 1.0,
            "spe" : 1.0,
        }
        self.stat_boosts = {
            "atk" : 0,
            "def" : 0,
            "spa" : 0,
            "spd" : 0,
            "spe" : 0,
            "acc" : 0,
            "eva" : 0,
        } # boost stages, not the actual multipliers
        self.other_boosts = {
            "focus energy": False
        }
    
    def get_move_choices(self)->list[str]:
        raise NotImplementedError
    
    def make_move(self, move)->tuple[bool, bool]:
        """
        Returns a tuple of (swap, baton_pass) saying whether a swap should occur and whether stat boosts are passed if so
        """
        raise NotImplementedError
    
    def change_stat(self, stat, stages:int):
        if stages > 0:
            self.stat_boosts[stat] = min(self.stat_boosts[stat]+stages, 6)
        else:
            self.stat_boosts[stat] = max(self.stat_boosts[stat]+stages, -6)

    def get_stat(self, stat)->float:
        # Returns true numeric value of stat
        if stat == "hp":
            return self._stats["hp"] # type: ignore
        elif stat in ("atk", "def", "spa", "spd", "spe"):
            if (stage := self.stat_boosts[stat]) > 0:
                multiplier = (stage+2)/2
            else:
                multiplier = 2/(-stage+2)
            return self._stats[stat] * multiplier # type: ignore
        elif stat in ("acc", "eva"):
            if (stage := self.stat_boosts[stat]) > 0:
                multiplier = (stage+3)/3
            else:
                multiplier = 3/(-stage+3)
            return self._stats[stat] * multiplier # type: ignore
        else:
            raise ValueError(f"Stat {stat} not recognized")
        
    def __repr__(self):
        return str((str(self), self.stat_boosts, self.other_boosts))
    
        
    def __str__(self):
        return type(self).__name__

class Boss(Pokemon):
    def __init__(self):
        super().__init__()
        self._stats = {
            "hp"  : 1.0,
            "atk" : 600,
            "def" : 600,
            "spa" : 600,
            "spd" : 600,
            "spe" : 1.0,
        }
        self.damage = 0
        self.types = set(["water"])

    def take_damage(self, damage, def_type, damage_type):
        neutral_damage = damage / self.get_stat(def_type)
        type_damage = neutral_damage
        if damage_type == "dark":
            if "ghost" in self.types:
                type_damage *= 2
            if "psychic" in self.types:
                type_damage *= 2
        else:
            raise ValueError(f"Damage type {damage_type} not recognized")
        self.damage += type_damage
        
    def __repr__(self):
        return str((str(self), self.stat_boosts, self.other_boosts, self.types))


class TeamPokemon(Pokemon):
    def __init__(self, boss):
        super().__init__()
        self.boss:Boss = boss

class Shuckle(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)
        self.turn = 1
        self._stats = {
            "hp"  : 11,
            "atk" : 5,
            "def" : 9,
            "spa" : 5,
            "spd" : 9,
            "spe" : 5,
        }
        self._state = 0 # 0 = full hp, 1 = after sturdy procs, 2 = dead

    def get_move_choices(self)->list[str]:
        if self._state == 0:
            return ["power split"]
        elif self._state == 1:
            return ["guard split"]
        else:
            raise ValueError # shuckle should be dead at this point
    
    def make_move(self, move):
        if self._state > 1:
            raise ValueError(f"Shuckle in invalid state {self._state}")
        if move == "power split":
            #nothing
            self._state += 1
        elif move == "guard split":
            new_def = (self.boss._stats["def"] + self._stats["def"]) / 2
            self.boss._stats["def"] = new_def
            self._stats["def"] = new_def
            new_spd = (self.boss._stats["spd"] + self._stats["spd"]) / 2
            self.boss._stats["spd"] = new_spd
            self._stats["spd"] = new_spd
            self._state += 1
        else:
            raise ValueError
        if self._state == 1:
            return (False, False)
        else: # Dead and must switch
            return (True, False)
        
class Eevee(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)
        self.can_z_move = True

    def get_move_choices(self)->list[str]:
        moves = ["double team", "baton pass"]
        if self.other_boosts["focus energy"] == False:
            moves.append("focus energy")
        if self.can_z_move:
            moves.append("extreme evoboost")
        return moves
    
    def make_move(self, move):
        if move == "double team":
            self.change_stat("eva", 2)
            return (False, False)
        elif move == "focus energy":
            self.other_boosts["focus energy"] = True
            return (False, False) # Swapping without baton pass
        elif move == "baton pass":
            return (True, True)
        elif move == "extreme evoboost":
            for stat in ("atk", "def", "spa", "spd", "spe"):
                self.change_stat(stat, 2)
            self.can_z_move = False
            return (False, False)
        else:
            raise ValueError

class Pangoro(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)
        self._stats = {
            "hp"  : 11,
            "atk" : 300,
            "def" : 9,
            "spa" : 5,
            "spd" : 9,
            "spe" : 5,
        }

    def get_move_choices(self)->list[str]:
        return ["power trip"]
    
    def make_move(self, move):
        if move == "power trip":
            base_damage = 20
            for stat in self.stat_boosts.values():
                if stat > 0:
                    base_damage += stat*20
            damage = base_damage * self.get_stat("atk")
            if self.other_boosts["focus energy"]:
                if PERFECT_ODDS:
                    damage *= 1.5
                else:
                    damage *= 1.25
            self.boss.take_damage(damage, "def", "dark")
            return (False, False)
        else:
            raise ValueError
        
class Smeargle(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)

    def get_move_choices(self)->list[str]:
        moves = ["magic powder", "trick or treat", "baton pass", "belly drum"]
        return moves
    
    def make_move(self, move):
        if move == "magic powder":
            self.boss.types = set(["psychic"])
            return (False, False)
        elif move == "trick or treat":
            self.boss.types.add("ghost")
            return (False, False) # Swapping without baton pass
        elif move == "baton pass":
            return (True, True)
        elif move == "belly drum":
            self.change_stat("atk", 6)
            return (False, False)
        else:
            raise ValueError
    