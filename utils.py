from pokemon import *
def baton_pass(src_pkmn:TeamPokemon, dst_pkmn:TeamPokemon):
    dst_pkmn.stat_boosts = src_pkmn.stat_boosts
    dst_pkmn.other_boosts = src_pkmn.other_boosts