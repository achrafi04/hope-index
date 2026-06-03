"""
QUALIFICATION MIRACLES — Monte-Carlo of the 2022 World Cup.

We freeze each team's Elo at the eve of the tournament (no hindsight), then
simulate the entire bracket tens of thousands of times. For each team we read
off the probability of reaching each stage. The "qualification miracle" of what
a team ACTUALLY achieved is (1 - P(reaching that stage)) * 100.

Knockout matches model penalty shootouts realistically:
    P(advance) = (1-Draw)*WinShare  +  Draw * (0.5 + tilt*(2E-1))
a shootout is near coin-flip with only a mild Elo tilt.
"""
import pandas as pd
import random
from collections import defaultdict

CUTOFF = "2022-11-20"          # WC2022 kicked off 2022-11-20; use only earlier data
N = 40000
SHOOTOUT_TILT = 0.08           # mild edge to the stronger side in a shootout
random.seed(7)

# ---- pre-tournament Elo -------------------------------------------------
HOME_ADV, DEFAULT = 100.0, 1500.0
def _k(t):
    t=t.lower()
    if "world cup" in t and "qualif" not in t: return 60.0
    if any(x in t for x in ["qualif","euro","copa","african","asian","confederations","nations league","gold cup"]): return 40.0
    if "friendly" in t: return 20.0
    return 30.0
def _gd(g):
    g=abs(g); return 1.0 if g<=1 else (1.5 if g==2 else (11.0+g)/8.0)

def pre_tournament_ratings(csv, cutoff):
    df=pd.read_csv(csv); df["date"]=pd.to_datetime(df["date"])
    df=df[df["date"]<cutoff].sort_values("date").dropna(subset=["home_score","away_score"])
    r={}
    for x in df.itertuples(index=False):
        rh,ra=r.get(x.home_team,DEFAULT),r.get(x.away_team,DEFAULT)
        adv=0.0 if str(x.neutral).upper()=="TRUE" else HOME_ADV
        eh=1/(1+10**((ra-rh-adv)/400))
        sh=1.0 if x.home_score>x.away_score else (0.5 if x.home_score==x.away_score else 0.0)
        k,g=_k(x.tournament),_gd(x.home_score-x.away_score)
        r[x.home_team]=rh+k*g*(sh-eh); r[x.away_team]=ra+k*g*((1-sh)-(1-eh))
    return r

# ---- match models (neutral venue) --------------------------------------
def expected(ra,rb): return 1/(1+10**((rb-ra)/400))

def sim_group_match(ra,rb):
    """Return points (a,b) for a round-robin match. 90-min, draws allowed."""
    e=expected(ra,rb)
    d=0.26*(1-abs(2*e-1))          # draw mass, max when even
    pa=(1-d)*e                     # a wins
    pb=(1-d)*(1-e)                 # b wins
    u=random.random()
    if u<pa:  return 3,0
    if u<pa+pb: return 0,3
    return 1,1

def sim_knockout(ra,rb):
    """Return True if a advances. Realistic shootout on the draw mass."""
    e=expected(ra,rb)
    d=0.22*(1-abs(2*e-1))          # draw-after-ET mass
    win_a=(1-d)*e
    win_b=(1-d)*(1-e)
    u=random.random()
    if u<win_a: return True
    if u<win_a+win_b: return False
    # shootout: near coin-flip, mild tilt
    return random.random() < (0.5 + SHOOTOUT_TILT*(2*e-1))

# ---- 2022 structure -----------------------------------------------------
GROUPS={
 "A":["Netherlands","Senegal","Ecuador","Qatar"],
 "B":["England","United States","Iran","Wales"],
 "C":["Argentina","Poland","Mexico","Saudi Arabia"],
 "D":["France","Australia","Tunisia","Denmark"],
 "E":["Japan","Spain","Germany","Costa Rica"],
 "F":["Morocco","Croatia","Belgium","Canada"],
 "G":["Brazil","Switzerland","Cameroon","Serbia"],
 "H":["Portugal","South Korea","Uruguay","Ghana"],
}
# Round-of-16 pairings (winner X vs runner-up Y)
R16=[("A","B"),("C","D"),("E","F"),("G","H"),("B","A"),("D","C"),("F","E"),("H","G")]

