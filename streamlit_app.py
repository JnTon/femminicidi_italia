import pandas as pd
import ssl
import streamlit as st
import plotly.express as px


# Disabilita la verifica del certificato SSL (NON consigliato in produzione)
ssl._create_default_https_context = ssl._create_unverified_context

# Specifica il percorso del file Excel
percorso_file = 'https://www.istat.it/it/files//2018/04/omicidi-relazione-autore-DCPC-anni-2002-2021_v.3.xlsx'

# Leggi il file Excel saltando le prime tre righe
totale = pd.read_excel(percorso_file, skiprows=3)
totale.dropna(inplace=True)
totale.reset_index(inplace=True)
del totale['index']
totale = totale.iloc[0:6]
totale.columns = totale.columns.astype(str)

# Specifica il percorso del file Excel
percorso_file = 'https://www.istat.it/it/files//2018/04/omicidi-relazione-autore-DCPC-anni-2002-2021_v.3.xlsx'

# Leggi il file Excel saltando le prime tre righe
uomo = pd.read_excel(percorso_file, sheet_name=1, skiprows=3)
uomo.dropna(inplace=True)
uomo.reset_index(inplace=True)
del uomo['index']
uomo=uomo.iloc[0:6]
uomo.columns = totale.columns.astype(str)


# Specifica il percorso del file Excel
percorso_file = 'https://www.istat.it/it/files//2018/04/omicidi-relazione-autore-DCPC-anni-2002-2021_v.3.xlsx'

# Leggi il file Excel saltando le prime tre righe
donna = pd.read_excel(percorso_file, sheet_name=2, skiprows=3)
donna.dropna(inplace=True)
donna.reset_index(inplace=True)
del donna['index']
donna=donna.iloc[0:6]
donna.columns = totale.columns.astype(str)


donna= donna.rename(columns={"RELAZIONE DELLA VITTIMA CON L'OMICIDA": 'Relazione vittima-omicida'})
uomo= uomo.rename(columns={"RELAZIONE DELLA VITTIMA CON L'OMICIDA": 'Relazione vittima-omicida'})
totale= totale.rename(columns={"RELAZIONE DELLA VITTIMA CON L'OMICIDA": 'Relazione vittima-omicida'})
# Crea l'app Streamlit
# Crea l'app Streamlit
st.title('Omicidi in Italia, analisi sui femminicidi')
st.write("Questa analisi si basa sugli omicidi in Italia in relazione alla vittima. L'obiettivo è quello di comprendere il fenomeno dei femminicidi")
st.write("L'Istituto europeo per l'uguaglianza di genere evidenzia la mancanza di una definizione comune di femminicidio tra gli Stati membri dell'UE e nella letteratura scientifica. Questa mancanza crea difficoltà nella raccolta di dati precisi. La Commissione statistica delle Nazioni Unite ha definito i femminicidi come omicidi volontari di donne in quanto tali. La raccolta accurata di dati su questo fenomeno rimane un'impresa complessa e le dichiarazioni basate su numeri devono considerare attentamente la definizione adottata. La Commissione statistica delle [Nazioni Unite](https://www.istat.it/it/files//2018/04/Statistical_framework_femicide_2022.pdf#page=14) identifica tre categorie di femminicidi: omicidi da partner o ex partner, da un parente, e quelli con specifiche motivazioni di genere, come violenze precedenti o sfruttamento. Questa classificazione mira a fornire un quadro completo e affidabile sul fenomeno, essenziale per valutare le dichiarazioni politiche sull'argomento. Purtroppo i dati ISTAT possono solo fornirci una parte dei dati relativi al fenomeno.")
# URL dell'immagine
image_url = "https://cdn.pagellapolitica.it/wp-content/uploads/2023/11/Screenshot-2023-11-21-alle-10.06.56-1024x695.png"

# Mostra l'immagine in Streamlit
st.image(image_url, caption='Caption here', use_column_width=True)

st.write("I dati sono estratti dalla relazione dell'Istituto Nazionale di Statistica ([ISTAT](https://www.istat.it/it/files//2018/04/omicidi-relazione-autore-DCPC-anni-2002-2021_v.3.xlsx)).")
st.write("Puoi scaricare i dataset già puliti utilizzati in questa visualizzazione dal pulsante apposito")


