
# LoL map champion tracker

## About The Project

This tool allows to track enemy champions on the League of Legends map and show the last known location of someone missing with a timer. It also has the advantage of replicating the map in large format on another screen.

There is no danger regarding Vanguard since the computer where League of Legends is installed only needs to provide screenshots of the game. Another computer will show the map and track the champions.

⚠️ At time of writing, this tool requires some prerequisites which can be restrictive:

- Need a second computer (e.g. laptop)
- The game resolution must be exactly 2560*1440
- The map scale must be set to 100 in the interface settings
- Requires the use of a Riot Games API key to be renewed every 24 hours (free and very easy to get)

This tool works quite well but can show some limitations, especially when two or more enemies are close to each other. Also, the detection thresholds of some champions probably need to be adjusted, but I can't test all the champions now. Feel free to create an issue if necessary.

If this is not a problem for you, you can skip ahead to see how to install it.

## Getting Started

### Prerequisites

- [Python](https://www.python.org/downloads/) (tested with 3.13.5)
- [Git](https://git-scm.com/downloads)

### Installation

- On the computer running League of Legends

    - In game, set resolution to 2560*1440 in video settings

    - In game, set map scale to 100 in interface settings

    - Clone [lol-map-screenshot-server](https://github.com/pierre-josselin/lol-map-screenshot-server)

        ```
        git clone https://github.com/pierre-josselin/lol-map-screenshot-server.git
        ```

    - Go to `lol-map-screenshot-server`

        ```
        cd lol-map-screenshot-server
        ```

    - Create a virtual environment

        ```
        python -m venv .venv
        ```

    - Activate the virtual environment

        ```
        # Windows
        .venv\Scripts\activate

        # Linux / macOS
        source .venv/bin/activate
        ```

    - Install dependencies

        ```
        pip install -r requirements.txt
        ```

    - Create the environment file

        ```
        # Windows
        copy .env.example .env

        # Linux / macOS
        cp .env.example .env
        ```

    - Open .env with a text editor and review all variables

- On another computer

    - Clone [this repository](https://github.com/pierre-josselin/lol-map-champion-tracker)

        ```
        git clone https://github.com/pierre-josselin/lol-map-champion-tracker.git
        ```

    - Go to `lol-map-champion-tracker`

        ```
        cd lol-map-champion-tracker
        ```

    - Create a virtual environment

        ```
        python -m venv .venv
        ```

    - Activate the virtual environment

        ```
        # Windows
        .venv\Scripts\activate

        # Linux / macOS
        source .venv/bin/activate
        ```

    - Install dependencies

        ```
        pip install -r requirements.txt
        ```

    - Create the environment file

        ```
        # Windows
        copy .env.example .env

        # Linux / macOS
        cp .env.example .env
        ```

    - Open .env with a text editor and review all variables

## Usage

- On the computer running League of Legends

    - Go to `lol-map-screenshot-server`

    - Activate the virtual environment

        ```
        # Windows
        .venv\Scripts\activate

        # Linux / macOS
        source .venv/bin/activate
        ```

    - Run the script

        ```
        python main.py
        ```

- On another computer

    - Login to the [Riot Developer Portal](https://developer.riotgames.com)

    - Regenerate the developement API key

    - Update the RIOT_GAMES_API_KEY variable in the `.env` file

        > [!IMPORTANT]  
        > The API key is only valid for 24 hours and must be renewed.

    - Go to `lol-map-champion-tracker`

    - Activate the virtual environment

        ```
        # Windows
        .venv\Scripts\activate

        # Linux / macOS
        source .venv/bin/activate
        ```

    - Run the script

        ```
        python main.py
        ```
