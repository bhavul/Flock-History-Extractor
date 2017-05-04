# Flock History Extractor

I went ahead and created a small Flock Chat History extractor on my own. Unfortunately, flock didn't have any APIs that could be used for this. And after lot of hurdles, ultimately I had to end up using Selenium for it. 

Here's a youtube video showing it's demo -  https://youtu.be/eF9S2GfX6-o 

## How to use it

1. Keep chromedriver binary (chromedriver.exe for windows and just chromedriver for linux/mac) AND flockHistorySaver.py in one folder. This is the folder where your chats will be downloaded as well.
2. Run selenium server  (java -jar selenium-server-standalone-3.x.x.jar) in one terminal tab
3. Run the code in another terminal tab as following: python flockHistorySaver.py "enduranceAD1@endurance.com" "enduranceAD2" "g:flockGroupName1" "g:flock Group Name 2" "enduranceAD3" . . . 

Example : If I want to extract conversation between me and rahul.b, and with kirit.p, and a conversation of a flock group called Lunch Group, my command would be:

python flockHistorySaver.py "rahul.b@endurance.com" "g:Lunch Group" "kirit.p"

For Personal conversations you can give full email or just the AD. full email helps in case of conflicts. Say you talk more with rahul.bu, but want to extract history with rahul.b. Just giving "rahul.b" as argument may open "rahul.bu" window due to common part in the name.

## Requirements

- Java installed on your machine (to run Selenium Server)
- Python v2.7 installed 
- Python Selenium installed (version 3.x) (http://selenium-python.readthedocs.io/installation.html)
- Download selenium standalone server driver ( http://seleniumhq.org/download/)
- Get chromedriver binary ( https://sites.google.com/a/chromium.org/chromedriver/downloads)
- Be on latest version of chrome (v56-v58 allowed). [check from top right three dots -> Help -> About chrome] 

## Limitations

1. This will not fetch any polls, code snippets, notes, files or images. It is only meant to extract text chats as of now.
2. On Windows, you may need to change paths in the python file by changing "/" to "\". Just open the file flockHistorySaver.py in an editor and you'll see my comment at the top. Whoever runs it on windows can probably share the changed python file.
3. No way to fetch conversations of all people n groups automatically. You need to specify the conversations whose history is to be extracted.

## Some tips (based on alpha testing of this)

- If you face popup "You langueage preference is set to Blah-Blah" (https://goo.gl/mqGqlz), click on "Continue in <language>" button. 
- If you face popup "Could not send invites" (https://goo.gl/NFG1MX), click on "Cancel" and then manually open the desired conversation in browser window. Post that, press Enter.
- In windows, try to use pip to install selenium and not conda. Conda has very old selenium package. Conda does provide pip script inside /scripts folder
- Don't run this program more than 10 times. Each time it runs Flock will send you a PIN in your mail. After 10 times of receiving the Flock PIN, you don't receive flock PIN anymore [flock abuse mitigation]. So, you won't be able to sign in to flock unless you contact their support. :P Have faced that once. 
- If you have multiple TEAMS in flock, then open "E" (Endurance) manually and then press 'Enter' [This is when it asks to press Enter once Flock Main screen is opened]
- Try to keep the browser window in front somewhere. Never minimize it, it may not scroll up due to Chrome's nature of queuing javascript.
- In case you chose Mode 1, and the html files seem to be created but txt files were not formed and program exited due to some reason, you can use the other python script I'm attaching here to just parse those html files to create txt files. [python Scrap_texts.py]  - No need to provide any names. 
- For windows, try to use cmd only instead of gitbash. python did not seem to be working well on gitbash.
- Keep your laptop connected to the charger. While you don't need to stare continuously at your laptop as this long process happens, you need to make sure the screen does not go off at any moment in between. 
- When it's all set and done, create a new private HipChat room, and dd the content of txt files in that room. This way you can search your old flock history using HipChat's search itself. :) 
