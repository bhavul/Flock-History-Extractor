from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from random import randint
import sys

# Based on contents of ScrapingLeft.txt, it picks up those html files and scrapes them to txt files.

options = Options()
options.add_argument("--disable-notifications")
baseDir = os.path.dirname(os.path.abspath(__file__))
path_to_chromedriver = baseDir+'/chromedriver' # change path as needed

#https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def findCorrectTitle(driver):
    try:
        TitleElts = driver.find_elements_by_class_name("profile_name")
        for titleElt in TitleElts:
            if titleElt.text.encode('ascii','ignore') != "":
                return titleElt.text.encode('ascii','ignore')
    except:
        print "couldn't find the title. returning a random one"
        return "Flock_"+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))

# validation (optional) that indeed we're at the top of the conversation
# find class=header-message__content having text containing "No more messages"   ---> then cool ! (y)

listOfConvoToBeScraped = []
with open(baseDir+"/ScrapingLeft.txt") as fileToRead:
    for line in fileToRead:
        listOfConvoToBeScraped.append(line.strip())
print "conversations to be scraped now - "+str(listOfConvoToBeScraped)+"\n"
count = 0
total = len(listOfConvoToBeScraped)
progress(count,total,"Getting your flock chat history")
driver = webdriver.Chrome(executable_path = path_to_chromedriver, chrome_options=options)
time.sleep(4)
for convoFileName in listOfConvoToBeScraped:
    newLocalUrl = "file://"+baseDir+"/"+str(convoFileName)
    driver.get(newLocalUrl)
    time.sleep(5)
    title = findCorrectTitle(driver)
    print "Going to extract history for "+title+". Please be patient."
    fileToWrite = open(baseDir+"/Flock_history_"+title+".txt","w")
    chatAreaRoot = driver.find_element_by_class_name("message_area_root")
    historyMessages = chatAreaRoot.find_element_by_class_name("history_messages")
    allMessages = [historyMessages]
    try:
        liveMessages = chatAreaRoot.find_element_by_class_name("liveMessages")
        allMessages = [historyMessages,liveMessages]
    except:
        pass
    #### inside that find class=daySeparator. Loop for each element in this.....  [days]
    for msgsElt in allMessages:
        daySeparatedChats = msgsElt.find_elements_by_class_name("daySeparator")
        for dayChat in daySeparatedChats:
            # 1. find class=dateContainer. This element has the "5 days ago" stuff. Print it out.
            dateContainer = dayChat.find_element_by_class_name("dateContainer")
            fileToWrite.write("------------ "+dateContainer.text.encode('utf-8','ignore')+" ------------\n")
            # 2. find elements with class=sender_or_info, loop over each of these
            chatMsgs = dayChat.find_elements_by_class_name("sender_or_info")
            for chat in chatMsgs:
                # i. find class="chat_message_sender". This has "Bhavul Gauri" or "Me". Print it out. Save it in a variable that you're gonna use.
                try:
                    sender = chat.find_element_by_class_name("chat_message_sender")
                except:
                    continue
                senderName = sender.text.encode('utf-8','ignore')
                # ii. find elements with class="minute_separator". Loop over each of these
                minuteWiseChats = chat.find_elements_by_class_name("minute_separator")
                for minute in minuteWiseChats:
                    timeContainer = minute.find_element_by_class_name("chat_message_time")
                    timeText = timeContainer.text.encode('utf-8','ignore')
                    # (b) find elements with class="chat_message_body". Print 'em out in format -  [time] name: msg
                    actualChatMsgs = minute.find_elements_by_class_name("chat_message_body")
                    fileToWrite.write("["+timeText+"] "+senderName+": ")
                    for message in actualChatMsgs:
                        fileToWrite.write(message.text.encode('utf-8', 'ignore')+"\n")
    fileToWrite.close()
    print "History txt file created for "+title+"."
    count += 1
    progress(count,total,"Getting your flock chat history")
driver.close()
os.remove(baseDir+"/ScrapingLeft.txt")
print "Scraping done for all conversations."