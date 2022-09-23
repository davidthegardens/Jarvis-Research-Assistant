import tkinter as tk
from tkinter import *
from tkinter.ttk import*
from tkinter import ttk
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import requests
import pandas as pd
from urllib.parse import urlparse
# run: pip install gitpython
from git import Repo
import pathlib
import os
import shutil
import random
import PyPDF2 as pypdf
import validators
import time
from tkinter import filedialog
from csv import reader

#toggle test mode to false to get operating app
TestVarList=['SushiSwap','https://app.sushi.com',"https://docs.sushi.com",'https://github.com/sushiswap/sushiswap']
TestMode=True
bigbuttonlist=[]
if TestMode==True:
    VariableResults=TestVarList

def saveDF(df,saveframe):
    saveframe.destroy()
    savelocation=str(filedialog.askdirectory())+'/'+VariableResults[0]+'.csv'
    ContentList=df['Content'].tolist()
    EncodedList=[]
    for line in ContentList:
        line=str(line).encode(encoding='UTF-8')
        EncodedList.append(line)
    EncodedList2=[]
    LocationList=df['Location'].tolist()
    for line in LocationList:
        line=str(line).encode(encoding='UTF-8')
        EncodedList2.append(line)
    TempDF=pd.DataFrame({'LocationList':EncodedList2,'Content':EncodedList})
    df['Content']=TempDF['Content']
    df=df.dropna(subset=['Content'])
    df=df.drop_duplicates(subset=['Content'])
    df.to_csv(savelocation,index=False)
    saveframe.destroy()
    print('saved to '+savelocation)

def importDF(root):
    importlocation=filedialog.askopenfile(filetypes=[('CSV', ['.csv'])])
    #,encoding='utf-8', encoding_errors='replace'
    df=pd.read_csv(importlocation,encoding='UTF-8',encoding_errors='strict')
    df['Location','Content']=df.to_string(['Location','Content'])
    CreateQueryer(root,df,[])
    print('imported')

def EstablishConnection():
    response_API=requests.get(URL)
    outputx=int(response_API.status_code)
    if outputx==200:
        returning="Healthy Connection"
    if outputx==204:
        returning="Successful connection without return of data"
    if outputx==301:
        returning="Moved permanently"
    if outputx==400:
        returning="Bad request, potentially erronious data"
    if outputx==401:
        returning="Authentication failed"
    if outputx==403:
        returning="Access forbidden"
    if outputx == 404:
        returning="API service not found"
    if outputx== 500:
        returning="Internal Server Error"
    if outputx not in [200,204,401,403,404,500,400]:
        returning="unknown error, output: "
    return str(returning)+": "+str(outputx)

def CloneRepo(ProtocolName,GitURL):
    print('cloning '+str(GitURL))
    localpath=str(pathlib.Path().resolve())
    pathlist=localpath.split('\\')
    newpathlist=[]
    breakage=False
    for x in pathlist:
        newpathlist.append(x)
        if breakage==True:
            break
        if x == "Users":
            breakage=True
    localpath="/".join(newpathlist)
    #pathbelow is specific to DeFiSafety synced folder, must be tweeked for other usage
    savelocation=localpath+"/Sync/DeFiSafety Common/Products/Processs Quality Reviews/Reviews - Copy/0.8/"+ProtocolName+'_Courtesy_Of_Jarvis'
    Repo.clone_from(GitURL, savelocation)
    print('cloned to '+savelocation)
    return savelocation

def PDFScraper(path,LocationList,ContentList):
    content = ""
    p = open(path, "rb")
    pdf = pypdf.PdfFileReader(p)
    num_pages=pdf.numPages-1
    for i in range(0, num_pages):
        content = pdf.getPage(i).extractText() + "\n"
        content = content.replace(u"\xa0", " ")
        ContentList.append('Page '+str(i+1)+':\n'+content.lower())
        LocationList.append(path)
    p.close()
    return LocationList,ContentList

def OtherScraper(path):
    file=open(path,encoding='utf-8')
    Content=file.readlines()
    Content=' '.join(Content)
    file.close()
    return Content

