# TheBackyardigans

Our project is a Web application that can ingest a JSON or Excel/CSV file to draw a building layout. The output of the app includes both a downloadable LaTeX file containing code to generate the layout and a PDF of the finished drawing. Users are able to further customize individual layouts with a flexible UI. Style settings are controlled in the app, and it is built using Django and Materialize-CSS.

## Project Setup Guide

This guide will walk you through setting up the project environment step-by-step.

### Step 1: Update Package Lists

Run the following command to update the package lists:

```bash
sudo apt-get update
```
### Step 2: Clone the Repository

Clone the project repository using Git:

```bash
git clone https://github.com/SCCapstone/TheBackyardigans.git
cd TheBackyardigans
```
### Step 3: Install Python 3.11

Install Python 3.11 using the following command:

```bash
sudo apt install python3.11
```
### Step 4: Install Pipenv

Our app utilizes Pipenv to keep our package requirements in check. Install and create an environment for Pipenv to manage Python dependencies using the following commands:

```bash
pip install pipenv
pipenv --python 3.11 install --ignore-pipfile
```
### Step 5: Activate the Pipenv Shell

You can then enter the Pipenv environment with the following command:

```bash
pipenv shell
```
### Step 6: Install LaTeX Dependencies

Our project incorporates LaTeX code to convert the Excel/CSV/JSON files to a viewable layout. Here's what you need to install:

```bash
sudo apt install texlive-luatex
sudo apt install texlive-fonts-recommended texlive-fonts-extra
sudo apt isntall dvipng
sudo apt install texlive-science
sudo apt install poppler-utils
```
### Step 8: Run the Application

You can run the Django server locally using:

```bash
python manage.py runserver
```
Once the server is running, you can head to http://127.0.0.1:8000/ in your web browser to view the application locally.


## Testing

In our project we have two primary types of tests that are being run: unit test and behavioral test. Both of these types of
tests have their own python file and are within the tests folder.

'/tests/unit_tests.py'
'/tests/behavioral_tests.py'

### Testing Technology

We are using Selenium to test our project.

### Running Tests

To run Unit Test:

```bash
python manage.py test app1.tests.unit_tests
```

### Behaviorial test setup:

Helpful Guide-

https://medium.com/@patrick.yoho11/installing-selenium-and-chromedriver-on-windows-e02202ac2b08

Install Selenium-

```bash
pip install selenium
```

Install Chromedriver and place within your system wide directory-

More helpful links to download Chromedriver
https://chromedriver.chromium.org/getting-started
https://chromedriver.chromium.org/downloads
https://googlechromelabs.github.io/chrome-for-testing/

### Running Behaviorial Tests:

Within Terminal One:

```bash
python manage.py runserver
```

Within Terminal Two:

```bash
python manage.py test app1.tests.behavioral_tests
```

# Authors

Tyler Beetle: tbeetle22@gmail.com (TBeetle)
Joey Missan: jmissan@email.sc.edu (jmissan)
Anna Michelitch: acm34@email.sc.edu (acm34)
Grant Ward: jgward@email.sc.edu (jgward)
Jordan Fowler: jsfowler@email.sc.edu (jordansfowler)
