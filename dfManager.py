import os
import pandas as pd

statsDirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stats") #cartella dove salvo i dataframe

def dfUpdate(dfName, dictArray):
    for obj in dictArray:
        dfName = dfName.append(obj,ignore_index=True)
    return dfName

def dfLoad():
    profile_list = pd.read_parquet(os.path.join(statsDirPath,"profile"))
    follow_list = pd.read_parquet(os.path.join(statsDirPath,"follow"))
    added_list = pd.read_parquet(os.path.join(statsDirPath,"added")) 
    stopped_list = pd.read_parquet(os.path.join(statsDirPath,"stopped"))
    return (profile_list, follow_list, added_list, stopped_list)

def dfSave(profile_list, follow_list, added_list, stopped_list):
    profile_list = profile_list.drop_duplicates(ignore_index=True)
    profile_list.to_parquet(os.path.join(statsDirPath,"profile"), index=False)

    follow_list = follow_list.drop_duplicates(ignore_index=True)
    follow_list.to_parquet(os.path.join(statsDirPath,"follow"), index=False)

    added_list = added_list.drop_duplicates(subset=['iid_followed','iid_following'],keep='first',ignore_index=True)
    added_list.to_parquet(os.path.join(statsDirPath,"added"), index=False)

    #stopped_list.to_parquet(os.path.join(statsDirPath,"stopped"), index=False)

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
    # stopped = pd.read_parquet("stats/stopped")

    print('------------PROFILE--------------')
    print(profile)
    print('------------FOLLOW--------------')
    print(follow)
    print('------------ADDED--------------')
    print(added)
    # print('------------STOPPED--------------')
    # print(stopped)
    print('--------------------------')