def ScrapeDir(directory,df):
    #toggle variable below to create flat directory
    CreateFlattenedDirectory=False
    LocationList=[]
    ContentList=[]
    scrapethesefileypes=['.md','.txt','.pdf']
    for dirpath,_,filenames in os.walk(directory):
        if 'Flattened_Courtesy_Of_Jarvis' in dirpath:
            continue
        for f in filenames:
            movethis=os.path.abspath(os.path.join(dirpath, f))
            file_extension = pathlib.Path(movethis).suffix
            if file_extension in scrapethesefileypes:
                if file_extension=='.pdf':
                    LocationList,ContentList=PDFScraper(movethis,LocationList,ContentList)
                else:
                    LocationList.append(movethis)
                    ContentList.append(OtherScraper(movethis).lower())
            else:
                LocationList.append(movethis)
                ContentList.append(f)
        
            if CreateFlattenedDirectory:
                dst_path=directory+'/Flattened_Courtesy_Of_Jarvis'
                os.mkdir(dst_path)
                if os.path.exists(dst_path+f):
                    f=f[:-len(file_extension)]+str(random.choice(range(999999999)))+file_extension
                try:
                    shutil.copy2(movethis,dst_path)
                    #print(movethis + " >>> " + dst_path)
                except Exception:
                    print('error: '+str(movethis))
                    pass
    newdf=pd.DataFrame({'Location':LocationList,'Content':ContentList})
    df=pd.concat([df,newdf], axis=0, ignore_index=True)
    return df

def Reporter(df,root,QueryKey,undigested):
    Header='''   _____  _______  _______  ___ ___  ___  _______ x
|   _   ||   _   ||   _   \|   Y   ||   ||   _   |x
|___|   ||.  1   ||.  l   /|.  |   ||.  ||   1___|x
|.  |   ||.  _   ||.  _   1|.  |   ||.  ||____   |x
|:  1   ||:  |   ||:  |   ||:  1   ||:  ||:  1   |x
|::.. . ||::.|:. ||::.|:. | \:.. ./ |::.||::.. . |x
`-------'`--- ---'`--- ---'  `---'  `---'`-------'x
    '''
    frameboy=Frame(root)
    frameboy.place(x=550,y=50)
    v = Scrollbar(frameboy)
    v.pack(side=RIGHT,fill=Y)
    t = tk.Text(frameboy, width = 54, height = 25,wrap=WORD,yscrollcommand = v.set)
    t.configure(font=("Courier",10))
    for line in Header.split('x'):
        t.insert(END,line)
    t.insert(END,'\nResults for query "'+QueryKey+'"\n\n')
    for idx,row in df.iterrows():
        text1=str(row['Location'])+'\n'+str(row['Content'])+'\n\n'
        t.insert(END,text1)
    t.insert(END,'Unscraped URLs in greylist:'+'\n\n')
    for i in undigested:
        t.insert(END,i+'\n\n')
    t.pack(side=LEFT)
    v.config(command=t.yview)

def QueryDF(root,SearchBar,framey,df,GreyList):
    QueryKey=str(SearchBar.get("1.0", "end-1c"))
    firstdf=df[df['Content'].str.contains(QueryKey.strip(), regex=False)]
    seconddf=df[df['Location'].str.contains(QueryKey.strip(), regex=False)]
    fulldf=pd.concat([firstdf,seconddf], axis=0, ignore_index=True)
    fulldf=fulldf.drop_duplicates(subset=['Content'])
    #print(fulldf)
    framey.destroy()
    undigested=[]
    for i in GreyList:
        if QueryKey in i:
            undigested.append(i)
    framey,SearchBar=CreateQueryer(root,df,GreyList)
    Reporter(fulldf,root,QueryKey,undigested)
    SearchBar.insert(END,QueryKey)

def CreateQueryer(root,df,GreyList):
    try:
        framey.destroy()
    except: Exception
    framey=Frame(root)
    framey.place(x=550,y=10)
    SearchBar= tk.Text(framey, height=1, width=50)
    SearchBar.pack(side=LEFT)
    SearchButton=tk.Button(framey,height=1,width=5,text='Search',command=lambda:QueryDF(root,SearchBar,framey,df,GreyList))
    SearchButton.pack(side=RIGHT)
    return framey,SearchBar

