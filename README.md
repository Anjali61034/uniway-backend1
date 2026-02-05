# Initial setup for working with APIs
1. Ensure that your machine has python and pip installed.
   
2. Clone this repo, create a virtual env using `python -m venv venv` and activate it using `source venv/bin/activate` (for MacOS) or `venv/Scripts/activate` (for Windows).
   
3. In uniwaybackend/settings.py, uncomment the settings for sqlite3 database and commment out the settings for postgreSQL.
   
4. Run the following commands:
```
pip install -r requirments.txt
cd uniwaybackend
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py runserver
```
Replace python with python3 if you have python v3 on your machine. Similarly, replace pip with pip3 if you have pip v3.

5. On the server, create a user (this will create a dept_head instead of the admin user createsuperuser created), login as the user you created, create at least one entry for all the sections.

6. Once the server is running and you have demo data, use PostMan to hit the following APIs and test everything -
```
http://127.0.0.1:8000/competitions/
http://127.0.0.1:8000/seminars/
http://127.0.0.1:8000/surveys/
http://127.0.0.1:8000/fests/
http://127.0.0.1:8000/student-initiatives/
http://127.0.0.1:8000/alumni/
```
