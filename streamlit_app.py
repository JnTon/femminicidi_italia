import pandas as pd
import ssl
import streamlit as st
import plotly.express as px

import requests
import zipfile
from io import BytesIO


# Disabilita la verifica del certificato SSL (NON consigliato in produzione)
ssl._create_default_https_context = ssl._create_unverified_context
# Definisci il percorso del file Excel
percorso_file = 'https://www.istat.it/it/files//2018/04/omicidi-relazione-autore-DCPC-anni-2002-2021_v.3.xlsx'


def pulisci_dataframe(df):
    df.dropna(inplace=True)
    df.reset_index(inplace=True)
    del df['index']
    df = df.iloc[0:6]
    df.columns = df.columns.astype(str)
    return df

# Leggi il file Excel per il totale
totale = pd.read_excel(percorso_file, skiprows=3)

# Leggi il file Excel per l'uomo
uomo = pd.read_excel(percorso_file, sheet_name=1, skiprows=3)


# Leggi il file Excel per la donna
donna = pd.read_excel(percorso_file, sheet_name=2, skiprows=3)


# Pulizia dei dati per i dataframe totale, uomo, donna
totale = pulisci_dataframe(totale)
uomo = pulisci_dataframe(uomo)
donna = pulisci_dataframe(donna)

def rinomina_colonne(df, nuova_colonna):
    df = df.rename(columns={"RELAZIONE DELLA VITTIMA CON L'OMICIDA": nuova_colonna})
    return df

# Rinomina le colonne
donna = rinomina_colonne(donna, 'Relazione vittima-omicida')
uomo = rinomina_colonne(uomo, 'Relazione vittima-omicida')
totale = rinomina_colonne(totale, 'Relazione vittima-omicida')


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
    'EU_V': 'Unione Europea',
    'XK': 'Kosovo'
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

#daataset reati da eurostat

violenze = eurostat.get_data_df('crim_hom_soff', True)
violenze.columns = violenze.columns.str.replace('_value', '')


violenze = pd.melt(violenze, id_vars=['freq', 'iccs', 'leg_stat', 'sex', 'unit', 'geo\TIME_PERIOD'], var_name='anno', value_name='valore')

violenze['geo\TIME_PERIOD'] = violenze['geo\TIME_PERIOD'].replace(nazioni_mapping)
violenze=violenze.dropna()

violenze['iccs'] = violenze['iccs'].replace({'ICCS0101': 'Omicidio intenzionale',
                                             'ICCS03011': 'Stupro',
                                             'ICCS03012': 'Violenza sessuale'})

violenze['leg_stat'] = violenze['leg_stat'].replace({'PER_CNV': 'Persona condannata',
                                             'PER_PRSC': 'Persona perseguita',
                                             'PER_SUSP': 'Persona sospettata',
                                              'PER_VICT': 'Vittima'})
violenze = violenze.rename(
    columns={'iccs': 'ICCS - categorie di reato', 'leg_stat':'Stato', 'sex': 'Sesso della vittima', 'unit': 'Unità', 'geo\TIME_PERIOD': 'Nazione',
             'anno': 'Anno', 'valore': 'Omicidi'})
violenze = violenze[~violenze['Anno'].str.contains('_flag')]
violenze.columns = violenze.columns.str.replace('_value', '')

violenze['Unità'] = violenze['Unità'].replace({'NR': 'Valori assoluti',

                                                               'P_HTHAB': 'Valori per centomila abitanti'

                                                               })

violenze_vittima = violenze[violenze['Stato'].isin(['Vittima'])]
violenze_vittima_ass = violenze_vittima[violenze_vittima['Unità'].isin(['Valori assoluti'])]
violenze_vittima_rel = violenze_vittima[violenze_vittima['Unità'].isin(['Valori per centomila abitanti'])]