def ConstructCanvas():
    #####Make below list into dict for enhanced readability
    
    def ExtractVariables():
        global VariableResults
        if TestMode:
            VariableResults=TestVarList
        else:
            VariableNames=[Text1,Text2,Text3,Text4]
            VariableResults=[]
            for x in VariableNames:
                bla=x.get("1.0", "end-1c")
                VariableResults.append(bla.strip())
        return VariableResults

    def initialize():
        #global URLs
        PopUp=Label(root,text='Initializing... This may take a minute')
        PopUp.configure(font=("Courier",25))
        PopUp.place(x=100,y=800)
        URLx=ExtractVariables()[2]
        whitelist=[URLx]
        option = webdriver.ChromeOptions()
        option.add_argument('—incognito')
        #option.add_argument("--headless")
        global browser
        #path below should be replaced by user's chromedriver location
        browser = webdriver.Chrome(service=Service('C:/Users/davidj.desjardins/Desktop/chromedriver'), options=option)
        #browser = webdriver.Chrome(service=Service('C:\\Users\\david\\Downloads\\chromedriver_win32\\chromedriver.exe'), options=option)
        blacklist=[]
        thisHTML=GetHTML(URLx)
        GreyList=ExtractURLs(thisHTML,URLx)
        #print(ExtractContent(thisHTML,URLx))
        df=ExtractContent(thisHTML,URLx)
        #print(GreyList)
        CreateLinkAdder(whitelist,GreyList,blacklist,df)
        PopUp.destroy()
        
    def CreateLinkAdder(whitelist,GreyList,blacklist,df):
        
        def LinkAdder(URL,whitelist,GreyList,blacklist,frame3,frame1,df,framey,override):
            if override==False:
                option=selected.get()
            else:
                option=override
            if option =='Remove':
                blacklist.append(URL)
                GreyList.remove(URL)
                #print(len(GreyList),len(GreyList))
                if override==False:
                    frame3.destroy()
                print("'"+URL+"' removed")
            else:
                print('adding '+"'"+URL+"'")
                whitelist.append(URL)
                ThisHTMLList=GetHTML(URL)
                GreyList.extend(ExtractURLs(ThisHTMLList,URL))
                GreyList=list(set(GreyList))
                removelist=[]
                removelist.extend(whitelist)
                removelist.extend(blacklist)
                for i in removelist:
                    if i in GreyList:
                        GreyList.remove(i)
                df=pd.concat([df,ExtractContent(ThisHTMLList,URL)], axis=0, ignore_index=True)
                #print(df)
                frame1.destroy()
                framey.destroy()
                GUIElements(whitelist,GreyList,blacklist,df)
                print("'"+URL+"'added")
            #print(len(GreyList))
            return GreyList,whitelist,blacklist,frame1,framey,df
            
        def GUIElements(whitelist,GreyList,blacklist,df):
            #global buttons
            #print('white')
            #print(whitelist)
            #print('grey')
            #print(GreyList)
            #print('black')
            #print(blacklist)
            try:
                saveframe.destroy()
            except: Exception
            framey,nouse=CreateQueryer(root,df,GreyList)
            saveframe=Frame(root)
            frame1=Frame(root)
            allframe=Frame(root)
            buttons=[]
            canvas_container=Canvas(frame1, height=400,width=300)
            canvas_container.configure(scrollregion=canvas_container.bbox("all"))
            myscrollbar=Scrollbar(frame1,orient="vertical",command=canvas_container.yview)
            #canvas_container.configure(yscrollcommand=myscrollbar.set)
            frame2=Frame(canvas_container)
            canvas_container.create_window((0,0),window=frame2,anchor='nw')#???
            counter=0
            GreyList=list(set(GreyList))
            GreyList.sort()
            #add if len(GreyList)==0 ...

            for i in GreyList:
                if validators.url(i)!=True:
                    #print(i)
                    GreyList.remove(i)
                    blacklist.append(i)
                    continue
                elif VariableResults[3] in i:
                    GreyList.remove(i)
                    whitelist.append(i)
                frame3=Frame(frame2)
                button = Button(frame3,text=i,command=lambda i=i,frame3=frame3,frame1=frame1:[LinkAdder(i,whitelist,GreyList,blacklist,frame3,frame1,df,framey,False)])
                buttons.append(button)
                frame3.pack(anchor='nw')
                button.pack(anchor='nw')
                counter=counter+1
            frame2.update()
            canvas_container.configure(yscrollcommand=myscrollbar.set, scrollregion="0 0 0 %s" % frame2.winfo_height())
            canvas_container.pack(side=LEFT)
            myscrollbar.pack(side=RIGHT, fill = Y)
            frame1.place(x=220,y=0)
            allframe.place(x=220,y=410)
            AllButton=tk.Button(allframe,text='ALL',height=2,width=10,command=lambda frame1=frame1:AllCommand(whitelist,blacklist,GreyList,frame1,df,allframe,framey,False,False))
            AllButton.pack(anchor='sw')
            SaveButton=tk.Button(saveframe,text="Save", height=1, width=6, command=lambda:saveDF(df,saveframe))
            saveframe.place(x=80,y=290)
            SaveButton.pack()
            return whitelist,blacklist,GreyList,frame1,df,allframe,framey,frame3

        def AllCommand(whitelist,blacklist,GreyList,frame1,df,allframe,framey,override,search):
            if override==False:
                option=selected.get()
                domain=domainscrape.get("1.0", "end-1c")
            else:
                option=override
                domain=search
            #print('domain: '+domain)
            if domain=='':
                moddedURLList=GreyList
            else:
                moddedURLList=[]
                for item in GreyList:
                    if domain in item:
                        moddedURLList.append(item)
                    else: continue
            #print(moddedURLList)
            if option=="Remove" and domain!='':
                #print('1')
                blacklist.extend(moddedURLList)
                for item in moddedURLList:
                    GreyList.remove(item)
            elif option=="Remove" and domain=='':
                blacklist.extend(moddedURLList)
                GreyList=[]
                #print('2')
            else:
                whitelist.extend(moddedURLList)
                counter=0
                NewURLs=[]
                #print('3')
                for i in moddedURLList:
                    ThisHTMLList=GetHTML(i)
                    NewURLs.extend(ExtractURLs(ThisHTMLList,i))
                    df=pd.concat([df,ExtractContent(ThisHTMLList,i)], axis=0, ignore_index=True)
                    counter=counter+1
                    print('This will take a moment... '+str(counter)+'/'+str(len(moddedURLList))+' completed')
                removelist=whitelist
                removelist.extend(blacklist)
                removelist=list(set(removelist))
                GreyList.extend(NewURLs)
                GreyList=list(set(GreyList))
                for i in removelist:
                    try:
                        GreyList.remove(i)
                    except:
                        Exception
                        pass
            frame1.destroy()
            allframe.destroy()
            #print(whitelist,GreyList,blacklist)
            framey.destroy()
            GUIElements(whitelist,GreyList,blacklist,df)
            return whitelist,blacklist,GreyList,frame1,df,allframe,framey

        
        selected = tk.StringVar()
        r1 = ttk.Radiobutton(root, text='Add', value='Add', variable=selected)
        r2 = ttk.Radiobutton(root, text='Remove', value='Remove', variable=selected)
        domainscrape=tk.Text(root, height=1, width=25)
        r1.place(x=320,y=410)
        r2.place(x=420,y=410)
        domainscrape.place(x=320,y=430)
        whitelist,blacklist,GreyList,frame1,df,allframe,framey,frame3=GUIElements(whitelist,GreyList,blacklist,df)
        GreyList,whitelist,blacklist,frame1,framey,df=LinkAdder(VariableResults[1],whitelist,GreyList,blacklist,frame3,frame1,df,framey,'Add')
        whitelist,blacklist,GreyList,frame1,df,allframe,framey=AllCommand(whitelist,blacklist,GreyList,frame1,df,allframe,framey,'Add',VariableResults[2])
        whitelist,blacklist,GreyList,frame1,df,allframe,framey=AllCommand(whitelist,blacklist,GreyList,frame1,df,allframe,framey,'Add',VariableResults[1])
        if VariableResults[3]!='':
            df=ScrapeDir(CloneRepo(VariableResults[0],VariableResults[3]),df)
            whitelist,blacklist,GreyList,frame1,df,allframe,framey=AllCommand(whitelist,blacklist,GreyList,frame1,df,allframe,framey,'Add',VariableResults[3])
        framey=CreateQueryer(root,df,GreyList)

    # get screen dimensions
    root = tk.Tk()
    root.wm_attributes("-topmost", 1)
    #root.option_add('*Font', 'Arial 8')
    height=root.winfo_screenheight()
    width=root.winfo_screenwidth()
    geo=str(width)+'x'+str(height)
    #print(height,width)
    #create canvas
    root.geometry(geo)
    root.title("JARVIS")
    Label1= tk.Label(root,text="Protocol name", height=1, width=16)
    Label2= tk.Label(root,text="Protocol URL", height=1, width=16)
    Label3= tk.Label(root,text="Docs URL", height=1, width=16)
    Label4= tk.Label(root,text="Repo URL", height=1, width=16)

    Text1= tk.Text(root, height=1, width=22)
    Text2= tk.Text(root, height=1, width=22)
    Text3= tk.Text(root, height=1, width=22)
    Text4= tk.Text(root, height=1, width=22)

    RunButton= tk.Button(root,text="Initialize", height=1, width=15, command=initialize)
    ImportButton=tk.Button(root,text="Import", height=1, width=6, command=lambda:importDF(root))
    ImportButton.place(x=20,y=290)

    Label1.place(x=0, y=20)
    Label2.place(x=0, y=80)
    Label3.place(x=0, y=140)
    Label4.place(x=0, y=200)

    Text1.place(x=20, y=50)
    Text2.place(x=20, y=110)
    Text3.place(x=20, y=170)
    Text4.place(x=20, y=230)

    RunButton.place(x=20,y=260)
    

    tk.mainloop()

