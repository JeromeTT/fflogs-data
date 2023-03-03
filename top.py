import csv
import requests
import os
ENCODED_SECRET = os.environ["ENCODED_SECRET"]
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

if __name__ == "__main__":
    # Get access token
    token = getToken()
    url = "https://www.fflogs.com/api/v2/client"
    payload = "{\"query\":\"{\\n\\treportData{\\n\\t\\treport(code: \\\"WAYVf16tcRHTvPDy\\\"){\\n\\t\\t\\tstartTime\\n\\t\\t\\tmasterData{\\n\\t\\t\\t\\tactors(type: \\\"player\\\"){\\n\\t\\t\\t\\t\\tname\\n\\t\\t\\t\\t\\tid\\n\\t\\t\\t\\t}\\n\\t\\t\\t}\\n\\t\\t\\tfights{\\n\\t\\t\\t\\tid\\n\\t\\t\\t\\tfriendlyPlayers\\n\\t\\t\\t\\tbossPercentage\\n\\t\\t\\t\\tfightPercentage\\n\\t\\t\\t\\tencounterID\\n\\t\\t\\t\\tlastPhase\\n\\t\\t\\t\\tlastPhaseIsIntermission\\n\\t\\t\\t\\tstartTime\\n\\t\\t\\t\\tendTime\\n\\t\\t\\t}\\n\\t\\t}\\n\\t}\\n}\"}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

    with open('output.csv', mode='w') as output_file:
        output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_writer.writerow(["LogStartTime","PullNumber","PullDuration","BossPercentage","FightPercentage","LastPhase","LastPhaseIntermission","P2Glitch","P3Defamation"])