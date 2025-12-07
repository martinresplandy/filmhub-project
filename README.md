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

Once you are on your virtual environment (it should be like (.venv)[user]@[computer_name]), you can build and run the project with

> make backend_local

## Potential problem with the Docker compose

If you can't run the docker-compose.yml and get this type of error :

> django.db.utils.OperationalError: connection to server at "localhost" (127.0.0.1), port 5432 failed: server closed the connection unexpectedly

You will have to give a full access to docker with theses commands :

> sudo groupadd docker

_creates the user group called "docker"_

> sudo usermod -aG docker ${USER}

_gives the admin access_

Now you just have to restart your machine and run the Makefile, enjoy !!

## Description of the API REST routes

All the parameters must be give in the Body of the request.

| ROUTES        | GET | POST | PATCH | DELETE |
| -------- | ------- | ------- | ------- | ------- |
| /register/            | X | {"username":string, "email":string, "password":string} | X | X |
| /login/               | X | {"username":string, "password":string} | X | X |
| /movie/               | {"external_id":number} | X | X | X |
| /movies/              | No Body | X | X | X |
| /movies/search/       | {"search":string, "search_type":string} | X | X | X |
| /movies/watched/      | No Body | {"external_id":number} | X | {"external_id":number} |
| /movies/watch_list/   | No Body | {"external_id":number} | X | {"external_id":number} |
| /movies/recommended/  | No Body | X | No Body | X |
| /ratings/             | No Body | {"external_movie_id":string, "score":number[0:5], "comment":string} | {"rating_id":number, "new_score":number, "new_comment":string} | {"rating_id":number} |

