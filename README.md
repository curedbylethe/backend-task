# Getting started

The **front end** is deployed to Netflify [here](https://super-kitten-8cba14.netlify.app/).\
You can find the frontend code in it's [repo](https://github.com/curedbylethe/frontend)
Clone this repo, in your terminal:\
```
$ gh repo clone curedbylethe/backend-task
$ cd backend-task/backend`
$ touch .env
```
Now set the env variables:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=<some gmail>
EMAIL_HOST_PASSWORD=<email password>
```
Go back and create another .env file:
```
$ cd ../
touch .env
```
Set the env variables:
```
export FRONTEND_URL = https://super-kitten-8cba14.netlify.app/
```

## Docker
Run the fallowing commands in the same directory as the Docker file:
```
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py collectstatic
$ docker build --tag <imagename>:latest .  
$ docker run --name <containername> -d -p 8000:8000 <imagename>:latest
```

With the docker image created and container running
the frontend can listen to the backend at http://localhost:8000/
Create two superusers (example: hradmin@admin.com and financeadmin@admin.com) and give them is_hr and is_finance permissions respectively in django-admin.
```
$ docker exect -it <containername> bash
> $ python manage.py createsuperuser
> ...
> exit
```

### Tips
You can authorize and access a user's incomes 
in the swagger panel at http://localhost:8000/
by clicking on **Authorize** and typing
`Bearer <token>`
where token is the token of the user you want to access.
Refresh the access token using the login api.