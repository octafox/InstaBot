import json

def parseObj(obj, keys):
    resObj = {}

    for key in keys:
        resObj[key] = obj[key]

    return resObj

def parseProfiles(obj):
    obj = obj['graphql']['user']
    keys = ['id','username','full_name']

    newData = parseObj(obj, keys)
    return newData

def parseFollowers(obj):
    arr = obj['data']['user']['edge_followed_by']['edges']
    keys = ['id','username','full_name']

    newDataArray = []
    for obj in arr:
        newData = jsonToDataFrame(obj['node'], keys)
        newDataArray.append(newData)

    return newDataArray