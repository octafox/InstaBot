from time import sleep
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import link
import json
import os
import pandas as pd

statsDirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stats") #cartella dove salvo i dataframe
maxProfile=1000 #n/50 = m requests to find all the profile
profile_list = pd.read_parquet(os.path.join(statsDirPath,"profile")) # il dataframe e` profile list e viene preso dal file stats/profile
follow_list = pd.read_parquet(os.path.join(statsDirPath,"follow")) # il dataframe e` follow list e viene preso dal file stats/follow_list

added_list = pd.read_parquet(os.path.join(statsDirPath,"added")) 
stopped_list = pd.read_parquet(os.path.join(statsDirPath,"stopped"))

def jsonToDfProfiling(jfile): #https://www.instagram.com/octateam/?__a=1
    iid = jfile['graphql']['user']['id']
    username = jfile['graphql']['user']['username']
    fullname = jfile['graphql']['user']['full_name']
    new_row = {'iid':iid,'username':username,'fullname':fullname}
    return new_row #prendo i dati che mi interessano dal json e li metto in una riga pronta per essere inserita nel stats/PROFILE

def jsonToDfFollower(jfile, folloewd_id): #https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables=%7B"id"%3A"1488187679"%2C"include_reel"%3Atrue%2C"fetch_mutual"%3Afalse%2C"first"%3A80%2C"after"%3A"QVFERmY3djBxOUo0Q3V3OFNKSHlERXI1SXBRa2NVLXYzRGJIUmlEenhEQnZvQVlCanRhaGp0TUd3ZEdSdmNKSnYxb0FaMXdyQWJBVzRUUkJiT09yU1ctdg%3D%3D"%7D
    global profile_list
    global follow_list
    # se mi trovo qui allora asserisco che le informazioni riguardanti al mittente allora
    for profile in jfile['data']['user']['edge_followed_by']['edges']:
        iid=profile['node']['id']
        username=profile['node']['username']
        fullname=profile['node']['full_name']
        #inserisco gli id del follower e del followed per collegarli in una relazione N a N 

        follow_row= {'iid_followed':folloewd_id,'iid_following':iid}
        addToFollowList(follow_row)

        #aggiungo le informazioni della persona nella lista dei profili
        new_row = {'iid':iid,'username':username,'fullname':fullname}
        profile_list = profile_list.append(new_row, ignore_index=True)

def cookie():  # accept cookie
    global browser
    cookie = browser.find_element_by_xpath('//div[@class="mt3GC"]/button[1]')  # TODO: set a better path
    cookie.click()  # click accept

def login():  # faccio il login
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

    if len(browser.find_elements_by_partial_link_text("cookie")) > 0:
        cookie()
    if len(browser.find_elements_by_css_selector("input[name='username']")) == 1:
        login()
    browser.implicitly_wait(5) 
    #semplicemente vado nella home di instagram e se ci sono i campi accetto i cookie e poi login, meglio non eseguire perche` spendi tempo nel cercare gli elementi

def addToFollowList(row):
    global follow_list
    global added_list
    #row= iid_followed, iid_following
    if follow_list[(follow_list['iid_followed']==row['iid_followed']) & (follow_list['iid_following']==row['iid_following'])].empty:
        follow_list = follow_list.append(row, ignore_index=True)
        added_list = added_list.append({'iid_followed':row['iid_followed'],'iid_following':row['iid_following'],'date':str(datetime.now())},ignore_index=True)

def getIidByUserName(username):
    #apro il df e cerco se esiste gia` iid corrispondente a username, altrimenti lo cerco e lo inserisco per il futuro
    global profile_list
    
    if profile_list[profile_list['username'] == username].empty: #se non e` presente username allora nemmeno id, quindi inizio a cercare
        browser.get(link.getProfile(username)) # carico il sito init per le info di base
        pre = browser.find_element_by_tag_name("pre").text #dentro tag html pre si trova il css 
        data = json.loads(pre) #parso il json
        if not data: #se e` True allora username probabilmente non esiste
            return "An error occurred"
        ris=jsonToDfProfiling(data) #il metodo mi restituisce una riga con le informazioni che voglio
        profile_list=profile_list.append(ris, ignore_index=True) # aggiungo la riga senza tenere conto dell` indice
        return ris["iid"] #instagram id, follower=seguito da N, following=segue N 

    else:    #altrimenti cerca le info e le salva
        res = profile_list[profile_list['username'] == username] #se username e` gia` presente in df allora anche iid e altre info
        return res.iloc[0]['iid']  #prendo tutto dalla riga e lo returno

def getFollowerByUserName(username): 
    iid=getIidByUserName(username) #iid = instagram id, (Il profilo e` seguito da tot persone), (il profilo segue tot presone)
    if "An error occurred" in iid: #se ho un errore che mi deriva dal caricamento della pagina ritorno una stringa di errore
        return "An error occurred"
    browser.get(link.getFollower(id=iid)) #traduco il link e carico il sito per prendere i primi follower
    pre = browser.find_element_by_tag_name("pre").text #dentro il tag pre html si trova il json 
    data = json.loads(pre) #parso il json
    hasnext = data['data']['user']['edge_followed_by']['page_info']['has_next_page']    #hasnext e` un boolean del json dove indica se siamo all' ultimo json di utenti
    id_after = data['data']['user']['edge_followed_by']['page_info']['end_cursor']      #id_after e` il cursore che indica l` ultimo utente visto, se hasnext=False alloraid_after=None

    follower_number= data['data']['user']['edge_followed_by']['count'] #prendo il numero di follower dal primo json, se non mi piace mollo tutto e nemmeno inizio a profilare
    if follower_number > maxProfile: #se ci sono troppi follower allora non mi conviene fare troppe richieste
        return "An error occurred: Il profilo richiede troppa potenza di calcolo. Contatta uno sviluppatore."
    #TODO lista primo pag #df.append(df, ignore_index=True) 
    jsonToDfFollower(data,iid)

    while hasnext:  #finche` ci sono pagine ciclo
        browser.get(link.getFollower(id=iid, after=id_after))  #traduco il link con aggiunta di cursore
        pre = browser.find_element_by_tag_name("pre").text #prendo json da html come sopra
        data = json.loads(pre) #parso json
        hasnext = data['data']['user']['edge_followed_by']['page_info']['has_next_page'] # vedo se c`e` un next
        id_after = data['data']['user']['edge_followed_by']['page_info']['end_cursor'] # preparo il prossimo puntatore
        #TODO lista N pag #df.append(df, ignore_index=True) 
        jsonToDfFollower(data,iid)
    assert id_after == None #se id_after non e` None allora ci sono ancora utenti da cercare

    #TODO if len(df)==0: return "profilo privato"

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(5)
    
    try:
        getFollowerByUserName("simone_mastella")
    except:
        print("Errore")
    finally:
        #follow_list = follow_list.drop_duplicates(ignore_index=True)
        follow_list.to_parquet(os.path.join(statsDirPath,"follow"), index=False)

        added_list.to_parquet(os.path.join(statsDirPath,"added"), index=False)
        stopped_list.to_parquet(os.path.join(statsDirPath,"stopped"), index=False)

        profile_list = profile_list.drop_duplicates(ignore_index=True)
        profile_list.to_parquet(os.path.join(statsDirPath,"profile"), index=False)
    #init() # > 1 sec < 8 sec
    browser.close()
