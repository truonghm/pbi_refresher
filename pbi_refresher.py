# !pip install --upgrade selenium
# !pip install --upgrade webdriver-manager

import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import datetime as dt
import getopt
import pandas as pd
import sys
import logging
import os

# import username and password from config
# import slack_noti from utilities module
from utils.config import pbi_config
from utils.slack import slack_noti

# create logger to trace errors and set slack alerts
os.makedirs('logs', exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('logs/pbi_refresher.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# selenium class
class pbi_refresher:

    login_url = "https://login.microsoftonline.com/"
    # username = pbi_config['username']
    # password = pbi_config['password']

    def __init__(self, headless = True, credentials = 'admin'):
        """initiate chrome driver"""

        self.fail_ids = []
        self.success_ids = []
        self.all_ids = []

        try:
            s=Service(ChromeDriverManager().install())
            chrome_options = Options()
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            if headless:
                chrome_options.add_argument("--headless")
            self.driver = webdriver.Chrome(service=s, options=chrome_options)
        except Exception as e:
            logger.exception("Driver initialization failed")
            raise e

        # print(pbi_config[credentials])
        self.username = pbi_config[credentials]['username']
        self.password = pbi_config[credentials]['password']
        # driver.maximize_window()
        # WebDriverWait(driver, 10)
        # HTML = driver.page_source

    def get_dataset_url(self, filename:str, ids=[]):
        """get dataset urls from text file"""

        url_df = pd.read_csv(f'url/{filename}.csv', names=['id', 'dataset_url'])
        if len(ids) > 0:
            url_df = url_df[url_df['id'].isin(ids)]

        self.url_df = url_df
        self.all_ids.extend(list(url_df['id']))

    def login(self):
        """logging in to power bi/microsoft"""
        try:
            self.driver.get(self.login_url)
            actions = ActionChains(self.driver)

            # time.sleep(5)
            WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.NAME,"loginfmt")))
            self.driver.find_element(By.NAME, "loginfmt").send_keys(self.username)
            self.driver.find_element(By.ID, "idSIButton9").click()
            time.sleep(2)
            actions.send_keys(self.password).perform()
            time.sleep(1)
            self.driver.find_element(By.ID, "idSIButton9").click()
            # time.sleep(1)
            
        except Exception as e:
            self.driver.close()
            logger.exception("Logging in failed")
            raise e

    def refresh_data(self):
        """refresh datasets"""

        def click_element_xpath(element_string: str, sleep_time: int = 3):
            WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH, element_string)))
            time.sleep(sleep_time)
            self.driver.find_element(By.XPATH, element_string).click()

        for index, row in self.url_df.iterrows():
            self.driver.get(row['dataset_url'])
            try:
                click_element_xpath("//button[@title='Refresh']", 3)
                click_element_xpath("//button[@title='Refresh now']", 1)
                time.sleep(1)
                self.success_ids.append(row['id'])
                # time.sleep(1)
            except Exception as e:
                try:
                    click_element_xpath("//button[@title='Refresh']", 3)
                    click_element_xpath("//button[@title='Refresh now']", 1)
                    time.sleep(1)
                    self.success_ids.append(row['id'])
                except Exception as e:
                    self.fail_ids.append(row['id'])
                    logger.exception(f"Refreshing dataset {row['id']} failed")

    def get_dataset_id(self):
        return self.all_ids

    def get_fail_id(self):
        return self.fail_ids
    
    def get_success_id(self):
        return self.success_ids

    def close_driver(self):
        self.driver.close()

    def __del__(self):
        self.driver.quit()

def main():

    id_list = []
    pbi_config = 'admin'
    alert = 2
    headless = True

    opts, args = getopt.getopt(sys.argv[1:], shortopts = "dpahcf", longopts=["dataset_id=", "pbi_config=", "alert=", "headless=", "channel=", "filename="])
    if len(opts) > 0:
        for opt, arg in opts:
            if opt in ["-d", "--dataset_id"]:
                id_list = arg.split(",")

            if opt in ["-p", "--pbi_config"]:
                pbi_config = arg

            if opt in ["-c", "--channel"]:
                slack_channel = arg.lower()

            if opt in ["-f", "--filename"]:
                filename = arg.lower()

            if opt in ["-h", "--headless"]:
                if arg.lower() == 'false':
                    headless = False

            if opt in ["-a", "--alert"]:
                if arg.lower() == 'true':
                    alert = 1
                elif arg.lower() == 'false':
                    alert = 0
        
    refresher = pbi_refresher(headless=headless, credentials=pbi_config)
    logger.info('driver intitialized successfully')
    refresher.login()
    logger.info('logging in successfully')
    refresher.get_dataset_url(filename=filename, ids=id_list)
    logger.info('get url successfully')
    refresher.refresh_data()
    success_dt = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    all_ids = ", ".join([str(i) for i in sorted(refresher.get_dataset_id())])
    fail_ids = ", ".join([str(i) for i in sorted(refresher.get_fail_id())])
    success_ids = ", ".join([str(i) for i in sorted(refresher.get_success_id())])

    suffix_msg = '; <https://docs.google.com/spreadsheets/d/1A2YQOSySyg0Ajhd2tVfqNIs1uqqO4wg8zwzvxXIUjnw|Add more datasets here>'
    if len(id_list) > 0:
        if len(success_ids) ==  len(id_list):
            success_msg = f'Datasets [{success_ids}] refreshed at {success_dt}'
        else:
            success_msg = f'Datasets [{success_ids}] refreshed at {success_dt}, but datasets [{fail_ids}] failed'
    else:
        if len(all_ids) == len(success_ids):
            success_msg = f'All datasets refreshed at {success_dt}'
        else:
            success_msg = f'Datasets [{success_ids}] refreshed at {success_dt}, but datasets [{fail_ids}] failed'

    logger.info(success_msg) 

    if alert == 1:
        slack_noti(success_msg + suffix_msg, user=slack_channel)
    elif alert == 2 and len(refresher.get_fail_id()) > 0:
        slack_noti(success_msg + suffix_msg, user=slack_channel)

    refresher.close_driver()

if __name__ == "__main__":
    sys.exit(main())