# -*- coding: utf-8 -*-

"""
Created on Fri Apr 03 20:33:46 2015

@author: Gaspard
"""

import urllib, urllib2, re, csv
from bs4 import BeautifulSoup

from Login import *

try:
    my_mail
except NameError:
    my_mail = raw_input("Enter you email: ")
print "Using email: " + my_mail

try:
    my_password
except NameError:
    my_password = raw_input("Enter you password: ")
print "Using password: " + my_password


heraclesBaseURL = "https://heracles.economie.gouv.fr"
heraclesURL = "https://heracles.economie.gouv.fr/Heracles"

def printDico(d):
    if d:
        for e in d:
            print e + " : " + d[e].encode('utf8')

def openURL(url, data=None, headers={}):
#    print 'Request: ' + url
#    print '------ Data ------'
#    printDico(data)
#    print '---- Headers -----'
#    printDico(headers)
#    print ''
    ans = None
    if data == None:
        req = urllib2.Request(url,None,headers)
        ans = urllib2.urlopen(req, timeout=2)
    else:
        datastr = urllib.urlencode(data)
#        headers['Content-Length'] = str(len(datastr))
        req = urllib2.Request(url,datastr,headers)
        ans = urllib2.urlopen(req, timeout=2)
#    print '---- Answer ----'
#    printDico(ans.headers)
#    print ''
    return ans


def getBasicHeader():
    return {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'fr,en;q=0.8,en-US;q=0.6',
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'Host':'heracles.economie.gouv.fr',
            'Pragma':'no-cache',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}



