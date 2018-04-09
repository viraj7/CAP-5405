from collections import defaultdict
from ast import literal_eval
from flask import Flask, request, abort
from flask_basicauth import BasicAuth
import json

app = Flask(__name__)

APP_URL = "http://localhost:5000"

def rec_dfs(g, s, visited):
    visited[s] = True
    for node in g[s]:
        if not visited[node]:
            rec_dfs(g, node, visited)
    return(visited)

def create_graph(data):
    edges = literal_eval(data["edges"])
    g = defaultdict(list)
    for i in edges:
        g[i[0]].append(i[1])
    return(g)

@app.route('/create', methods = ['POST'])
def create():
    data = request.get_json(force=True)
    g = create_graph(data)
    return("Graph created: \n" + json.dumps(g) + "\n")

@app.route('/shortest_path', methods = ['POST'])
def shortest_path():
    data = request.get_json(force=True)
    g = defaultdict(dict)
    #print(data["edges"])
    edges = data["edges"]
    nodes = data["nodes"]
    #print(type(edges))
    for edge in edges:
        g[edge[0]][edge[1]] = edge[2]
        g[edge[1]][edge[0]] = edge[2]
    unvisited = {node: None for node in nodes} #using None as +inf
    visited = {}
    current = 'B'
    currentDistance = 0
    unvisited[current] = currentDistance
    while True:
        for neighbour, distance in g[current].items():
            if neighbour not in unvisited: continue
            newDistance = currentDistance + distance
            if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:
                unvisited[neighbour] = newDistance
        visited[current] = currentDistance
        del unvisited[current]
        if not unvisited: break
        candidates = [node for node in unvisited.items() if node[1]]
        current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
    return(json.dumps({"status": 1, "shortest path": visited}) + "\n")
    '''        
    source = data["source_node"]
    target = data["target_node"].setdefault(None)
    nodes = data[nodes]
    nodes.remove(source)
    visited = defaultdict(bool)
    visited[source] = True    
    dist = defaultdict(lambda: float(inf))
    for vnode in stack:
        for node, dis in g[vnode]:
            if not visited[n]:
                pass
    '''

@app.route('/strongly_connected', methods = ['POST'])
def is_sc():
    data = request.get_json(force=True)
    nodes = literal_eval(data["nodes"])
    edges = literal_eval(data["edges"])
    gc = defaultdict(list)
    for i in edges:
        gc[i[1]].append(i[0])
    g = create_graph(data)
    visited = defaultdict(bool)
    visited = rec_dfs(g, nodes[0], visited)
    if any (visited[i] == False for i in nodes):
        return(json.dumps({"status":"0", "msg":"Not strongly connected"}) + "\n")
    visited = defaultdict(bool)
    visited = rec_dfs(gc, nodes[0], visited)
    if any (visited[i] == False for i in nodes):
        return(json.dumps({"status":"0", "msg":"Not strongly connected"}) + "\n")
    return(json.dumps({"status":"1", "msg":"Strongly connected"}) + "\n")

@app.route('/is_reachable', methods = ['POST'])
def is_reachable():
    data = request.get_json(force=True)
    if "source" not in data or "target" not in data:
        return(json.dumps({"Status":"Error", "msg":"source/target node(s) not specified"}))
    s = literal_eval(data["source"])
    t = literal_eval(data["target"])
    g = create_graph(data)
    if s not in nodes or t not in nodes:
        return(json.dumps({"Status":"Error", "msg":"Invalid source/target node"}))
    visited = defaultdict(bool)
    nodes = []
    nodes.append(s)
    visited[s] = True
    while nodes:
        x = nodes.pop(0)
        for i in g[x]:
            if not visited[i]:
                nodes.append(i)
                visited[i] = True
    if visited[t]:
        return(json.dumps({"Status":1, "msg":"Source and target nodes are connected"}))
    return(json.dumps({"Status":0, "msg":"Source and target nodes are not connected"}))


@app.route('/is_dag', methods = ['POST'])
def is_dag():
    data = request.get_json(force=True)
    edges = data["edges"]
    g = defaultdict(list)
    for i in edges:
        g[i[0]].append(i[1])
    path = set()
    visited = set()
    def visit(vertex):
        if vertex in visited:
            return False
        visited.add(vertex)
        path.add(vertex)
        for neighbour in g.get(vertex, ()):
            if neighbour in path or visit(neighbour):
                return True
        path.remove(vertex)
        return False
    return(json.dumps({"status": 1, "Cycle present":any(visit(v) for v in g)}) + "\n")

def isCycle(g, src, visited, parent):
    visited[src] = True
    for i in g[src]:
        if not visited[i]:
            if isCycle(g, i, visited, src):
                return(True)
        elif i != parent:
            return(True)
    return(False)            

@app.route('/is_tree', methods = ['POST'])
def is_tree():
    data = request.get_json(force=True)
    nodes = data["nodes"]
    edges = data["edges"]
    v = nodes[0] 
    g = defaultdict(list)
    for i in edges:
        g[i[0]].append(i[1])
        g[i[1]].append(i[0])
    visited = defaultdict(bool)
    if isCycle(g, v, visited, -1):
        return(json.dumps({"status": 1, "msg":"Not a tree"}) + "\n")
    s, res = [], []
    s.append(v)
    visited[v] = True
    while s:
         x = s.pop(0)
         res.append(x)
         for i in g[x]:
             if not visited[i]:
                 s.append(i)
                 visited[i] = True    
    for i in nodes:
        if not visited[i]:
            return(json.dumps({"status": 1, "msg":"Not a tree"}) + "\n")



@app.route('/is_bipartite', methods = ['POST'])
def is_bipartite():
    data = request.get_json(force=True)
    nodes = data["nodes"]
    edges = data["edges"]
    g = defaultdict(list)
    for i in edges:
        g[i[0]].append(i[1])
    src = nodes[0]    
    visited = defaultdict(bool)
    colorArr = defaultdict(lambda: -1)
    colorArr[src] = 1
    queue = []
    queue.append(src)
    #print(g)    
    while queue:
        u = queue.pop()
        if u in g[u]:
            return False
        for v in nodes:
            if v in g[u] and colorArr[v] == -1:
                colorArr[v] = 1 - colorArr[u]
                queue.append(v)
            elif v in g[u] and colorArr[v] == colorArr[u]:
                return(json.dumps({"Graph is bipartite": False})+ "\n")
            #print(colorArr, queue)    
    return(json.dumps({"Graph is bipartite": True}) + "\n")           

@app.route('/bfs', methods = ['POST'])
def bfs():
    data = request.get_json(force=True)
    nodes = literal_eval(data["nodes"])
    v = data.setdefault("start_node", nodes[0])
    g = create_graph(data)
    visited = defaultdict(bool)
    s, res = [], []
    s.append(v)
    visited[v] = True
    while s:
         x = s.pop(0)
         res.append(x)
         for i in g[x]:
             if not visited[i]:
                 s.append(i)
                 visited[i] = True
    return(json.dumps({"BFS traversal":res}) + "\n")

def dfs():
    pass

if __name__ == "__main__":
    app.run(host= '0.0.0.0', debug=True)
