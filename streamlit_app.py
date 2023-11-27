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


#Import dataset eurostat
import eurostat

nazioni_mapping = {
    'AL': 'Albania',
    'AT': 'Austria',
    'BA': 'Bosnia ed Erzegovina',
    'BE': 'Belgio',
    'BG': 'Bulgaria',
    'CH': 'Svizzera',
    'CY': 'Cipro',
    'CZ': 'Repubblica Ceca',
    'DE': 'Germania',
    'DK': 'Danimarca',
    'EE': 'Estonia',
    'EL': 'Grecia',
    'ES': 'Spagna',
    'FI': 'Finlandia',
    'FR': 'Francia',
    'HR': 'Croazia',
    'HU': 'Ungheria',
    'IE': 'Irlanda',
    'IS': 'Islanda',
    'IT': 'Italia',
    'LT': 'Lituania',
    'LU': 'Lussemburgo',
    'LV': 'Lettonia',
    'ME': 'Montenegro',
    'MK': 'Macedonia del Nord',
    'MT': 'Malta',
    'NL': 'Paesi Bassi',
    'NO': 'Norvegia',
    'PL': 'Polonia',
    'PT': 'Portogallo',
    'RO': 'Romania',
    'RS': 'Serbia',
    'SE': 'Svezia',
    'SI': 'Slovenia',
    'SK': 'Slovacchia',
    'TR': 'Turchia',
    'UK': 'Regno Unito',
    'UKN': 'Irlanda del Nord',
    'UKM': 'Scozia',
    'UKC-L': 'Inghilterra e Galles',
    'LI': 'Liechtenstein',
    'EU_V': 'Unione Europea'
}

# Ottieni il dataset Eurostat
data = eurostat.get_data_df('crim_hom_vrel', True)

data.columns = data.columns.str.replace('_value', '')

# Usa la funzione melt per "sciogliere" il DataFrame
dataset_eurostat = pd.melt(data, id_vars=['freq', 'pers_cat', 'sex', 'unit', 'geo\\TIME_PERIOD'],
                           var_name='anno', value_name='valore')

# Sostituisci i valori specifici con etichette desiderate
dataset_eurostat['pers_cat'] = dataset_eurostat['pers_cat'].replace({'IPTN_FAM': 'Partner o familiare',

                                                                     'FAM': 'Familiare',

                                                                     'IPTN': 'Partner'})
dataset_eurostat = dataset_eurostat.rename(
    columns={'pers_cat': 'Omicida', 'sex': 'Sesso della vittima', 'unit': 'Unità', 'geo\TIME_PERIOD': 'Nazione',
             'anno': 'Anno', 'valore': 'Omicidi'})
dataset_eurostat = dataset_eurostat.dropna()

# Filtra le righe in cui la colonna dell'anno contiene la scritta "_flag"
dataset_eurostat = dataset_eurostat[~dataset_eurostat['Anno'].str.contains('_flag')]
data.columns = data.columns.str.replace('_value', '')

dataset_eurostat['Unità'] = dataset_eurostat['Unità'].replace({'NR': 'Valori assoluti',

                                                               'P_HTHAB': 'Valori per centomila abitanti'

                                                               })
dataset_eurostat['Nazione'] = dataset_eurostat['Nazione'].replace(nazioni_mapping)

# Visualizza il DataFrame melted


