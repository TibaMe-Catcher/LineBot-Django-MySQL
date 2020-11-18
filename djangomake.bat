django-admin startproject %1 
cd %1
copy ..\ngrok.exe
python manage.py startapp %2
python manage.py makemigrations
python manage.py migrate
md templates
md static
md module
cd module
copy /y nul func.py