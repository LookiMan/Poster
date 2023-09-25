# Poster

### Simple web admin for posting posts to many telegram and discord channels

![](https://github.com/LookiMan/Poster/blob/master/screenshots/posts.png)


## Configuration:

**Create .env environment file using .env.ini as template:**

`cp .env.ini .env`

**Create local_settings.py file using local_settings.py.ini as template:**

`cp ./config/local_settings.py.ini ./config/local_settings.py`

**Build container:**

`docker compose build`

**Up container:**

`docker compose up -d`

**Migrate:**

`docker compose exec app python manage.py migrate`

**Create superuser:**

`docker compose exec app python manage.py createsuperuser`

**Compile messages:**

`docker compose exec app python manage.py compilemessages`

**Configure pre-commit validation:**

`cp ./bin/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`

## Development:

**Up container:**

`docker compose up`

**Down container:**

`docker compose down`

**Make migrations:**

`docker compose exec app python manage.py makemigrations`

**Migrate:**

`docker compose exec app python manage.py migrate`

**Make translation file:**

`docker compose exec app python manage.py makemessages -l uk`

`docker compose exec app python manage.py makemessages -l en`

**Validate-python:**

`docker compose exec app sh -c ./bin/validate-python.sh`

**Run tests:**

`docker compose exec app python manage.py test`

**Build styles use**

`docker compose exec app sh -c ./bin/build-sass.sh`
