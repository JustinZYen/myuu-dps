from pokemon import *
import copy
def baton_pass(src_pkmn:TeamPokemon, dst_pkmn:TeamPokemon):
    undo_info = {}
    undo_info["pkmn"] = dst_pkmn
    undo_info["stat_boosts"] = copy.copy(dst_pkmn.stat_boosts) # Might not need to copy
    undo_info["other_boosts"] = copy.copy(dst_pkmn.other_boosts) # Might not need to copy
    dst_pkmn.stat_boosts = copy.copy(src_pkmn.stat_boosts)
    dst_pkmn.other_boosts = copy.copy(src_pkmn.other_boosts)
    return undo_info

def undo_baton_pass(undo_info):
    pkmn = undo_info["pkmn"]
    pkmn.stat_boosts = undo_info["stat_boosts"]
    pkmn.other_boosts = undo_info["other_boosts"]

def get_type_multiplier(move_type: str, pkmn_types: set[str]):
    multiplier = 1
    if move_type == "dark":
        if "fighting" in pkmn_types:
            multiplier /= 2
        if "psychic" in pkmn_types:
            multiplier *= 2
        if "ghost" in pkmn_types:
            multiplier *= 2
        if "dark" in pkmn_types:
            multiplier /= 2
        if "fairy" in pkmn_types:
            multiplier /= 2
    elif move_type == "ghost":
        if "normal" in pkmn_types:
            multiplier *= 0
        if "psychic" in pkmn_types:
            multiplier *= 2
        if "ghost" in pkmn_types:
            multiplier *= 2
        if "dark" in pkmn_types:
            multiplier /= 2
    else:
        raise ValueError(f"Unrecognized move type {move_type}")
    return multiplier