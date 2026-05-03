import db

def get_all_attributes():
    sql = "SELECT title, value FROM attributes ORDER BY id"
    result = db.query(sql)

    attributes = {}
    for title, value in result:
        attributes[title] = []
    for title, value in result:
        attributes[title].append(value)

    return attributes

def add_item(title, movie, review, score, user_id, attributes):
    sql = """INSERT INTO items (title, movie, review, score, user_id) 
            VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [title, movie, review, score, user_id])

    item_id = db.last_insert_id()

    sql = "INSERT INTO item_attributes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in attributes:
        db.execute(sql, [item_id, title, value])

def add_comment(item_id, user_id, comment):
    sql = """INSERT INTO comments (item_id, user_id, comment) 
            VALUES (?, ?, ?)"""
    db.execute(sql, [item_id, user_id, comment])

def get_comments(item_id):
    sql = """SELECT comments.comment, users.id user_id, users.username
            FROM comments, users
            WHERE comments.item_id = ? AND comments.user_id = users.id
            ORDER BY comments.id DESC"""
    return db.query(sql, [item_id])

def get_attributes(item_id):
    sql = "SELECT title, value FROM item_attributes WHERE item_id = ?"
    return db.query(sql, [item_id])

def get_items():
    sql = """SELECT i.id, i.user_id, i.title, i.movie, i.score, u.username 
            FROM items i
            JOIN users u ON u.id = i.user_id
            ORDER BY i.id DESC"""
    return db.query(sql)

def get_item(item_id):
    sql = """SELECT items.id,
                    items.title,
                    items.movie, 
                    items.review, 
                    items.score,
                    users.id user_id,
                    users.username
            FROM items, users
            WHERE items.user_id = users.id AND
                items.id = ?"""
    result = db.query(sql, [item_id])
    return result[0] if result else None

def update_item(item_id, title, movie, review, score, attributes):
    sql = """UPDATE items SET title = ?, movie = ?, review = ?, score = ? WHERE id = ?"""
    db.execute(sql, [title, movie, review, score, item_id])

    sql = "DELETE FROM item_attributes WHERE item_id = ?"
    db.execute(sql, [item_id])

    sql = "INSERT INTO item_attributes (item_id, title, value) VALUES (?, ?, ?)"
    for title, value in attributes:
        db.execute(sql, [item_id, title, value])

def remove_item(item_id):
    sql = "DELETE FROM comments WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM item_attributes WHERE item_id = ?"
    db.execute(sql, [item_id])
    sql = "DELETE FROM items WHERE id = ?"
    db.execute(sql, [item_id])

def find_items(query):
    sql = """SELECT id, title, movie
             FROM items
             WHERE title LIKE ? OR movie LIKE ? OR review LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like])
