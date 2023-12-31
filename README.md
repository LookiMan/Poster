![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)

# Poster

### Simple web admin for posting posts to many telegram and discord channels

![](https://github.com/LookiMan/Poster/blob/main/screenshots/posts.png)

## Usage:

**1. Add Telegram or Discord bots:**

To add a new bot you should: go to the "Bots" tab and click the "Add Bot" button, select the bot type and specify its token obtained from @BotFather (for Telegram) or in the developer panel (for Discord).

**2. Add Telegram or Discord channels:**

To add a new channel you should: go to the "Channels" tab and click the "Add Channel" button, specify the type of channel (Discord/Telegram), add a previously created bot and specify the channel id

**3. Create new post:**

To add a new post you should: go to the "Posts" tab and click the "Add Post" button, select the type of post, select the channels for sending message and fill in the required fields for the selected type of post

**4. Supported message types for messengers:**

|       Message Type    |   Telegram    |       Discord |
| --------------------- | ------------- | ------------- |
|          Audio        |       ✅      |      ✅       |
|         Document      |       ✅      |      ✅       |
|   Gallery Documents   |       ✅      |      ✅       |
|     Gallery Photos    |       ✅      |      ✅       |
|          Text         |       ✅      |      ✅       |
|         Photo         |       ✅      |      ✅       |
|         Video         |       ✅      |      ✅       |
|         Voice         |       ✅      |       ⚠️       |


**5. Supported actions:**

- Publish post (send messages upon channels)
- Publish post silently (send messages upon channels without sound notification)
- Edit post (messages will be edited in channels)
- Unpublish post (messages will be deleted only from channels, but not from admin panel)
- Delete post (messages will be deleted from channels and from the admin panel)

![](https://github.com/LookiMan/Poster/blob/main/screenshots/published_post.png)

![](https://github.com/LookiMan/Poster/blob/main/screenshots/unpublished_post.png)

## TODO:

- Fix sending voice messages in discord

- Finalize the function annotations and type hints

- Finalize the tests :)


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

**Build styles:**

`docker compose exec app sh -c ./bin/build-sass.sh`

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

**Watch styles:**

`docker compose exec app sh -c ./bin/watch-sass.sh`
