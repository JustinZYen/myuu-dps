from pokemon import *
def baton_pass(src_pkmn:TeamPokemon, dst_pkmn:TeamPokemon):
    dst_pkmn.stat_boosts = src_pkmn.stat_boosts
    dst_pkmn.other_boosts = src_pkmn.other_boosts

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