# Crea l'app Streamlit
st.title('Omicidi in Italia, analisi sui femminicidi')
st.write("Questa analisi si basa sugli omicidi in Italia in relazione alla vittima. L'obiettivo è quello di comprendere il fenomeno dei femminicidi")
st.write("L'Istituto europeo per l'uguaglianza di genere evidenzia la mancanza di una definizione comune di femminicidio tra gli Stati membri dell'UE e nella letteratura scientifica. Questa mancanza crea difficoltà nella raccolta di dati precisi. La Commissione statistica delle Nazioni Unite ha definito i femminicidi come omicidi volontari di donne in quanto tali. La raccolta accurata di dati su questo fenomeno rimane un'impresa complessa e le dichiarazioni basate su numeri devono considerare attentamente la definizione adottata. La Commissione statistica delle [Nazioni Unite](https://www.istat.it/it/files//2018/04/Statistical_framework_femicide_2022.pdf#page=14) identifica tre categorie di femminicidi: omicidi da partner o ex partner, da un parente, e quelli con specifiche motivazioni di genere, come violenze precedenti o sfruttamento. Questa classificazione mira a fornire un quadro completo e affidabile sul fenomeno, essenziale per valutare le dichiarazioni politiche sull'argomento. Purtroppo i dati ISTAT possono solo fornirci una parte dei dati relativi al fenomeno.")
# URL dell'immagine
image_url = "https://cdn.pagellapolitica.it/wp-content/uploads/2023/11/Screenshot-2023-11-21-alle-10.06.56-1024x695.png"

# Mostra l'immagine in Streamlit
st.image(image_url, caption='Gli omicidi con vittime femminili sono suddivisi in tre categorie - Fonte: Commissione statistica delle Nazioni Unite', use_column_width=True)

st.write("I dati sono estratti dalla relazione dell'Istituto Nazionale di Statistica ([ISTAT](https://www.istat.it/it/files//2018/04/omicidi-relazione-autore-DCPC-anni-2002-2021_v.3.xlsx)).")
st.write("Puoi scaricare i dataset già puliti utilizzati in questa visualizzazione dal pulsante apposito")

# URL del file Excel
url = "https://www.istat.it/it/files//2011/04/tavole.zip"

# Effettua la richiesta per ottenere il contenuto del file ZIP
response = requests.get(url)
with zipfile.ZipFile(BytesIO(response.content), "r") as zip_ref:
    # Nome del file Excel nel terzo foglio
    excel_filename = "tavole.xls"
    # Leggi il terzo foglio del file Excel
    suicidi = pd.read_excel(zip_ref.read(excel_filename), sheet_name=2, skiprows=2)
suicidi=suicidi.dropna()


renamed_s = {
    'Unnamed: 0': 'Anno',
    'Suicidi': 'Suicidi M',
    'Unnamed: 2': 'Suicidi F',
    'Unnamed: 3': 'Suicidi totali',
    'Tentativi di suicidio': 'Tentativi di suicidio M',
    'Unnamed: 5': 'Tentativi di suicidio F',
    'Unnamed: 6': 'Tentativi di suicidio totali'
}

# Rinomina le colonne utilizzando il metodo "rename"
suicidi.rename(columns=renamed_s, inplace=True)
suicidi=suicidi.loc[0:6]
suicidi['Suicidi / tentativi di suicidio F']=suicidi['Suicidi F']/(suicidi['Tentativi di suicidio F']+suicidi['Suicidi F'])*100
suicidi['Suicidi / tentativi di suicidio M']=suicidi['Suicidi M']/(suicidi['Tentativi di suicidio M']+suicidi['Suicidi F'])*100


# Aggiungi le tabelle
tab1, tab2, tab6, tab3, tab5, tab4 = st.tabs(["Confronto fra Uomo e Donna per relazione con la vittima", "Omicidi per relazione con la vittima", 'Suicidi', 'Confronto Europa', 'Reati sessuali', "Dataset"])

