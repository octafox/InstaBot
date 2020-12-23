from time import sleep
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import os, pickle
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def cookie(): #accept cookie
    global browser  
    cookie = browser.find_element_by_xpath('//div[@class="mt3GC"]/button[1]') #TODO: set a better path
    cookie.click() #click accept


def login(): #faccio il login
    import config as cfg
    global browser
    browser.find_element_by_css_selector("input[name='username']").send_keys(cfg.INSTA_USER)
    password_input = browser.find_element_by_css_selector("input[name='password']")
    password_input.send_keys(cfg.INSTA_PASS)
    password_input.submit()
    sleep(3)


def init():
    global browser
    browser.get('https://www.instagram.com/')
    browser.implicitly_wait(0.5)

    if len(browser.find_elements_by_partial_link_text("cookie"))>0:
        cookie()
    if len(browser.find_elements_by_css_selector("input[name='username']"))==1:
        login()
    browser.implicitly_wait(5)



def getFollowerByUserName(username):
    browser.get('https://www.instagram.com/'+username+'/')
    followerlist = browser.find_element_by_partial_link_text(' follower')
    followerlist.click() #open follower list
    element_present = EC.presence_of_element_located((By.XPATH, '//div/ul/div/li'))
    WebDriverWait(browser, 2).until(element_present)

    while 1: #has next -> to implement
        action = ActionChains(browser) 


        scrolla= browser.find_elements_by_xpath('//div/ul/div/li')
        action.move_to_element(scrolla[-1]).perform()


"""
for request in browser.requests:
    if request.response:
        print(
            request.url,
            request.response.status_code,
            request.response.headers['Content-Type']
        )
"""
if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(5)

    #init() # min 1 sec to ~8 sec
    getFollowerByUserName("simone_mastella")
    input()
    browser.close()


    