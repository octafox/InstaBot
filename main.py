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
    
    username = 'octateam'
    dfPrint()
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
    """profile_list = dfUpdate(profile_list,followers) # {id, username, full_name}
    followerList = map(lambda follower: {'iid_followed':user['id'], 'iid_following':follower['id']}, followers) # {'iid_followed','iid_following'}

    now_follow= pd.DataFrame(columns=['iid_followed','iid_following'])
    now_follow= dfUpdate(now_follow, list(followerList))
    prev_follow = follow_list[follow_list.iid_followed==user['id']]
    new_stoped = pd.merge(prev_follow,now_follow, how = 'left' ,indicator=True).loc[lambda x : x['_merge']=='left_only']
    new_added = pd.merge(prev_follow,now_follow, how = 'right' ,indicator=True).loc[lambda x : x['_merge']=='right_only']
    new_added.drop('_merge', inplace=True, axis=1)
    new_stoped.drop('_merge', inplace=True, axis=1)
    
    follow_list = follow_list.append(new_added,ignore_index=True)

    follow_list = follow_list.append(new_stoped,ignore_index=True).drop_duplicates(keep=False)

    new_added['date']=str(datetime.now())
    new_stoped['date']=str(datetime.now())
    added_list=added_list.append(new_added,ignore_index=True)
    stopped_list=stopped_list.append(new_stoped,ignore_index=True)"""




    #followings = getUserFollowing(user['id'])
    #profile_list = dfUpdate(profile_list,followings) # {id, username, full_name}
    #followingList= map(lambda follower: {'iid_followed':follower['id'], 'iid_following':user['id']}, followings) # {'iid_followed','iid_following'}




    dfSave(profile_list, follow_list, added_list, stopped_list)
    dfPrint()

    
    browser.close()
   