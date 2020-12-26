from linkBuilder import getProfileLink, getFollowerLink,getFollowingLink
from utils import parseObj
from dfManager import dfUpdate, dfLoad, dfSave, dfReset, dfPrint, dfUpdateAll
from chrome import start, fetchJsonData
import config as cfg


maxProfile=1000 #n/50 = m requests to find all the profile
browser = None

def getUserData(username):
    jsonData = fetchJsonData(browser,getProfileLink(username))
    userJson = parseObj(jsonData['graphql']['user'],['id','username','full_name'])
    return userJson

def getUserFollower(id):
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
    if follower_number < maxProfile == 0:
        print('Errore: Troppi follower')
    return followers

def getUserFollowing(id):
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
    if following_number < maxProfile == 0:
        print('Errore: Troppi following')
    return followings




if __name__ == '__main__':
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)

    #dfReset()
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    
    username = 'kaj_oskar'
    
    if profile_list[profile_list['username'] == username].empty:
        print('create')
        user = getUserData(username)
        profile_list = dfUpdate(profile_list,[user])
    else:
        print('load')
        user = profile_list[profile_list['username'] == username].iloc[0].to_dict()
    
    # update DataFrames
    followers = getUserFollowing(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='following')
    
    
    followers = getUserFollower(user['id'])
    profile_list, follow_list, added_list, stopped_list = dfUpdateAll(profile_list, follow_list, added_list, stopped_list, followers, user['id'], target='follower')


    dfSave(profile_list, follow_list, added_list, stopped_list)
    dfPrint()
    browser.close()
   