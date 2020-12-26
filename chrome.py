from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

def cookie(browser):  # accept cookie
    cookie = browser.find_element_by_xpath('//div[@class="mt3GC"]/button[1]')  # TODO: set a better path
    cookie.click()  # click accept

def login(browser, username, password):  # faccio il login
    browser.find_element_by_css_selector("input[name='username']").send_keys(username)
    password_input = browser.find_element_by_css_selector("input[name='password']")
    password_input.send_keys(password)
    password_input.submit()
    sleep(3)

def init(browser,username,password):
    browser.get('https://www.instagram.com/')
    browser.implicitly_wait(0.5)

    if len(browser.find_elements_by_partial_link_text("cookie")) > 0:
        cookie(browser)
    if len(browser.find_elements_by_css_selector("input[name='username']")) == 1:
        login(browser,username,password)
    browser.implicitly_wait(5) 

    #semplicemente vado nella home di instagram e se ci sono i campi accetto i cookie e poi login, meglio non eseguire perche` spendi tempo nel cercare gli elementi

def fetchJsonData(browser, url):
    browser.get(url)
    pre = browser.find_element_by_tag_name("pre").text
    jsonData = json.loads(pre)
    return jsonData

def start(username,password):
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(5)

    #init(browser,username,password)

    return browser

