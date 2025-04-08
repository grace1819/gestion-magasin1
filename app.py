import streamlit as st
import pandas as pd
from datetime import datetime
import io
import matplotlib.pyplot as plt
import seaborn as sns
from db_config import init_db, connect_db
from data_operations import get_ventes, get_produits, get_clients, insert_vente, insert_produit, insert_client
from visualizations import plot_ventes_par_periode, plot_top_produits, plot_repartition

# Initialisation de la base de données
init_db()


# --- Fonctions utilitaires ---
@st.cache_data
def convert_to_excel(df):
    """Convertit un DataFrame en fichier Excel pour le téléchargement"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output


def login():
    """Gère l'authentification"""
    st.sidebar.subheader("Connexion Admin")
    user = st.sidebar.text_input("Nom d'utilisateur")
    password = st.sidebar.text_input("Mot de passe", type="password")
    if st.sidebar.button("Se connecter"):
        if user == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.sidebar.error("Identifiants invalides")


# --- Application principale ---
def main():
    st.set_page_config(page_title="Analyse des Ventes", layout="wide")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
        return

    st.title("📊 Dashboard Analyse des Ventes")

    # Onglets
    tabs = ["📈 Tableau de bord", "➕ Ajouter des données", "🔍 Analyse approfondie"]
    selected_tab = st.sidebar.radio("Navigation", tabs)

    # Récupération des données
    df_ventes = get_ventes()
    df_produits = get_produits()
    df_clients = get_clients()

    # Filtres communs
    with st.sidebar:
        st.header("🔍 Filtres")

        # Filtre de date - Version sécurisée
        try:
            df_ventes['date_vente'] = pd.to_datetime(df_ventes['date_vente'], errors='coerce')
            df_ventes = df_ventes.dropna(subset=['date_vente'])

            if not df_ventes.empty:
                min_date = df_ventes['date_vente'].min().date()
                max_date = df_ventes['date_vente'].max().date()
            else:
                min_date = datetime.now().date() - pd.Timedelta(days=30)
                max_date = datetime.now().date()
                st.warning("Aucune donnée de vente disponible. Période par défaut utilisée.")
        except Exception as e:
            st.error(f"Erreur de traitement des dates : {str(e)}")
            min_date = datetime.now().date() - pd.Timedelta(days=30)
            max_date = datetime.now().date()

        date_range = st.date_input("Période", [min_date, max_date])

        if not df_ventes.empty:
            selected_cat = st.multiselect("Catégories", df_ventes["categorie"].unique())
            selected_prod = st.multiselect("Produits", df_ventes["produit"].unique())
            selected_client = st.multiselect("Clients", df_ventes["client"].dropna().unique())
        else:
            selected_cat = []
            selected_prod = []
            selected_client = []
            st.warning("Aucune donnée disponible pour les filtres")

    # Application des filtres
    filtered_df = df_ventes.copy()

    if len(date_range) == 2 and not df_ventes.empty:
        try:
            filtered_df = filtered_df[
                (filtered_df['date_vente'].dt.date >= date_range[0]) &
                (filtered_df['date_vente'].dt.date <= date_range[1])
                ]
        except Exception as e:
            st.error(f"Erreur lors du filtrage par date : {str(e)}")
            filtered_df = df_ventes.copy()

    if selected_cat:
        filtered_df = filtered_df[filtered_df["categorie"].isin(selected_cat)]
    if selected_prod:
        filtered_df = filtered_df[filtered_df["produit"].isin(selected_prod)]
    if selected_client:
        filtered_df = filtered_df[filtered_df["client"].isin(selected_client)]

    # Onglet Tableau de bord
    if selected_tab == tabs[0]:
        # KPI
        total_ventes = filtered_df['montant'].sum()
        total_quantite = filtered_df['quantite'].sum()
        avg_vente = filtered_df['montant'].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total ventes", f"{total_ventes:,.2f} €")
        col2.metric("📦 Quantité vendue", f"{total_quantite:,}")
        col3.metric("📊 Moyenne par vente", f"{avg_vente:,.2f} €")

        st.subheader("📈 Données filtrées")
        st.dataframe(filtered_df, height=300)

        st.download_button(
            "📥 Exporter Excel",
            convert_to_excel(filtered_df),
            file_name="ventes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Visualisations rapides
        st.subheader("📊 Aperçu des ventes")

        if filtered_df.empty:
            st.warning("⚠️ Aucune donnée disponible avec les filtres actuels.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Montant des ventes par produit**")
                fig, ax = plt.subplots(figsize=(8, 4))
                try:
                    sns.barplot(
                        data=filtered_df,
                        x="produit",
                        y="montant",
                        estimator=sum,
                        ci=None,
                        ax=ax,
                        palette="viridis"
                    )
                    plt.xticks(rotation=45)
                    ax.set_ylabel("Montant total (€)")
                    ax.set_xlabel("")

                    for p in ax.patches:
                        ax.annotate(
                            f"{p.get_height():.2f}€",
                            (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center',
                            va='center',
                            xytext=(0, 5),
                            textcoords='offset points'
                        )

                    st.pyplot(fig)
                    plt.close(fig)  # Fermeture explicite de la figure
                except Exception as e:
                    st.error(f"Erreur lors de la génération du graphique : {str(e)}")

            with col2:
                st.markdown("**Quantité vendue par produit**")
                fig, ax = plt.subplots(figsize=(8, 4))
                try:
                    sns.barplot(
                        data=filtered_df,
                        x="produit",
                        y="quantite",
                        estimator=sum,
                        ci=None,
                        ax=ax,
                        palette="magma"
                    )
                    plt.xticks(rotation=45)
                    ax.set_ylabel("Quantité totale")
                    ax.set_xlabel("")

                    for p in ax.patches:
                        ax.annotate(
                            f"{int(p.get_height())}",
                            (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center',
                            va='center',
                            xytext=(0, 5),
                            textcoords='offset points'
                        )

                    st.pyplot(fig)
                    plt.close(fig)  # Fermeture explicite de la figure
                except Exception as e:
                    st.error(f"Erreur lors de la génération du graphique : {str(e)}")

    # Onglet Ajout de données
    elif selected_tab == tabs[1]:
        st.subheader("Ajouter de nouvelles données")

        tab1, tab2, tab3 = st.tabs(["➕ Nouvelle vente", "🆕 Nouveau produit", "👤 Nouveau client"])

        with tab1:
            with st.form("form_vente"):
                col1, col2 = st.columns(2)

                with col1:
                    date = st.date_input("Date de vente", value=datetime.now())

                    if not df_produits.empty:
                        produit_id = st.selectbox(
                            "Produit",
                            options=df_produits['id'],
                            format_func=lambda
                                x: f"{df_produits[df_produits['id'] == x]['nom'].iloc[0]} - {df_produits[df_produits['id'] == x]['categorie'].iloc[0]}"
                            if not df_produits[df_produits['id'] == x].empty else "Produit inconnu"
                        )
                    else:
                        st.warning("Aucun produit disponible.")
                        produit_id = None

                    client_options = [None]
                    if not df_clients.empty:
                        client_options += df_clients['id'].tolist()

                    client_id = st.selectbox(
                        "Client (optionnel)",
                        options=client_options,
                        format_func=lambda x: df_clients[df_clients['id'] == x]['nom'].iloc[0]
                        if x and not df_clients[df_clients['id'] == x].empty else "Aucun"
                    )

                with col2:
                    quantite = st.number_input("Quantité", min_value=1, step=1)

                    if produit_id is not None and not df_produits.empty:
                        produit_data = df_produits[df_produits['id'] == produit_id]
                        if not produit_data.empty:
                            prix_unitaire = produit_data['prix_unitaire'].iloc[0]
                            montant = quantite * prix_unitaire
                            st.metric("Prix unitaire", f"{prix_unitaire:,.2f} €")
                            st.metric("Montant total", f"{montant:,.2f} €")
                        else:
                            st.warning("Produit non trouvé")
                            montant = 0
                    else:
                        montant = 0

                submit = st.form_submit_button("Enregistrer la vente")
                if submit:
                    if produit_id is not None and montant > 0:
                        insert_vente(date, produit_id, client_id, quantite, montant)
                        st.success("✅ Vente enregistrée avec succès !")
                        st.rerun()
                    else:
                        st.error("Veuillez sélectionner un produit valide")

        with tab2:
            with st.form("form_produit"):
                nom = st.text_input("Nom du produit")
                categorie = st.text_input("Catégorie")
                prix_unitaire = st.number_input("Prix unitaire", min_value=0.01, step=0.01, format="%.2f")

                submit = st.form_submit_button("Ajouter le produit")
                if submit:
                    if nom and categorie and prix_unitaire:
                        insert_produit(nom, categorie, prix_unitaire)
                        st.success("✅ Produit ajouté avec succès !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs")

        with tab3:
            with st.form("form_client"):
                nom = st.text_input("Nom complet")
                email = st.text_input("Email")
                telephone = st.text_input("Téléphone")

                submit = st.form_submit_button("Ajouter le client")
                if submit:
                    if nom and email:
                        insert_client(nom, email, telephone)
                        st.success("✅ Client ajouté avec succès !")
                        st.rerun()
                    else:
                        st.error("Veuillez au moins remplir le nom et l'email")

    # Onglet Analyse approfondie
    elif selected_tab == tabs[2]:
        st.subheader("Analyse approfondie des ventes")

        analysis_type = st.radio(
            "Type d'analyse",
            ["📅 Par période", "🏆 Top produits", "📊 Répartition"],
            horizontal=True
        )

        if analysis_type == "📅 Par période":
            periode = st.selectbox("Période", ["Mensuel", "Trimestriel", "Annuel"])
            fig, df_period = plot_ventes_par_periode(filtered_df, periode)
            st.pyplot(fig)
            plt.close(fig)
            st.dataframe(df_period)

        elif analysis_type == "🏆 Top produits":
            top_n = st.slider("Nombre de produits à afficher", 3, 10, 5)
            fig, df_top = plot_top_produits(filtered_df, top_n)
            st.pyplot(fig)
            plt.close(fig)
            st.dataframe(df_top)

        elif analysis_type == "📊 Répartition":
            repartition_type = st.radio(
                "Type de répartition",
                ["Par catégorie", "Par client"],
                horizontal=True
            )

            if filtered_df.empty or 'montant' not in filtered_df.columns:
                st.warning("⚠️ Pas de données disponibles ou colonne 'montant' manquante.")
            else:
                try:
                    by_type = 'categorie' if repartition_type == "Par catégorie" else 'client'
                    fig, df_repartition = plot_repartition(filtered_df, by=by_type)
                    st.pyplot(fig)
                    plt.close(fig)
                    st.dataframe(df_repartition)

                except ValueError as ve:
                    st.error(f"Erreur : {str(ve)}")


if __name__ == "__main__":
    main()


