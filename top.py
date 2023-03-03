import csv
import requests
import os
import pandas as pd
ENCODED_SECRET = "OTg5OGFmOGUtNzlhNC00MTc1LTk5NjMtNGFmMzI3NDA3MTUyOnZtcXRPOFc1UXp6VnRJR0Q2amFHOFFnNHU3ajU5cUxKYTZOblljdW8=" #os.environ["ENCODED_SECRET"]
GUILD_ID = 103532
NAME = "Minty Evergreen"
REMOTEID = 1003428
MIDID = 1003427
DEFAMATIONID = 1003437
BLUEID = 1003439

def getToken():
    url = "https://www.fflogs.com/oauth/token"
    querystring = {"":""}
    payload = "grant_type=client_credentials"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {ENCODED_SECRET}"
    }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    token = response.json().get("access_token")
    return token

def clientRequest(token, payload):
    url = "https://www.fflogs.com/api/v2/client"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url = url,headers=headers, json={"query": payload})
    return response

def guildQuery(pages, startTime = 0, limit = 100):
    return """{{
        reportData {{
            reports(guildID: 103532, startTime: {0}, limit:{1}, page:{2}){{
                data{{
                    code
                }}
                has_more_pages
            }}
        }}
    }}""".format(startTime, limit, pages)

def reportInfoQuery(code):
    return """{{
        reportData{{
            report(code: "{0}"){{
                startTime
                masterData{{
                    actors(type: "player"){{
                        name
                        id
                    }}
                }}
                fights{{
                    id
                    friendlyPlayers
                    bossPercentage
                    fightPercentage
                    encounterID
                    lastPhase
                    lastPhaseIsIntermission
                    startTime
                    endTime
                }}
            }}
        }}
    }}
    """.format(code)

def reportDebuffQuery(code, abilityID, phase):
    return """{{
        reportData{{
            report(code: "{0}"){{
                events(startTime: 0, endTime: 1000000000, dataType: Debuffs, abilityID: {1}, filterExpression: "encounterPhase = {2}", limit: 10000),{{
                    data
                }}
            }}
        }}
    }}
    """.format(code, abilityID, phase)

if __name__ == "__main__":
    # Get access token
    token = getToken()

    # Get guild logs from online
    logList = []
    hasMore = True
    currentPage = 1
    while hasMore:
        load = guildQuery(pages = currentPage)
        response = clientRequest(token, load)
        reports = response.json()["data"]["reportData"]["reports"]
        hasMore = reports["has_more_pages"]
        logList += [i["code"] for i in reports["data"]]
        currentPage += 1

    # Get guild logs locally
    with open('toplogs.csv') as toplogs_read:
        logListLocal = [line.strip() for line in toplogs_read.readlines()]

    # We want to find all the logs online, which we do not have locally
    logListDifference = list(set(logList).symmetric_difference(set(logListLocal)))
    print("Total : ", logListDifference)

    # Record the new logs
    with open('toplogs.csv', mode='a', newline='') as toplogs_file:
        if len(logListDifference) > 0:
            toplogs_file.write("\n".join(logListDifference)+"\n")

    with open('output.csv', mode='a', newline='') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for id in logListDifference:
            print(f"RETRIEVING LOG WITH ID: {id}")
            response = clientRequest(token, reportInfoQuery(id))
            report = response.json()["data"]["reportData"]["report"]
            startDate = report["startTime"]
            mainPlayerIndex = {p["id"] for p in report["masterData"]["actors"] if p["name"] == NAME}
            fights = report["fights"]

            # Remote Glitch P2 List
            response = clientRequest(token, reportDebuffQuery(id, REMOTEID, 2))
            events = response.json()["data"]["reportData"]["report"]["events"]["data"]
            P2RemoteGlitch = { event["fight"] for event in events }

            # Mid Glitch P2 List
            response = clientRequest(token, reportDebuffQuery(id, MIDID, 2))
            events = response.json()["data"]["reportData"]["report"]["events"]["data"]
            P2MidGlitch = { event["fight"] for event in events }

            response = clientRequest(token, reportDebuffQuery(id, DEFAMATIONID, 3))
            events = response.json()["data"]["reportData"]["report"]["events"]["data"]
            P3Defamation = {}
            for event in events:
                P3Defamation.setdefault(event["fight"], set())
                P3Defamation[event["fight"]].add(event["targetID"])

            response = clientRequest(token, reportDebuffQuery(id, BLUEID, 3))
            events = response.json()["data"]["reportData"]["report"]["events"]["data"]
            P3BlueRot = {}
            for event in events:
                P3BlueRot.setdefault(event["fight"], set())
                P3BlueRot[event["fight"]].add(event["targetID"])

            for fight in fights:
                allPlayerIndexes = set(fight["friendlyPlayers"]) & mainPlayerIndex
                if (fight["encounterID"] == 1068 and len(allPlayerIndexes) > 0):
                    pullNumber = fight["id"]
                    startTime = fight["startTime"] 
                    endTime = fight["endTime"]
                    newDate = startDate + startTime
                    pullDuration = endTime - startTime

                    bossPercentage = fight["bossPercentage"]
                    fightPercentage = fight["fightPercentage"]

                    lastPhase = fight["lastPhase"]
                    lastPhaseIntermission = int(fight["lastPhaseIsIntermission"])
                    
                    glitch = "R" if pullNumber in P2RemoteGlitch else "M" if pullNumber in P2MidGlitch else "N"
                    defamation = ""
                    try:
                        result = P3BlueRot[pullNumber]
                        result &= P3Defamation[pullNumber]
                        defamation = "B" if len(result) > 0 else "R" 
                    except:
                        defamation = "N"
                    assert defamation != ""

                    finalList = [newDate,pullNumber,pullDuration,bossPercentage,fightPercentage,lastPhase,lastPhaseIntermission,glitch,defamation]
                    print(finalList)
                    output_writer.writerow(finalList)
    # Use pandas to sort and clean data, then reexport the csv.
    print("wow")
    df = pd.read_csv("output.csv")
    df.sort_values(by="LogStartTime", inplace=True)
    df.drop_duplicates(inplace=True)
    df.to_csv("output.csv", encoding='utf-8', index=False)