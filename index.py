import pickle
import Corpus
from importlib import reload
# import numpy as np
# import pandas as pd
from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from datetime import datetime

reload(Corpus) # Reload the module to ensure that the latest changes are used

app = Dash(__name__)    # Create a Dash instance
# Ouverture du fichier, puis lecture avec pickle
with open("./data/id2doc.pkl", "rb") as f:
    id2doc = pickle.load(f)
    f.close()


# Ouverture du fichier, puis lecture avec pickle
with open("./data/id2author.pkl", "rb") as f:
    id2aut = pickle.load(f)
    f.close()


corpus = Corpus.Corpus("Machine-Learning",id2aut,id2doc)

corpus.matrice()
dfid2doc = corpus.get_id2doc_DF()

dfReddit, dfArxiv = dfid2doc[dfid2doc["Type"]=="Reddit"], dfid2doc[dfid2doc["Type"]=="Arxiv"]
n_doc = len(corpus.id2doc)

print(f"Stats générales du corpus: {corpus.stat()}")


auteurReddit = dfReddit["Auteur"].unique()
auteurArxiv = dfArxiv["Auteur"].unique()

statsVoc = list()
statsVoc.append("Longueur du vocab : "+str(len(corpus.voc)))
statsVoc.append(html.Br())
statsVoc.append(corpus.stat())
statsVoc.append(html.Br())
statsVoc.append(html.Br())

statsVoc.append("Les 10 premières de TF-IDF : ")
statsVoc.append(html.Br())
statsVoc.append(html.Br())

dictTFIDF = dict()
for indx, row in corpus.getdfTfIdf().iterrows():
    dictTFIDF[indx] = row.sum()

for k, v in sorted(dictTFIDF.items(), key=lambda item: item[1], reverse=True)[0:10]:
    l = html.Label(k+" : TF-IDF = "+str(round(v, 2)))
    statsVoc.append(l)
    statsVoc.append(html.Br())

app.layout = html.Div([dcc.Dropdown(
    id = 'cbMenu',
    options=[
        {'label': 'Informations générales', 'value': 'infoGen'},
        {'label': 'Détails des corpus par Document', 'value': 'docDetail'}
    ],
    value = 'infoGen'
),html.Div(id="divInfos",children=
[html.Center(html.H1('Informations générales')),
    
    html.Center(html.Label("Cette application dispose d'un moteur de recherche permettant de comparer différentes statistiques de pertinence en fonction")),
    html.Br(),
    html.Center(html.Label("de mot clés tapés dans une barre de recherche (utilisez le menu scroll du dessus afin de changer de menu)")),
    
    
    html.Center(html.H2("Statistiques : ")),
    html.Center(html.Div(id="divStats",children=statsVoc)),
]),
html.Div(id='mainDocDetails',children=[
    html.Div([
        dcc.Input(id='txtSearch',type='text',placeholder='Saisir les mots clés...',style={'margin':'0 auto','display':'block','margin-bottom':'5px'}),
        html.Div([
            html.Div(
                dcc.Dropdown(auteurReddit,id='cbAuteurLeft',style={'width':'120px','margin-left':'calc(50% + 10px)'})
                ,style={'float':'left','width':'30%'}),
            html.Div([
                dcc.Dropdown(auteurArxiv,id='cbAuteurRight',style={'width':'120px','margin-left':'calc(50% - 120px)'})
                ,
                html.Button('Rechercher', id='btnFilter', n_clicks=None,style={'float':'right'}),
                html.Button('Effacer les filtres', id='btnClear', n_clicks=None,style={'float':'right'})],style={'float':'right','width':'30%'}),
            html.Center([
                dcc.DatePickerRange(
                    display_format='DD/MM/YYYY',
                    end_date_placeholder_text='DD/MM/YYYY',
                    start_date=min(dfid2doc['Date']),
                    end_date=max(dfid2doc['Date']),
                    min_date_allowed=min(dfid2doc['Date']),
                    max_date_allowed=max(dfid2doc['Date']),
                    id="dateFilter")
            ]),
        ]),html.Br()
    ],id="divSearch", style={'float':'top','width':'100%','height':'10%','border-style':'solid'}),
    html.Div([html.Br(),html.Center('Corpus "ML" de Reddit',style={'font-size':'30px','font-weight':'bold'}),html.Br(),
              dash_table.DataTable(
                  id='tableReddit',page_size=5,page_action='native',
                  data=dfReddit.to_dict('records'),   
                  columns=[
                      {'id': 'Id', 'name': 'ID'},
                      {'id': 'Nom', 'name': 'Titre'},
                      {'id': 'Auteur', 'name': 'Auteur'},
                      {'id': 'dateFr', 'name': 'Date'},
                      {'id': 'URL', 'name': 'URL'},
                      {'id': 'Textabrv', 'name': 'Texte'},
                  ],style_cell={"width":"5px",'minWidth':'5px','maxWidth':'5px'},style_table={'width':'99.5%'}),html.Div(id='divDetailsLeft',children=[html.Div(id='divWordsLeft')],style={'display':'none','float':'left','width':'50%','height':'100%'})],id="divLeft",style={'z-index':'0','float':'left','width':'50%','height':'45%'}),
    html.Div([html.Br(),html.Center('Corpus "ML" d\'Arxiv',style={'font-size':'30px','font-weight':'bold'}),html.Br(),
              dash_table.DataTable(
                  id='tableArxiv',page_size=5,page_action='native',
                  data=dfArxiv.to_dict('records'),     
                  columns=[
                      {'id': 'Id', 'name': 'ID'},
                      {'id': 'Nom', 'name': 'Titre'},
                      {'id': 'Auteur', 'name': 'Auteur' },
                      {'id': 'dateFr', 'name': 'Date'},
                      {'id': 'URL', 'name': 'URL'},
                      {'id': 'Textabrv', 'name': 'Texte'},
                  ],style_cell={"width":"5px",'minWidth':'5px','maxWidth':'5px'},style_table={'width':'99.5%'}),html.Div(id='divDetailsRight',children=[html.Div(id='divWordsRight')],style={'display':'block','float':'right','width':'50%','height':'100%'})],id="divRight",style={'float':'right','width':'50%','height':'90%',"display":"block"})],style={'z-index':'-1'})])
