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

Everything is delpoyed now

# FRONTEND

# BACKEND

## Configure the backend

The easiest way to configure the backend and install the dependencies is to create a virtual environment with the command :

> python3 -m venv .venv

After this step, you will have to change your environment source with :

> source .venv/bin/activate

Once you are on your virtual environment (it should be like (.venv)[user]@[computer_name]), you can build and run the project with

> make backend

## Potential problem with the Docker compose

If you can run the docker-compose.yml you will have to give a full access to docker with theses commands :

> sudo groupadd docker

_creates the user group called "docker"_

> sudo usermod -aG docker ${USER}

_gives the admin access_

Now you just have to restart your machine and run the Makefile, enjoy !!