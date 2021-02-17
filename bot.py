from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import os.path
from os import path
import sqlite3
import schedule
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import discord_webhook


opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--start-maximized")
# Pass the argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", { \
    "profile.default_content_setting_values.media_stream_mic": 1, 
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 1, 
    "profile.default_content_setting_values.notifications": 1 
  })

#driver = webdriver.Chrome(chrome_options=opt,service_log_path='NUL')
driver = None
#driver = webdriver.Chrome(r"C:/Users/harsh/Downloads/chromedriver_win32/chromedriver.exe")

URL = "https://teams.microsoft.com"

timetable = 'timetable_cse2_a.db'  #change this to change database file name and wirte .db here only.
#timetable='timetable_cse2_a'

#put your teams credentials here
CREDS = {'email' : ' ','passwd':' '} #write your credientials here. 



def login():
	global driver
	#login required
	print("logging in")
	time.sleep(5)
	emailField = driver.find_element_by_xpath('//*[@id="i0116"]')
	emailField.click()
	emailField.send_keys(CREDS['email'])
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Next button
	time.sleep(5)
	passwordField = driver.find_element_by_xpath('//*[@id="i0118"]')
	passwordField.click()
	passwordField.send_keys(CREDS['passwd'])
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #Sign in button
	time.sleep(5)
	driver.find_element_by_xpath('//*[@id="idSIButton9"]').click() #remember login
	time.sleep(5)
	# return driver


def createDB():
	conn = sqlite3.connect(timetable)															
	c=conn.cursor()
	# Create table
	c.execute('''CREATE TABLE timetable_cse2_a(id integer,class text, start_time text, end_time text, day text)''') #timetable name change
	conn.commit()
	conn.close()
	print("Created timetable Database")



def validate_input(regex,inp):
	if not re.match(regex,inp):
		return False
	return True

def validate_day(inp):
	days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

	if inp.lower() in days:
		return True
	else:
		return False


def add_timetable():
	if(not(path.exists(timetable))):
			createDB()
	op = int(input("1. Add class\n2. Done adding\nEnter option : "))

	while(op==1):
		try:
			view_timetable()
		except:
			print("No Database exist until now. ")
		row_no = int(input("Enter the next number ID:"))
		name = input("Enter class name : ")
		start_time = input("Enter class start time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",start_time)):
			print("Invalid input, try again")
			start_time = input("Enter class start time in 24 hour format: (HH:MM) ")

		end_time = input("Enter class end time in 24 hour format: (HH:MM) ")
		while not(validate_input("\d\d:\d\d",end_time)):
			print("Invalid input, try again")
			end_time = input("Enter class end time in 24 hour format: (HH:MM) ")

		day = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")
		while not(validate_day(day.strip())):
			print("Invalid input, try again")
			end_time = input("Enter day (Monday/Tuesday/Wednesday..etc) : ")


		conn = sqlite3.connect(timetable)																	
		c=conn.cursor()

		# Insert a row of data
		
		c.execute("INSERT INTO timetable_cse2_a VALUES ('%d','%s','%s','%s','%s')"%(row_no,name,start_time,end_time,day))#timetable name change

		conn.commit()
		conn.close()

		print("Class added to database\n")

		op = int(input("1. Add class\n2. Done adding\nEnter option : "))



def view_timetable():
	conn = sqlite3.connect(timetable)																
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable_cse2_a'):											#timetable name change
		print(row)
	conn.close()



def joinclass(class_name,start_time,end_time):
	global driver

	try_time = int(start_time.split(":")[1]) + 15
	try_time = start_time.split(":")[0] + ":" + str(try_time)

	time.sleep(5)


	classes_available = driver.find_elements_by_class_name("name-channel-type")

	for i in classes_available:
		if class_name.lower() in i.get_attribute('innerHTML').lower():
			print("JOINING CLASS ",class_name)
			i.click()
			break


	time.sleep(4)


	try:
		joinbtn = driver.find_element_by_class_name("ts-calling-join-button")
		joinbtn.click()

	except:
		#join button not found
		#refresh every minute until found
		k = 1
		while(k<=30):
			print("Join button not found, trying again")
			time.sleep(60)
			driver.refresh()
			joinclass(class_name,start_time,end_time)
			# schedule.every(1).minutes.do(joinclass,class_name,start_time,end_time)
			k+=1
		print("Seems like there is no class today.")
		discord_webhook.send_msg(class_name=class_name,status="noclass",start_time=start_time,end_time=end_time)


	time.sleep(4)
	webcam = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[2]/toggle-button[1]/div/button/span[1]')
	if(webcam.get_attribute('title')=='Turn camera off'):
		webcam.click()
	time.sleep(1)

	microphone = driver.find_element_by_xpath('//*[@id="preJoinAudioButton"]/div/button/span[1]')
	if(microphone.get_attribute('title')=='Mute microphone'):
		microphone.click()

	time.sleep(1)
	joinnowbtn = driver.find_element_by_xpath('//*[@id="page-content-wrapper"]/div[1]/div/calling-pre-join-screen/div/div/div[2]/div[1]/div[2]/div/div/section/div[1]/div/div/button')
	joinnowbtn.click()

	discord_webhook.send_msg(class_name=class_name,status="joined",start_time=start_time,end_time=end_time)
	
	#now schedule leaving class
	tmp = "%H:%M"

	class_running_time = datetime.strptime(end_time,tmp) - datetime.strptime(start_time,tmp)

	time.sleep(class_running_time.seconds)

	try:
		if(driver.find_element_by_class_name("ts-calling-screen").isDisplayed()):
			driver.find_element_by_class_name("ts-calling-screen").click()
	except:
		print("Class has ended before given time(ts-calling-screen)")

	try:
		if(driver.find_element_by_class_name("ts-btn").isDisplayed()):
			driver.find_element_by_class_name("ts-btn").click()
	except:
		print("Class has ended before given time(ts-btn)")


	
	driver.find_element_by_xpath('//*[@id="teams-app-bar"]/ul/li[3]').click() #come back to homepage
	time.sleep(1)

	try:
		driver.find_element_by_xpath('//*[@id="hangup-button"]').click()
	except:
		print("Class has ended before given time.(hangup-button)")

	#driver.find_element_by_xpath('//*[@id="hangup-button"]').click()
	print("Class left")
	discord_webhook.send_msg(class_name=class_name,status="left",start_time=start_time,end_time=end_time)


