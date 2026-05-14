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

    def maximize_swap(self, turns_remaining:int, boss:Boss, team:list[TeamPokemon], use_boosts, old_pkmn:None|TeamPokemon = None)->tuple[list[str], float]:
        """
        Make the swap that maximizes final damage to boss
        Returns actions in reverse order to take advantage of append performance
        """
        if turns_remaining <= 0 or len(team) == 0:
            return ([], 0)
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
            actions, damage = self.maximize_move(turns_remaining, new_boss, new_team, swap_target)
            if damage > best_damage:
                best_actions = actions+[f"Swap to {swap_target}"]
                best_damage = damage
        return (best_actions, best_damage)


    def maximize_move(self, turns_remaining:int, boss:Boss, team:list[TeamPokemon], active:TeamPokemon)->tuple[list[str], float]:
        if turns_remaining <= 0:
            return ([], 0)
        memo_key = repr((turns_remaining, boss, tuple(team), active))
        if memo_key in self.memo:
            return self.memo[memo_key]
        turns_remaining-=1
        best_actions = []
        best_damage = -1
        for move in active.get_move_choices():
            move_result = active.make_move(move)
            if move_result.swap:
                actions, damage = self.maximize_swap(
                    turns_remaining, boss, team, use_boosts=move_result.baton_pass, old_pkmn=active)
            else:
                actions, damage = self.maximize_move(turns_remaining, boss, team, active)
            if move_result.damage + damage > best_damage:
                best_actions = actions+[f"{active} used {move}"]
                best_damage = move_result.damage + damage
            active.undo_move(move, move_result.undo_info)

            # validate correctness
            test_memo_key = repr((turns_remaining+1, boss, tuple(team), active))
            if test_memo_key != memo_key:
                print(f"MOVE: {move} by {active}")
                print(test_memo_key)
                print("----------")
                print(memo_key)
                exit()
        self.memo[memo_key] = (best_actions, best_damage)
        return (best_actions, best_damage)