def GetEasyHTML(URL):
    session=HTMLSession()
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"}
    response=session.get(URL,headers=headers)
    if str(response.html.absolute_links)=='set()':
        Validity=False
    else:
        Validity=True
    result=response.content
    return result,Validity
#Takes URL in string, returns HTML file in bytes

def GetHardHTML(URL):
    browser.get(URL)
    browser.fullscreen_window()
    print("handshake successful")
    elements=browser.find_elements(by=By.TAG_NAME, value="button")
    htmllist=[]
    def ComplexHTML():
        if LONGSTRING not in htmllist:
            LONGSTRING=browser.page_source
            htmllist.append(LONGSTRING)
            status="PASS"
        else:
            status="FAIL"
        return status
    counter=1
    if elements not in bigbuttonlist:
        bigbuttonlist.append(elements)
        print('ButtonList length: '+str(len(bigbuttonlist)))
        for x in elements:
            try:
                hover=ActionChains(browser).move_to_element(to_element=x)
                hover.perform()
                ComplexHTML()
            except:
                try:
                    x.click()
                    ComplexHTML()
                    if browser.current_url != URL:
                        browser.back()
                except:
                    Exception
            
            print(str(counter)+"/"+str(len(elements))+" button(s) evaluated")
            counter=counter+1
    else:
        htmllist.append(browser.page_source)
        print('skipped button scrape')
    print('complex scrape completed')
    return htmllist