def start_browser():

	global driver
	driver = webdriver.Chrome(r" ",chrome_options=opt,service_log_path='NUL')#your chromedriver.exe path between the " "
																#change chromedriver.exe path
	driver.get(URL)

	WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))

	if("login.microsoftonline.com" in driver.current_url):
		login()



def sched():
	conn = sqlite3.connect(timetable)																	
	c=conn.cursor()
	for row in c.execute('SELECT * FROM timetable_cse2_a'):												#change timetable
		#schedule all classes
		name = row[1]
		start_time = row[2]
		end_time = row[3]
		day = row[4]

		if day.lower()=="monday":
			schedule.every().monday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="tuesday":
			schedule.every().tuesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="wednesday":
			schedule.every().wednesday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="thursday":
			schedule.every().thursday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="friday":
			schedule.every().friday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="saturday":
			schedule.every().saturday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))
		if day.lower()=="sunday":
			schedule.every().sunday.at(start_time).do(joinclass,name,start_time,end_time)
			print("Scheduled class '%s' on %s at %s"%(name,day,start_time))


	#Start browser
	start_browser()
	while True:
		# Checks whether a scheduled task
		# is pending to run or not
		schedule.run_pending()
		time.sleep(1)

def del_timetable():
	if(not(path.exists(timetable))):
			createDB()
	op = int(input("1. Delete a row in timetable\n2. Done deleting\nEnter option : "))
	
	while(op==1):
		try:
			view_timetable()
		except:
			print("No Database exist until now. ")
		row_n = int(input("Enter row number : "))
		conn = sqlite3.connect(timetable)
		c=conn.cursor()
		c.execute('DELETE FROM timetable_cse2_a WHERE id=?',(int(row_n),))						#change timetable
		conn.commit()
		conn.close()
		print("Class deleted to database\n")

		op = int(input("1. Delete a row in timetable\n2. Done deleting\nEnter option : "))


def update_timetable():
	if(not(path.exists(timetable))):
			createDB()
	op = int(input("1. Update a row in timetable\n2. Done updating\nEnter option : "))
	
	while(op==1):
		try:
			view_timetable()
		except:
			print("No Database exist until now. ")
		y = int(input("1. Update class\n2. Update start time\n3. Update end time\n4. Update day\nEnter option : "))
		if y==1:
			row_n = int(input("Enter row number : "))
			nam=input("Enter new name : ")
			conn = sqlite3.connect(timetable)								           
			c=conn.cursor()
			c.execute('UPDATE timetable_cse2_a SET class=? WHERE id=?',(nam,int(row_n),))						#change timetable
			conn.commit()
			conn.close()
			print("Class updated in database\n")

		elif y==2:
			row_n = int(input("Enter row number : "))
			nam=input("Enter new time : ")
			conn = sqlite3.connect(timetable)
			c=conn.cursor()
			c.execute('UPDATE timetable_cse2_a SET start_time=? WHERE id=?',(nam,int(row_n),))						#change timetable
			conn.commit()
			conn.close()
			print("Start updated in database\n")

		elif y==3:
			row_n = int(input("Enter row number : "))
			nam=input("Enter new end time : ")
			conn = sqlite3.connect(timetable)								          
			c=conn.cursor()
			c.execute('UPDATE timetable_cse2_a SET end_time=? WHERE id=?',(nam,int(row_n),))						#change timetable
			conn.commit()
			conn.close()
			print("End TIme updated in database\n")

		elif y==4:
			row_n = int(input("Enter row number : "))
			nam=input("Enter new day : ")
			conn = sqlite3.connect(timetable)								          
			c=conn.cursor()
			c.execute('UPDATE timetable_cse2_a SET day=? WHERE id=?',(nam,int(row_n),))						#change timetable
			conn.commit()
			conn.close()
			print("Day updated in database\n")


		op = int(input("1. Update a row in timetable\n2. Done updating\nEnter option : "))

		


if __name__=="__main__":
	# joinclass("Maths","15:13","15:15","sunday")
	op = int(input(("1. Add Timetable\n2. View Timetable\n3. Start Bot\n4. Delete Timetable\n5. Update Timetable\nEnter option : ")))
	
	if(op==1):
		add_timetable()
	if(op==2):
		view_timetable()
	if(op==3):
		sched()
	if(op==4):               #no bug
		del_timetable()
	if(op==5):               #no bug
		update_timetable()