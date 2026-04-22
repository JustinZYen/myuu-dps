from pokemon import *
from optimizer import Optimizer
import utils

def automatic_optimize():
    boss = Boss()
    team = [Shuckle(boss), Eevee(boss), Pangoro(boss), Smeargle(boss)]
    opt = Optimizer()
    best = opt.maximize_swap(7, boss, team, use_boosts=False)
    print("---ACTION ORDER---")
    print(" | ".join(reversed(best)))
    print("---TOTAL DAMAGE---")
    print(boss.damage)

def manual_optimize():
    boss = Boss()
    shuckle = Shuckle(boss)
    eevee = Eevee(boss)
    pangoro = Pangoro(boss)
    smeargle = Smeargle(boss)
    eevee.make_move("extreme evoboost")
    eevee.make_move("focus energy")

    eevee.make_move("baton pass")
    utils.baton_pass(eevee, pangoro)
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")
    pangoro.make_move("power trip")

    print("---TOTAL DAMAGE---")
    print(boss.damage)
    

if __name__ == "__main__":
    automatic_optimize()
    manual_optimize()
    
