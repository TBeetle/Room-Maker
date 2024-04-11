from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import time
#from chromedriver_binary.auto import find_driver_version

#1: Log into the application
class LoginTestCase(LiveServerTestCase):

  def test_login(self):
    selenium = webdriver.Chrome()
    
    selenium.get('http://127.0.0.1:8000/')
    
    username_input = selenium.find_element('id','username')
    password_input = selenium.find_element('id','password')
    login_button = selenium.find_element("id",'loginbutton')
    
    username_input.send_keys("user_test")
    password_input.send_keys("pass_test")
    login_button.click()

    time.sleep(5)

#2: Log into the application and then log out
class LoginAndOutTestCase(LiveServerTestCase):

  def test_login_and_logout(self):
        selenium = webdriver.Chrome()
        
        selenium.get('http://127.0.0.1:8000/')
        
        # Login process
        username_input = selenium.find_element('id', 'username')
        password_input = selenium.find_element('id', 'password')
        login_button = selenium.find_element('id', 'loginbutton')
        
        username_input.send_keys("user_test")
        password_input.send_keys("pass_test")
        login_button.click()
        
        time.sleep(5)
        
        logout_button = selenium.find_element('id', 'logoutButton')
        logout_button.click()
        
        time.sleep(5)

#3-5: Download Sample File Format (Make sure to Delete it)
class DownloadExcel(LiveServerTestCase):

    # Example test method
  def test_download_excel_sample_template(self):
      chromeOptions = webdriver.ChromeOptions()
      prefs = {"download.default_directory" : "/some/path"}
      # chromeOptions.add_experimental_option("prefs",prefs)
      selenium = webdriver.Chrome(options=chromeOptions)
      
      selenium.get('http://127.0.0.1:8000/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("user_test")
      password_input.send_keys("pass_test")
      login_button.click()
      
      time.sleep(3)

      excel_button = selenium.find_element('id','excelButton')
      excel_button.click()

      time.sleep(3)
    
class DownloadCSV(LiveServerTestCase):

    # Example test method
  def test_download_csv_sample_template(self):
      chromeOptions = webdriver.ChromeOptions()
      prefs = {"download.default_directory" : "/some/path"}
      # chromeOptions.add_experimental_option("prefs",prefs)
      selenium = webdriver.Chrome(options=chromeOptions)
      
      selenium.get('http://127.0.0.1:8000/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("user_test")
      password_input.send_keys("pass_test")
      login_button.click()
      
      time.sleep(3)

      excel_button = selenium.find_element('id','csvButton')
      excel_button.click()

      time.sleep(3)

class DownloadJSON(LiveServerTestCase):

    # Example test method
  def test_download_json_sample_template(self):
      chromeOptions = webdriver.ChromeOptions()
      prefs = {"download.default_directory" : "/some/path"}
      # chromeOptions.add_experimental_option("prefs",prefs)
      selenium = webdriver.Chrome(options=chromeOptions)
      
      selenium.get('http://127.0.0.1:8000/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("user_test")
      password_input.send_keys("pass_test")
      login_button.click()
      
      time.sleep(3)

      excel_button = selenium.find_element('id','jsonButton')
      excel_button.click()

      time.sleep(3)
      
#6: Upload Excel Template
class UploadExcelTemplate(LiveServerTestCase):
   
   def test_upload_excel_template(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('http://127.0.0.1:8000/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("user_test")
      password_input.send_keys("pass_test")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_format.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(3)

#7: Upload CSV Template
class UploadCSVTemplate(LiveServerTestCase):
   
   def test_upload_csv_template(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('http://127.0.0.1:8000/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("user_test")
      password_input.send_keys("pass_test")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_csv_format.csv')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(3)

#8: Upload JSON Template
class UploadJSONTemplate(LiveServerTestCase):
   
   def test_upload_json_template(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('http://127.0.0.1:8000/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("user_test")
      password_input.send_keys("pass_test")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_json_format.json')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(3)

      #Upload Working Files

      #Upload Files that test boundary conditions

      #Layout Library Testing

      