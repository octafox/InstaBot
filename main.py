from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import link
import json
import os
import pandas as pd

statsDirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"stats") #cartella dove salvo i dataframe

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

def getFollowerByUserName(username): 
    iid,follower,following=getIidByUserName(username) #iid = instagram id, (Il profilo e` seguito da tot persone), (il profilo segue tot presone)

    if iid=="An error occurred" or sn >500: #se ho un errore che mi deriva dal caricamento della pagina ritorno una stringa di errore, OR, se ci sono troppi follower allora non conviene fare troppe richieste
        return "An error occurred"

    browser.get(link.getFollower(id=iid)) #traduco il link e carico il sito per prendere i primi follower
    pre = browser.find_element_by_tag_name("pre").text #dentro il tag pre html si trova il json 
    data = json.loads(pre) #parso il json
    hasnext = data['data']['user']['edge_followed_by']['page_info']['has_next_page']    #hasnext e` un boolean del json dove indica se siamo all' ultimo json di utenti
    id_after = data['data']['user']['edge_followed_by']['page_info']['end_cursor']      #id_after e` il cursore che indica l` ultimo utente visto, se hasnext=False alloraid_after=None
    #TODO lista primo pag
    while hasnext:  #finche` ci sono pagine ciclo
        browser.get(link.getFollower(id=iid, after=id_after))  #traduco il link con aggiunta di cursore
        pre = browser.find_element_by_tag_name("pre").text #prendo json da html come sopra
        data = json.loads(pre) #parso json
        hasnext = data['data']['user']['edge_followed_by']['page_info']['has_next_page'] # vedo se c`e` un next
        id_after = data['data']['user']['edge_followed_by']['page_info']['end_cursor'] # preparo il prossimo puntatore
        #TODO lista N pag
    assert id_after=None #se id_after non e` None allora ci sono ancora utenti da cercare

    #if len(df)==0: return "profilo privato"

def jsonToProfile(jfile):
    iid = jfile['graphql']['user']['id']
    username = jfile['graphql']['user']['username']
    fullname = jfile['graphql']['user']['full_name']
    bio = jfile['graphql']['user']['biography']
    fbid= jfile['graphql']['user']['fbid']
    follows_viewer =  jfile['graphql']['user']['follows_viewer']
    follower_number = jfile['graphql']['user']['edge_followed_by']['count']
    following_number = jfile['graphql']['user']['edge_follow']['count']
    is_private = jfile['graphql']['user']['is_private']
    is_verified = jfile['graphql']['user']['is_verified']
    blocked_viewer = jfile['graphql']['user']['has_blocked_viewer']
    new_row = {'iid':iid,'username':username,'fullname':fullname,'bio':bio,'fbid':fbid,'follows_viewer':follows_viewer,'follower_number':follower_number,'following_number':following_number,'is_private':is_private,'is_verified':is_verified,'blocked_viewer':blocked_viewer}
    return new_row #prendo i dati che mi interessano dal json e li metto in una riga pronta per essere inserita nel stats/PROFILE
    
def getIidByUserName(username):
    #apro il df e cerco se esiste gia` iid corrispondente a username, altrimenti lo cerco e lo inserisco per il futuro
    profileList = pd.read_parquet(os.path.join(statsDirPath,"profile")) # il dataframe e` profile list e viene preso dal file stats/profile
    if profileList[profileList['username'] == username].empty: #se non e` presente username allora nemmeno id, quindi inizio a cercare
        browser.get(link.getProfile(username)) # carico il sito init per le info di base
        pre = browser.find_element_by_tag_name("pre").text #dentro tag html pre si trova il css 
        data = json.loads(pre) #parso il json
        if not data: #se e` True allora username probabilmente non esiste
            return "An error occurred"
        ris=jsonToProfile(data) #il metodo mi restituisce una riga con le informazioni che voglio
        profileList=profileList.append(ris, ignore_index=True) # aggiungo la riga senza tenere conto dell` indice
        profileList.to_parquet(os.path.join(statsDirPath,"profile"), index=False) # lo salvo in stats/parquet
        return ris["iid"],ris['follower_number'],ris['following_number'] #instagram id, follower=seguito da N, following=segue N 

    else:    #altrimenti cerca le info e le salva
        res = profileList[profileList['username'] == username] #se username e` gia` presente in df allora anche iid e altre info
        return res.iloc[0]['iid'],res.iloc[0]['follower_number'],res.iloc[0]['following_number']  #prendo tutto dalla riga e lo returno
     
    

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=selenium")
    browser = webdriver.Chrome(options=chrome_options)
    browser.implicitly_wait(5)

    #init() # > 1 sec < 8 sec

    browser.close()
