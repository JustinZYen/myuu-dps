PERFECT_ODDS = False
from move_result import *
import utils
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
    
    def make_move(self, move)->DefaultResult:
        """
        Returns a Result object containing information about the move done
        """
        raise NotImplementedError
    
    def undo_move(self, move, undo_info):
        """
        Undoes a move. undo_info may vary in its type as what must be undone
        will vary from pokemon to pokemon and move to move.
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
        return str(self.get_relevant_fields())
    
    def get_relevant_fields(self):
        return [str(self), self.stat_boosts, self.other_boosts]
        
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
        self._damage = 0
        self.types = set(["water"])

    def take_damage(self, damage, def_type, damage_type):
        neutral_damage = damage / self.get_stat(def_type)
        type_damage = neutral_damage * utils.get_type_multiplier(damage_type, self.types)
        self._damage += type_damage
        return type_damage
        
    def get_relevant_fields(self):
        return super().get_relevant_fields() + [self.types]


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
        
        old_state = self._state
        self._state += 1
        if self._state == 1:
            res = DefaultResult()
        else: # Dead and must switch
            res = DeadResult()
        res.undo_info["state"] = old_state

        if move == "power split":
            #nothing
            pass
        elif move == "guard split":
            res.undo_info["self_def"] = self._stats["def"]
            res.undo_info["self_spd"] = self._stats["spd"]
            res.undo_info["boss_def"] = self.boss._stats["def"]
            res.undo_info["boss_spd"] = self.boss._stats["spd"]

            new_def = (self.boss._stats["def"] + self._stats["def"]) / 2
            self.boss._stats["def"] = new_def
            self._stats["def"] = new_def
            new_spd = (self.boss._stats["spd"] + self._stats["spd"]) / 2
            self.boss._stats["spd"] = new_spd
            self._stats["spd"] = new_spd
        else:
            raise ValueError

        return res
    
    def undo_move(self, move, undo_info):
        if move == "power split":
            self._state = undo_info["state"]
        elif move == "guard split":
            self._state = undo_info["state"]
            self._stats["def"] = undo_info["self_def"]
            self._stats["spd"] = undo_info["self_spd"]
            self.boss._stats["def"] = undo_info["boss_def"]
            self.boss._stats["spd"] = undo_info["boss_spd"]
        else:
            raise ValueError

    def get_relevant_fields(self):
        return super().get_relevant_fields() + [{"_state":self._state}]
        
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
            res =  DefaultResult()
            res.undo_info["eva"] = self.stat_boosts["eva"]
            self.change_stat("eva", 2)
            return res
        elif move == "focus energy":
            res =  DefaultResult()
            res.undo_info["focus energy"] = self.other_boosts["focus energy"]
            self.other_boosts["focus energy"] = True
            return res
        elif move == "baton pass":
            return BatonPassResult()
        elif move == "extreme evoboost":
            res = DefaultResult()
            for stat in ("atk", "def", "spa", "spd", "spe"):
                res.undo_info[stat] = self.stat_boosts[stat]
                self.change_stat(stat, 2)
            res.undo_info["z move"] = self.can_z_move
            self.can_z_move = False
            return res
        else:
            raise ValueError
    
    def undo_move(self, move, undo_info):
        if move == "double team":
            self.stat_boosts["eva"] = undo_info["eva"]
        elif move == "focus energy":
            self.other_boosts["focus energy"] = undo_info["focus energy"]
        elif move == "baton pass":
            pass # nothing to undo
        elif move == "extreme evoboost":
            for stat in ("atk", "def", "spa", "spd", "spe"):
                self.stat_boosts[stat] = undo_info[stat]
            self.can_z_move = undo_info["z move"]
        else:
            raise ValueError

    def get_relevant_fields(self):
        return super().get_relevant_fields() + [{"can_z_move":self.can_z_move}]

class Pangoro(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)
        self._stats = {
            "hp"  : 11,
            "atk" : 381,
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
            hp_damage = self.boss.take_damage(damage, "def", "dark")
            return DamageResult(hp_damage)
        else:
            raise ValueError
    
    def undo_move(self, move, undo_info):
        if move == "power trip":
            pass # nothing to undo
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
            res = DefaultResult()
            res.undo_info["types"] = self.boss.types
            self.boss.types = set(["psychic"])
            return res
        elif move == "trick or treat":
            res = DefaultResult()
            res.undo_info["types"] = self.boss.types
            self.boss.types.add("ghost")
            return res
        elif move == "baton pass":
            return BatonPassResult()
        elif move == "belly drum":
            res = DefaultResult()
            res.undo_info["atk"] = self.stat_boosts["atk"]
            self.change_stat("atk", 6)
            return res
        else:
            raise ValueError
    
    def undo_move(self, move, undo_info):
        if move == "magic powder":
            self.boss.types = undo_info["types"]
        elif move == "trick or treat":
            self.boss.types = undo_info["types"]
        elif move == "baton pass":
            pass # nothing to do
        elif move == "belly drum":
            self.stat_boosts["atk"] = undo_info["atk"]
        else:
            raise ValueError
        

class Scolipede(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)

    def get_move_choices(self)->list[str]:
        moves = ["screech", "baton pass"]
        return moves
    
    def make_move(self, move):
        if move == "screech":
            res = DefaultResult()
            res.undo_info["boss_def"] = self.boss.stat_boosts["def"]
            res.undo_info["self_spe"] = self.stat_boosts["spe"]

            self.boss.change_stat("def", -2)
            # speed boost
            self.change_stat("spe", 1)
            return res
        elif move == "baton pass":
            return BatonPassResult()
        else:
            raise ValueError
        
    def undo_move(self, move, undo_info):
        if move == "screech":
            self.boss.stat_boosts["def"] = undo_info["boss_def"]
            self.stat_boosts["spe"] = undo_info["self_spe"]
        elif move == "baton pass":
            pass
        else:
            raise ValueError
    
class Shieldon(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)
        self.turn = 1
        self._stats = {
            "hp"  : 11,
            "atk" : 5,
            "def" : 6,
            "spa" : 5,
            "spd" : 9,
            "spe" : 5,
        }
        self._state = 0 # 0 = full hp, 1 = after sturdy procs, 2 = dead

    def get_move_choices(self)->list[str]:
        if self._state == 0:
            return ["screech"]
        elif self._state == 1:
            return ["guard split"]
        else:
            raise ValueError # shuckle should be dead at this point
    
    def make_move(self, move):
        if self._state > 1:
            raise ValueError(f"{str(self)} in invalid state {self._state}")
        
        old_state = self._state
        self._state += 1
        if self._state == 1:
            res = DefaultResult()
        else: # Dead and must switch
            res = DeadResult()
        res.undo_info["state"] = old_state

        if move == "screech":
            res.undo_info["def"] = self.boss.stat_boosts["def"]
            self.boss.change_stat("def", -2)
            self._state += 1
        elif move == "guard split":
            res.undo_info["self_def"] = self._stats["def"]
            res.undo_info["self_spd"] = self._stats["spd"]
            res.undo_info["boss_def"] = self.boss._stats["def"]
            res.undo_info["boss_spd"] = self.boss._stats["spd"]
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
            return DefaultResult()
        else: # Dead and must switch
            return DeadResult()
        
    def undo_move(self, move, undo_info):
        if move == "screech":
            self._state = undo_info["state"]
            self.boss.stat_boosts["def"] = undo_info["def"]
        elif move == "guard split":
            self._state = undo_info["state"]
            self._stats["def"] = undo_info["self_def"]
            self._stats["spd"] = undo_info["self_spd"]
            self.boss._stats["def"] = undo_info["boss_def"]
            self.boss._stats["spd"] = undo_info["boss_spd"]
        else:
            raise ValueError

    
    def get_relevant_fields(self):
        return super().get_relevant_fields() + [{"_state":self._state}]
    
class Carbink(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)
        self.turn = 1
        self._stats = {
            "hp"  : 11,
            "atk" : 5,
            "def" : 7,
            "spa" : 5,
            "spd" : 9,
            "spe" : 5,
        }
        self._state = 0 # 0 = full hp, 1 = after sturdy procs, 2 = dead

    def get_move_choices(self)->list[str]:
        if self._state == 0:
            return ["charm"]
        elif self._state == 1:
            return ["guard split"]
        else:
            raise ValueError # shuckle should be dead at this point
    
    def make_move(self, move):
        if self._state > 1:
            raise ValueError(f"{str(self)} in invalid state {self._state}")
        
        old_state = self._state
        self._state += 1
        if self._state == 1:
            res = DefaultResult()
        else: # Dead and must switch
            res = DeadResult()
        res.undo_info["state"] = old_state

        if move == "charm":
            res.undo_info["atk"] = self.boss.stat_boosts["atk"]
            self.boss.change_stat("atk", -2)
            self._state += 1
        elif move == "guard split":
            res.undo_info["self_def"] = self._stats["def"]
            res.undo_info["self_spd"] = self._stats["spd"]
            res.undo_info["boss_def"] = self.boss._stats["def"]
            res.undo_info["boss_spd"] = self.boss._stats["spd"]
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
            return DefaultResult()
        else: # Dead and must switch
            return DeadResult()
    
    def undo_move(self, move, undo_info):
        if move == "screech":
            self._state = undo_info["state"]
            self.boss.stat_boosts["atk"] = undo_info["atk"]
        elif move == "guard split":
            self._state = undo_info["state"]
            self._stats["def"] = undo_info["self_def"]
            self._stats["spd"] = undo_info["self_spd"]
            self.boss._stats["def"] = undo_info["boss_def"]
            self.boss._stats["spd"] = undo_info["boss_spd"]
        else:
            raise ValueError
        
    def get_relevant_fields(self):
        return super().get_relevant_fields() + [{"_state":self._state}]
    
class Annihilape(TeamPokemon):
    def __init__(self, boss):
        super().__init__(boss)
        self._stats = {
            "hp"  : 11,
            "atk" : 361,
            "def" : 9,
            "spa" : 5,
            "spd" : 9,
            "spe" : 5,
        }
        self.hits_taken = 0

    def get_move_choices(self)->list[str]:
        return ["rage fist", "screech"]
    
    def make_move(self, move):
        self.hits_taken += 1
        if move == "rage fist":
            
            base_damage = 50 + min(6, self.hits_taken) * 50
            damage = base_damage * self.get_stat("atk")
            if self.other_boosts["focus energy"]:
                if PERFECT_ODDS:
                    damage *= 1.5
                else:
                    damage *= 1.25
            hp_damage = self.boss.take_damage(damage, "def", "ghost")
            res = DamageResult(hp_damage)
            res.undo_info["hits"] = self.hits_taken -1
            return res
        elif move == "screech":
            res =  DefaultResult()
            res.undo_info["hits"] = self.hits_taken -1
            res.undo_info["def"] = self.boss.stat_boosts["def"]

            self.boss.change_stat("def", -2)
            return res
        else:
            raise ValueError
        
    def undo_move(self, move, undo_info):
        if move == "rage fist":
            self.hits_taken = undo_info["hits"]
        elif move == "screech":
            self.hits_taken = undo_info["hits"]
            self.boss.stat_boosts["def"] = undo_info["def"]
        else:
            raise ValueError
        
    def get_relevant_fields(self):
        return super().get_relevant_fields() + [{"hits_taken":self.hits_taken}]