import db_connector as db


def addLocation(username, api_key, datetime, lat, long):
    query = "INSERT INTO live_locations (username, api_key, created_at, latitude, longitude) VALUES (?, ?, ?, ?, ?)"
    db.executeQuery(query, params=[username, api_key, datetime, lat, long])
    return True

def getLocations(api_key):
    query = """
    SELECT username, latitude, longitude, created_at
    FROM live_locations l1
    WHERE API_KEY LIKE ?
    AND created_at = (
        SELECT MAX(created_at)
        FROM live_locations l2
        WHERE l2.username = l1.username
    )"""
    return db.selectQuery(query, params=[api_key])

def addMessage(username, api_key, message):
    query = "INSERT INTO messages (username, api_key, message) VALUES (?, ?, ?)"
    db.executeQuery(query, params=[username, api_key, message])
    return True

def getMessages(api_key):
    query = """
    SELECT username, message, created_at
    FROM messages m
    WHERE API_KEY LIKE ?
    ORDER BY created_at DESC
    LIMIT 50"""
    return db.selectQuery(query, params=[api_key])

def getAnnouncement():
    query = """
    SELECT message
    FROM announcements
    ORDER BY created_at DESC
    LIMIT 1"""
    return db.selectQuery(query)