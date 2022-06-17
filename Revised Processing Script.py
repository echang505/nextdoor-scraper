#Python 3
import time
from datetime import date
from threading import Thread

#pip install pandas xlrd
import pandas as pd

#pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

#pip install bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from random import randint
import numpy as np

import xlsxwriter
import config #Contains Username and Password to Login


def main(fileName):

   #File that contains data from previous run (MainScraper-WriteLinksToExcel.py)
   #rawDataFile = "PrimaryLinksList{}.xlsx".format(fileName)
   rawDataFile = "{}.xlsx".format(fileName)
   df = pd.read_excel(rawDataFile)
   df.replace("", np.nan, inplace = True)
   df.replace(" ", np.nan, inplace = True)
   df.replace('', np.nan, inplace = True)

   df.dropna(subset=['Link'], inplace = True)
   df.dropna(subset=['Date Posted'], inplace = True)
   df.dropna(subset=['Title'], inplace = True)

   print(df)
   columnNames = df.columns.values.tolist()
   #dateAccessed = columnNames[4]

   postNameList = pd.DataFrame(df, columns = ['Title']).values.tolist()
   postLinkList = pd.DataFrame(df, columns = ['Link']).values.tolist()
   postDateList = pd.DataFrame(df, columns = ['Date Posted']).values.tolist()

   print(postNameList, "\n")
   print(postLinkList, "\n")
   print(postDateList, "\n")


   #-------------------------------------------------New Excel Sheets Config-------------------------------------------------
   resultsFileName = "FinalScrapedData{}.xlsx".format(fileName)
   workbook = xlsxwriter.Workbook(resultsFileName)
   #Post worksheet Config
   worksheetPost = workbook.add_worksheet('Post')
   postColumnName = ['Post ID', 'Author Name', 'Neighborhood', 'Date', 'Subject', 'Post Link', 'Content of Post', 'Type of Post', '# of reactions', '# of comments']
   col = 0
   for item in postColumnName:
      worksheetPost.write(0, col, item)
      col += 1
      
   #Comment worksheet Config
   worksheetComm = workbook.add_worksheet('Comment')
   commColumnName = ['Post ID', 'Author Name', 'Neighborhood',	'Date', 'Comment_Author', 'Comment', 'Comment_neighborhood']
   col = 0
   for item in commColumnName:
      worksheetComm.write(0, col, item)
      col += 1
      
   #Reaction worksheet Config
   worksheetReac = workbook.add_worksheet('Reaction')
   reacColumnName = ['Post ID', 'Author Name', 'Neighborhood', 'Date', 'Reaction Author', 'Reaction_name', 'Reaction_neighborhood']
   col = 0
   for item in reacColumnName:
      worksheetReac.write(0, col, item)
      col += 1
   #HelpMap worksheet Config
   worksheetHelp = workbook.add_worksheet('Help Map_Content')
   reacColumnName = ['Neighorhood', 'Name', 'Help_post_content']
   col = 0
   for item in reacColumnName:
      worksheetReac.write(0, col, item)
      col += 1
   #Nearby Neighborhoods worksheet Config
   worksheetNear = workbook.add_worksheet('Nearby Neighborhoods')
   worksheetNear.write(0, 0, 'Focal')

   #*************************************************Initializing Site> Opens website, logs in, and converts view to list mode*************************************************
   #-------------------------------------------------Opens Site-------------------------------------------------
   url = "https://nextdoor.com/neighborhood_feed/"
   driverPath = "/chromedriver.exe"
   options = Options()
   options.page_load_strategy = 'eager'
   driver = webdriver.Chrome(options=options)
   driver.get(url)
   driver.maximize_window()
   time.sleep(2)

   #-------------------------------------------------Login - Make sure that config.py has username = "" and password = ""-------------------------------------------------
   WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.ID, "id_email"))).send_keys(config.username)
   WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.ID, "id_password"))).send_keys(config.password)
   driver.find_element_by_id("signin_button").send_keys(Keys.RETURN)
   driver.implicitly_wait(5) #seconds


   #-------------------------------------------------Scraping for nearby Neighborhoods + basic info-------------------------------------------------
   time.sleep(1)
   driver.get("https://nextdoor.com/map/")
   time.sleep(2)
   neighborhoodName = driver.find_element_by_css_selector('#map_legend_header > h4').text
   neighborhoodHouseholds = driver.find_element_by_css_selector('#map_legend > ul > li:nth-child(2) > span.totals').text
   neighborhoodPercent = driver.find_element_by_css_selector('#map_legend > div.growth-cta > div.growth-microcopy').text
   
   worksheetNear.write(0, 3, "neighborhoodName")
   worksheetNear.write(0, 4, "neighborhoodHouseholds")
   worksheetNear.write(0, 5, "neighborhoodPercent")
   
   worksheetNear.write(1, 3, neighborhoodName)
   worksheetNear.write(1, 4, neighborhoodHouseholds)
   worksheetNear.write(1, 5, neighborhoodPercent)


   #-------------------------------------------------Opens Each link and scrapes-------------------------------------------------
   time.sleep(3)
   commentRow = 1
   reacRow = 1
   postID = 1 #post ID for each post
   for i in range(len(postLinkList)):
      #removes [' and '] at ends of string
      print("Currently on post: " , postID, " / " , len(postLinkList))
      postLinkFixed = str(postLinkList[i])[2:-2] 
      driver.execute_script("window.open('{}');".format(postLinkFixed))
      driver.implicitly_wait(1)
      time.sleep(1)
      driver.switch_to.window(driver.window_handles[1])
      #start scraping current tab
      
      #scraping for Post worksheet
      driver.implicitly_wait(1)
      try: 
         authorName = driver.find_element_by_css_selector('#main_content > div > div > div._3sAFzPEm > div > div._11ZQQRUn._1tdcB7sn > span > span._1m8VqDxS > a').text
      except NoSuchElementException:
         authorName = ""
         
      try:
         authorNeighborhood = driver.find_element_by_css_selector('#main_content > div > div > div._3sAFzPEm > div > div._11ZQQRUn._1tdcB7sn > span > span._2P02evKh._3AsYwNHz > button').text
      except NoSuchElementException:
         authorNeighborhood = ""
         
      try:
         authorDate = driver.find_element_by_css_selector('#main_content > div > div > div._3sAFzPEm > div > div._11ZQQRUn._1tdcB7sn > span > span._2P02evKh._3AsYwNHz > a').text
      except NoSuchElementException:
         authorDate = ""

      try:
         entirePostContent = driver.find_element_by_css_selector('#main_content > div > div > div:nth-child(2) > div.content.clearfix > p > span > span > span').text.encode("utf-8")
      except NoSuchElementException:
         entirePostContent = ""
         
      authorSubject = str(postNameList[i])[2:-2]
      authorPostLink = str(postLinkList[i])[2:-2] 
       
      
      try:
         authorTypeOfPost = driver.find_element_by_css_selector('#main_content > div > div > div:nth-child(2) > div > div > span > a').text
      except NoSuchElementException:  #spelling error making this code not work as expected
         authorTypeOfPost = '-'
         pass

      try:
         authorNumberOfReactions = driver.find_element_by_css_selector('#main_content > div > div > div:nth-child(3) > div > div._13uYEoxe.css-1srqc6z > div > button > div._3n-MWIpy.nuanMjzR._3endVnpJ').text.rstrip("Neighbors")
      except NoSuchElementException:  #spelling error making this code not work as expected
         authorNumberOfReactions = '0'
         pass
     
      try:
         authorNumberOfComments = driver.find_element_by_css_selector('#main_content > div > div > div:nth-child(3) > div > div._13uYEoxe.css-1srqc6z > span > span').text.rstrip("Comments").rstrip("Comment")
      except NoSuchElementException:  #spelling error making this code not work as expected
         authorNumberOfComments = '0'
         pass
       
      postWorksheetInfo = [postID, authorName, authorNeighborhood, authorDate, authorSubject, authorPostLink, entirePostContent, authorTypeOfPost, authorNumberOfReactions, authorNumberOfComments]
      col = 0
      for item in postWorksheetInfo:
         worksheetPost.write(postID, col, str(item))
         col += 1
         
      #scraping for Reaction worksheet  
      if int(authorNumberOfReactions) >= 1:
         reactionButtonList = driver.find_elements_by_class_name('_1p1i18kz')
         if len(reactionButtonList) >= 1:
            reactionButtonList[0].click()
         
            driver.implicitly_wait(2)
            reactionList = driver.find_elements_by_class_name('css-1aj8q0q')
            

            for item in reactionList:
         #       print(postID)
         #       print(authorName)
         #       print(authorNeighborhood)
         #       print(authorDate)
                  try:
                     reactionAuthorList = item.find_elements_by_class_name('css-1on6jxn')
                  except StaleElementReferenceException:
                     reactionAuthorList = []
                  if len(reactionAuthorList) >= 1:
                     reactionAuthor = reactionAuthorList[0].text
                  else:
                     reactionAuthor = "Not Accessible"

         
                  try:
                     reactionNameList = item.find_elements_by_css_selector("div.css-1ficv68 img")
                  except StaleElementReferenceException:
                     reactionNameList = []
                  if len(reactionNameList) == 1:
                     reactionName = reactionNameList[0].get_attribute('alt')
                  elif (len(reactionNameList) == 0):
                     reactionName = "Not Accessible"
                  else:
                     reactionName = reactionNameList[1].get_attribute('alt')
                     
                  #print(reactionNameList)
                  
                  
                  try:
                     reactionNeighborhoodList = item.find_elements_by_class_name('css-12yzc8f')
                  except StaleElementReferenceException:
                     reactionNeighborhoodList = []
                  if len(reactionNeighborhoodList) >= 1:
                     reactionNeighborhood = reactionNeighborhoodList[0].text
                  else:
                     reactionNeighborhood = "Not Accessible"
                  
                  #print(reactionAuthor, reactionName, reactionNeighborhood)
                  
                  reacCol = 0   
                  reacWorksheetInfo = [postID, authorName, authorNeighborhood, authorDate, reactionAuthor, reactionName, reactionNeighborhood]
                  
                  
                  for item in reacWorksheetInfo:
                     worksheetReac.write(reacRow, reacCol, str(item))
                     reacCol += 1
                  reacRow += 1
                  
         else:
            reactionname = ""
            reactionNeighborhood = ""
            
         driver.implicitly_wait(1)       
         tempList = driver.find_elements_by_class_name('css-8jfvtp')
         if len(tempList) >= 2:
            try:
               tempList[1].click()
            except ElementClickInterceptedException:
               pass
            #scraping for Comment worksheet
      #scroll to load full site
      if authorNumberOfComments != '0':
         screen_height = driver.execute_script("return window.screen.height;")
         expandButtonList = []   
         i = 1
         for count in range(2):
            expandButtonList = []
            try:
               driver.implicitly_wait(3)
               expandButtonList = driver.find_elements_by_class_name('see-previous-comments-button-paged')
               if len(expandButtonList) != 0:
                  if expandButtonList[0].is_displayed():
                     try:
                        expandButtonList[0].click()
                     except ElementClickInterceptedException:
                        pass
               #WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.CLASS_NAME, "see-previous-comments-button-paged"))).click()
            except NoSuchElementException:  #spelling error making this code not work as expected
               pass
            
         while True:
            userInput = None
            # scroll one screen height each time
            driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
            i += 1
            time.sleep(randint(1,2))
            # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
            scroll_height = driver.execute_script("return document.body.scrollHeight;")  
            # Break the loop when the height we need to scroll to is larger than the total scroll height
            try:
               driver.implicitly_wait(2)
               expandButtonList = driver.find_elements_by_class_name('see-previous-comments-button-paged')
               if len(expandButtonList) != 0:
                  try:
                     expandButtonList[0].click()
                  except ElementClickInterceptedException:
                     pass
                  #WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.CLASS_NAME, "see-previous-comments-button-paged"))).click()
            except NoSuchElementException:  #spelling error making this code not work as expected
               pass
            if (screen_height) * i > scroll_height:
               break

      listOfComments =  driver.find_elements_by_class_name('js-media-comment')

      #print(listOfComments)
      for post in listOfComments:
   #       print(postID)
   #       print(authorName)
   #       print(authorNeighborhood)
         commentDateList = post.find_elements_by_class_name('css-9p9z55')
         commentDate = commentDateList[0].text.encode("utf-8")
         commentAuthorList = post.find_elements_by_class_name('comment-detail-author-name')
         commentAuthor = commentAuthorList[0].text.encode("utf-8")
         commentContentList = post.find_elements_by_class_name('_1ZgzHEd5')
         if len(commentContentList) >=1:
            commentContent = commentContentList[0].text.encode("utf-8")
         else:
            commentContent = ""
            
         commentNeighborhoodList = post.find_elements_by_class_name('css-27f5wi')
         if len(commentNeighborhoodList) >= 1:
            commentNeighborhood = commentNeighborhoodList[0].text.encode("utf-8")
         else:
            commentNeighborhood = ""
            
         commWorksheetInfo = [postID, authorName, authorNeighborhood, commentDate, commentAuthor, commentContent, commentNeighborhood]

         commentCol = 0
         for item in commWorksheetInfo:
            worksheetComm.write(commentRow, commentCol, str(item))
            commentCol += 1

         commentRow += 1
         
      

      #closes tab
      time.sleep(1)   
      driver.close()
      driver.switch_to.window(driver.window_handles[0])
      postID += 1
      
   workbook.close()
   driver.quit()


listOfFiles = ["FairchesterWoodsLinks3", "FairchesterWoodsLinks4" ]
for item in listOfFiles:
   main(item)