with tab6:
    st.write('In questa tab vengono rappresentati i casi di suicidio e i tentatativi di suicidio. La serie storica si interrompe al 2009.')
    st.write('[Dataset ISTAT](https://www.istat.it/it/files//2011/04/tavole.zip)')
    fig_suicidi_ass = px.line(suicidi,
                              x="Anno",
                              y=['Suicidi totali', 'Suicidi F', 'Suicidi M'],
                              title='Suicidi per genere - Italia',
                              labels={'variable': 'Genere', 'Value': 'Suicidi', 'value': 'Suicidi'},
                              color_discrete_map={
                                  'Suicidi totali': 'green',
                                  'Suicidi M': 'blue',
                                  'Suicidi F': 'red'
                              },
                              range_y=[0, suicidi[['Suicidi totali', 'Suicidi F', 'Suicidi M']].max().max()]

                              )

    st.plotly_chart(fig_suicidi_ass)

    fig_tentativi_suicidio = px.line(suicidi,
                          x="Anno",
                          y=['Tentativi di suicidio F', 'Tentativi di suicidio M'],
                          title='Tentativi di suicidio - Italia',
                          labels={'variable': 'Genere', 'value': 'Tentativi', 'Value': 'Tentativi'},
                                     color_discrete_map={
                                         'Suicidi totali': 'green',
                                         'Tentativi di suicidio M': 'blue',
                                         'Tentativi di suicidio F': 'red'
                                     },
                            range_y = [0, suicidi[['Tentativi di suicidio F', 'Tentativi di suicidio M']].max().max()]
                                     )
    st.plotly_chart(fig_tentativi_suicidio)

    fig_suicidi_ratio = px.line(suicidi,
                          x="Anno",
                          y=['Suicidi / tentativi di suicidio F', 'Suicidi / tentativi di suicidio M'],
                          title='Rapporto fra suicidi e tentativi di suicidio per genere',
                          labels={'variable': 'Genere', 'value': 'Rapporto'},
                                color_discrete_map={
                                    'Suicidi totali': 'green',
                                    'Suicidi / tentativi di suicidio M': 'blue',
                                    'Suicidi / tentativi di suicidio F': 'red'
                                },
                                range_y=[0, suicidi[['Suicidi / tentativi di suicidio F', 'Suicidi / tentativi di suicidio M']].max().max()]
                                )
    st.plotly_chart(fig_suicidi_ratio)

