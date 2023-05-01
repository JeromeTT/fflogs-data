import pandas as pd
df = pd.read_csv("jobs/TOPPhases.csv")
for column in ["TotalTime", "P1Time", "P2Time", "P3Time", "P4Time", "P5Time", "P6Time"]:
    df[column] = df[column].map(lambda x: x[:len(x)-1])
    print(df[column])

df.sort_values(by="TotalDPS", ascending=False, inplace=True)
df["Rank"] = range(1, len(df.index)+1)
df.to_csv("jobs/TOPPhasesNew2.csv", encoding='utf-8', index=False)
