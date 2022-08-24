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