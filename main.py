from linkBuilder import getProfileLink, getFollowerLink,getFollowingLink
from utils import parseObj
from dfManager import dfUpdate, dfLoad, dfSave, dfReset, dfPrint, dfUpdateAll, dfGetProfileByUsername, dfGetProfileByID,dfGetFollowersUsername,dfGetFollowingsUsername
from chrome import start, fetchJsonData
from time import sleep
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import json
import pandas as pd

import config as cfg
startTime=datetime.now()
maxProfile=1000 #n/50 = m requests to find all the profile
browser = None

def fetchUserData(username):
    jsonData = fetchJsonData(browser,getProfileLink(username))
    userJson = parseObj(jsonData['graphql']['user'],['id','username','full_name'])
    return userJson

def fetchUserFollower(id):
    nextPage = True
    afterId = None
    followers = []
    follower_number = 0
    while nextPage and follower_number < maxProfile:
        jsonData = fetchJsonData(browser,getFollowerLink(id=id, after=afterId))
        jsonData = jsonData['data']['user']['edge_followed_by']
        follower_number = jsonData['count']
        hasnext = jsonData['page_info']['has_next_page']
        id_after = jsonData['page_info']['end_cursor']
        for follower in jsonData['edges']:
            parsedFollower = parseObj(follower['node'],['id','username','full_name'])
            followers.append(parsedFollower)
        afterId = id_after
        nextPage = hasnext
    if follower_number > maxProfile:
        print('Errore: Troppi follower')
    return followers

def fetchUserFollowing(id):
    nextPage = True
    afterId = None
    followings = []
    following_number = 0
    while nextPage and following_number < maxProfile:
        jsonData = fetchJsonData(browser,getFollowingLink(id=id, after=afterId))
        jsonData = jsonData['data']['user']['edge_follow']
        following_number = jsonData['count']
        hasnext = jsonData['page_info']['has_next_page']
        id_after = jsonData['page_info']['end_cursor']
        for following in jsonData['edges']:
            parsedFollowing = parseObj(following['node'],['id','username','full_name'])
            followings.append(parsedFollowing)
        afterId = id_after
        nextPage = hasnext
    if following_number > maxProfile:
        print('Errore: Troppi following')
    return followings

def fetchUserStories(username):
    browser.get("https://www.instagram.com/"+username)
    storie=browser.find_element_by_xpath('//header/div/div/span/img')
    storie.click()
    sleep(1)
    visualAllIGS={}
    while browser.current_url != "https://www.instagram.com/"+username+"/":
        del browser.requests
        visual=browser.find_element_by_xpath('//body/div/section/div/div/section/div/div/div/button')
        numerovisual= int(visual.find_element_by_xpath('div/span/span').text)
        visual.click()
        sleep(1)
        elemVisual=[]
        while len(elemVisual)<numerovisual:
            action = ActionChains(browser) 
            scrolla= browser.find_elements_by_xpath('//div[@role="dialog"]/div/div/div/div/div/div')
            for visualizzatore in scrolla:
                link= visualizzatore.find_element_by_xpath('div/a').get_attribute("href").replace("https://www.instagram.com/","")[:-1]
                if not link in elemVisual:
                    elemVisual.append(link)
            action.move_to_element(scrolla[-1]).perform()
        visualizzatori=[]
        for request in browser.requests:
            if request.method == "GET" and "?include_blacklist_sample=true&max_id=" in request.url:
                data = json.loads(request.response.body.decode("utf8"))
                for user in data['users']:
                    visualizzatori.append(parseObj(user,['pk','username','full_name']))
            elif request.method == "GET" and "?include_blacklist_sample=true" in request.url:
                data = json.loads(request.response.body.decode("utf8"))
                owner = data['updated_media']['user']['pk']
                upload_time = data['updated_media']['taken_at']
                for user in data['users']:
                    visualizzatori.append(parseObj(user,['pk','username','full_name']))
        visualAllIGS[upload_time]=(visualizzatori)
        close=browser.find_element_by_xpath('//body/div/div/div/div/div/div/div/button')
        close.click()
        nextPage=browser.find_element_by_xpath('//div[@class="coreSpriteRightChevron"]')
        nextPage.click()
    return owner, visualAllIGS

def checkIfUsernameExist(profile_list, username):
    if profile_list[profile_list['username'] == username].empty:
        user = fetchUserData(username)
        profile_list = dfUpdate(profile_list,[user])
    else:
        user=dfGetProfileByUsername(profile_list, username)
    return profile_list, user

def checkIfUsernameHasNews(follow_list, profile_list, date):
    return 0


