from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import sys
from random import randint

######## FOR WINDOWS ####################################################
# Line numbers you may need to replace path for windows - 20, 58,96,126,163,170,175,210
#########################################################################


url = "http://web.flock.co"
options = Options()
options.add_argument("--disable-notifications")
baseDir = os.path.dirname(os.path.abspath(__file__))
path_to_chromedriver = baseDir+'/chromedriver' # change path as needed

def switchToConversationFrame(driver):
    iframe_conversations = driver.find_element_by_css_selector('[src*="https://web.flock.co/client_base/apps/conversation"]')
    driver.switch_to.frame(iframe_conversations)
    return driver

#https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()
    print "\n"

def scrollUpToTheTopOfConversation(driver,sleep_more):
    currentTopMessage = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'chat_message_body')][1]")))
    driver.execute_script("return arguments[0].scrollIntoView();",driver.find_element_by_xpath("//div[contains(@class,'header-message__content')][1]"))
    if sleep_more:
        time.sleep(6)
    else:
        time.sleep(4)
    nowTopMessage = driver.find_element_by_xpath("//div[contains(@class,'chat_message_body')][1]")
    if currentTopMessage != nowTopMessage:
        return scrollUpToTheTopOfConversation(driver,sleep_more)
    else:
        try:
            driver.find_element_by_class_name("noMoreHistory")
            return driver
        except:
            print "Scrolling had some issue. Gonna retry scrolling..."
            return scrollUpToTheTopOfConversation(driver,sleep_more)


def scrapChatsAndWriteToFile(driver,title):
    fileToWrite = open(baseDir+"/flock_history_"+title+".txt","w")
    print "Going to extract history for "+title+". Please be patient."
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

def writePageSourceToFile(driver,title):
    f = open(baseDir+"/ToDo_"+title+".html","w")
    f.write(driver.page_source.encode('utf-8', 'ignore'))
    f.close()
    print "made a html file successfully."


def findCorrectTitle(driver):
    try:
        TitleElts = driver.find_elements_by_class_name("profile_name")
        for titleElt in TitleElts:
            if titleElt.text.encode('ascii','ignore') != "":
                return titleElt.text.encode('ascii','ignore')
    except:
        print "couldn't find the title. returning a random one"
        return "Flock_"+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))+str(randint(0,9))

def initialPrinting():
    print "==================================\n    WHAT THE FLOCK (beta)   \n=================================="
    print "                     by bhavul.g"
    print "\n"
    print "This program will save your flock chats before flock gets depricated.\n"


def switchToGroupConversationFrame(driver):
    iframe_conversations = driver.find_element_by_css_selector('[src*="https://web.flock.co/client_base/apps/group_conversation"]')
    driver.switch_to.frame(iframe_conversations)
    return driver


def runHtmlExtractorAndThenScraperMode(driver,convoList):
    scrapingLeftConvoFile = open(baseDir+"/ScrapingLeft.txt","w")
    count = 0
    total = 2*len(convoList)
    progress(count,total,"Extracting your flock chats")
    for convo in convoList:
        driver = tryToEnterConvoScreen(convo, driver)
        raw_input("\nConfirm by pressing Enter if ["+str(convo).upper()+"] seems to be opened now. If not, open it manually in the browser window and then press enter here.")
        driver.switch_to.default_content()
        driver = switchToCorrectConvoFrame(convo, driver)
        if "g:" in convo:
            sleepMore = True
        else:
            sleepMore = False
        try:
            print "Going to scroll up to the top now...Please be patient"
            driver = scrollUpToTheTopOfConversation(driver,sleepMore)
            try:
                time.sleep(1)
            except:
                pass
            print "Scrolling up done. Will write this chat into html."
            title = findCorrectTitle(driver)
            writePageSourceToFile(driver,title)
            scrapingLeftConvoFile.write("ToDo_"+title+".html")
            scrapingLeftConvoFile.write("\n")
            print "done writing html to file successfully!\n"
        except TimeoutException:
            print "failed to scroll up. Sorry"
            driver.switch_to.default_content()
        except:
            print "caught exception. don't worry"
            driver.switch_to.default_content()
        count += 1
        time.sleep(0.25)
        progress(count,total,"Extracting your flock chats")
    scrapingLeftConvoFile.close()
    print "\nhtml extraction done for all conversations. Now let's move to step 2."
    driver.close()
    listOfConvoToBeScraped = []
    with open(baseDir+"/ScrapingLeft.txt") as fileToRead:
        for line in fileToRead:
            listOfConvoToBeScraped.append(line.strip())
    print "conversations to be scraped now - "+str(listOfConvoToBeScraped)
    newDriver = webdriver.Chrome(executable_path = path_to_chromedriver,chrome_options=options)
    time.sleep(3)
    for convoFileName in listOfConvoToBeScraped:
        newLocalUrl = "file://"+baseDir+"/"+str(convoFileName)
        newDriver.get(newLocalUrl)
        newDriver.switch_to.default_content()
        time.sleep(5)
        title = findCorrectTitle(newDriver)
        print "\nGoing to extract history of "+title+". Please be patient."
        fileToWrite = open(baseDir+"/Flock_history_"+title+".txt","w")
        chatAreaRoot = newDriver.find_element_by_class_name("message_area_root")
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
                dateContainer = dayChat.find_element_by_class_name("dateContainer")
                fileToWrite.write("------------ "+dateContainer.text.encode('utf-8','ignore')+" ------------\n")
                chatMsgs = dayChat.find_elements_by_class_name("sender_or_info")
                for chat in chatMsgs:
                    try:
                        sender = chat.find_element_by_class_name("chat_message_sender")
                    except:
                        continue
                    senderName = sender.text.encode('utf-8','ignore')
                    minuteWiseChats = chat.find_elements_by_class_name("minute_separator")
                    for minute in minuteWiseChats:
                        timeContainer = minute.find_element_by_class_name("chat_message_time")
                        timeText = timeContainer.text.encode('utf-8','ignore')
                        actualChatMsgs = minute.find_elements_by_class_name("chat_message_body")
                        fileToWrite.write("["+timeText+"] "+senderName+": ")
                        for message in actualChatMsgs:
                            fileToWrite.write(message.text.encode('utf-8', 'ignore')+"\n")
        fileToWrite.close()
        print "History txt file made for "+title+"."
        count += 1
        progress(count,total,"Extracting your flock chats")
    newDriver.close()
    os.remove(baseDir+"/ScrapingLeft.txt")
    print "Scraping done for all conversations."


