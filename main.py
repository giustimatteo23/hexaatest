# python -m venv selenv
# on windows .\selenv\Scripts\activate
# with this method you dont have to install the webdriver if you already have chrome dowlnoaded
# make an exe: pyinstaller.exe --onefile -w "main.py" 
# delete the created folders after

import subprocess
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import os
from jinja2 import Environment, FileSystemLoader
import json

root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))

#make a chrome browser
options = webdriver.ChromeOptions()
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.headless = True
options.add_experimental_option("excludeSwitches", ["enable-logging"]) #used to surpress a bluetooth error -> Bluetooth: bluetooth_adapter_winrt.cc:1074 Getting Default Adapter failed.
options.add_argument('--headless')
options.add_argument("--disable-gpu")
options.add_argument("--screen-size=1200x800")
options.add_argument('--remote-debugging-port=9222')
options.add_argument('--disable-blink-features=AutomationControlled') ## to avoid getting detected
#options.add_argument("--silent")
#options.add_argument("--log-level=1")
browser = webdriver.Chrome(service=Service(executable_path=ChromeDriverManager().install()),options=options)
#browser = webdriver.Chrome(service=Service(executable_path="/usr/local/bin/chromedriver"),options=options)

with open(os.environ.get("CFGLOC","/hexaahealthcheck/cfg.json")) as json_file:
 vars = json.load(json_file)


LOGINURL=vars["HEXAAURL"]
IDPSRCKEYS=vars["IDPSRCKEYS"]
TESTUSER=vars["TESTUSER"]
TESTPASS=vars["TESTPASS"]

urlexceptionlist=vars["NOVISITURLS"]
errorexceptionlist=vars["TOLERATEDERRORS"]
urlstovisit=vars["URLSTOVISIT"]

data={}
data["errlist"] = []

def login(loginurl=LOGINURL, idpsrckeys=IDPSRCKEYS, USER=TESTUSER, PASS=TESTPASS, browser=browser):
    browser.get(loginurl)
    WebDriverWait(browser,10).until(lambda x: "Please login..." in browser.title)
    mdxsearchfield = browser.find_element(By.XPATH,'//*[@id="searchinput"]')
    mdxsearchfield.send_keys("asdfghj")
    mdxsearchfield.clear()
    mdxsearchfield.send_keys(idpsrckeys)
    mdxsearchfield.send_keys(Keys.RETURN)
    
    
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ds-search-list"]/div/div/div[2]')))
    browser.find_element(By.XPATH, '//*[@id="ds-search-list"]/div/div/div[2]').click()
    #wait for IDP then enter
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
    
    browser.find_element(By.XPATH,'//*[@id="username"]').send_keys(USER)
    browser.find_element(By.XPATH,'//*[@id="password"]').send_keys(PASS)
    browser.find_element(By.XPATH,'//*[@id="submit"]').click()
    if LOGINURL in browser.current_url:
        logging.info("\nLogin successfull!\n")
        return True
    else: 
        logging.error("\nLogin failed!\n")
        data["errlist"].append("Login failed!")
        return False

def runscripts(dir):
    allgood=True
    scriptslist = list(map(lambda name: name if(name.endswith(".sh")) and os.path.isfile(dir+"/"+name) else "",os.listdir(dir)))
    scriptslist = [x for x in scriptslist if x != ""]
    logging.info("Loaded scripts with sh ending are: ")
    logging.info(scriptslist)
    for script in scriptslist:
        logging.info("Running ")
        cmd = [dir+"/"+script]
        logging.info(cmd)
        #result = subprocess.run(cmd,executable='/bin/bash',stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        PIPE = subprocess.PIPE
        proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE)
        output, err = proc.communicate()
        errcode = proc.returncode
        
        logging.info(output.decode('utf-8'))
        logging.info(err.decode('utf-8'))
        if output.decode('utf-8') != "0":
            logging.error("This script didnt exit with status code 0: "+script)
            allgood=False
    return allgood

def urltest(urllist, browser=browser, exceptionlist=urlexceptionlist):
    allgood=True
    trycount=0
    for url in urllist:
        if url in exceptionlist: continue
        trycount+=1
        browser.get(url)
        for entry in browser.get_log('browser'):
            if entry["level"]=="SEVERE" and entry["message"] not in errorexceptionlist:
                logging.error(" "+entry["message"])
                data["errlist"].append(entry["message"])
                allgood=False
            else: logging.info(" "+entry["message"])
    logging.info(" Visited "+str(trycount)+" out of "+str(len(urllist))+" urls.")
    return allgood



def geturlsonpage(browser=browser):
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    welementlist=browser.find_elements(By.XPATH,"//a[@href]")
    return list(map(lambda x: x.get_attribute("href"),welementlist))

def myrender():
    #print(os.getcwd())
    pageloc = os.environ.get("PAGELOC","/var/www/html/index.html")
    environment = Environment(loader=FileSystemLoader("./templates/"))
    template = environment.get_template("page.j2")
    rendered= template.render(data)
    with open(pageloc, mode="w", encoding="utf-8") as message:
        message.write(rendered)


def main():
    allgood = True
    allgood &= login()
    allgood &= runscripts(vars["SCRIPTSDIR"])
    allgood &= urltest(geturlsonpage())
    allgood &= urltest(urlstovisit)

    data["allgood"]=allgood
    myrender()
    sleep(1000)

    browser.quit()
    

try:
    exit(main())
except Exception:
    logging.exception("Exception in main(): ")
    exit(1)