class Connection:
    
    def __init__(self, mail, password):
        self.mail = mail
        self.password = password
        
    def handleResponse(self, data):
        self.data    = data
        self.headers = self.data.headers.dict
        self.bs      = BeautifulSoup(self.data)
        self.code    = self.data.code
        if 'set-cookie' in self.headers:
            self.updateCookies(self.headers['set-cookie'])

    def POSTquery(self, data, headers):
        self.handleResponse(openURL(heraclesURL, data, headers))
    
    def CALLBACKquery(self, data, urldata):
        headers = self.getPoliteHeaders()
        headers['Accept'] = '*/*'
        url = heraclesBaseURL + '/callback/1/' + self.session_id + '?'
        url = url + urllib.urlencode(urldata)
        self.handleResponse( openURL(url, data, headers) )
    
    def updateCookies(self, cookie):
        pos = cookie.find('IntraWeb_Heracles=')
        if pos == -1:
            return
        self.session_id = cookie[pos + 18:pos+46]
        self.cookie = self.session_id + '_'
        cookie = cookie[pos + 47:]
        pos = cookie.find(';')
        if pos != 0:
            self.session_count = int(cookie[:pos])
            self.cookie = self.session_id + '_' + str(self.session_count)
        return self.updateCookies(cookie[pos:])
    
    
    def startNewConnection(self):
        url = openURL(heraclesBaseURL, None, getBasicHeader())
        self.updateCookies(url.headers.dict['set-cookie'])
        
    def politeResponse(self):
        self.POSTquery(self.getPoliteData(), self.getPoliteHeaders())
        
    def clickRequest1(self):
        d = {'callback':'IWEDLOGIN.DoOnAsyncClick','x':'124','y':'8','which':'1','modifiers':''}
        self.CALLBACKquery( self.getClickData1(), d)

    def clickRequest2(self):
        d = {'callback':'IWEDLOGIN.DoOnAsyncClick','x':'24','y':'7','which':'1','modifiers':''}
        self.CALLBACKquery( self.getClickData2(), d)
    
    def connect(self):
        self.POSTquery(self.getLoginData(), self.getConnectHeaders())
        
    def gotoSearch(self):
        self.POSTquery(self.getGotoSearchData(), self.getConnectHeaders())
        
    def searchPromo(self, promo):
        self.promo = str(promo)
        self.POSTquery(self.getGotoSearchPromoData(), self.getConnectHeaders())
    
    def searchPerso(self, perso_id):
        self.perso_id = perso_id
        self.POSTquery(self.getInfoPersoData(), self.getConnectHeaders())
        textarea = self.bs.find('textarea')
        if not textarea or textarea.attrs['id'] != 'IWMEMONOTICEBIO':
            raise Exception("No textarea found !" + str(promo) + " : " + perso_id)
        self.perso_info = textarea.contents[0]
    
    def returnPerso(self):
        self.POSTquery(self.getReturnData(), self.getConnectHeaders())
        self.perso_id = None
        self.perso_info = None
    
    def tableauActifs(self):
        self.POSTquery(self.getTableauActifsData(), self.getConnectHeaders())
    
    def returnTableauActifs(self):
        self.POSTquery(self.getTableauActifsReturnData(), self.getConnectHeaders())

    def tableauDispos(self):
        self.POSTquery(self.getTableauDisposData(), self.getConnectHeaders())
    
    def returnTableauDispos(self):
        self.POSTquery(self.getTableauDisposReturnData(), self.getConnectHeaders())


    def getPoliteHeaders(self):
        d = getBasicHeader()
        d['Accept-Encoding']='gzip, deflate'
        d['Content-Type']='application/x-www-form-urlencoded'
        d['Cookie']='IntraWeb_Heracles=' + self.cookie + '; IW_CookieCheck_=Enabled'
        d['Origin']='https://heracles.economie.gouv.fr'
        d['Referer']='https://heracles.economie.gouv.fr/'
        return d

    def getConnectHeaders(self):
        d = self.getPoliteHeaders()
        d['Referer']='https://heracles.economie.gouv.fr/Heracles'
        return d

    def getPoliteData(self):
        return {'IW_width':'1570',
                'IW_height':'120',
                'IW_SessionID_':self.session_id,
                'IW_TrackID_':str(self.session_count) }

    def getInitHeaders(self):
        d = getBasicHeader()
        d['Cookie']='IW_CookieCheck_=Enabled; IntraWeb_Heracles=' + self.cookie
        return d
    
    def getLoginData(self):
        return {'IWEDLOGIN'   :self.mail,
                'IWEDPASSWORD':self.password,
                'LNKSIGNIN':'Valider',
                'IW_Action':'LNKSIGNIN',
                'IW_ActionParam':'',
                'IW_FormName':'FormLoginHeracles',
                'IW_FormClass':'TFormLoginHeracles',
                'IW_width':'1581',
                'IW_height':'602',
                'IW_TrackID_':'1' }
    
    def getClickData1(self):
        return {'IWEDLOGIN':'Votre E.Mail',
                '':'',
                'IW_Action':'IWEDLOGIN',
                'IW_ActionParam':'',
                'IW_FormName':'FormLoginHeracles',
                'IW_FormClass':'TFormLoginHeracles',
                'IW_width':'1581',
                'IW_height':'602',
                'IW_TrackID_':'1' }
    
    def getClickData2(self):
        return {'IWEDLOGIN':'',
                '':'',
                'IW_Action':'IWEDLOGIN',
                'IW_ActionParam':'',
                'IW_FormName':'FormLoginHeracles',
                'IW_FormClass':'TFormLoginHeracles',
                'IW_width':'1581',
                'IW_height':'602',
                'IW_TrackID_':'1' }
                
    def getGotoSearchData(self):
        return {'IW_Action':'IWMENU1',
                'IW_ActionParam':'IWMENU1_submenu1',
                'IW_FormName':'FormMenu',
                'IW_FormClass':'TFormMenu',
                'IW_width':'1598',
                'IW_height':'149',
                'IW_TrackID_':str(self.session_count) }

    def getGotoSearchPromoData(self):
        return {'IWBTRETOUR':'',
                'IWBTRAZ':'',
                'IWBTRECHERCHE':'Lancer la recherche',
                'IWERECHERCHEPARNOM':'',
                'IWERECHERCHEPROMOTION':self.promo,
                'IWECODEPOSTAL':'',
                'IWERAISONSOCIALE':'',
                'IWEFONCTIONS':'',
                'IWDBLCBPAYS':'-1',
                'IW_Action':'IWBTRECHERCHE',
                'IW_ActionParam':'',
                'IW_FormName':'IWFormRecherche',
                'IW_FormClass':'TIWFormRecherche',
                'IW_width':'1598',
                'IW_height':'234',
                'IW_TrackID_':str(self.session_count) }

    def getInfoPersoData(self):
        return {'IWBTRETOUR':'',
                'IWBTRAZ':'',
                'IWDBGRIDLISTE':'',
                'IWBTRECHERCHE':'Lancer la recherche',
                'IWERECHERCHEPARNOM':'',
                'IWERECHERCHEPROMOTION':self.promo,
                'IWECODEPOSTAL':'',
                'IWERAISONSOCIALE':'',
                'IWEFONCTIONS':'',
                'IWDBLCBPAYS':'-1',
                'IW_Action':'IWDBGRIDLISTE',
                'IW_ActionParam':self.perso_id,
                'IW_FormName':'IWFormRecherche',
                'IW_FormClass':'TIWFormRecherche',
                'IW_width':'1598',
                'IW_height':'325',
                'IW_TrackID_':str(self.session_count) }

    def getReturnData(self):
        return {'IWBUTTON2':'',
                'IWMEMONOTICEBIO':'', #self.perso_info,
                'IW_Action':'IWBUTTON2',
                'IW_ActionParam':'',
                'IW_FormName':'IWFormNoticeBio',
                'IW_FormClass':'TIWFormNoticeBio',
                'IW_width':'1598',
                'IW_height':'325',
                'IW_TrackID_':str(self.session_count) }

    def getTableauActifsData(self):
        return { 'IW_Action':'IWMENU1',
                 'IW_ActionParam':'IWMENU1_submenu18',
                 'IW_FormName':'FormMenu',
                 'IW_FormClass':'TFormMenu',
                 'IW_width':'1918',
                 'IW_height':'395',
                 'IW_TrackID_':str(self.session_count) }

    def getTableauActifsReturnData(self):
        return {'IWBTRETOUR':'',
                'IWEDNODOSSIER':'',
                'IWEDNOM':'',
                'IWEDPRENOM':'',
                'IWDBGRIDINGACTIVITE':'',
                'IWDBGRID1':'',
                'IWREGIONTITRE_data':'0,105',
                'IW_Action':'IWLKMENU',
                'IW_ActionParam':'',
                'IW_FormName':'IWFormTabIngActivite',
                'IW_FormClass':'TIWFormTabIngActivite',
                'IW_width':'1918',
                'IW_height':'395',
                'IW_TrackID_':str(self.session_count) }


    def getTableauDisposData(self):
        return { 'IW_Action':'IWMENU1',
                 'IW_ActionParam':'IWMENU1_submenu19',
                 'IW_FormName':'FormMenu',
                 'IW_FormClass':'TFormMenu',
                 'IW_width':'1918',
                 'IW_height':'395',
                 'IW_TrackID_':str(self.session_count) }

    def getTableauDisposReturnData(self):
        return {'IWBTRETOUR':'',
                'IWEDNODOSSIER':'',
                'IWEDNOM':'',
                'IWEDPRENOM':'',
                'IWDBGRIDINGACTIVITE':'',
                'IWDBGRID1':'',
                'IWREGIONTITRE_data':'0,97',
                'IW_Action':'IWLKMENU',
                'IW_ActionParam':'',
                'IW_FormName':'IWFormTabIngDispo',
                'IW_FormClass':'TIWFormTabIngDispo',
                'IW_width':'1918',
                'IW_height':'395',
                'IW_TrackID_':str(self.session_count) }