with tab5:

    # Descrizione generica dei reati
    generic_description = (
        "I reati inclusi in questo dataset sono categorizzati "
        "conformemente agli standard internazionali ICCS. L'omicidio intenzionale rappresenta l'atto intenzionale di causare "
        "la morte di un'altra persona. Il reato di stupro coinvolge l'atto sessuale non consensuale, mentre la violenza "
        "sessuale comprende varie forme di assalto di natura sessuale."
    )

    st.write("Descrizione generica dei reati:")
    st.write(generic_description)

    # Aggiunta di una descrizione al dataset
    dataset_link = "https://db.nomics.world/Eurostat/crim_hom_soff?offset=10&tab=table"
    st.write(f"Il dataset è stato filtrato per lo status della vittima. [Link al dataset]({dataset_link})")
    st.write(
        "([Per saperne di più riguardo alla categorizzazione dei reati si rinvia alla documentazione](https://ec.europa.eu/eurostat/documents/64346/2989606/Methodological+guide+for+users/bfd3bb4a-67b7-44de-860e-cb911df9e17a))")

    fig_violenze_vittima_ass = px.bar(
        violenze_vittima_ass,
        x=violenze_vittima_ass.Anno,
        y="Omicidi",
        color="ICCS - categorie di reato",
        facet_col="Sesso della vittima",  # Aggiungi una suddivisione in colonne
        title="Reati sessuali e omicidi per genere - Valori assoluti",
        labels={'index': 'Anno', 'Omicidi': 'Reati'},
        hover_data=['Nazione', 'Sesso della vittima', 'Unità']
    )
    st.plotly_chart(fig_violenze_vittima_ass)

    violenze_vittima_ass_naz=violenze_vittima_ass[violenze_vittima_ass['ICCS - categorie di reato'].isin(['Stupro','Violenza sessuale'])]

    fig_violenze_vittima_ass_naz = px.bar(
        violenze_vittima_ass_naz,
        x='Anno',
        y="Omicidi",
        color="Nazione",
        facet_col="Sesso della vittima",
        facet_row="ICCS - categorie di reato",# Aggiungi una suddivisione in colonne
        title="Reati sessuali (Stupro e Violenza sessuale) per nazione e genere - Valori assoluti",
        labels={'index': 'Anno', 'Omicidi': 'Reati'},
        hover_data=['ICCS - categorie di reato', 'Sesso della vittima', 'Unità', "Omicidi",]
    )
    fig_violenze_vittima_ass_naz.update_layout(
        height=800,  # Imposta l'altezza desiderata in pixel
        width=800  # Imposta la larghezza desiderata in pixel
    )

    st.plotly_chart(fig_violenze_vittima_ass_naz)

    fig_violenze_vittima_rel = px.bar(
        violenze_vittima_rel,
        x=violenze_vittima_rel.Anno,
        y="Omicidi",
        color="ICCS - categorie di reato",
        facet_col="Sesso della vittima",  # Aggiungi una suddivisione in colonne
        title="Reati sessuali e omicidi per genere - Valori relativi",
        labels={'index': 'Anno', 'Omicidi': 'Reati per centomila abitanti'},
        hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_violenze_vittima_rel)

    violenze_vittima_rel_naz=violenze_vittima_rel[violenze_vittima_rel['ICCS - categorie di reato'].isin(['Stupro','Violenza sessuale'])]

    fig_violenze_vittima_rel_naz = px.bar(
        violenze_vittima_rel_naz,
        x='Anno',
        y="Omicidi",
        color="Nazione",
        facet_col="Sesso della vittima",
        facet_row="ICCS - categorie di reato",# Aggiungi una suddivisione in colonne
        title="Reati sessuali (Stupro e Violenza sessuale) per nazione e genere - Valori relativi",
        labels={'index': 'Anno', 'Omicidi': 'Reati'},
        hover_data=['ICCS - categorie di reato', 'Sesso della vittima', 'Unità', "Omicidi",]
    )
    fig_violenze_vittima_rel_naz.update_layout(
        height=800,  # Imposta l'altezza desiderata in pixel
        width=800  # Imposta la larghezza desiderata in pixel
    )

    st.plotly_chart(fig_violenze_vittima_rel_naz)


