from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import link
import json 

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
    browser.get(link.getProfile(username))
    pre = browser.find_element_by_tag_name("pre").text
    data = json.loads(pre)
    id=data['graphql']['user']['id']

    browser.get(link.getFollower(id=id))

    pre = browser.find_element_by_tag_name("pre").text
    data = json.loads(pre)

    hasnext = data['data']['user']['edge_followed_by']['page_info']['has_next_page']
    id_after = data['data']['user']['edge_followed_by']['page_info']['end_cursor']

    while hasnext:
        
        browser.get(link.getFollower(id=id, after=id_after))
        pre = browser.find_element_by_tag_name("pre").text
        data = json.loads(pre)
        hasnext = data['data']['user']['edge_followed_by']['page_info']['has_next_page']
        id_after = data['data']['user']['edge_followed_by']['page_info']['end_cursor']





if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(5)

    #init() # > 1 sec < 8 sec
    getFollowerByUserName("simone_mastella")
    input()
    browser.close()


    