# Crea l'app Streamlit
st.title('Omicidi in Italia, analisi sui femminicidi')
st.write("Questa analisi si basa sugli omicidi in Italia in relazione alla vittima. L'obiettivo è quello di comprendere il fenomeno dei femminicidi")
st.write("L'Istituto europeo per l'uguaglianza di genere evidenzia la mancanza di una definizione comune di femminicidio tra gli Stati membri dell'UE e nella letteratura scientifica. Questa mancanza crea difficoltà nella raccolta di dati precisi. La Commissione statistica delle Nazioni Unite ha definito i femminicidi come omicidi volontari di donne in quanto tali. La raccolta accurata di dati su questo fenomeno rimane un'impresa complessa e le dichiarazioni basate su numeri devono considerare attentamente la definizione adottata. La Commissione statistica delle [Nazioni Unite](https://www.istat.it/it/files//2018/04/Statistical_framework_femicide_2022.pdf#page=14) identifica tre categorie di femminicidi: omicidi da partner o ex partner, da un parente, e quelli con specifiche motivazioni di genere, come violenze precedenti o sfruttamento. Questa classificazione mira a fornire un quadro completo e affidabile sul fenomeno, essenziale per valutare le dichiarazioni politiche sull'argomento. Purtroppo i dati ISTAT possono solo fornirci una parte dei dati relativi al fenomeno.")
# URL dell'immagine
image_url = "https://private-user-images.githubusercontent.com/143170925/285752293-c4a36380-f88d-4ab3-b96a-3bfd4015de54.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTEiLCJleHAiOjE3MDEwNjk2MjYsIm5iZiI6MTcwMTA2OTMyNiwicGF0aCI6Ii8xNDMxNzA5MjUvMjg1NzUyMjkzLWM0YTM2MzgwLWY4OGQtNGFiMy1iOTZhLTNiZmQ0MDE1ZGU1NC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBSVdOSllBWDRDU1ZFSDUzQSUyRjIwMjMxMTI3JTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDIzMTEyN1QwNzE1MjZaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT1kODI1OTc2NzNmZTZlMDk2NTRmNzQ5OTkwMDdhNzU4YTQ0NTMxZjBlMDVkYmRkMjMwY2MyNWY0M2JmOTY4N2JmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCZhY3Rvcl9pZD0wJmtleV9pZD0wJnJlcG9faWQ9MCJ9.WnvUaTlWLpu7hVNjXJwYmEq8Oc4K1So-05UUlZqQD9k"

# Mostra l'immagine in Streamlit
st.image(image_url, caption='Gli omicidi con vittime femminili sono suddivisi in tre categorie - Fonte: Commissione statistica delle Nazioni Unite', use_column_width=True)

st.write("I dati sono estratti dalla relazione dell'Istituto Nazionale di Statistica ([ISTAT](https://www.istat.it/it/files//2018/04/omicidi-relazione-autore-DCPC-anni-2002-2021_v.3.xlsx)).")
st.write("Puoi scaricare i dataset già puliti utilizzati in questa visualizzazione dal pulsante apposito")


# Aggiungi le tabelle
tab1, tab2, tab3, tab4 = st.tabs(["Confronto fra Uomo e Donna per relazione con la vittima", "Omicidi per relazione con la vittima", 'Confronto Europa', "Dataset"])

with tab4:
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

    st.header('Omicidi in relazione alla vittima - Eurostat')
    st.table(dataset_eurostat)
    st.download_button("Download dataset Eurostat", dataset_eurostat.to_csv(index=False).encode('utf-8'), 'dataset_eurostat.csv',
                       'text/csv')



    # Aggiungi link di riferimento a ISTAT
    st.write("Per ulteriori dettagli e analisi approfondite, consulta la relazione completa di ISTAT:")
    st.markdown("[ISTAT - Relazione sugli omicidi in Italia](https://www.istat.it/)")


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
    fig_totale = px.bar(totale, x=totale.index, y="value", color="Relazione vittima-omicida", title="Totale omicidi",  labels={'index': 'Anno', 'value': 'Omicidi'})

    # Mostra il grafico con Streamlit
    st.plotly_chart(fig_totale)
    # Crea il grafico a barre impilate con Plotly Express
    fig_uomo = px.bar(uomo, x=uomo.index, y="value", color="Relazione vittima-omicida", title="Totale omicidi - Vittima uomo", labels={'index': 'Anno', 'value': 'Omicidi'},)

    # Mostra il grafico con Streamlit
    st.plotly_chart(fig_uomo)

    # Crea il grafico a barre impilate con Plotly Express
    fig_donna = px.bar(donna, x=donna.index, y="value", color="Relazione vittima-omicida", title="Totale omicidi - Vittima donna", labels={'index': 'Anno', 'value': 'Omicidi'},)

    # Mostra il grafico con Streamlit
    st.plotly_chart(fig_donna)

