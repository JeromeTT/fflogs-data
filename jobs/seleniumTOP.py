from turtle import goto
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BOSS_ID = 1068
specList = [
 "Astrologian",
 "Bard",
 "BlackMage",
 "DarkKnight",
 "Dragoon",
 "Machinist",
 "Monk",
 "Ninja",
 "Paladin",
 "Scholar",
 "Summoner",
 "Warrior",
 "WhiteMage",
 "RedMage",
 "Samurai",
 "Dancer",
 "Gunbreaker",
 "Reaper",
 "Sage"]

def finder(driver):
    elem = driver.find_element(By.ID, "view-tabs-and-table-container")
    atrString = elem.get_attribute("style")
    #print(atrString)
    return atrString.find("opacity") == -1



def parser(spec):
    for wow in range (2971, 10000):
        page = wow // 100 + 1
        rank = wow % 100 + 1
        boss_url = f"https://www.fflogs.com/zone/rankings/53#metric=dps&boss={BOSS_ID}&page={page}&search=date.0.1678798800000"
        driver.get(boss_url)
        with open(f'jobs/newOutput.txt', 'a') as f:
            print(f"Getting rank: {rank}")
            storage = []
            jobs = []
            id = ""
            actualRank = rank + ((page - 1) * 100)
            storage.append(str(actualRank))
            # Go to rankings page
            driver.get(boss_url)
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#row-{BOSS_ID}-{actualRank} > td.main-table-name > div > div.players-table-name > a")))
            except:
                return
            # Accept cookies or whatever
            try:
                driver.find_element(By.CLASS_NAME, "cc-btn.cc-dismiss").click()
            except:
                pass
            # GET JOB OF CURRENT LOG
            mainJob = driver.find_element(By.CSS_SELECTOR, f"#row-{BOSS_ID}-{actualRank} > td.main-table-name > div > div.players-table-name > img").get_attribute("alt")
            print(mainJob)
            # CLICK ON RANKING
            storage.append(mainJob)
            driver.find_element(By.CSS_SELECTOR, f"#row-{BOSS_ID}-{actualRank} > td.main-table-name > div > div.players-table-name > a").click()
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "filter-source-selection-dropdown")))
            except:
                pass
            
            currentURL = driver.current_url
            # GET URL
            storage.append(currentURL)
            #main-table-row-46-0-2 > td.main-table-name.report-table-name > table > tbody > tr > td:nth-child(1)
            # GET COMPOSITION
            try:
                WebDriverWait(driver, 5).until(finder)
            except:
                pass
            for i in range(1,10):
                huh = driver.find_element(By.XPATH, f"//*[@id=\'main-table-0\']/tbody/tr[{i}]/td[2]/table/tbody/tr/td[1]/img").get_attribute("class")[46:]
                jobs.append(huh)
                if huh == mainJob:
                    huh2 = driver.find_element(By.XPATH, f"//*[@id=\'main-table-0\']/tbody/tr[{i}]/td[2]/table/tbody/tr/td[1]/img").get_attribute("id")
                    id = "main-table-row" + huh2[4:]

            
            storage += ["1" if job in jobs else "0" for job in specList]
            print(storage)
            for phase in range(0,7):
                newURL = currentURL + f"&phase={phase}"
                driver.get(newURL)
                try:
                    WebDriverWait(driver, 5).until(finder)
                except:
                    pass
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id=\'main-table-0\']/tbody/tr[1]/td[1]')))
                if phase != 0:
                    for i in range(1,10):
                        huh = driver.find_element(By.XPATH, f"//*[@id=\'main-table-0\']/tbody/tr[{i}]/td[1]/table/tbody/tr/td[1]/img").get_attribute("class")[46:]
                        if huh == mainJob:
                            huh2 = driver.find_element(By.XPATH, f"//*[@id=\'main-table-0\']/tbody/tr[{i}]/td[1]/table/tbody/tr/td[1]/img").get_attribute("id")
                            id = "main-table-row" + huh2[4:]
                            break

                phaseDPS = driver.find_element(By.CSS_SELECTOR, f"#{id}>:nth-last-child(2)").text.replace(",", "")
                time = driver.find_element(By.CSS_SELECTOR, "#main-table-row-totals-0>:nth-last-child(4)").text.replace(",", "")
                #result = driver.find_element(By.XPATH, '//*[@id=\'main-table-0\']/tbody/tr[1]/td[5]').text.replace(",", "")
                #if phase == 0:
                    #time = driver.find_element(By.XPATH, '//*[@id=\'main-table-0\']/tfoot/tr[1]/td[4]').text.replace(",", "")
                #else:
                    #time = driver.find_element(By.XPATH, '//*[@id=\'main-table-0\']/tfoot/tr[1]/td[3]').text.replace(",", "")
                storage.append(phaseDPS)
                storage.append(time)
                #storage.append(link)
                print(f"Rank {rank} Phase {phase} DPS: {phaseDPS} over {time}")
            print(storage)
            f.write(",".join(storage)+"\n")
            f.flush()
            #driver.close()
    return

chrome_options = Options()
options = FirefoxOptions()
options.page_load_strategy = 'eager'
#options.headless = True
chrome_options.add_argument('--ignore-certificate-errors')
#chrome_options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

for spec in specList:
    parser(spec)
    