# How to Contribute 🛠️

## Step 1: Find an Issue

Browse the open issues in the main repository and pick one you want to work on.
Or create one if you have found a bug or have a feature request.

## Step 2: Fork the Project 🍴

Click the "Fork" button on the main page of the repository to make a copy in your own account.

## Step 3: Clone the repositry and create a Branch 🌿

Clone repositry:

```bash
git clone <forked_repositry_name>
```

```bash
git switch -c <your_branch_name>
```

## Step 4: Telegram set-up

- Create a new public channel.
- Add your bot to the channel and give it admin rights
- Copy _.env.example_ and change name to _.env_, you can do like this: `cp .env.example .env`
- Open the new file
- Edit the following environment variables in the .env file:
  - `TELEGRAM_BOT_TOKEN`: Your bot's token. To obtain it, open [the
    bot](https://telegram.me/BotFather) and follow the instructions on how to
    create a new bot. In the end, you will receive a token that should be set
    as the value for the `TELEGRAM_BOT_TOKEN` environment variable.
  - `CHANNEL_USERNAME`: The channel name to which messages will be sent. If
    your public channel's link is https://t.me/some_name, use "some_name" as
    the value for CHANNEL_USERNAME.
  - `REDIS_URL`, `REDIS_DB`, `REDIS_POOL_SIZE`, `REDIS_PREFIX_KEY`: Redis-related
    environment variables. Only change these if you are confident in what you
    are doing.
  - `BOT_LANGUAGE`: The language for the bot's interface. List of available languages is updating

## Step 5: Project set-up

- [Docker set-up](#docker)
- [Local set-up](#local)

### Docker

Docker's installation guide you can find [here](https://docs.docker.com/get-docker/).

Docker Compose installation guide you can find [here](https://docs.docker.com/compose/install/)

If Docker is installed and running execute the following command:

```bash
docker-compose up
```

### Local

#### Install dependencies

Dependencies:

- python
- pip
- git
- poetry

###### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

# Install git and python
brew install git python

# Install Poetry
pip install poetry
```

###### Linux

- Ubuntu

```bash
sudo apt update
sudo apt install git python3 python3-pip python3-poetry
```

- Arch

```bash
sudo pacman -Syu git python python-pip python-poetry
```

###### Windows

- Python: Download the installer from the official Python [website](https://www.python.org/downloads/windows/) and follow the installation steps.
- Git: Download the installer from the official Git [website](https://git-scm.com/download/win) and follow the installation steps.
- Poetry: Open a Command Prompt or PowerShell window and run the following command to install Poetry:

```bash
pip install poetry
```

You can check if everything installed by this command:

```bash
poetry -v && git -v && pip -v && python --version
```

#### Set-up python virtual environment

Create a virtual environment with poetry
For more information visit this [website](https://python-poetry.org/docs/basic-usage/)

You can run do it like this in terminal:

```bash
poetry install && poetry shell
```

If you're using **PyCharm** or **Visual Studio Code** with the Python extension, it should use the virtual environment created by Poetry by default.

#### Problem with redis

If you want to use redis on your local dev set-up set
`REDIS_URL=localhost` in the _.env_ file.

## Step 6: Work on the Task 👨‍💻👩‍💻

Make the necessary changes in the code or documentation.

## Step 7: Test your code

Make sure that the changes you've made work locally before creating a Pull Request

❕ **IMPORTANT**. Make sure to refactor your code using "Black" formatter before creating a Pull Request

To install Black formatter run:

```bash
pip install black
```

To format your code run:

```bash
black .
```

## Step 8: Commit ✅

Add your changes through Git and create a commit with a descriptive message.

```bash
git add .
```

Create a Commit

```bash
git commit -m 'Your descriptive message'
```

NOTE: Each pull request (PR) should contain only one commit. If you have multiple commits, they need to be squashed.

## Step 9: Work Remotely 🌍

When your work is ready and complies with project conventions, upload your changes to your fork:

```bash
# Push your work to your remote repository
git push -u origin <your_branch_name>
```

## Step 10: Create a Pull Request ➡️

Go to the page of your fork on GitHub and click "New Pull Request". Verify that the changes are displayed correctly, and then submit your pull request.
