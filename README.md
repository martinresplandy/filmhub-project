Package             Version
------------------- -------
asgiref             3.10.0

Django              5.2.8

djangorestframework 3.16.1

pip                 24.3.1

sqlparse            0.5.3

I installed django and djangorest framework , and also npm ( for the frontend)

also :    pip install django-cors-headers ; npm install react-router-dom axios ( also fetch option but axios works best)


to start the backend in the main folder python maange.py runserver

to start the frontend cd frontend : npm start

# BACKEND

## Configure the backend

The easiest way to configure the backend and install the dependencies is to create a virtual environment with the command :

> python3 -m venv .venv

After this step, you will have to change your environment source with :

> source .venv/bin/activate

Once you are on your virtual environment (it should be like ...), you can build and run the project with

> make super_backend

_if you want to create a super user in your terminal_

> make backend

_otherwise_