class Results:
    def __init__(self, email, password):
        self.data = {}
        self.data_perso = {}
        self.tableauActifs = []
        self.tableauDispos = []
        self.con = Connection(email, password)
        self.con.startNewConnection()
        self.con.politeResponse()
        self.con.clickRequest1()
        self.con.clickRequest2()
        self.con.connect()
        self.con.gotoSearch()

    def addActifs(self):
        self.con.tableauActifs()
        table = self.con.bs.find('table')
        if not table:
            raise Exception("No table found !")
        if table.attrs['id'] != 'TBLIWDBGRIDLISTE':
            raise Exception("Wrong id: " + table.attrs['id'])
        rows = table.find_all('tr')
        res = []
        for r in rows:
            if 'onclick' in r.attrs:
                a = []
                a.append( re.findall(',\'(.*)\',', r.attrs['onclick'])[0] )
                a += [ e.contents[0].contents[0] for e in r.find_all('td')]
                res.append(a)
        self.tableauActifs = res
        self.con.returnTableauActifs()
    
    def addDispos(self):
        self.con.tableauDispos()
        self.tableauDispos.append(self.con.bs)
        self.con.returnTableauDispos()
    
    def addPromos(self, start, end):
        for promo in range(start,end+1):
            self.addPromo(promo)
    
    def addPromo(self, promo):
        self.con.searchPromo(promo)
        table = self.con.bs.find('table')
        if not table:
            raise Exception("No table found !")
        if table.attrs['id'] != 'TBLIWDBGRIDLISTE':
            raise Exception("Wrong id: " + table.attrs['id'])
        rows = table.find_all('tr')
        res = []
        for r in rows:
            if 'onclick' in r.attrs:
                a = []
                a.append( re.findall(',\'(.*)\',', r.attrs['onclick'])[0] )
                a += [ e.contents[0].contents[0] for e in r.find_all('td')]
                if len(a) != 9:
                    raise Exception("Wrong length array.")
                d = {'ID':a[0].encode('utf-8'),
                     'Nom':a[1].encode('utf-8'),
                     'Prenom':a[2].encode('utf-8'),
                     'Grade':a[3].encode('utf-8'),
                     'Promo':a[4].encode('utf-8'),
                     'Statut':a[5].encode('utf-8'),
                     'Fonctions': '' if a[6] == u'\xa0' else a[6].encode('utf-8'),
                     'Employeur':a[7].encode('utf-8'),
                     'Pays':a[8].encode('utf-8'),
                     'Bio':''}
                res.append(d)
        self.data[promo] = res
        # enrich data
        print "Promo " + str(promo) + " parsed. (" + str(len(res)) + "found)."
        for e in res:
            self.con.searchPerso( e['ID'] )
            e['Bio'] = self.con.perso_info.encode('utf-8')
            self.con.returnPerso()
        return res

    def writeAllData(self, filename):
        fieldnames = ['ID', 'Nom', 'Prenom', 'Grade', 'Promo', 'Statut', 'Fonctions', 'Employeur', 'Pays', 'Bio']
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for e in self.data:
                writer.writerows(self.data[e])
    
    def addDataPerso(self, perso_id):
        self.con.searchPerso(perso_id)
        self.data_perso[perso_id] = self.con.perso_info
        self.con.returnPerso()



r = Results(my_mail, my_password)


#r.addActifs()

r.addPromos(2010, 2014)

r.writeAllData("results.csv")
