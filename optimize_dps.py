from pokemon import *
from optimizer import Optimizer
import utils

def automatic_optimize():
    boss = Boss()
    team = [Shuckle(boss), Eevee(boss), Pangoro(boss), Smeargle(boss)]
    opt = Optimizer()
    best_actions, best_damage = opt.maximize_swap(20, boss, team, use_boosts=False)
    print("---ACTION ORDER---")
    print(" | ".join(reversed(best_actions)))
    print("---TOTAL DAMAGE---")
    print(best_damage)

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
    automatic_optimize()
    manual_optimize()
    
