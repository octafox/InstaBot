def getProfile(username):
    return 'https://www.instagram.com/'+username+'/?__a=1'

def getFollower(id,after=None, first=50,   fetch="false", reel="false"):
    if after != None:
        return "https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables=%7B%22id%22%3A%22"+str(id)+"%22%2C%22include_reel%22%3A"+str(reel)+"%2C%22fetch_mutual%22%3A"+str(fetch)+"%2C%22first%22%3A"+str(first)+"%2C%22after%22%3A%22"+str(after).replace("=","%3D")+"%22%7D"
    else: 
        return "https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables=%7B%22id%22%3A%22"+str(id)+"%22%2C%22include_reel%22%3A"+str(reel)+"%2C%22fetch_mutual%22%3A"+str(fetch)+"%2C%22first%22%3A"+str(first)+"%7D"