with tab3:
    st.write("In questa sezione puoi visualizzare i dati realtivi agli omicidi per genere e relazione con la vittima in Europa")
    eurostat_filtrato_donna=dataset_eurostat.copy()
    eurostat_filtrato_donna=  eurostat_filtrato_donna[eurostat_filtrato_donna['Sesso della vittima'].isin(['F'])]
    eurostat_filtrato_donna = eurostat_filtrato_donna[eurostat_filtrato_donna['Unità'].isin(['Valori assoluti'])]
    eurostat_filtrato_donna = eurostat_filtrato_donna[eurostat_filtrato_donna['Omicida'].isin(['Partner'])]
    fig_eurostat_donna = px.bar(eurostat_filtrato_donna, x='Anno', y='Omicidi', color='Nazione',
                          labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                          title='Omicidi commessi dal partner, sesso della vittima = Donna',
                          hover_data=['Nazione', 'Sesso della vittima', 'Unità'])

    # Visualizza il diagramma
    st.plotly_chart(fig_eurostat_donna)

    eurostat_filtrato_uomo = dataset_eurostat.copy()
    eurostat_filtrato_uomo = eurostat_filtrato_uomo[eurostat_filtrato_uomo['Sesso della vittima'].isin(['M'])]
    eurostat_filtrato_uomo = eurostat_filtrato_uomo[eurostat_filtrato_uomo['Unità'].isin(['Valori assoluti'])]
    eurostat_filtrato_uomo = eurostat_filtrato_uomo[eurostat_filtrato_uomo['Omicida'].isin(['Partner'])]
    fig_eurostat_uomo = px.bar(eurostat_filtrato_uomo, x='Anno', y='Omicidi', color='Nazione',
                                labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                                title='Omicidi commessi dal partner sesso della vittima = Uomo',
                                hover_data=['Nazione', 'Sesso della vittima', 'Unità'])

    # Visualizza il diagramma
    st.plotly_chart(fig_eurostat_uomo)

    fig_eurostat_donna_anno = px.bar(eurostat_filtrato_donna, x='Nazione', y='Omicidi', color='Anno',
                          labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                          title='Omicidi per nazione commessi dal partner sesso della vittima = Donna',
                          hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_donna_anno)

    fig_eurostat_uomo_anno = px.bar(eurostat_filtrato_uomo, x='Nazione', y='Omicidi', color='Anno',
                                     labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                                     title='Omicidi per nazione commessi dal partner sesso della vittima = Uomo',
                                     hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_uomo_anno)

    eurostat_filtrato_donna_centomila = dataset_eurostat.copy()
    eurostat_filtrato_donna_centomila = eurostat_filtrato_donna_centomila[eurostat_filtrato_donna_centomila['Sesso della vittima'].isin(['F'])]
    eurostat_filtrato_donna_centomila = eurostat_filtrato_donna_centomila[
    eurostat_filtrato_donna_centomila['Unità'].isin(['Valori per centomila abitanti'])]
    eurostat_filtrato_donna_centomila = eurostat_filtrato_donna_centomila[eurostat_filtrato_donna_centomila['Omicida'].isin(['Partner'])]

    fig_eurostat_donna_cento = px.bar(eurostat_filtrato_donna_centomila, x='Anno', y='Omicidi', color='Nazione',
                          labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                          title='Omicidi commessi dal partner sesso della vittima = Donna - Dati per centomila abitanti',
                          hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_donna_cento)

    eurostat_filtrato_uomo_centomila = dataset_eurostat.copy()
    eurostat_filtrato_uomo_centomila = eurostat_filtrato_uomo_centomila[eurostat_filtrato_uomo_centomila['Sesso della vittima'].isin(['U'])]
    eurostat_filtrato_uomo_centomila = eurostat_filtrato_uomo_centomila[eurostat_filtrato_uomo_centomila['Unità'].isin(['Valori per centomila abitanti'])]
    eurostat_filtrato_uomo_centomila = eurostat_filtrato_uomo_centomila[eurostat_filtrato_uomo_centomila['Omicida'].isin(['Partner'])]

    fig_eurostat_uomo_cento = px.bar(eurostat_filtrato_donna_centomila, x='Anno', y='Omicidi', color='Nazione',
                                      labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                                      title='Omicidi commessi dal partner sesso della vittima = Uomo - Dati per centomila abitanti',
                                      hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_uomo_cento)

    fig_eurostat_donna_cento_nazione = px.bar(eurostat_filtrato_donna_centomila, x='Nazione', y='Omicidi', color='Anno',
                                      labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                                      title='Omicidi per nazione commessi dal partner sesso della vittima = Donna - Dati per centomila abitanti',
                                      hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_donna_cento_nazione)

    fig_eurostat_uomo_cento_nazione = px.bar(eurostat_filtrato_donna_centomila, x='Nazione', y='Omicidi', color='Anno',
                                      labels={'Valore': 'Omicidi', 'Anno': 'Anno di riferimento'},
                                      title='Omicidi commessi dal partner sesso della vittima = Uomo - Dati per centomila abitanti',
                                      hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_uomo_cento_nazione)

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
        title="Totale omicidi per relazione e sesso",
        labels={'index': 'Anno', 'value': 'Omicidi'},
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
st.write("La documentazione completa è disponibile [qui](https://github.com/DrElegantia/femminicidi_italia/tree/main).")