def switchToCorrectConvoFrame(convo, driver):
    if "g:" in convo:
        driver = switchToGroupConversationFrame(driver)
    else:
        driver = switchToConversationFrame(driver)
    return driver


def tryToEnterConvoScreen(convo, driver):
    driver.switch_to.default_content()
    driver.find_element_by_id("universalSearchField").click()
    if "g:" in convo:
        actualConvo = convo.replace("g:","")
        driver.switch_to.active_element.send_keys(actualConvo)
    else:
        driver.switch_to.active_element.send_keys(convo)
    driver.switch_to.active_element.send_keys(Keys.RETURN)
    return driver


def runFlockScraperDirectMode(driver,convoList):
    count = 0
    total = len(convoList)
    progress(count,total,"Extracting your flock chat history")
    for convo in convoList:
        driver = tryToEnterConvoScreen(convo, driver)
        raw_input("\nConfirm by pressing Enter if ["+str(convo).upper()+"] seems to be opened now. If not, open it manually and then press enter here.")
        driver = switchToCorrectConvoFrame(convo, driver)
        try:
            if "g:" in convo:
                sleep_more = True
            else:
                sleep_more = False
            print "Going to scroll up to the top now...Please be patient"
            driver = scrollUpToTheTopOfConversation(driver,sleep_more)
            print "\n"
            time.sleep(1)
            title = findCorrectTitle(driver)
            print "Scrolling up done."
            try:
                scrapChatsAndWriteToFile(driver,title)
                print "Successfully scrapped chats for "+str(convo)+"\n"
            except Exception as e:
                print "for some reason scraping chats for "+str(convo)+" failed. Reason - "+e
        except TimeoutException:
            print "failed to scroll up. Sorry"
            driver.switch_to.default_content()
        except:
            print "caught exception. don't worry"
            driver.switch_to.default_content()
        count += 1
        time.sleep(0.25)
        progress(count,total,"Extracting your flock chat history")
    print "Scraping done for all chats."



def main(args):
    initialPrinting()
    email = raw_input("\nenter your email address for flock: ")
    driver = getDriver()
    driver = goTillVerificationPinScreen(driver,email)
    raw_input("You would be asked to enter your PIN in a moment. Please look into your mail and enter the PIN and click on 'Verify'. Once you have logged into Flock and see the main screen, press Enter.")
    print "\n\n-----------------------------------------------"
    print "This program can run in two modes:"
    print "1. Create html files first, and use another script to scrap chats from it (slower, but you get timestamps, html as well with the txt chats)"
    print "Example : [05:55] Rama: please leave Sita, Ravana."
    print "\n2. Try to directly create txt files having chat data (faster, but you only get txt files without timestamps)"
    print "Example : [] Rama: please leave Sita, Ravana"
    print "-----------------------------------------------\n\n"
    modeChosen = raw_input("Which mode would you like the program to take?\nAns. ")
    if modeChosen == '1':
        runHtmlExtractorAndThenScraperMode(driver,args)
    elif modeChosen == '2':
        runFlockScraperDirectMode(driver,args)
    else:
        print "Invalid input. Please only enter 1 or 2 when asked for mode. Exiting program."
    print "Thank you and bye-bye."


def getDriver():
    driver = webdriver.Chrome(executable_path = path_to_chromedriver,chrome_options=options)
    driver.get(url)
    time.sleep(4)
    return driver

def goTillVerificationPinScreen(driver,email):
    iframe = driver.find_element_by_css_selector('[src*="https://auth.flock.co"]')
    driver.switch_to.frame(iframe)
    time.sleep(3)
    emailWrapper = driver.find_element_by_xpath("//div[contains(@class,'emailInput')]/input")
    emailWrapper.clear()
    emailWrapper.send_keys(email)
    submitButton = driver.find_element_by_xpath("//div[contains(@class,'emailField')]/a")
    submitButton.click()
    SkipStepLink = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'google-auth-footer')]/a"))
    )
    SkipStepLink.click()
    return driver

if len(sys.argv[1:]) >= 1:
    print "The conversations chosen by you to be scraped are : "+str(sys.argv[1:])
    print "\n"
    main(sys.argv[1:])