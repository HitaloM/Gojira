#####################
Gojira - Telegram Bot
#####################

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json
    :target: https://github.com/charliermarsh/ruff
    :alt: Ruff

.. image:: https://badges.crowdin.net/gojira/localized.svg
    :target: https://crowdin.com/project/gojira/
    :alt: crowdin status

.. image:: https://results.pre-commit.ci/badge/github/HitaloM/Gojira/main.svg
   :target: https://results.pre-commit.ci/latest/github/HitaloM/Gojira/main
   :alt: pre-commit.ci status

This bot can get information from AniList through its API with GraphQL, supporting all AniList media.

Features
========

- Retrieve information about anime, manga, characters, staff, and studios using the AniList API.

How to contribute
=================

Every open source project lives from the generous help by contributors that sacrifices their time and Gojira is no different.

Translations
------------
Translations should be done in our `Crowdin Project <https://crowdin.com/project/gojira>`_,
as Crowdin checks for grammatical issues, provides improved context about the string to be translated and so on,
thus possibly providing better quality translations. But you can also submit a pull request if you prefer to translate that way.

Bot setup
=========

Below you can learn how to set up the Gojira project.

Requirements
------------

- Python 3.12.X.
- An Unix-like operating system (Windows isn't supported).
- Redis

Instructions
------------

1. Create a virtualenv (This step is optional, but **highly** recommended to avoid dependency conflicts)

   - ``python3 -m venv .venv`` (You don't need to run it again)
   - ``. .venv/bin/activate`` (You must run this every time you open the project in a new shell)

2. Install dependencies from the pyproject.toml with ``python3 -m pip install . -U``.
3. Go to https://my.telegram.org/apps and create a new app.
4. Compile the desired locales (languages) using the `pybabel` tool:

   - ``pybabel extract --keywords='__ _' --input-dirs=. -o locales/bot.pot``
   - ``pybabel compile -d locales -D bot``

5. Start the Redis service:

   - ``systemctl start redis``

6. Create a new ``config.env`` in ``data/``, there is a ``config.example.env`` file for you to use as a template.
7. After completing the ``config.env`` file, run the bot using the ``gojira/__main__.py`` file:

   - ``python3 -m gojira``

Tools
-----

- Use `ruff <https://pypi.org/project/ruff/>`_ to lint and format your code.
- We recommend using `pre-commit <https://pre-commit.com/>`_ to automate the above tools.
- We use VSCode and recommend it with the Python, Pylance and Intellicode extensions.