def sim_group(teams,R):
    pts=defaultdict(int)
    for i in range(len(teams)):
        for j in range(i+1,len(teams)):
            a,b=teams[i],teams[j]
            pa,pb=sim_group_match(R.get(a,DEFAULT),R.get(b,DEFAULT))
            pts[a]+=pa; pts[b]+=pb
    # rank by points, random tiebreak (we don't model goal difference)
    order=sorted(teams,key=lambda t:(pts[t],random.random()),reverse=True)
    return order[0],order[1]      # winner, runner-up

def sim_tournament(R):
    w,ru={},{}
    for g,teams in GROUPS.items():
        w[g],ru[g]=sim_group(teams,R)
    # round of 16
    r16=[]
    for x,y in R16:
        a = w[x] if (x,y) in R16[:4] or True else None
    # build the 8 R16 ties explicitly: winner of first vs runner of second
    ties=[(w[x],ru[y]) for x,y in R16]
    stage={t:"Group" for g in GROUPS.values() for t in g}
    # everyone in r16:
    qf_in=[]
    for a,b in ties:
        stage[a]="R16"; stage[b]="R16"
        adv=a if sim_knockout(R.get(a,DEFAULT),R.get(b,DEFAULT)) else b
        qf_in.append(adv)
    # quarter-finals: pair (0,1)(2,3)(4,5)(6,7)
    sf_in=[]
    for i in range(0,8,2):
        a,b=qf_in[i],qf_in[i+1]
        stage[a]=stage[b]="QF"
        sf_in.append(a if sim_knockout(R.get(a,DEFAULT),R.get(b,DEFAULT)) else b)
    # semis: (0,1)(2,3)
    f_in=[]
    for i in range(0,4,2):
        a,b=sf_in[i],sf_in[i+1]
        stage[a]=stage[b]="SF"
        f_in.append(a if sim_knockout(R.get(a,DEFAULT),R.get(b,DEFAULT)) else b)
    # final
    a,b=f_in
    stage[a]=stage[b]="Final"
    champ=a if sim_knockout(R.get(a,DEFAULT),R.get(b,DEFAULT)) else b
    stage[champ]="Champion"
    return stage

# ---- run ----------------------------------------------------------------
R=pre_tournament_ratings("results.csv",CUTOFF)
ORDER=["Group","R16","QF","SF","Final","Champion"]
RANK={s:i for i,s in enumerate(ORDER)}
reach=defaultdict(lambda:defaultdict(int))   # team -> stage -> count of reaching >= stage

for _ in range(N):
    st=sim_tournament(R)
    for team,s in st.items():
        depth=RANK[s]
        for k in range(1,depth+1):           # reached every stage up to depth
            reach[team][ORDER[k]]+=1

def p_reach(team,stage): return reach[team][stage]/N

# actual deepest stage each team reached in 2022
ACTUAL={
 "Argentina":"Champion","France":"Final","Croatia":"SF","Morocco":"SF",
 "Netherlands":"QF","England":"QF","Brazil":"QF","Portugal":"QF",
 "United States":"R16","Australia":"R16","Japan":"R16","Senegal":"R16",
 "Poland":"R16","Switzerland":"R16","Spain":"R16","South Korea":"R16",
}
NAME={"SF":"semi-final","Final":"final","Champion":"title","QF":"quarter-final","R16":"round of 16"}

rows=[]
for team,stage in ACTUAL.items():
    p=p_reach(team,stage)
    rows.append((team,stage,round(p*100,1),round((1-p)*100,1)))
rows.sort(key=lambda r:-r[3])

print(f"Pre-tournament Elo frozen at {CUTOFF} | {N:,} simulations\n")
print(f"{'QUALIFICATION MIRACLES — 2022':40}{'reached':>12}{'prob':>8}{'miracle':>9}")
print("-"*70)
for team,stage,prob,mir in rows:
    print(f"{team:<22}{NAME[stage]:<18}{prob:>6}% {mir:>9}")

print("\nMOROCCO — full path probabilities (pre-tournament):")
for s in ORDER[1:]:
    print(f"  reach {NAME.get(s,s):<14} {p_reach('Morocco',s)*100:>5.1f}%")

import json
out={"miracles":[{"team":t,"stage":s,"prob":p,"miracle":m} for t,s,p,m in rows],
     "morocco_path":{s:round(p_reach("Morocco",s)*100,1) for s in ORDER[1:]},
     "N":N,"cutoff":CUTOFF}
json.dump(out,open("qualification_data.json","w"),indent=2)
print("\n[ok] qualification_data.json written")