def getNewFollowers(username):
    global browser
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    profile_list, user = checkIfUsernameExist(profile_list,username)
    followers = fetchUserFollower(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='follower')
    new_added=added_list[(pd.to_datetime(added_list.date)>startTime) & (added_list.iid_followed == user['id'])]
    dfSave(profile_list, follow_list, added_list, stopped_list)
    browser.close()
    return new_added

def getNewFollowings(username):
    global browser
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    profile_list, user = checkIfUsernameExist(profile_list,username)
    followers = fetchUserFollowing(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='following')
    new_adding=added_list[(pd.to_datetime(added_list.date)>startTime) & (added_list.iid_following == user['id'])]
    dfSave(profile_list, follow_list, added_list, stopped_list)
    browser.close()
    return new_adding

def getNewFollowS(username):
    global browser
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    profile_list, user = checkIfUsernameExist(profile_list,username)

    followers = fetchUserFollowing(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='following')
    new_adding=added_list[(pd.to_datetime(added_list.date)>startTime) & (added_list.iid_following == user['id'])]

    followers = fetchUserFollower(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='follower')
    new_added=added_list[(pd.to_datetime(added_list.date)>startTime) & (added_list.iid_followed == user['id'])]

    dfSave(profile_list, follow_list, added_list, stopped_list)
    browser.close()
    return new_adding, new_added

def getALLFollowS(username):
    global browser
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    profile_list, user = checkIfUsernameExist(profile_list,username)

    followers = fetchUserFollowing(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='following')
    new_stoping=stopped_list[(pd.to_datetime(stopped_list.date)>startTime) & (stopped_list.iid_following == user['id'])]
    new_adding=added_list[(pd.to_datetime(added_list.date)>startTime) & (added_list.iid_following == user['id'])]

    followers = fetchUserFollower(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='follower')
    new_stoped=stopped_list[(pd.to_datetime(stopped_list.date)>startTime) & (stopped_list.iid_followed == user['id'])]

    dfSave(profile_list, follow_list, added_list, stopped_list)
    browser.close()
    return new_stoping,new_stoped,new_adding, new_added

def getStpFollowS(username):
    global browser
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    profile_list, user = checkIfUsernameExist(profile_list,username)

    followers = fetchUserFollowing(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='following')
    new_stoping=stopped_list[(pd.to_datetime(stopped_list.date)>startTime) & (stopped_list.iid_following == user['id'])]

    followers = fetchUserFollower(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='follower')
    new_stoped=stopped_list[(pd.to_datetime(stopped_list.date)>startTime) & (stopped_list.iid_followed == user['id'])]
    new_added=added_list[(pd.to_datetime(added_list.date)>startTime) & (added_list.iid_followed == user['id'])]


    dfSave(profile_list, follow_list, added_list, stopped_list)
    browser.close()
    return new_stoping, new_stoped

def getStpFollowers(username):
    global browser
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    profile_list, user = checkIfUsernameExist(profile_list,username)
    followers = fetchUserFollower(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='follower')
    new_stoped=stopped_list[(pd.to_datetime(stopped_list.date)>startTime) & (stopped_list.iid_followed == user['id'])]
    dfSave(profile_list, follow_list, added_list, stopped_list)
    browser.close()
    return new_stoped
    
def getStpFollowings(username):
    global browser
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    profile_list, user = checkIfUsernameExist(profile_list,username)
    followers = fetchUserFollowing(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='following')
    new_stoping=stopped_list[(pd.to_datetime(stopped_list.date)>startTime) & (stopped_list.iid_following == user['id'])]
    dfSave(profile_list, follow_list, added_list, stopped_list)
    browser.close()
    return new_stoping




if __name__ == '__main__':
    #
    #dfReset()
    #print(len(getNewFollowers("simone_mastella")))
    #dfPrint()
    a,b,c,d= getALLFollowS("simone_mastella")
    print(len(a))
    print(len(b))
    print(len(c))
    print(len(d))
    #dfPrint()
    

    #dfReset()
    #profile_list, follow_list, added_list, stopped_list = dfLoad()
    
    #username = 'simone_mastella'
    #print(dfGetProfileByID(profile_list,'10620577766'))
    
    #print(dfGetProfileByUsername(profile_list,"simone_mastella"))
    #profile_list, user=checkIfUsernameExist(profile_list,username)
    
   

    #restituisce un dataframe con la lista dei nomi  
    #dfGetFollowingsUsername(profile_list,follow_list,user['username'])

    #restituisce un dataframe con la lista dei nomi  
    #dfGetFollowersUsername(profile_list,follow_list,user['username'])

    #scrappa e aggiorna i following
    #followers = fetchUserFollowing(user['id'])
    #profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='following')

    #scrappa e aggiorna i follower
    #followers = fetchUserFollower(user['id'])
    #profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='follower')
    
    #dfSave(profile_list, follow_list, added_list, stopped_list)
    #dfPrint()
   