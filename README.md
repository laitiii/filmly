# Filmly

Filmly is a platform for movie reviews. 
The features include:

* Account creation and login 
* Posting, editing and deleting movie reviews and rating movies 
* Tagging review by category for example "comedy" or "horror"
* Searching for reviews by movie or review name 
* Viewing the reviews for a movie from other users
* Account profile page listing the reviews made by an user
* Commenting on other users reviews

### [Releases](https://github.com/laitiii/filmly/releases)

## Usage instructions
After cloning or downloading the repository and changing your terminal working directory there run these commands:

Creating the virtual environment and installing requirements:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On windows the process is a bit different:

```
python -m venv venv
venv\scripts\activate
pip install -r requirements.txt
```

Create the database tables:

```
sqlite3 database.db < schema.sql
```

Start the app with:

```
flask run
```

Then go to http://localhost:5000 in your browser to use the app.


Note: This app was used in the same course (Tikawe period 1 autumn 2025) but did not pass due to a flaw in the code. I was instructed to apply to the same course at a later date. My goal is to better understand the development of web apps and polish/rework this app.
