from selenium import webdriver                    
from selenium.webdriver.common.keys import Keys   
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time     
import pandas as pd
import csv
start_time = time.time() #starts timer for how long porgrams runs for

def scrape_posts():
    post_list = [] #list of all the fully filtered comments
    df = pd.DataFrame() #creates a dataframe that filtered data is being put into
    writer = pd.ExcelWriter('File') #outputs to excel file i specified 
    URL = 'url to forum login' #URL for login page to forum 
    browser = webdriver.Chrome() #creates browser for selenium
    wait = WebDriverWait(browser, 4) #instantiates WebDriverWait as wait
    specificWait = WebDriverWait(browser, 1.5) #instantiates WebDriverWait as wait for multiple pages in thread 
    browser.get(URL)    
    username = wait.until(EC.element_to_be_clickable((By.ID, 'user_login'))) #finds username box
    username.send_keys('username') #inserts username into username box                                  
    password = wait.until(EC.element_to_be_clickable((By.ID, 'user_pass'))) #finds password box
    password.send_keys('password') #inserts password into password box         
    signIn_button =  wait.until(EC.element_to_be_clickable((By.ID, 'wppb-submit'))).click() #finds sign in button and clicks on it
    goToForums =  wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'FORUMS'))).send_keys(Keys.ENTER) #finds forum tab and clicks on it
    goToSpecificForum = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="top"]/div[4]/div/div[3]/div[1]/div[1]/div[2]/div/div/div[3]/div/div[1]/h3/a'))).click() #finds button for specific forum
    maxPage = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="top"]/div[4]/div/div[3]/div/div[1]/div/div[1]/div[1]/nav/div[1]/ul/li[5]/a'))) #finds the max page
    maxPage = maxPage.text #turns max page to text
    goToPage2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="top"]/div[4]/div/div[3]/div/div[1]/div/div[1]/div[1]/nav/div[1]/ul/li[2]/a'))).click() #goes to page 2 of forum because page 1 has unique XPATHS
    currentPage = 2 #starting page
    while(currentPage<int(maxPage)): #loops through every page as long as it isn't on the last one
        threadNames_list = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'structItem-title'))) #gets list of all the thread names
        turnListToText(threadNames_list)
        for threadName in threadNames_list: #loops through every thread
            goToEachThread =  wait.until(EC.element_to_be_clickable((By.LINK_TEXT, threadName))).click() #clicks on the thread
            pageCountInThread = 1 #current page count within thread
            stillRunning = True #used to check if there are still pages in thread that need to be scraped
            while(stillRunning==True): #while there are still pages to scrape in thread
                try: #if it can go to next page in the thread
                    comment_list = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'message-body.js-selectToQuote'))) #gets list of all the comments in thread
                    turnListToText(comment_list)
                    filteredComment_list = [] #list for after comments are filtered based on if they have a reply
                    for box in comment_list: #loops through comments to determine if they have reply and add them to appropiate list
                        testBox = str(box)[:40] #used to look if a comment contains a reply
                        if(testBox.find('said:')==-1): #if they don't have a reply
                            filteredComment_list.append(box) #appends comment if it doesn't have a reply
                    list1AppendToList2(filteredComment_list, post_list) #appends all comments in a specifc thread to list of all comments
                    if(pageCountInThread==1): #page 1 next button in thread is different from others
                        goToNextPage = specificWait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'pageNav-jump.pageNav-jump--next'))).click() #clicks on the next button to go to the next page
                        pageCountInThread = pageCountInThread + 1
                    else:
                        goToNextPage = specificWait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'pageNav-jump.pageNav-jump--next'))).click() #clicks on the next button to go to the next page
                        pageCountInThread = pageCountInThread + 1
                except: #if there are no more pages to scrape in the thread
                    for i in range(pageCountInThread): #loops as many times as there are pages in thread
                        browser.back() #presses back as many times as pages in thread to go back to list of threads
                    stillRunning = False #done scraping thread
        currentPage = currentPage + 1
        time.sleep(2)
        goToNextPage = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="top"]/div[4]/div/div[3]/div/div[1]/div/div[1]/div[1]/nav/div[1]/a[2]'))).click() #clicks on the next button to go to the next page in forum
    df['Comment']  = post_list #creates "Comment" column in dataframe and adds a list to it 
    print("The dataframe has been created!") #signals that program has created the dataframe 
    df.to_excel(writer, index = None) #sends the dataframe to excel
    writer.save() #saves the new excel file that the dataframe was sent to
    print("It has saved to excel!") #signals that the excel sheet has been created

def turnListToText(listPassed): #method for turning list that was scraped to text
    listCount = 0
    for item in listPassed:
        listPassed[listCount] = item.text
        listCount = listCount + 1

def list1AppendToList2(list1, list2): #method for appending one list to another
    for item in list1:
        list2.append(item)
    
scrape_posts() #calls scrape method
print("%s seconds      " % (time.time() - start_time)) #prints the time that the program ran for