import pandas as pd
from db_config import connect_db

def get_ventes():
    """Récupère toutes les ventes avec les informations des produits et clients"""
    conn = connect_db()
    query = '''
    SELECT v.id, v.date_vente, p.nom as produit, p.categorie, 
           c.nom as client, v.quantite, v.montant
    FROM ventes v
    JOIN produits p ON v.produit_id = p.id
    LEFT JOIN clients c ON v.client_id = c.id
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_produits():
    """Récupère tous les produits"""
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM produits", conn)
    conn.close()
    return df

def get_clients():
    """Récupère tous les clients"""
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM clients", conn)
    conn.close()
    return df

def insert_vente(date, produit_id, client_id, quantite, montant):
    """Insère une nouvelle vente"""
    conn = connect_db()
    cursor = conn.cursor()
    query = "INSERT INTO ventes (date_vente, produit_id, client_id, quantite, montant) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, (date, produit_id, client_id, quantite, montant))
    conn.commit()
    conn.close()

def insert_produit(nom, categorie, prix_unitaire):
    """Insère un nouveau produit"""
    conn = connect_db()
    cursor = conn.cursor()
    query = "INSERT INTO produits (nom, categorie, prix_unitaire) VALUES (?, ?, ?)"
    cursor.execute(query, (nom, categorie, prix_unitaire))
    conn.commit()
    conn.close()

def insert_client(nom, email, telephone):
    """Insère un nouveau client"""
    conn = connect_db()
    cursor = conn.cursor()
    query = "INSERT INTO clients (nom, email, telephone) VALUES (?, ?, ?)"
    cursor.execute(query, (nom, email, telephone))
    conn.commit()
    conn.close()