import logging
import xml.etree.ElementTree as ET
import sys
import json
from os.path import realpath
from idac_sdk import (
    IDACRequestSync, 
    IDACRequestType,
    IDACControllerSync,
    IDACAuthType,
    SessionData
)
import os
import time
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

# def external_ip():
#     url= "http://checkip.dyndns.org/"
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     result = soup.find("body")
#     ipAdd= re.compile('(\d{1,3}\.){3}\d{1,3}').search(result.text).group()
#     return ipAdd


formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

logger = setup_logger('main_logger', 'C:\\dcloud\\session_automation.log')

def pathfile():    
    parent_dir= 'C:\\dcloud'
    path= os.path.join(parent_dir)
    THIS_FOLDER = os.path.abspath(path)
    return THIS_FOLDER

def fileExist():
    try:
        filelication =os.path.join(pathfile(), 'session'+'.xml')
        while not os.path.exists(filelication):
            print('looking for session xml')
            logger.info('looking for session xml')
            time.sleep(5)
        if os.path.isfile(filelication):
            print('session xml file exist')
            logger.info(' session xml found')
            return filelication
    except:
        print('no file xml found')

def session_id():
    filelication = fileExist()
    try:
        if os.path.isfile(filelication):
            with open(filelication, 'r') as f:
                data = f.read()
                bs_data = BeautifulSoup(data, 'xml')
                result = bs_data.find('id')
                return result.get_text()
    except Exception as e:
        logger.error(f'No data found' + str(e))
        return 'No data found' + str(e)

def owner():
    filelication = fileExist()
    try:
        if os.path.isfile(filelication):
            with open(filelication, 'r') as f:
                data = f.read()
                bs_data = BeautifulSoup(data, 'xml')
                result = bs_data.find('owner')
                return result.get_text()
    except Exception as e:
        logger.error(f'No data found' + str(e))
        return 'No data found' + str(e)

def pod_name():
    filelication = fileExist()
    try:
        if os.path.isfile(filelication):
            with open(filelication, 'r') as f:
                data = f.read()
                bs_data = BeautifulSoup(data, 'xml')
                result = bs_data.find('name')
                for r in result:
                    pod= str(r[-2:])
                return result.get_text()
    except Exception as e:
        logger.error(f'No data found' + str(e))
        return 'No data found' + str(e)

def parse_session_xml():
    # Parse session.xml file to get session details
    
    filelication = fileExist()

    tree = ET.parse(filelication)
    root = tree.getroot()

    for item in root.iter('session'):
        datacenter = item.find('datacenter').text
        datacenter = datacenter.lower()
        sessionID = item.find('id').text
        owner = item.find('owner').text
    # for device in root.iter('device'):
    #     pod_name = device.find('name').text
      
    logger.info("-------------------------------------------------")
    logger.info(f'Got the following session parameters: \n Datacenter: {datacenter}, sessionID: {sessionID}, Session owner: {owner}')
    return  datacenter

def sessionSuccess():
    strl = ""
    msg = "Session automation completed."
    file1 = open('C:\\dcloud\\session_automation.log', 'r')
    fileresults = file1.read()
    result = re.findall(msg, fileresults)
    for i in result:
        strl += i
    return strl

def idac_start_automation(recipeName, recipePath, datacenter ):
    sessionst = sessionSuccess()
    msg= "Session automation completed."
    
    
    try:
        if msg == sessionst:
            logger.info('Session already exist')
            print('Session already exist')
            exit()
        else:   
            logger.info("-------------------------------------------------")
            logger.info('Starting iDAC session automation...')
            print('Starting iDAC session automation...') 
            # load data from session.xml and set recipeName and recipePath
            sd = SessionData(recipeName=recipeName, recipePath=recipePath)
            sd.set("dcloud_datacenter", datacenter)
            
            

            # create sync controller with dCloud Session auth type
            ctrl = IDACControllerSync(auth_type=IDACAuthType.DCLOUD_SESSION)

            # create request object
            logger.info(f'Sending request to the iDAC controller with these parameters: {sd.dict()}')
            req = IDACRequestSync(session_data=sd, controller=ctrl)

            # create request
            req.create(request_type=IDACRequestType.SIMPLE)
            req.wait_for_status(max_attempts=40) 
            state = req.get_state()
            # output_url = state.tasks.Start[0]["output"]["outputUrl"]
            output_url = state.outputUrl
            # output_url = state.get_task_outputs("Start", "Generate TE Autologin")["outputUrl"]

            sessionStatus =state.status
            print(sessionStatus)
        
            
            logger.info(f'Received the following request UUID from iDAC: {state.request.uuid}')
            logger.info(f'Session status = {state.status}')
            logger.info(f'Received the following redirect URL from iDAC: {output_url}')
            logger.info("-------------------------------------------------")
            
            
            return output_url

    except Exception as e:
        logger.info(f"Session status = {e}")
        logger.error(f"Failed to start session automation: {e}")
        logger.info("-------------------------------------------------")

        exit()

def link_url(url):
    try:
        fileInfo = open('C:\\dcloud\\url.txt', 'w', encoding="utf-8")
        result =fileInfo.write(url)
        fileInfo.close()
        return result
    except:
        return "File not created"



def add_chrome_bookmark(url):
    # adds new bookmark to the Chrome browser with Umbrella SSO

    logger.info('Adding new bookmark to Chrome')

    file = "C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks"
    resolved = realpath(file)
    
    with open(resolved) as reader:
        body = json.load(reader)

    body['roots']['bookmark_bar']['children'].append(
        {
            "date_added": "13279388863961984",
            "name": "Login Url",
            "type": "url",
            "url": url
         }
        )

    with open(resolved, "w") as writer:
        json.dump(body, writer, indent=4)
        
def saveData(url):
    try:
        fileInfo = open('C:\\dcloud\\teyes.txt', 'w', encoding="utf-8")
        result =fileInfo.write(url)
        fileInfo.close()
        return result
    except:
        return "File not created"




if __name__ == "__main__":
    print('Welcome to dCloud, please wait your session is starting ...')
    

    # recipeName and recipePath show be received from get_master_script.py as arguments
    try:
        #get arguments: First one is the source folder
        folder=sys.argv[1]
        #Second Argument is the recipeName 
        recipeName=sys.argv[2]
        #Third Argument is the recipePath 
        recipePath=sys.argv[3]
    except:
        folder = ''
        recipePath = 'cpoc/eargueda/'
        recipeName = 'vpc+ec2-test'

    logger.info("-------------------------------------------------")
    logger.info('Getting dCloud session parameters and starting iDAC automation ...')
    logger.info("-------------------------------------------------")

    dcloud_datacenter = parse_session_xml()
    
    
    outUrl = idac_start_automation(recipeName, recipePath, dcloud_datacenter )

    logger.info("-------------------------------------------------")
    logger.info('iDAC Automation completed.')
    logger.info('creating txt file for output url.')
    link_url(outUrl)
    add_chrome_bookmark(outUrl)
    logger.info('file created.')
    logger.info("-------------------------------------------------")
    logger.info('Session automation completed.')
    logger.info("-------------------------------------------------")
    print('Your session is completed')
    

    exit()
