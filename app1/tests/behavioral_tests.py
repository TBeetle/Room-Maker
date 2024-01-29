from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
#from chromedriver_binary.auto import find_driver_version

class LoginTestCase(LiveServerTestCase):

  def testform(self):
    selenium = webdriver.Chrome()
    #Choose your url to visit
    selenium.get('http://127.0.0.1:8000/')
    
    username_input = selenium.find_element('id','username')
    password_input = selenium.find_element('id','password')
    login_button = selenium.find_element("id",'loginbutton')
    
    username_input.send_keys("user_test")
    password_input.send_keys("pass_test")
    login_button.click()

    time.sleep(5)