# Aggiungi le tabelle
tab1, tab2, tab3 = st.tabs(["Confronto fra Uomo e Donna per relazione con la vittima", "Omicidi per relazione con la vittima", "Dataset"])

with tab3:
    st.write("In questa sezione puoi visualizzare e scaricare i dataset")
    st.header('Dati totali sugli omicidi in Italia')
    st.table(totale)
    st.download_button("Download dataset totale", totale.to_csv(index=False).encode('utf-8'), 'dataset_totale.csv', 'text/csv')

    st.header('Omicidi in relazione alla vittima - Uomo')
    st.table(uomo)
    st.download_button("Download dataset uomo", uomo.to_csv(index=False).encode('utf-8'), 'dataset_uomo.csv', 'text/csv')

    st.header('Omicidi in relazione alla vittima - Donna')
    st.table(donna)
    st.download_button("Download dataset donna", donna.to_csv(index=False).encode('utf-8'), 'dataset_donna.csv', 'text/csv')

    # Aggiungi link di riferimento a ISTAT
    st.write("Per ulteriori dettagli e analisi approfondite, consulta la relazione completa di ISTAT:")
    st.markdown("[ISTAT - Relazione sugli omicidi in Italia](https://www.istat.it/)")

# ...

# ...
totale.set_index("Relazione vittima-omicida", inplace=True)
totale=totale.T
totale = totale.melt(ignore_index=False)
uomo.set_index("Relazione vittima-omicida", inplace=True)
uomo=uomo.T
uomo = uomo.melt(ignore_index=False)
donna.set_index("Relazione vittima-omicida", inplace=True)
donna=donna.T
donna = donna.melt(ignore_index=False)
with tab2:
    # Crea il grafico a barre impilate con Plotly Express
    st.write("In questa sezione puoi visualizzare i dati realtivi agli omicidi per genere e relazione con la vittima")
    fig_totale = px.bar(totale, x=totale.index, y="value", color="Relazione vittima-omicida", title="Totale omicidi")

    # Mostra il grafico con Streamlit
    st.plotly_chart(fig_totale)
    # Crea il grafico a barre impilate con Plotly Express
    fig_uomo = px.bar(uomo, x=uomo.index, y="value", color="Relazione vittima-omicida", title="Totale omicidi - Vittima uomo")

    # Mostra il grafico con Streamlit
    st.plotly_chart(fig_uomo)

    # Crea il grafico a barre impilate con Plotly Express
    fig_donna = px.bar(donna, x=donna.index, y="value", color="Relazione vittima-omicida", title="Totale omicidi - Vittima donna")

    # Mostra il grafico con Streamlit
    st.plotly_chart(fig_donna)

with tab1:
    st.write("In questa sezione puoi confrontare i dati realtivi agli omicidi per genere e relazione con la vittima")
    donna['Sesso vittima'] = 'Donna'
    uomo['Sesso vittima'] = 'Uomo'
    concatenati = pd.concat([uomo, donna])

    fig_concatenati = px.bar(
        concatenati,
        x=concatenati.index,
        y="value",
        color="Relazione vittima-omicida",
        facet_col="Sesso vittima",  # Aggiungi una suddivisione in colonne
        title="Totale omicidi per relazione e sesso"
    )

    # Mostra il grafico con Streamlit
    st.plotly_chart(fig_concatenati)

# Aggiungi elementi SEO
st.write("""
    <meta name="description" content="Dataset sugli omicidi in Italia in relazione alla vittima. ANalisi sui femminicidi. Dati estratti dalla relazione dell'Istituto Nazionale di Statistica (ISTAT).">
    <meta name="keywords" content="omicidi, Italia, ISTAT, dataset, relazione, vittima, omicida, femminicidi">
    <meta name="author" content="Umberto Bertonelli">
    <link rel="canonical" href="https://umbertobertonelli.it">
""", unsafe_allow_html=True)

# Aggiungi il link al tuo sito
st.write("Questa app è stata creata da [Umberto Bertonelli](https://umbertobertonelli.it).")
