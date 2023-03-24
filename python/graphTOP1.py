# %%
from pathlib import Path
from numpy import dot, where, flipud
import pandas as pd
import matplotlib.pyplot as plt
from numpy import where
import datetime
import time
import os
GROUPNAME = ""
FIGHTNAME = "The Omega Protocol (Ultimate)"
FILENAME = "top1"
PHASES = [(1,0,'#9028c4', 'Phase 1: Omega', "o", "p1"),
    (2,0,'#969ac3', 'Phase 2: Omega M/F', "o", "p2"),
    (3,0,'#eb87ca', 'Phase 3: Omega Reconfigured', "o", "p3"),
    (4,0,'blue', 'Phase 4: Blue Screen', "o", "p4"),
    (5,0,'red', 'Phase 5: Run: Dynamis', "o", "p5"),
    (6,0,'green', 'Phase 6: Alpha Omega', "o", "p6"),
    (100,0,'white', 'Cleared', "o", "clear")]
ROLLINGAVG = 100
# Enter the output location below:
# For example "C:/Users/Minty/Desktop/Output"
INPUTLOC = Path(os.path.dirname(__file__)).parents[0].joinpath("output.csv")
OUTPUTLOC = Path(os.path.dirname(__file__)).parents[0].joinpath("Graphs")
COLORLIST = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink", "tab:cyan"]

if __name__=="__main__":
    currentTime = time.time()
    # Load csv, remove duplicates, filter early pulls
    df = pd.read_csv(INPUTLOC)
    df.sort_values(by="LogStartTime")
    df.drop_duplicates(inplace=True)
    df = df[df.FightPercentage <= 98].reset_index()
    df["PullDuration"] = df["PullDuration"].apply(lambda x: x/1000)

    plt.figure(figsize=(8,7))
    plt.title(f"{FIGHTNAME} Progression")
    
    pTrack = []
    # Iterate through phases, and plot on the graph
    # Track the number of pulls for each phase also
    for p in PHASES:
        phase, intermission, color, label, m, _ = p
        newdf = df[(df["LastPhase"] == phase) & (df["LastPhaseIntermission"] == intermission)]
        plt.scatter(newdf.index, newdf["PullDuration"], c=color, s = 100 if color =='orangered' else 20, label = label, marker = m)
        pTrack.append(str(len(newdf.index)))

    plt.legend(loc='upper left')
    plt.xlabel("Pull", fontsize = 18)
    plt.ylabel("Seconds in Combat", fontsize = 18)
    plt.ylim(bottom=0)

    plt.text(-8,225,s = f'Total tracked pulls: {str(len(df.index))}' + 
        "".join( f"\n{PHASES[i][3]}: {pTrack[i]}"  for i in range(len(PHASES))) +
        f'\nTime in Combat: {str(datetime.timedelta(seconds=int(df["PullDuration"].sum())))}'
    )
    
    plt.savefig(OUTPUTLOC.joinpath(f"{FILENAME}_{len(df)}_{currentTime}.png"), dpi=200)
    # %%
    # ROLLING AVERAGE OF PHASES
    newdf = df[["LastPhase", "LastPhaseIntermission"]].copy()
    for phase in PHASES:
        lastPhase, lastPhaseIntermission, _, _, _, id = phase
        newdf[id] = 0
        newdf.loc[(newdf.LastPhase == lastPhase) & (newdf.LastPhaseIntermission == lastPhaseIntermission), id] = 1
        newdf[id] = newdf[id].rolling(ROLLINGAVG, min_periods=1).mean()
    
    for i in range(len(PHASES)):
        name = PHASES[i][3]
        color = COLORLIST[i]
        plt.plot([],[],color=color, label=name, linewidth=3)

    plt.legend(loc="lower left")
    plt.ylim(bottom=0, top=1)
    plt.xlim(0, len(df.index)-1)
    plt.title(f"{GROUPNAME} TOP phase pull distribution (Rolling average of {ROLLINGAVG})")
    plt.stackplot(newdf.index, *[newdf[p[5]] for p in PHASES], colors=COLORLIST)

    # %%
    #### Defamation counts
    glitchCounts = df['P2Glitch'].value_counts()
    defamationCounts = df['P3Defamation'].value_counts()
    p3Plus = df[(df.LastPhase >= 3)]
    glitchConsistencyCounts = p3Plus['P2Glitch'].value_counts()
    print(f"What glitch did they get for P2+ clears?\n{glitchConsistencyCounts}")
    print(f"Glitch amounts\n{glitchCounts}")
    print(f"Defamation counts\n{defamationCounts}")

    # %%
    #### DEFAMATION GRAPH
    defa = [defamationCounts.B, defamationCounts.R]
    plt.pie(defa, startangle=90, autopct = lambda x: '{:.2f}%\n({:.0f})'.format(x, sum(defa)*x/100),
        colors=["dodgerblue","crimson"])
    plt.savefig(OUTPUTLOC.joinpath(f"defamation_{len(df)}.png"), transparent=True)