with tab4:
    st.write("In questa sezione puoi visualizzare e scaricare i dataset")
    st.header('Dati totali sugli omicidi in Italia')
    st.table(totale)
    st.download_button("Download dataset totale", totale.to_csv(index=False).encode('utf-8'), 'dataset_totale.csv', 'text/csv')

    st.header('Omicidi in relazione alla vittima in Italia - Uomo')
    st.table(uomo)
    st.download_button("Download dataset uomo", uomo.to_csv(index=False).encode('utf-8'), 'dataset_uomo.csv', 'text/csv')

    st.header('Omicidi in relazione alla vittima in Italia - Donna')
    st.table(donna)
    st.download_button("Download dataset donna", donna.to_csv(index=False).encode('utf-8'), 'dataset_donna.csv', 'text/csv')

    st.header('Omicidi in relazione alla vittima - Eurostat')
    st.dataframe(dataset_eurostat)
    st.download_button("Download dataset Omicidi in relazione alla vittima - Eurostat", dataset_eurostat.to_csv(index=False).encode('utf-8'), 'dataset_eurostat.csv',
                       'text/csv')
    st.header('Reati sessuali e omicidi - Eurostat')
    st.dataframe(violenze)
    st.download_button("Download dataset Reati sessuali e omicidi - Eurostat", dataset_eurostat.to_csv(index=False).encode('utf-8'), 'dataset_eurostat.csv',
                       'text/csv')

    st.header('Suicidi e tantativi di suicidio')
    st.dataframe(suicidi)
    st.download_button("Download dataset Suicidi e tantativi di suicidio - ISTAT",
                       dataset_eurostat.to_csv(index=False).encode('utf-8'), 'suicidi.csv',
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
                          labels={'Valore': 'Omicidi', 'Nazione': 'Nazione di riferimento'},
                          title='Omicidi per nazione commessi dal partner sesso della vittima = Donna',
                          hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_donna_anno)

    fig_eurostat_uomo_anno = px.bar(eurostat_filtrato_uomo, x='Nazione', y='Omicidi', color='Anno',
                                     labels={'Omicidi': 'Omicidi', 'Nazione': 'Nazione di riferimento'},
                                     title='Omicidi per nazione commessi dal partner sesso della vittima = Uomo',
                                     hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_uomo_anno)

    eurostat_filtrato_donna_centomila = dataset_eurostat.copy()
    eurostat_filtrato_donna_centomila = eurostat_filtrato_donna_centomila[eurostat_filtrato_donna_centomila['Sesso della vittima'].isin(['F'])]
    eurostat_filtrato_donna_centomila = eurostat_filtrato_donna_centomila[
    eurostat_filtrato_donna_centomila['Unità'].isin(['Valori per centomila abitanti'])]
    eurostat_filtrato_donna_centomila = eurostat_filtrato_donna_centomila[eurostat_filtrato_donna_centomila['Omicida'].isin(['Partner'])]

    fig_eurostat_donna_cento = px.bar(eurostat_filtrato_donna_centomila, x='Anno', y='Omicidi', color='Nazione',
                          labels={'Omicidi': 'Omicidi per centomila abitanti', 'Anno': 'Anno di riferimento'},
                          title='Omicidi commessi dal partner sesso della vittima = Donna - Dati per centomila abitanti',
                          hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_donna_cento)

    eurostat_filtrato_uomo_centomila = dataset_eurostat.copy()
    eurostat_filtrato_uomo_centomila = eurostat_filtrato_uomo_centomila[eurostat_filtrato_uomo_centomila['Sesso della vittima'].isin(['M'])]
    eurostat_filtrato_uomo_centomila = eurostat_filtrato_uomo_centomila[eurostat_filtrato_uomo_centomila['Unità'].isin(['Valori per centomila abitanti'])]
    eurostat_filtrato_uomo_centomila = eurostat_filtrato_uomo_centomila[eurostat_filtrato_uomo_centomila['Omicida'].isin(['Partner'])]

    fig_eurostat_uomo_cento = px.bar(eurostat_filtrato_uomo_centomila, x='Anno', y='Omicidi', color='Nazione',
                                      labels={'Omicidi': 'Omicidi per centomila abitanti', 'Anno': 'Anno di riferimento'},
                                      title='Omicidi commessi dal partner sesso della vittima = Uomo - Dati per centomila abitanti',
                                      hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_uomo_cento)

    fig_eurostat_donna_cento_nazione = px.bar(eurostat_filtrato_donna_centomila, x='Nazione', y='Omicidi', color='Anno',
                                      labels={'Omicidi': 'Omicidi per centomila abitanti', 'Nazione': 'Nazionedi riferimento'},
                                      title='Omicidi per nazione commessi dal partner sesso della vittima = Donna - Dati per centomila abitanti',
                                      hover_data=['Nazione', 'Sesso della vittima', 'Unità'])
    st.plotly_chart(fig_eurostat_donna_cento_nazione)

    fig_eurostat_uomo_cento_nazione = px.bar(eurostat_filtrato_uomo_centomila, x='Nazione', y='Omicidi', color='Anno',
                                      labels={'Omicidi': 'Omicidi per centomila abitanti', 'Nazione': 'Nazione di riferimento'},
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
