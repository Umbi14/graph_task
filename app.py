# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import networkx as nx
from random import random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# generate a random graph with 'n_nodes' nodes and 0.1 probability of edge
n_nodes = 10
random_graph = nx.fast_gnp_random_graph(n_nodes, 0.1, directed=True)
# assign random position
for node in random_graph.nodes():
    random_graph.node[node]['pos'] = [round(random(),3), round(random(),3)]

# Return nodes traces and edges traces to display on the graph
def graph_traces(G):
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.node[node]['pos']
        G.node[node]['property_1'] = [e[1] for e in list(G.edges()) if e[0]==node] # list of outgoing edges
        #G.node[node]['property_1'] = 'property'
        node_x.append(x)
        node_y.append(y)
    node_text = list(G.nodes())

    node_trace = go.Scatter( x=node_x, y=node_y, text = node_text,
                            textposition='top center',
                            mode='markers+text',
                            hoverinfo='text',marker = { 'size': 10, 'line': {'width': 2, 'color': 'black'} }
                            )

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')
    return edge_trace, node_trace


introductive_text = '''
This simple Web App displays a random generated graph with 10 nodes.

If you click on a node the property of that node are shown on the right.

The properties are position (x and y) and the outgoing edges.

You can modify the node's propertis. When you click "Update" the graph will be updated'''
app.layout = html.Div([html.H1(children='Graph Task'),
    dcc.Markdown(children = introductive_text),

    html.Table([html.Tr([html.Td(
                        dcc.Graph(
                            id='network-graph',
                            figure={
                                'data': graph_traces(random_graph),
                                'layout': go.Layout(
                                    title = 'Network Graph',
                                    titlefont_size=16,
                                    showlegend=False,
                                    hovermode='closest',
                                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                                )
                            }
                        )
        ),
                        html.Td(#properties and update button
                            html.Table([html.Tr([html.Td(
                                                    html.Div([html.H5('Selected Node'),html.P(id='selected-node', children = '')])
                                        )]),
                                        html.Tr([html.Td(
                                                    html.Div([html.H5('x'),dcc.Input(id='node-x', type='number', placeholder='x', value='')])
                                        )]),
                                        html.Tr([html.Td(
                                                    html.Div([html.H5('y'),dcc.Input(id='node-y', type='number', placeholder='y', value='')])
                                        )]),
                                        html.Tr([html.Td(
                                                    html.Div([html.H5('Outgoing edges'),
                                                            dcc.Dropdown(id='node-property',
                                                                        options=[{'label': str(n), 'value': n} for n in random_graph],
                                                                        value=[],
                                                                        multi=True)
                                                            ])
                                        )]),
                                        html.Tr([html.Td(
                                                    html.Button('Update', id='update-button')
                                        )])
                                ])
                        )])])
]
)

# when click on a node show properties
@app.callback(
    [Output('selected-node', 'children'),Output('node-x', 'value'), Output('node-y', 'value'), Output('node-property', 'value')],
    [Input('network-graph', 'clickData')])
def display_click_data(clickData):
    if clickData:
        node = int(clickData['points'][0]['text'])
        return node, clickData['points'][0]['x'], clickData['points'][0]['y'], random_graph.node[node]['property_1']
    else:
        raise PreventUpdate

# when click 'update' update node properties
@app.callback(
    Output('network-graph', 'figure'),
    [Input('update-button', 'n_clicks')],
    [State('selected-node', 'children'), State('node-x', 'value'), State('node-y', 'value'), State('node-property', 'value')])
def update_output(n_clicks, selected_node, x, y, property):
    if n_clicks is None or selected_node == '':
        raise PreventUpdate
    else:
        node = int(selected_node)
        random_graph.node[node]['pos'] = [x, y]
        random_graph.node[node]['property_1'] = property
        # remove node's edges
        del_edges = [(node, nbr) for nbr in random_graph[node]]
        random_graph.remove_edges_from(del_edges)
        # add new node's edges
        for e in property:
            random_graph.add_edge(node, e)
        return {
            'data': graph_traces(random_graph),
            'layout': go.Layout(
                title = 'Network Graph',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
        }


if __name__ == '__main__':
    app.run_server(debug=True,dev_tools_hot_reload=False)
