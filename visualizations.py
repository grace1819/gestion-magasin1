from turtle import st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit
import streamlit as st

def plot_ventes_par_periode(df, periode):
    """Visualise les ventes par période (mensuelle, trimestrielle, annuelle)"""
    df_period = df.copy()
    df_period['date_vente'] = pd.to_datetime(df_period['date_vente'])

    if periode == 'Mensuel':
        df_period['periode'] = df_period['date_vente'].dt.to_period('M')
        title = "Ventes mensuelles"
    elif periode == 'Trimestriel':
        df_period['periode'] = df_period['date_vente'].dt.to_period('Q')
        title = "Ventes trimestrielles"
    else:  # Annuel
        df_period['periode'] = df_period['date_vente'].dt.to_period('Y')
        title = "Ventes annuelles"

    df_grouped = df_period.groupby('periode').agg({'montant': 'sum', 'quantite': 'sum'}).reset_index()
    df_grouped['periode'] = df_grouped['periode'].astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df_grouped['periode'], df_grouped['montant'], color='skyblue')
    ax.set_title(title)
    ax.set_xlabel('Période')
    ax.set_ylabel('Montant total')
    plt.xticks(rotation=45)

    return fig, df_grouped


def plot_top_produits(df, top_n=5):
    """Visualise les top produits par quantité et montant"""
    # Vérification des colonnes nécessaires
    required_columns = ['produit', 'quantite', 'montant']
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        raise ValueError(f"Colonnes manquantes dans le DataFrame: {missing_cols}")

    # Conversion des colonnes numériques
    df = df.copy()
    df['quantite'] = pd.to_numeric(df['quantite'], errors='coerce')
    df['montant'] = pd.to_numeric(df['montant'], errors='coerce')

    # Vérification des valeurs NaN après conversion
    if df['quantite'].isna().any() or df['montant'].isna().any():
        st.warning("Certaines valeurs numériques sont invalides et ont été remplacées par NaN")

    # Agrégation des données
    df_top = df.groupby('produit').agg({'quantite': 'sum', 'montant': 'sum'})

    # Vérification si le DataFrame est vide
    if df_top.empty:
        st.warning("Aucune donnée disponible pour le graphique")
        return None, df_top
    if df_top.empty:
        streamlit.warning("Aucune donnée disponible pour le graphique")
        return None, df_top
    # Sélection des top produits
    df_top = df_top.sort_values('quantite', ascending=False).head(top_n)

    # Création du graphique
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    try:
        # Top produits par quantité
        df_top.sort_values('quantite', ascending=True).plot.barh(
            y='quantite',
            ax=ax1,
            color='green',
            xlabel='Quantité vendue'
        )
        ax1.set_title(f'Top {top_n} produits (quantité)')

        # Top produits par montant
        df_top.sort_values('montant', ascending=True).plot.barh(
            y='montant',
            ax=ax2,
            color='orange',
            xlabel='Montant total'
        )
        ax2.set_title(f'Top {top_n} produits (montant)')

        plt.tight_layout()

    except Exception as e:
        st.error(f"Erreur lors de la création du graphique: {str(e)}")
        return None, df_top

    return fig, df_top


def plot_repartition(df, by='categorie'):
    """Visualise la répartition des ventes par catégorie ou client"""

    # Vérification des données d'entrée
    if df.empty or 'montant' not in df.columns:
        raise ValueError("Le DataFrame est vide ou ne contient pas de colonne 'montant'")

    if by == 'categorie':
        if 'categorie' not in df.columns:
            raise ValueError("La colonne 'categorie' n'existe pas dans le DataFrame")
        data = df.groupby('categorie')['montant'].sum()
        title = "Répartition par catégorie"
    else:  # par client
        if 'client' not in df.columns:
            raise ValueError("La colonne 'client' n'existe pas dans le DataFrame")
        data = df.groupby('client')['montant'].sum().nlargest(10)
        title = "Top 10 clients par montant"

    # Vérification qu'il y a des données à afficher
    if data.empty:
        raise ValueError("Aucune donnée à afficher après regroupement")

    # Création explicite de la figure et des axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Camembert (seulement si <= 15 catégories pour lisibilité)
    if len(data) <= 15:
        data.plot.pie(
            autopct=lambda p: f'{p:.1f}%' if p >= 1 else '',
            ax=ax1,
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
            startangle=90
        )
        ax1.set_title(f"{title} (en %)")
        ax1.set_ylabel('')
    else:
        ax1.axis('off')  # Cache le subplot s'il y a trop de catégories

    # Barplot
    data.sort_values(ascending=False).plot.bar(
        ax=ax2,
        color='skyblue'
    )
    ax2.set_title(f"{title} (en valeur absolue)")
    ax2.set_ylabel('Montant total')
    ax2.tick_params(axis='x', rotation=45)

    plt.tight_layout()

    return fig, data.reset_index()
