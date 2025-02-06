import sqlite3

con = sqlite3.connect('videodb.db')
cur = con.cursor()

cur.execute(
    """
    create table if not exists videos (
        id INTEGER PRIMARY KEY,
        video_id TEXT,
        title TEXT,
        upload_date TEXT,
        unique (video_id)
    )
    """
)

con.commit()
con.close()