from pokemon import *
import utils
import copy
class Optimizer:
    def __init__(self):
        self.memo = {}
        # Memo is mapping of (turns_remaining, boss, team, active pokemon) to (actions, damage)
        # Tracks the best possible actions and the damage that they deal given that state
    
    @staticmethod
    def update_boss(boss:Boss, team:list[TeamPokemon], active:TeamPokemon|None = None):
        """
        Updates the boss variable for each team member with a specific boss
        """
        for pokemon in team:
            pokemon.boss = boss
        if active is not None:
            active.boss = boss

    def maximize_swap(self, turns_remaining:int, boss:Boss, team:list[TeamPokemon], use_boosts, old_pkmn:None|TeamPokemon = None)->list[str]:
        """
        Make the swap that maximizes final damage to boss
        Returns actions in reverse order to take advantage of append performance
        """
        if turns_remaining <= 0 or len(team) == 0:
            return []
        best_actions = []
        best_damage = -1
        for i, _ in enumerate(team):
            new_boss = copy.deepcopy(boss)
            new_team = copy.deepcopy(team)
            self.update_boss(new_boss, new_team)
            swap_target = new_team[i]
            new_team.remove(swap_target)
            if use_boosts:
                assert(old_pkmn is not None)
                utils.baton_pass(old_pkmn, swap_target)
            actions = self.maximize_move(turns_remaining, new_boss, new_team, swap_target)
            if new_boss.damage > best_damage:
                best_actions = actions+[f"Swap to {swap_target}"]
                best_damage = new_boss.damage
        boss.damage = best_damage
        return best_actions


    def maximize_move(self, turns_remaining:int, boss:Boss, team:list[TeamPokemon], active:TeamPokemon)->list[str]:
        if turns_remaining <= 0:
            return []
        memo_key = repr((turns_remaining, boss, tuple(team), active))
        # if memo_key in self.memo:
        #     actions, damage = self.memo[memo_key]
        #     boss.damage = damage
        #     return actions
        turns_remaining-=1
        best_actions = []
        best_damage = -1
        for move in active.get_move_choices():
            new_boss = copy.deepcopy(boss)
            new_team = copy.deepcopy(team)
            new_active = copy.deepcopy(active)
            self.update_boss(new_boss, new_team, new_active)

            swap, baton_pass = new_active.make_move(move)
            if swap:
                actions = self.maximize_swap(
                    turns_remaining, new_boss, new_team, use_boosts=baton_pass, old_pkmn=new_active)
            else:
                actions = self.maximize_move(turns_remaining, new_boss, new_team, new_active)
            if new_boss.damage > best_damage:
                best_actions = actions+[f"{new_active} used {move}"]
                best_damage = new_boss.damage
        boss.damage = best_damage
        self.memo[memo_key] = (best_actions, best_damage)
        return best_actions