# @Telegram Flea - Your Open-Source Flea-Market Bot for Telegram 🛒

Telegram Flea is an open-source bot for Telegram designed to serve as a handy tool for flea-markets for any Community!.
It is scalable and can be used by anyone around the globe!
Currently, a basic version of the project is available, you can easily post your items to a dedicated Telegram-channel. Please refer to the attached photo for an example.

# Table of Contents 📚

- [How your project looks like 🏞](#photos)
- [Supported Languages and Status 🌍](#languages)
- [ToDo's 🌟](#todo)
- [Clone the repository 🗂](#clone)
- [Install dependencies ⬇️](#install)
- [Redis installation](#redis-installation)
- [Contribution 🤝](#contribution)
- [License 📝](#license)
- [Acknowledgements 🙏](#acknowledgements)

## Photos

![image](https://github.com/Salz0/telegram_flea/assets/76848642/9466e8cd-7b95-4c01-95d1-c46598aa40f7)

![image](https://github.com/Salz0/telegram_flea/assets/76848642/7d92f843-9ab7-4c4b-a36d-2120eff5255a)

## Languages

| Language   | Code | Status |
| ---------- | ---- | ------ |
| English    | en   | ✅     |
| German     | de   | ✅     |
| Ukrainian  | uk   | ✅     |
| Indonesian | id   | ✅     |
| Hindi      | hi   | ✅     |
| Spanish    | es   |        |
| French     | fr   |        |
| Japanese   | ja   |        |
| Chinese    | zh   |        |
| Arabic     | ar   |        |
| Portuguese | pt   |        |
| Bengali    | bn   |        |
| Punjabi    | pa   |        |
| Italian    | it   |        |
| Turkish    | tr   |        |
| Dutch      | nl   |        |
| Polish     | pl   |        |
| Vietnamese | vi   |        |
| Tamil      | ta   |        |
| Telugu     | te   |        |
| Marathi    | mr   |        |
| Kannada    | kn   |        |
| Malay      | ms   |        |
| Urdu       | ur   |        |

## Todo

- [todo] Moderation system of items applied

## Clone

```bash
git clone https://github.com/your_username/telegram_flea.git
```

### Install

```bash
cd telegram_flea
```

```bash
pip install poetry
```

```bash
poetry install
```

Set up your .env file with your Telegram API credentials.

## Redis-installation

### Overview

Redis is a powerful and lightning-fast open-source database system that is
often used to store and manage data in a very simple way. It's often referred
to as a "key-value store" because it stores data as pairs of keys and their associated values.

Repository contains Docker file. This file is used for creating Docker image with Redis.
First you need is Docker. How to install docker please find [here](https://www.docker.com/get-started/)
`docker build -t <enter name> .`
To create new image with specific name.

```
docker run -p 6379:6379 -p 8001:8001 <image name>
```

To create new container.

After that you can start your bot.

## Contribution

We love contributions! Please read our Contribution Guidelines to get started.

## License

This project is licensed under the MIT License. See the LICENSE.md file for details.

## Acknowledgements

- Thanks to aiogram for the awesome Telegram Bot API wrapper.
- And @mykolasolodukha for sharing the Telegram bot template for this repository
- All contributors are welcome! 🌟