@app.callback(
    Output('tableReddit', 'data'),
    Output('tableArxiv', 'data'),
    State('cbAuteurLeft', 'value'),
    State('cbAuteurRight', 'value'),
    State('txtSearch', 'value'),
    State('dateFilter', 'start_date'),
    State('dateFilter', 'end_date'),
    Input('btnFilter', 'n_clicks'),
)
def apply_filter(cbAuteur_value_left,cbAuteur_value_right,keywords,start,end,clicks):
    df_filtered_1 = dfReddit.copy()
    df_filtered_2 = dfArxiv.copy()

    start_val = ''
    end_val=''

    print(start)
    print(end)

    if cbAuteur_value_left:
        df_filtered_1 = df_filtered_1[df_filtered_1['Auteur'].eq(cbAuteur_value_left)]
    if cbAuteur_value_right:
        df_filtered_2 = df_filtered_2[df_filtered_2['Auteur'].eq(cbAuteur_value_right)]

    if not(start):
        start_val=datetime.date(min(dfid2doc['Date']))
    else:
        start_val=datetime.strptime(start, "%Y-%m-%d").date()
    if not(end):
        end_val=datetime.date(min(dfid2doc['Date']))
    else:
        end_val=datetime.strptime(end, "%Y-%m-%d").date()

    df_filtered_1=df_filtered_1[(df_filtered_1['Date'] >=start_val) & (df_filtered_1['Date']<=end_val)]
    df_filtered_2=df_filtered_2[(df_filtered_2['Date'] >=start_val) & (df_filtered_2['Date']<=end_val)]

    if keywords:
        print('---------------------',keywords)
        keywords_clean = corpus.clean_text(keywords)
        arr_keywords=keywords_clean.split(" ")
        dictest=corpus.searchCosine(arr_keywords)
        df_filtered_1['score'] = df_filtered_1['Nom'].apply(lambda x:dictest[x])
        df_filtered_2['score'] = df_filtered_2['Nom'].apply(lambda x:dictest[x])
        dfReddit['score']=dfReddit['Nom'].apply(lambda x:dictest[x])
        dfArxiv['score']=dfArxiv['Nom'].apply(lambda x:dictest[x])
        df_filtered_1 = df_filtered_1.sort_values('score',ascending=False)
        df_filtered_2 = df_filtered_2.sort_values('score',ascending=False)

        if cbAuteur_value_left:
            df_filtered_1 = df_filtered_1[df_filtered_1['Auteur'].eq(cbAuteur_value_left)]
        if cbAuteur_value_right:
            df_filtered_2 = df_filtered_2[df_filtered_2['Auteur'].eq(cbAuteur_value_right)]

    df_filtered_1=df_filtered_1[(df_filtered_1['Date'] >=start_val) & (df_filtered_1['Date']<=end_val)]
    df_filtered_2=df_filtered_2[(df_filtered_2['Date'] >=start_val) & (df_filtered_2['Date']<=end_val)]

    return df_filtered_1.to_dict(orient='records'),df_filtered_2.to_dict(orient='records')


