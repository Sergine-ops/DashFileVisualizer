from dash import Dash,dash_table,dcc,html,Input,Output,State,callback
import base64
import datetime
import io
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__,external_stylesheets=external_stylesheets)

app.layout = html.Div([
    
    dcc.Upload(id='upload-data',

    children=html.Div([
        'Drag and Drop or',
        html.A('Select Files')
         ]),
    style={
        'width':'100%',
        'height':'60px',
        'lineHeight':'60px',
        'borderWidth':'1px',
        'borderStyle':'dashed',
        'borderRadius':'5px',
        'textAlign':'center',
        'margin':'10px',
    },
    multiple=True
    ),
    dcc.Dropdown(id='xaxis-column',placeholder='Select your xaxis'),
    dcc.Dropdown(id='yaxis-column',placeholder='Select your yaxis'),
    html.Div(id='output-data-uploaded')

])

def uploaded_data(contents,filename,date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:

            df= pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename:

            df=pd.read_csv(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error in processing the file.'
        ])  

    return df 


@callback(
    Output('xaxis-column','options'),
    Output('yaxis-column','options'),
    Output('output-data-uploaded','children'),
    Input('upload-data','contents'),
    State('upload-data','filename'),
    State('upload-data','last_modified'),


) 


def update_output(list_of_contents,list_of_names,list_of_dates):

    if list_of_contents is not None:
        children = [
            uploaded_data(c,n,d) for c, n, d in zip(list_of_contents,list_of_names,list_of_dates)


        ]

        df = children[0]
        options = [{'label':col,'value':col} for col in df.columns]

        last_modified_time = list_of_dates[0] if list_of_dates else None  # Get the first timestamp or None
        if last_modified_time:
            last_modified_date = datetime.datetime.fromtimestamp(last_modified_time)
        else:
            last_modified_date = "Unknown"
        
        return options,options,html.Div([
        html.H5(list_of_names),
        html.H6(datetime.datetime.fromtimestamp(list_of_dates[0])),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name':i,'id':i} for i in df.columns]
        ),
       

       
    ])   

    return [],[],html.Div() 
  

  

def update_graph(xaxis_column,yaxis_column,contents,filename,date):
    if contents is not None:

        df=uploaded_data(contents[0],filename[0],date[0])


        if xaxis_column and yaxis_column:

            figure = px.scatter(df,x=xaxis_column,y=yaxis_column)
            return html.Div([
                dcc.Graph(figure=figure)
            ])

    return html.Div()        



if __name__ == '__main__':
    app.run(debug=True)        

