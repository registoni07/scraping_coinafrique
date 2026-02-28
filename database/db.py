import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "animals.db")

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie TEXT,
            nom TEXT,
            prix TEXT,
            adresse TEXT,
            image_lien TEXT
        )
    """)
    conn.commit()
    conn.close()

def clear_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM animals")
    conn.commit()
    conn.close()

def save_to_db(categorie, nom, prix, adresse, image_lien):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO animals (categorie, nom, prix, adresse, image_lien)
        VALUES (?, ?, ?, ?, ?)
    """, (categorie, nom, prix, adresse, image_lien))
    conn.commit()
    conn.close()