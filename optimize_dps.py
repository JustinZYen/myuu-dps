from pokemon import *
from optimizer import Optimizer
import utils
import itertools

def automatic_optimize(team):
    boss = Boss()
    opt = Optimizer()
    team_pokemon = [constructor(boss) for constructor in team]
    result = opt.maximize_swap(20, boss, team_pokemon, use_boosts=False)
    return result

def manual_optimize():
    boss = Boss()
    shuckle = Shuckle(boss)
    eevee = Eevee(boss)
    pangoro = Pangoro(boss)
    smeargle = Smeargle(boss)
    shuckle.make_move("power split")
    shuckle.make_move("guard split")
    eevee.make_move("double team")
    eevee.make_move("double team")
    eevee.make_move("double team")
    eevee.make_move("focus energy")
    eevee.make_move("extreme evoboost")
    eevee.make_move("baton pass")
    utils.baton_pass(eevee, smeargle)
    smeargle.make_move("magic powder")
    smeargle.make_move("trick or treat")
    smeargle.make_move("belly drum")
    smeargle.make_move("baton pass")
    utils.baton_pass(smeargle, pangoro)
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")

    print("---TOTAL DAMAGE---")
    print(boss._damage)
    

if __name__ == "__main__":
    setup_choices = [Shuckle, Eevee, Smeargle, Scolipede, Shieldon, Carbink]
    damage_choices = [Pangoro, Annihilape]
    results = []
    for setup in itertools.combinations(setup_choices, 5):
        for damage in itertools.combinations(damage_choices, 1):
            team = setup+damage
            print("Team:", team)
            result = automatic_optimize(team)
            results.append(result)
    results.sort(key=lambda result: result[1], reverse=True)
    for i in range(3):
        print("---ACTION ORDER---")
        print(" | ".join(reversed(results[i][0])))
        print("---TOTAL DAMAGE---")
        print(results[i][1])