@app.callback(
    Output('cbAuteurLeft', 'value'),
    Output('cbAuteurRight', 'value'),
    Output('txtSearch', 'value'),
    Output('dateFilter', 'start_date'),
    Output('dateFilter', 'end_date'),
    [State('cbAuteurLeft', 'value'),
     State('cbAuteurRight', 'value'),
     State('txtSearch', 'value')],
    State('dateFilter', 'start_date'),
    State('dateFilter', 'end_date'),
    [Input('btnClear', 'n_clicks')]
)
def clear_filter(cbAuteurLeft,cbAuteurRight,txtSearch,start,end,clicks):
    if cbAuteurLeft or cbAuteurRight or txtSearch or datetime.strptime(start, "%Y-%m-%d").date()!=min(dfid2doc['Date']) or datetime.strptime(end, "%Y-%m-%d").date()!=max(dfid2doc['Date']):
        return '','','',min(dfid2doc['Date']),max(dfid2doc['Date'])

@app.callback(
    [Output("divDetailsLeft", "children"),
     Output("divWordsLeft", "children"),
     Output("divDetailsLeft", "style")],
    Input('tableReddit', 'active_cell'),
    [State('tableReddit', 'data'),
     State('txtSearch', 'value'),
     State('tableReddit', 'page_current'),
     State('tableReddit', 'page_size')]
)
def update_left_pannel(active_cell,data,txt,page_curr,page_size):
    return_value=()
    if active_cell:
        if page_curr is not(None):
            row = active_cell['row']+page_curr*page_size
        else:
            row = active_cell['row']
        Id=data[row]['Id']
        txtDoc = dfReddit[dfReddit['Id'].eq(Id)]['Text']
        nbComms = dfReddit[dfReddit['Id'].eq(Id)]['Caractéristiques'].values[0]
        if txt:
            score = dfReddit[dfReddit['Id'].eq(Id)]['score'].values[0]
            if score==0.00:
                color = 'rgb(220,220,220)'
            elif score<=0.25:
                color = 'rgb(176,242,182)'
            elif score<=0.5:
                color = 'rgb(104,230,116)'
            else:
                color = 'rgb(47,221,63)'

            dfTFxIdfdup = corpus.getdfTfIdf().copy()
            tfxidfWords = []
            keywords_clean = corpus.clean_text(txt)
            arr_keywords=keywords_clean.split(" ")

            tfxidfWords.append(html.B('TFxIDF des mots clés :',style={'font-size':'20px'}))
            tfxidfWords.append(html.Br())
            for word in arr_keywords:
                if word in dfTFxIdfdup.index:
                    tfxidf = dfTFxIdfdup.loc[word][dfReddit[dfReddit['Id'].eq(Id)]['Nom']].values[0]
                    if tfxidf==0.0:
                        colorTfxIdf='rgb(220,220,220)'
                    elif tfxidf <=0.25:
                        colorTfxIdf='rgb(176,242,182)'
                    elif tfxidf <=0.5:
                        colorTfxIdf='rgb(104,230,116)'
                    else:
                        colorTfxIdf='rgb(47,221,63)'

                    value = html.Label(children =[word + ' : ',tfxidf],style={'margin-left':'20px','background-color':colorTfxIdf,'font-size':'20px'})
                else:
                    value = html.Label(children =[word + ' : ',0.0],style={'margin-left':'20px','background-color':'rgb(220,220,220)','font-size':'20px'})

                tfxidfWords.append(value)
                tfxidfWords.append(html.Br())

            return_value = html.Div([html.Center([html.Br(),html.B('Score : ',style={'font-size':'25px'}),html.Label(children=[score],style={'background-color':color,'font-size':'20px'}),html.Br(),html.Div(id='divWordsLeft'),html.Br(),html.B('Full text : ',style={'font-size':'25px'}),html.Br(),dcc.Textarea(style={'font-size':'20px'},value=txtDoc,rows=10,cols=30),html.Br(),'Nombre de commentaire(s) : '+str(nbComms)])]),html.Div(children=tfxidfWords),{'display':'block'}
        else:
            return_value = html.Div([html.Center([html.B('Full text : ',style={'font-size':'25px'}),html.Br(),html.Div(id='divWordsLeft'),dcc.Textarea(style={'font-size':'20px'},value=txtDoc,rows=10,cols=30),html.Br(),'Nombre de commentaire(s) : '+str(nbComms)])]),html.Div(),{'display':'block','border-right':'solid 0.5px'}
    return return_value

