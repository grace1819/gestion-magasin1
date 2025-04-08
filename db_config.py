import sqlite3


def connect_db():
    """Établit une connexion à la base de données SQLite"""
    return sqlite3.connect('ventes.db', check_same_thread=False)


def init_db():
    """Initialise la base de données avec les tables nécessaires"""
    conn = connect_db()
    cursor = conn.cursor()

    # Table clients
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        email TEXT,
        telephone TEXT
    )
    ''')

    # Table produits
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        categorie TEXT NOT NULL,
        prix_unitaire REAL NOT NULL
    )
    ''')

    # Table ventes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_vente DATE NOT NULL,
        produit_id INTEGER NOT NULL,
        client_id INTEGER,
        quantite INTEGER NOT NULL,
        montant REAL NOT NULL,
        FOREIGN KEY (produit_id) REFERENCES produits(id),
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )
    ''')

    conn.commit()
    conn.close()