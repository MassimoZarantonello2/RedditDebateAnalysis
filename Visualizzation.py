from dash import Dash, html, dcc, Input, Output
import dash_daq as daq
import dash_cytoscape as cyto
import pandas as pd
import igraph as ig

def create_graph_from_dataframe(dataframe):
    graph = ig.Graph(directed=True)
    graph.add_vertex(name='root', label='root')
    for comment in dataframe.iterrows():
        if comment[1]['comment_author_name'] not in graph.vs['name']:
            graph.add_vertex(name=comment[1]['comment_author_name'], label=comment[1]['comment_author_name'], color='lightblue')
        if comment[1]['comment_parent_name'] not in graph.vs['name']:
            graph.add_vertex(name=comment[1]['comment_parent_name'], label=comment[1]['comment_parent_name'], color='lightblue')

        graph.add_edge(source=comment[1]['comment_author_name'], 
                       target=comment[1]['comment_parent_name'],
                       comment_id = comment[1]['comment_id'] ,
                       comment_body = comment[1]['comment_body'])
    
    graph.delete_vertices(['OP', 'deleted'])
    return graph

def from_graph_to_visualization(graph):
    elements = []
    
    for v in graph.vs:
        elements.append({'data': {'id': v['name'], 
                                  'label': v['label'], 
                                  'color': v['color'],
                                  'debate_group': v['debate_id']
                                 }})

    for e in graph.es:
        elements.append({'data': {'source': graph.vs[e.source]['name'],
                                  'target': graph.vs[e.target]['name'],
                                  'comment_id': graph.es[e.index]['comment_id'],
                                  'comment_body': graph.es[e.index]['comment_body']
                                 }})

    return elements

def delete_isolated_vertices(graph):
    graph.delete_vertices(graph.vs.select(_degree=0))
    return graph

def find_minimal_debate(graph):
    color_list = ['yellow', 'green', 'blue', 'purple', 'orange', 'pink', 'brown', 'black','lightblue','lightgreen','lime','magenta','maroon','navy','olive','purple','silver','teal','white','yellow']
    i = 0
    graph.vs['debate_id'] = 0
    for vertex in graph.vs:
        if vertex['debate_id'] == 0:
            color = color_list[i % len(color_list)]
            i += 1
            neighbors = vertex.neighbors()
            if neighbors != []:
                for vertex_neighbor in neighbors:
                    if vertex_neighbor['debate_id'] == 0:
                        try:
                            vertex_to_neighbor = graph.es.find(_source=vertex.index, _target=vertex_neighbor.index)
                        except:
                            vertex_to_neighbor = None
                        try:
                            neighbors_to_vertex = graph.es.find(_source=vertex_neighbor.index, _target=vertex.index)
                        except:
                            neighbors_to_vertex = None
                        if vertex_to_neighbor and neighbors_to_vertex:
                            vertex['color'] = color
                            vertex['debate_id'] = i
                            vertex_neighbor['color'] = color
                            vertex_neighbor['debate_id'] = i
                            break
    return graph

def find_complete_discussion(vertex, graph, deep):
    deep += 1
    color = vertex['color']
    debate_id = vertex['debate_id']
    neighbors = vertex.neighbors()
    for neighbor in neighbors:
        if neighbor['debate_id'] != debate_id:
            try:
                vertex_to_neighbor = graph.es.find(_source=vertex.index, _target=neighbor.index)
            except:
                vertex_to_neighbor = None
            
            try:
                neighbors_to_vertex = graph.es.find(_source=neighbor.index, _target=vertex.index)
            except:
                neighbors_to_vertex = None

            if neighbors_to_vertex or (vertex_to_neighbor and neighbors_to_vertex):

                neighbor['color'] = color
                neighbor['debate_id'] = debate_id
                neighbor['depth'] = deep
                find_complete_discussion(neighbor, graph, deep)

    def max(list):
        max = 0
        for i in list:
            if i > max:
                max = i
        return max


if __name__ == '__main__':
    df = pd.read_csv('reddit_comments.csv')
    deep = 0
    post_df = df[df['post_id'] == '19aeo2k']

    graph = create_graph_from_dataframe(post_df)
    graph = delete_isolated_vertices(graph)
    graph.vs['depth'] = deep
    graph = find_minimal_debate(graph)
    for vertex in graph.vs:
        if vertex['debate_id'] != 0:
            find_complete_discussion(vertex, graph, deep)

    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'background-color': 'data(color)',
                'label': 'data(label)'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'line-color': '#ccc',
                'width': 2
            }
        }
    ]

    elements = from_graph_to_visualization(graph)

    app = Dash(__name__)
    app.layout = html.Div([
        html.H1("Reddit Dataset Analysis", style={'text-align': 'center', 'color': 'lightblue', 'font-family': 'Arial, sans-serif'}),
        cyto.Cytoscape(
            id='cytoscape',
            elements=elements,
            layout={'name': 'cose',
                    'idealEdgeLength': 100,  # Lunghezza ideale degli edge
                    'nodeOverlap': 100,       # Sovrapposizione tra nodi
                    'edgeElasticity': 10,  # Elasticità degli edge (0 significa nessuna elasticità)
                    'nodeRepulsion': 1000000,  # Repulsione tra nodi              
                    },
            stylesheet=stylesheet,
            style={'width': '1500px', 'height': '600px', 'border': '1px solid black', 'margin': 'auto'}
        ),
        html.Div(id='output'),
        html.Label('Adjust edge width:'),
        dcc.Slider(
            id='width-slider',
            min=0,
            max= max(graph.vs['depth'])+1,
            step=1,
            value=0,
            marks={i: str(i) for i in range(1, max(graph.vs['depth'])+1)}
        ),
        daq.BooleanSwitch(id='show-debate', on=False)
        ])

    @app.callback(
        Output('output', 'children'),
        Input('cytoscape', 'tapEdge')
    )
    def display_comment_body(edge_data):
        if edge_data is None:
            return "Click on an edge to see the comment body."
        
        selected_comment_id = edge_data['data']['comment_id']
        source_edge = graph.es.find(comment_id = selected_comment_id)
        comment_body = source_edge['comment_body']
        
        return html.Div([
            html.P(comment_body)
        ])
    
    @app.callback(
        Output('cytoscape', 'elements'),
        [Input('width-slider', 'value'),        
        Input('show-debate', 'on')]
    )
    def update_graph_visibility(slider_value, on):
        elements = []
        depth_graph = graph.copy()
        for vertex in depth_graph.vs:
            if vertex['depth'] >= slider_value:
                vertex['color'] = 'lightblue'

        if on:
            for edge in depth_graph.es:
                if depth_graph.vs[edge.source]['debate_id'] != depth_graph.vs[edge.target]['debate_id']:
                    depth_graph.delete_edges(edge)

        elements = from_graph_to_visualization(depth_graph)
        return elements

    app.run_server(debug=True)
