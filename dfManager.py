import os
import pandas as pd
from datetime import datetime

statsDirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stats") #cartella dove salvo i dataframe

def dfUpdate(dfName, dictArray):
    for obj in dictArray:
        dfName = dfName.append(obj,ignore_index=True)
    return dfName

def dfUpdateAll(profile_list, follow_list, added_list, stopped_list, dictArray, user_id, target='follower'):
    profile_list = dfUpdate(profile_list,dictArray).drop_duplicates(ignore_index=True) # {id, username, full_name}
    if target=='follower':
        followerList = map(lambda follower: {'iid_followed':user_id, 'iid_following':follower['id']}, dictArray) # {'iid_followed','iid_following'}
        prev_follow = follow_list[follow_list['iid_followed']==user_id]
    elif target=='following':
        followerList = map(lambda follower: {'iid_followed':follower['id'], 'iid_following':user_id}, dictArray) # {'iid_followed','iid_following'}
        prev_follow = follow_list[follow_list['iid_following']==user_id]
    else:
        return profile_list, follow_list, added_list, stopped_list
    now_follow= pd.DataFrame(columns=['iid_followed','iid_following'])
    now_follow= dfUpdate(now_follow, list(followerList))
    new_stoped = pd.merge(prev_follow,now_follow, how = 'left' ,indicator=True).loc[lambda x : x['_merge']=='left_only']
    new_added = pd.merge(prev_follow,now_follow, how = 'right' ,indicator=True).loc[lambda x : x['_merge']=='right_only']
    new_added.drop('_merge', inplace=True, axis=1)
    new_stoped.drop('_merge', inplace=True, axis=1)
    follow_list = follow_list.append(new_added,ignore_index=True)
    follow_list = follow_list.append(new_stoped,ignore_index=True).drop_duplicates(keep=False)
    new_added['date']=str(datetime.now())#.drop_duplicates(subset=['iid_followed','iid_following'],keep='last',ignore_index=True)
    new_stoped['date']=str(datetime.now())
    added_list=added_list.append(new_added,ignore_index=True)
    stopped_list=stopped_list.append(new_stoped,ignore_index=True)
    return profile_list, follow_list, added_list, stopped_list


def dfUpdateStories(profile_list, stories_list, visualAllIGS, owner):
    for date in visualAllIGS:
        uploadDate = datetime.fromtimestamp(date)
        followArray = list(map(lambda follower: {'id':str(follower['pk']), 'username':follower['username'], 'full_name':follower['full_name']}, visualAllIGS[date]))
        profile_list = dfUpdate(profile_list,followArray)
        profile_list=profile_list.drop_duplicates(ignore_index=True)
        storyNew= list(map(lambda viewer: {'id_owner':owner['id'],'id_viewer': str(viewer['pk']),'date_updload':uploadDate}, visualAllIGS[date]))
        stories_list=dfUpdate(stories_list, storyNew).drop_duplicates(ignore_index=True)    
    return profile_list, stories_list

def dfLoad():
    profile_list = pd.read_parquet(os.path.join(statsDirPath,"profile"))
    follow_list = pd.read_parquet(os.path.join(statsDirPath,"follow"))
    added_list = pd.read_parquet(os.path.join(statsDirPath,"added")) 
    stopped_list = pd.read_parquet(os.path.join(statsDirPath,"stopped"))
    return (profile_list, follow_list, added_list, stopped_list)

def dfSave(profile_list, follow_list, added_list, stopped_list):
    profile_list.to_parquet(os.path.join(statsDirPath,"profile"), index=False)
    follow_list.to_parquet(os.path.join(statsDirPath,"follow"), index=False)
    added_list.to_parquet(os.path.join(statsDirPath,"added"), index=False)
    stopped_list.to_parquet(os.path.join(statsDirPath,"stopped"), index=False)

def dfReset():
    added = pd.DataFrame(columns=['iid_followed','iid_following','date'])
    added.to_parquet(os.path.join(statsDirPath,"added"),index=False)

    stoped = pd.DataFrame(columns=['iid_followed','iid_following','date'])
    stoped.to_parquet(os.path.join(statsDirPath,"stopped"),index=False)

    follow_list=pd.DataFrame(columns=['iid_followed','iid_following'])
    follow_list.to_parquet(os.path.join(statsDirPath,"follow"),index=False)

    profile=pd.DataFrame(columns=['id','username','full_name'])
    profile.to_parquet(os.path.join(statsDirPath,"profile"),index=False)

def dfPrint():
    profile = pd.read_parquet("stats/profile")
    follow = pd.read_parquet("stats/follow")
    added = pd.read_parquet("stats/added")
    stopped = pd.read_parquet("stats/stopped")
    print('------------PROFILE--------------')
    print(profile)
    print('------------FOLLOW--------------')
    print(follow)
    print('------------ADDED--------------')
    print(added)
    print('------------STOPPED--------------')
    print(stopped)
    print('--------------------------')

def dfGetProfileByUsername(profile_list, username):
    return profile_list[profile_list['username'] == username].iloc[0].to_dict()

def dfGetProfileByID(profile_list, id):
    return profile_list[profile_list['id'] == id].iloc[0].to_dict()

def dfGetFollowersUsername(profile_list,follow_list, username):
    ids=profile_list[profile_list['username'] ==username ].iloc[0]["id"]
    now_follow = follow_list[follow_list['iid_followed']==ids]
    now_follow=now_follow.replace(ids,profile_list[profile_list['username'] ==username].iloc[0]["username"])
    return pd.merge(left=now_follow, right=profile_list, left_on=['iid_following'], right_on=['id'], how='inner').drop(['id','full_name','iid_following'],axis=1).rename(columns={'username':'username_following','iid_followed':'username_followed'})

def dfGetFollowingsUsername(profile_list,follow_list, username):
    ids=profile_list[profile_list['username'] ==username ].iloc[0]["id"]
    now_follow = follow_list[follow_list['iid_following']==ids]
    now_follow=now_follow.replace(ids,profile_list[profile_list['username'] ==username].iloc[0]["username"])
    return pd.merge(left=now_follow, right=profile_list, left_on=['iid_followed'], right_on=['id'], how='inner').drop(['id','full_name','iid_followed'],axis=1).rename(columns={'username':'username_followed','iid_following':'username_following'})



