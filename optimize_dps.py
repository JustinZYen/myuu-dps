from pokemon import *
from optimizer import Optimizer

def automatic_optimize():
    boss = Boss()
    team = [Shuckle(Boss), Eevee(Boss), Pangoro(Boss), Smeargle(Boss)]
    opt = Optimizer()
    best = opt.maximize_swap(10, boss, team, use_boosts=False)
    print("---ACTION ORDER---")
    print(" | ".join(reversed(best)))
    print("---TOTAL DAMAGE---")
    print(boss.damage)

def manual_optimize():
    pass

if __name__ == "__main__":
    automatic_optimize()
    