#Takes URL in string, returns HTML file in bytes in list

def GetHTML(URL):
    if requests.get(URL).status_code!=200:
        HTMLis='dead'
    result,Validity=GetEasyHTML(URL)
    if Validity is True:
        HTMLis=[result]
    else:
        HTMLis=GetHardHTML(URL)
    return HTMLis
#Takes URL in string, returns HTML file in bytes in list

def test():
    testurl="https://www.google.com/"
    bruh=ExtractURLs(GetHardHTML(testurl),testurl,[])
    book=open('C:\\Users\\david\\Downloads\\complexscrape.txt','a', encoding="utf-8")
    for x in bruh:
        book.write(x)

def ExtractURLs(ThisHTMLList,URL):
    GreyList=[]
    if ThisHTMLList!='dead':
        for x in ThisHTMLList:
            soup = BeautifulSoup(x, 'html.parser')
            for link in soup.find_all('a', href=True):
                templink=link.get('href')
                if len(templink)<=1:
                    continue
                if templink[:1]=="#":
                    continue
                if '/#' in templink:
                    continue
                if templink[:1]=="/":
                    schemelist=URL.split('://')
                    scheme=schemelist[0]+"://"
                    tempURL=urlparse(URL).netloc
                    output=scheme+tempURL+templink
                    if output[-1]=="/":
                        output=output[:-1]
                    GreyList.append(output)
                else:
                    if templink[-1]=="/":
                        templink=templink[:-1]
                    GreyList.append(templink)
        GreyList=list(set(GreyList))
        replacementlist=[]
        for i in GreyList:
            if ' ' in i:
                replacementlist.append(i.replace(' ','%20'))
            else:
                replacementlist.append(i)
        GreyList=replacementlist
    return GreyList
