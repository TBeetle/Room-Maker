from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import os
import time
#from chromedriver_binary.auto import find_driver_version

#1: Log into the application
class LoginTestCase(LiveServerTestCase):

  def test_login(self):
    selenium = webdriver.Chrome()
    
    selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
    
    username_input = selenium.find_element('id','username')
    password_input = selenium.find_element('id','password')
    login_button = selenium.find_element("id",'loginbutton')
    
    username_input.send_keys("testing12")
    password_input.send_keys("testing12")

    login_button.click()

    time.sleep(5)

#2: Log into the application and then log out
class LoginAndOutTestCase(LiveServerTestCase):

  def test_login_and_logout(self):
        selenium = webdriver.Chrome()
        
        selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
        
        # Login process
        username_input = selenium.find_element('id', 'username')
        password_input = selenium.find_element('id', 'password')
        login_button = selenium.find_element('id', 'loginbutton')
        
        username_input.send_keys("testing12")
        password_input.send_keys("testing12")

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
      
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")

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
      
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")

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
      
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
    
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
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")

      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_format.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#7: Upload CSV Template
class UploadCSVTemplate(LiveServerTestCase):
   
   def test_upload_csv_template(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
    
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
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
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

#9: Upload Excel Minimum X Values
class UploadExcelMinimumX(LiveServerTestCase):
   
   def test_upload_excel_minimum_x(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_Min_X.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#10: Upload Excel Maximum X Values
class UploadExcelMaximumX(LiveServerTestCase):
   
   def test_upload_excel_maximum_x(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_max_x.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#11: Upload Excel Minimum Y Values
class UploadExcelMinimumY(LiveServerTestCase):
   
   def test_upload_excel_minimum_y(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_max_x.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#12: Upload Excel Value Out of Bounds (too small)
class UploadExcelOOBS(LiveServerTestCase):
   
   def test_upload_excel_OOOBS(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_format_out_of_bounds_small.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#13: Upload Excel minimum calibration
class UploadExcelMinimumCali(LiveServerTestCase):
   
   def test_upload_excel_minimum_cali(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_min_calibration.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#14: Upload Excel maximum calibration
class UploadExcelMaxCali(LiveServerTestCase):
   
   def test_upload_excel_max_cali(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_max_calibration.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#15: Upload Excel Value Out of Bounds (too large)
class UploadExcelOOBL(LiveServerTestCase):
   
   def test_upload_excel_OOBL(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_out_of_bounds_large.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#16: Upload Excel Camera has different sizes
class UploadExcelDifCamSize(LiveServerTestCase):
   
   def test_upload_excel_dif_cam_size(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_out_of_bounds_large.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#17: Upload Excel Camera large rotation
class UploadExcelCamRot(LiveServerTestCase):
   
   def test_upload_excel_cam_large_rotation(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_table_large_rotation.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

#18: Upload Excel Template and then change object colors
class UploadExcelEditColors(LiveServerTestCase):
   
   def test_upload_excel_new_colors(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_format.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

      edit_style_button = selenium.find_element('id','editStyle')
      edit_style_button.click()

      color_dropdown = Select(selenium.find_element_by_id('id_sensor_label_color'))
      color_dropdown.select_by_value('cyan')

      submit_changes = selenium.find_element('id','submit-all')
      submit_changes.click()

#19: Upload Excel Template and then change boundary colors
class UploadExcelTemplate(LiveServerTestCase):
   
   def test_upload_excel_boundary_colors(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_format.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

      edit_style_button = selenium.find_element('id','editStyle')
      edit_style_button.click()

      color_dropdown = Select(selenium.find_element_by_id('id_door_color'))
      color_dropdown.select_by_value('cyan')

      submit_changes = selenium.find_element('id','submit-all')
      submit_changes.click()

#20: Upload Excel Template and then change landscape
class UploadExcelLandscape(LiveServerTestCase):
   
   def test_upload_excel_new_landscape(self):
      chromeOptions = webdriver.ChromeOptions()
      selenium = webdriver.Chrome(options=chromeOptions)
      selenium.get('https://thebackyardigans-test.up.railway.app/accounts/login/')
      
      # Login process
      username_input = selenium.find_element('id', 'username')
      password_input = selenium.find_element('id', 'password')
      login_button = selenium.find_element('id', 'loginbutton')
      
      username_input.send_keys("testing12")
      password_input.send_keys("testing12")
      login_button.click()
      
      time.sleep(3)

      current_dir = os.path.dirname(__file__)
      #print(f"Current directory: {current_dir}")
      upload_file_path = os.path.join(current_dir, 'testsfiles/example_excel_format.xlsx')
      #print(upload_file_path)

      upload_input = selenium.find_element('id', 'formFile')
      upload_input.send_keys(upload_file_path)

      convert_button = selenium.find_element('id', 'convertButton').click()

      time.sleep(15)

      edit_style_button = selenium.find_element('id','editStyle')
      edit_style_button.click()

      time.sleep(5)

      edit_style_button = selenium.find_element('id','landscapeButton')
      edit_style_button.click()

      time.sleep(5)

      submit_changes = selenium.find_element('id','submit-all')
      submit_changes.click()









