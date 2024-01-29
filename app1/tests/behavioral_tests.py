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
    
    #username_input = selenium.find_element('id','login_button')
    #password_input = self.driver.find_element_by_name("pass")
    #login_button = self.driver.find_element_by_name("login_button")


    # service = Service(executable_path='/Users/jordanfowler/chromedriver')
    # options = webdriver.ChromeOptions()
    # self.driver = webdriver.Chrome(service=service, options=options)

    # self.driver.get('http://127.0.0.1:8000/')
    # self.driver.implicitly_wait(1000)

# class LoginTestCase(LiveServerTestCase):
#     def setUp(self):

#         service = Service(executable_path='/Users/jordanfowler/chromedriver')
#         options = webdriver.ChromeOptions()

#         self.driver = webdriver.Chrome(service=service, options=options)
#         self.driver.implicitly_wait(10)  # Set an implicit wait time for elements to load

#         # #chrome_version = find_driver_version()
#         # self.driver = webdriver.Chrome(executable_path='/Users/jordanfowler/chromedriver')  # Specify the path to your Chrome WebDriver
#         # self.driver.implicitly_wait(10)  # Set an implicit wait time for elements to load

#     def tearDown(self):
#         self.driver.quit()

#     def test_login(self):
#         # Open the login page
#         self.driver.get("'http://127.0.0.1:8000/'")  # Replace with the actual URL of your login page

#         # Find the username and password input fields and the login button
#         username_input = self.driver.find_element_by_name("username")
#         password_input = self.driver.find_element_by_name("pass")
#         login_button = self.driver.find_element_by_name("login_button")

#         # Enter the hardcoded username and password
#         username_input.send_keys("user_test")
#         password_input.send_keys("pass_test")

#         # Click the login button
#         login_button.click()

#         # Check if the login was successful (you can modify this based on your website's behavior)
#         assert "Welcome" in self.driver.page_source

# if __name__ == "__main__":
#     import unittest
#     unittest.main()