#Takes HTML in bytes in list, URL in string, and preexisting list of URLs. Outputs added URLs in the list provided in string
#print(ExtractURLs(GetHTML(testurl),testurl,[]))

def ExtractContent(ThisHTMLList,URL):
    if ThisHTMLList!='dead':
        for x in ThisHTMLList:
            soup = BeautifulSoup(x, 'html.parser')
            content=soup.get_text(separator="nobodywilleverfindthisstringrealistically12345678910$%^*@^)!")
            contlist=content.split("\n")
            blankcount=contlist.count('')
            for i in range(blankcount):
                    contlist.remove('')
            contlist=content.split("nobodywilleverfindthisstringrealistically12345678910$%^*@^)!")
            finallist=[]
            for i in contlist:
                lowered=i.lower()
                stripped=lowered.strip()
                if "nobodywilleverfindthisstringrealistically12345678910$%^*@^)!" in i:
                    finallist.extend(stripped.split("nobodywilleverfindthisstringrealistically12345678910$%^*@^)!"))
                else:
                    finallist.append(stripped)

            URLList=[]
            for i in finallist:
                URLList.append(URL)
            ContentDict={'Location':URLList,'Content':finallist}
            df=pd.DataFrame.from_dict(ContentDict)
            return df
#Takes list of html bytes, returns list of content in string
#print(ExtractContent(GetHTML(testurl),testurl))

def ScrollableWindow():
    root = Tk()
    v = Scrollbar(root)
    v.place(x = 400, y=300)
    t = Text(root, width = 15, height = 15, wrap = NONE,yscrollcommand = v.set)
    for i in range(20):
        t.insert(END,"this is some text\n")
    t.place(x=200, y=300)
    v.config(command=t.yview)
    root.mainloop()

#ScrollableWindow()
ConstructCanvas()

def Experimental():
    root=Tk()
    frame_container=Frame(root)
    canvas_container=Canvas(frame_container, height=300,width=100)
    frame2=Frame(canvas_container)
    myscrollbar=Scrollbar(frame_container,orient="vertical",command=canvas_container.yview)
    canvas_container.create_window((0,0),window=frame2,anchor='nw')#???
    mylist = ['item1','item2','item3','item4','item5','item6','item7','item8','item9']
    for item in mylist:
        button = Button(frame2,text=item)
        button.pack()
    frame2.update()
    canvas_container.configure(yscrollcommand=myscrollbar.set, scrollregion="0 0 0 %s" % frame2.winfo_height())
    canvas_container.pack(side=LEFT)
    myscrollbar.pack(side=RIGHT, fill = Y)
    frame_container.pack()
    root.mainloop()

#saveDF(pd.read_csv('C:\\Users\\david\\Downloads\\TestFolder\\SushiSwap.csv'),None)