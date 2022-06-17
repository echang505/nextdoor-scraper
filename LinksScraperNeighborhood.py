#python 3

import time
from datetime import date
import random

#contains username and password to login
import config

#pip install xlsxwriter
import xlsxwriter

#pip install selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


class LocalStorage:

    def __init__(self, driver) :
        self.driver = driver

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def items(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, items = {}; " \
            "for (var i = 0, k; i < ls.length; ++i) " \
            "  items[k = ls.key(i)] = ls.getItem(k); " \
            "return items; ")

    def keys(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, keys = []; " \
            "for (var i = 0; i < ls.length; ++i) " \
            "  keys[i] = ls.key(i); " \
            "return keys; ")

    def get(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def set(self, key, value):
        self.driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def has(self, key):
        return key in self.keys()

    def remove(self, key):
        self.driver.execute_script("window.localStorage.removeItem(arguments[0]);", key)

    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")

    def __getitem__(self, key) :
        value = self.get(key)
        if value is None :
          raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return self.items().__iter__()

    def __repr__(self):
        return self.items().__str__()





#Chromedriver Options
driverPath = "/chromedriver.exe"
options = webdriver.ChromeOptions()
prefs={"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 0 }
options.add_experimental_option('prefs', prefs)
options.page_load_strategy = 'eager'
options.add_argument("--no-sandbox")
options.add_argument('--disable-gpu')
options.add_argument('--enable-logging')
options.add_argument('--v=1')
# options.add_argument("--disable-extensions")
# options.add_argument('--disable-dev-shm-usage')
options.add_argument("--start-maximized")
options.add_argument("--window-size=1920,1080")

#options.headless = True
# driver = webdriver.Chrome(options=options)
# driver.set_script_timeout(2000000)
# driver.maximize_window()
currentDate = date.today().strftime("%B%d%Y")


#User Configs
desiredDate = "1 Jan 18"
neighborhoodName = "FairchesterWoods"

fileName = "{}Links.xlsx".format(neighborhoodName)
workbook = xlsxwriter.Workbook(fileName)
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, "Title")
worksheet.write(0, 1, "Link") 
worksheet.write(0, 2, "Date Posted")


def InitDriver():
	global driver

	driver = webdriver.Chrome(options=options)
	driver.set_script_timeout(2000000)
	driver.maximize_window()

def Login():
	InitDriver()
	url = "https://nextdoor.com/neighborhood_feed/"
	driver.get(url)
	WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.ID, "id_email"))).send_keys(config.username)
	WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.ID, "id_password"))).send_keys(config.password)
	driver.find_element_by_id("signin_button").send_keys(Keys.RETURN)
	time.sleep(2)
	driver.implicitly_wait(5) #seconds
	driver.find_element_by_css_selector('#layout_container > div > div > div.container.layout-container.with-navbar.scroll-locked > div > div.col-md-12.feed-container.with-navbar.scroll-locked > div.toggle-view-bar-with-alpha-above.toggle-view-bar > span > div > div > div > button').click()
	driver.find_element_by_css_selector('#layout_container > div > div > div.container.layout-container.with-navbar.scroll-locked > div > div.col-md-12.feed-container.with-navbar.scroll-locked > div.toggle-view-bar-with-alpha-above.toggle-view-bar > span > div > div:nth-child(2) > div.menu-box > div > div:nth-child(3) > button').click()
	driver.find_element_by_xpath('//html').click()
	driver.implicitly_wait(2) #seconds

def Scrape():
	scrollCheckInterval = 100
	currentScrollNum = 1
	row = 1

	storage = LocalStorage(driver)
	storage.clear()


	last_height = driver.execute_script("return document.body.scrollHeight")

	while True:
		if currentScrollNum < 20:
			SCROLL_PAUSE_TIME = random.randint(15,25)
		elif currentScrollNum < 50: 
			SCROLL_PAUSE_TIME = random.randint(40,60)
		elif currentScrollNum < 100: 
			SCROLL_PAUSE_TIME = random.randint(60,70)
		# elif currentScrollNum < 150: 
# 			SCROLL_PAUSE_TIME = random.randint(35,45)
# 		elif currentScrollNum < 200: 
# 			SCROLL_PAUSE_TIME = random.randint(45,55)
		else: 
			SCROLL_PAUSE_TIME = random.randint(70,80)
		

		postList = driver.find_elements_by_class_name('css-1dkvlfs')


		for i in range(len(postList)-6):
			row = RecordObject(row)
			


		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(SCROLL_PAUSE_TIME)

		try:
			currentDate = driver.find_elements_by_class_name('post-list-item-timestamp')
			if len(currentDate) > 1:
				currentDate = currentDate[-1].text
			print("Current Date: ", currentDate)
			if currentDate == desiredDate:
				print("Desired Date Reached, Ending Loop")
				break
		except TimeoutException:
			time.sleep(120)
			pass
		if (currentScrollNum != 0) and (currentScrollNum % scrollCheckInterval == 0):
			userInput = input("Enter End to end loop and start scraping. Any other key will continue scrolling: ")
			if userInput == "End":
				break
			else:
				print("User has requested to continue the loop.")
		print("Current Number of Scrolls: " , currentScrollNum)
		currentScrollNum += 1

		
def RecordObject(row):
	col = 0
	postList = driver.find_elements_by_class_name('css-1dkvlfs')
	post = postList[0]

	#current element
	try:
		name = post.find_element_by_class_name("post-list-item-subject")
		name = name.text.encode("utf-8")        
		try:
			hrefLink = post.find_element_by_class_name('post-list-item-link').get_attribute("href")
			try:
				datePosted = post.find_element_by_class_name("post-list-item-timestamp").text
			except NoSuchElementException:
				datePosted = "" 
	
		except NoSuchElementException:
			hrefLink = ""  
			datePosted = "" 

	except NoSuchElementException:
		name = ""
		hrefLink = ""
		datePosted = ""


	#remove element
	driver.execute_script("""var l = document.getElementsByClassName("css-1dkvlfs")[0];l.parentNode.removeChild(l);""")


   
	print(name, datePosted, hrefLink)
	worksheet.write(row, col, str(name))
	worksheet.write(row, col + 1, str(hrefLink))
	worksheet.write(row, col + 2, str(datePosted))
	row += 1
	return row


def Main():

	Login()
	Scrape()
	workbook.close()


	driver.close()
	driver.quit()
Main()