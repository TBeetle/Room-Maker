# TheBackyardigans

Our project will be a Web application that can ingest a JSON or Excel/CSV file to draw a building layout. The output of the app would be both a downloadable LaTeX file and PDF of the finished drawing. Users would be able to adjust items live in the browser (e.g. shift a wall around, move a chair) with a flexible UI. Style settings would be controlled in the app, and it would be built using Django and Materialize-CSS. A bonus feature would allow for an upload of a PDF building plan that auto-converts walls/doors/windows to LaTeX.

## External Requirements

In order to build this project you first have to install:

- [Pip](https://pypi.org/project/pip/)
- [Pipenv](https://pypi.org/project/pipenv/)
- [Django](https://www.djangoproject.com/)
- [Black](https://pypi.org/project/black/)

Install pip:
Pip comes on device but to upgrade look at commands here - https://pip.pypa.io/en/stable/installation/

Install pipenv:

To install:

We're going to use pipenv to create virtual environments which can be created with -

pipenv --python "<path-to-python>" install --ignore-pipfile

Install Django:

Django is a little bit more complicated to install and prepare, but you can view installation tutorial with commands here - https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django

Install Black:

Black is our group's style guide of choice. To install use -

pip install black

## Setup

If you plan on using pipenv, make sure you use pipenv shell to enter the environment.

## Running

Make sure you have correctly cloned the repository and it is the most recent version by using git pull command. Then, to run our web app type:

cd layoutGenerator
python3 manage.py runserver

# Deployment

We are planning on deploying using Railway, but this is subject to change.

# Testing

Not applicable at this point in time.

## Testing Technology

Not applicable at this time.

## Running Tests

Not applicable at this time.

# Authors

Tyler Beetle: tbeetle22@gmail.com (TBeetle)
Joey Missan: jmissan@email.sc.edu (jmissan)
Anna Michelitch: acm34@email.sc.edu (acm34)
Grant Ward: jgward@email.sc.edu (jgward)
Jordan Fowler: jsfowler@email.sc.edu (jordansfowler)
