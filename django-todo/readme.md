This is obviously not a complete Django project, but the main files used by it. I use daphne async web server, which integrates easily with the django runserver command which makes development easy as well.
To recreate this project, install django and daphne into your virtual-environment. Then create the project, add an app named datastar (or change it if you wish) and add to your settings.py the following:

This must be at the top before middleware etc.

    INSTALLED_APPS = [
    'daphne',
      ...]

Then the asgi server

    ASGI_APPLICATION = 'hello_world.asgi.application'
That is enough to get it running off the default project setup.

This project uses an sqlite database to store all the todos, but could use other databses as well.