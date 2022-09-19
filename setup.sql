CREATE TABLE IF NOT EXISTS live_locations (
    username varchar(255) NOT NULL,
    api_key varchar(255) NOT NULL,
    created_at datetime default (datetime('now', 'localtime')),
    latitude float,
    longitude float,

    PRIMARY KEY (username, api_key, created_at)
);

CREATE TABLE IF NOT EXISTS messages (
    person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username varchar(255) NOT NULL,
    api_key varchar(255) NOT NULL,
    created_at datetime default (datetime('now', 'localtime')),
    message varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS announcements (
   person_id INTEGER PRIMARY KEY AUTOINCREMENT,
    message varchar(255) NOT NULL,
    created_at datetime default (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS vossen_locations (
    api_key varchar(255) NOT NULL,
    vossen_team varchar(255) NOT NULL,
    datetime varchar(255) NOT NULL,
    location_type varchar(255) NOT NULL default 'unknown',
    latitude float,
    longitude float,

    PRIMARY KEY (vossen_team, datetime)
);

CREATE TABLE IF NOT EXISTS scorelijst (
    groep varchar(255) NOT NULL,
    datetime datetime NOT NULL,
    woonplaats varchar(255) NOT NULL,
    hunts integer NOT NULL,
    tegenhunts integer NOT NULL,
    opdrachten integer NOT NULL,
    fotoopdrachten integer NOT NULL,
    hints integer NOT NULL,
    bonus integer NOT NULL,
    penalties integer NOT NULL,

    PRIMARY KEY (groep, datetime)
);