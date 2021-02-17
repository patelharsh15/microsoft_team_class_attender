# Microsoft Teams Online Class Attender

This bot attends the online classes (or meetings) held on Microsoft teams, according to the given timetable.


## Configure

There are few things you need to configure before running this bot.
 - for students of class CSE 2 batch A -> no change in timetable database file.(I had already done for you;)
 - If you are not in Class CSE 2 batch A _> Delete the timetable_cse2_a.db file, and create your own by using option 1. Add timetable.
 - To change database change code in bot.py at line 36(write .db here only), 67, 118, 132, 246, 294, 315, 325, 335 & 345.
 - Open Microsoft teams on your browser, login to your account, change the dashboard view to list view (from grid view), so that your classes are displayed in a list view. 
 - ![This is how list view looks like](https://i.imgur.com/SSDo8c6.png)
 - Open *bot.py*, and put your microsoft teams credentials in the **CREDS** dictionary. 
 - Example - `CREDS  = {'email' : 'myemail@email.com', 'passwd':'''mypassword'''}`
 - Open *discord_webhook.py* and put your discord webhook URL in the **webhook_url** variable. 
 - Example - `webhook_url = "https://discordapp.com/...."`
 - Make sure that the timezone of the PC is correct. If you're running the bot on cloud, you may want to manually change the timezone of the virtual machine to an appropriate time zone (i.e., the timezone that your online classes follow)
 - Also those who are getting chromedriver PATH error then pass the path of chromedriver.exe in the bot.py line 232.
 - Never ever delete the inbuild database file. just change it's name. Otherwise it will giver error while reading new file.


## Install

 - Clone the repository `git clone https://github.com/teja156/microsoft-teams-class-attender`
 - Install requirements.txt `pip install -r requirements.txt`

 

## Run the bot

 - Run the bot `python bot.py`

Written on Python3.
