from datetime import datetime
from linkBuilder import getProfileLink, getFollowerLink
from utils import parseObj
from dfManager import dfUpdate, dfLoad, dfSave, dfReset, dfPrint#
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

if __name__ == '__main__':
    browser = start(cfg.INSTA_USER,cfg.INSTA_PASS)

    dfReset()
    profile_list, follow_list, added_list, stopped_list = dfLoad()
    
    username = 'octateam'

    if profile_list[profile_list['username'] == username].empty:
        print('create')
        user = getUserData(username)
        profile_list = dfUpdate(profile_list,[user])
    else:
        print('load')
        user = profile_list[profile_list['username'] == username].iloc[0].to_dict()

    # update DataFrames
    followers = getUserFollower(user['id'])
    profile_list = dfUpdate(profile_list,followers) # {id, username, full_name}

    followerList = map(lambda follower: {'iid_followed':user['id'], 'iid_following':follower['id']}, followers) # {'iid_followed','iid_following'}
    follow_list = follow_list[follow_list.iid_followed!=user['id']] # TODO: usare questa riga per fare innerjoin e outerjoin con df di riga sotto per trovare le added e le stopped
    follow_list = dfUpdate(follow_list,list(followerList)) # {id, username, full_name}
    # TODO: aggiungere il follower nella follow_list solo se non si trova già nella follow_list

    addedList = map(lambda follower: {'iid_followed':user['id'], 'iid_following':follower['id'], 'date': str(datetime.now())}, followers) # {'iid_followed','iid_following','date'}
    # TODO: aggiungere il follower nella added_list solo se non si trova nella follow_list
    added_list = dfUpdate(added_list,list(addedList))

    dfSave(profile_list, follow_list, added_list, stopped_list)
    dfPrint()

    
    browser.close()
   