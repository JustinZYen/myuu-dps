import copy
from pokemon import *

def update_boss(boss:Boss, team:list[TeamPokemon], active:TeamPokemon|None = None):
    """
    Updates the boss variable for each team member with a specific boss
    """
    for pokemon in team:
        pokemon.boss = boss
    if active is not None:
        active.boss = boss

def baton_pass(src_pkmn:TeamPokemon, dst_pkmn:TeamPokemon):
    dst_pkmn.stat_boosts = src_pkmn.stat_boosts
    dst_pkmn.other_boosts = src_pkmn.other_boosts

def maximize_swap(turns_remaining:int, boss:Boss, team:list[TeamPokemon], use_boosts, old_pkmn:None|TeamPokemon = None)->list[str]:
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
        update_boss(new_boss, new_team)
        swap_target = new_team[i]
        new_team.remove(swap_target)
        if use_boosts:
            assert(old_pkmn is not None)
            baton_pass(old_pkmn, swap_target)
        actions = maximize_move(turns_remaining, new_boss, new_team, swap_target)
        if new_boss.damage > best_damage:
            best_actions = actions+[f"Swap to {swap_target}"]
            best_damage = new_boss.damage
    boss.damage = best_damage
    return best_actions


def maximize_move(turns_remaining:int, boss:Boss, team:list[TeamPokemon], active:TeamPokemon)->list[str]:
    if turns_remaining <= 0:
        return []
    turns_remaining-=1
    best_actions = []
    best_damage = -1
    for move in active.get_move_choices():
        new_boss = copy.deepcopy(boss)
        new_team = copy.deepcopy(team)
        new_active = copy.deepcopy(active)
        update_boss(new_boss, new_team, new_active)

        swap, baton_pass = new_active.make_move(move)
        if swap:
            actions = maximize_swap(
                turns_remaining, new_boss, new_team, use_boosts=baton_pass, old_pkmn=new_active)
        else:
            actions = maximize_move(turns_remaining, new_boss, new_team, new_active)
        if new_boss.damage > best_damage:
            best_actions = actions+[f"{new_active} used {move}"]
            best_damage = new_boss.damage
    boss.damage = best_damage
    return best_actions
            
def automatic_optimize():
    boss = Boss()
    team = [Shuckle(Boss), Eevee(Boss), Pangoro(Boss), Smeargle(Boss)]
    best = maximize_swap(9, boss, team, use_boosts=False)
    print("---ACTION ORDER---")
    print(" | ".join(reversed(best)))
    print("---TOTAL DAMAGE---")
    print(boss.damage)

def manual_optimize():
    pass

if __name__ == "__main__":
    automatic_optimize()
    
