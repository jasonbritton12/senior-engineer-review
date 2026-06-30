import sqlite3


def get_user(conn, name):
    # Planted (Critical): SQL injection via f-string interpolation of user input.
    query = f"SELECT * FROM users WHERE name = '{name}'"
    return conn.execute(query).fetchall()


def checkout(cart, customer):
    # Planted (Major): unhandled None when a guest customer has no address.
    line1 = customer.address.line1
    return {"ship_to": line1, "total": sum(i.price for i in cart)}