@app.callback(
    [Output("divDetailsRight", "children"),
     Output("divWordsRight", "children"),
     Output("divDetailsRight", "style")],
    Input('tableArxiv', 'active_cell'),
    [State('tableArxiv', 'data'),
     State('txtSearch', 'value'),
     State('tableArxiv', 'page_current'),
     State('tableArxiv', 'page_size')]
)
def update_right_pannel(active_cell,data,txt,page_curr,page_size):
    return_value=()
    if active_cell:

        if page_curr is not(None):
            row = active_cell['row']+page_curr*page_size
        else:
            row = active_cell['row']
        Id=data[row]['Id']
        txtDoc = dfArxiv[dfArxiv['Id'].eq(Id)]['Text']
        coAuteurs = ' - '.join(dfArxiv[dfArxiv['Id'].eq(Id)]['Caractéristiques'].values[0])
        if txt:
            score = dfArxiv[dfArxiv['Id'].eq(Id)]['score'].values[0]
            if score==0.00:
                color = 'rgb(220,220,220)'
            elif score<=0.25:
                color = 'rgb(176,242,182)'
            elif score<=0.5:
                color = 'rgb(104,230,116)'
            else:
                color = 'rgb(47,221,63)'

            dfTFxIdfdup = corpus.getdfTfIdf().copy()
            tfxidfWords = []
            keywords_clean = corpus.clean_text(txt)
            arr_keywords=keywords_clean.split(" ")


            tfxidfWords.append(html.B('TFxIDF des mots clés :',style={'font-size':'20px'}))
            tfxidfWords.append(html.Br())
            for word in arr_keywords:
                if word in dfTFxIdfdup.index:
                    tfxidf = dfTFxIdfdup.loc[word][dfArxiv[dfArxiv['Id'].eq(Id)]['Nom']].values[0]
                    if tfxidf==0.0:
                        colorTfxIdf='rgb(220,220,220)'
                    elif tfxidf <=0.25:
                        colorTfxIdf='rgb(176,242,182)'
                    elif tfxidf <=0.5:
                        colorTfxIdf='rgb(104,230,116)'
                    else:
                        colorTfxIdf='rgb(47,221,63)'

                    value = html.Label(children =[word + ' : ',tfxidf],style={'margin-left':'20px','background-color':colorTfxIdf,'font-size':'20px'})
                else:
                    value = html.Label(children =[word + ' : ',0.0],style={'margin-left':'20px','background-color':'rgb(220,220,220)','font-size':'20px'})

                tfxidfWords.append(value)
                tfxidfWords.append(html.Br())

            return_value = html.Div([html.Center([html.Br(),html.B('Score : ',style={'font-size':'25px'}),html.Label(children=[score],style={'background-color':color,'font-size':'20px'}),html.Br(),html.Div(id='divWordsRight'),html.Br(),html.B('Full text : ',style={'font-size':'25px'}),html.Br(),dcc.Textarea(style={'font-size':'20px'},value=txtDoc,rows=10,cols=30),html.Br(),'Auteur(s) : '+coAuteurs])]),html.Div(children=tfxidfWords),{'display':'block'}
        else:
            return_value = html.Div([html.Center([html.B('Full text : ',style={'font-size':'25px'}),html.Br(),html.Div(id='divWordsRight'),dcc.Textarea(style={'font-size':'20px'},value=txtDoc,rows=10,cols=30),html.Br(),'Auteur(s) : '+coAuteurs])]),html.Div(),{'display':'block','border-left':'solid 0.5px'}
    return return_value

# df = pd.DataFrame.from_dict(vocab)
# column_names = df.columns.values.tolist()
# df = df.transpose()
# df.insert(0, "Mot", column_names)

@app.callback(
    Output('divInfos', 'style'),
    [Input('cbMenu', 'value')]
)
def adjust_div_visibility(selected_option):
    """
    @brief Adjust the visibility of the divInfos div based on the selected menu option
    @param selected_option The selected menu option
    """
    # Define common style properties
    common_style = {
        'z-index': '1',
        'width': '100%',
        'height': '100%',
        'position': 'absolute',
        'background-color': 'white'
    }
    # Adjust visibility based on the selected menu option
    if selected_option == 'infoGen':
        return {**common_style, 'display': 'block'}
    elif selected_option == 'docDetail':
        return {**common_style, 'display': 'none'}
    


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)