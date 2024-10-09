import os
import pandas as pd
import networkx as nx
from pyvis.network import Network
from flask import Flask, request, redirect, render_template, url_for, send_from_directory

app = Flask(__name__)

# Pasta de upload e pasta de gráficos
UPLOAD_FOLDER = 'uploads'
GRAPH_FOLDER = 'graphs'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(GRAPH_FOLDER):
    os.makedirs(GRAPH_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GRAPH_FOLDER'] = GRAPH_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect('/')
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Processa o arquivo e gera o gráfico
        return redirect(url_for('render_graph', filename=file.filename))

@app.route('/graph/<filename>')
def render_graph(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Ler o arquivo Excel
    df = pd.read_excel(filepath)
    
    # Deleta a planhilha após leitura
    os.remove(filepath)
    
    # Criar o grafo
    graph = nx.DiGraph()
    
    # Adiciona nós e arestas com formatação personalizada
    for index, row in df.iterrows():
        entidade_a = row['Entidade A']
        entidade_b = row.get('Entidade B', None)  
        entidade_c = row.get('Entidade C', None)  
        relacionamento = row['Relacionamento']

        # Cor amarela para Entidade A com relacionamento "contador"
        if relacionamento == "CONTADOR":
            graph.add_node(entidade_a, shape="circle", color="yellow")
        else:
            graph.add_node(entidade_a, shape="circle")  # Cor padrão
        
        # Entidades B Empresas
        if pd.notna(entidade_b):
            # Entidades B qEmpresas
            graph.add_node(entidade_b, shape="database", color="#33dd33")
            graph.add_edge(entidade_a, entidade_b, label=relacionamento)
        
        #Entidade C pessoas relacionadas
        elif pd.notna(entidade_c):
            graph.add_node(entidade_c, shape="box", color="#ff8888" ) 
            graph.add_edge(entidade_a, entidade_c, label=relacionamento)

    
    # Gerar o gráfico com PyVis
    nt = Network(notebook=False, width="2000px", height="1600px")
    nt.repulsion(node_distance=400, spring_length=200)
    nt.from_nx(graph)
    
    # Salvar o gráfico como arquivo HTML
    graph_html_path = os.path.join(app.config['GRAPH_FOLDER'], 'graph.html')
    nt.save_graph(graph_html_path)
    
    # Exibir o gráfico diretamente no navegador
    return redirect(url_for('serve_graph', filename='graph.html'))

# Rota para servir o arquivo gráfico (HTML)
@app.route('/graphs/<filename>')
def serve_graph(filename):
    return send_from_directory(app.config['GRAPH_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
