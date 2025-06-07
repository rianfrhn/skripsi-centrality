import json
from fastapi import APIRouter, Depends, HTTPException, Query
from networkx import Graph
from sqlalchemy.orm import Session
import networkx as nx
from collections import deque
import numpy as np
from core.security import get_current_agent
import models

from core.dependencies import get_current_active_agent, get_db
from routers.agents import list_agents

from fastapi.responses import JSONResponse
from networkx.readwrite import json_graph


router = APIRouter(prefix="/centrality", tags=["centrality"])

@router.get("/")
def none():
    return {}

@router.get("/get_graph")
def get_graph_json(db: Session = Depends(get_db)):
    graph = get_graph(db)
    data = json_graph.node_link_data(graph)  # serialize graph
    return JSONResponse(content=data)

def get_graph(db: Session):
    G = nx.DiGraph()
    agents = list_agents(0, 500, db)

    for agent in agents:
        G.add_node(agent.id,
            agent_name=agent.name,)

    valid_ids = {agent.id for agent in agents}

    for agent in agents:
        ref_id = agent.referred_by_id
        if ref_id and ref_id in valid_ids:
            G.add_edge(ref_id, agent.id)

    return G

@router.get("/graph")
def get_agent_graph(
    level: int = Query(3, ge=1, description="Levels deep (1 = immediate children)"),
    db: Session = Depends(get_db),
    current_agent: models.Agent = Depends(get_current_agent),

):
    agent_id = current_agent.id
    return get_downline_subgraph_json(agent_id,level=level, db=db)

@router.get("/graph/{user_id}", summary="Get subgraph up to N levels from a given agent")
def get_downline_subgraph_json(
    user_id: int,
    level: int = Query(3, ge=1, description="Levels deep (1 = immediate children)"),
    db: Session = Depends(get_db),
    #current=Depends(get_current_active_agent),
):
    subgraph = get_downline_subgraph_up_to_level(db, user_id, level)
    if subgraph.number_of_nodes() == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Tidak ada agen dalam downline dari user {user_id} dengan {level} level"
        )

    data = json_graph.node_link_data(subgraph)
    return JSONResponse(content=data)

def build_full_agent_graph(db: Session) -> nx.DiGraph:
    G = nx.DiGraph()

    agents = db.query(models.Agent).all()

    for agent in agents:
        G.add_node(
            agent.id, 
            agent_name = agent.name)

    valid_ids = {agent.id for agent in agents}

    for agent in agents:
        ref_id = agent.referred_by_id  
        if ref_id and ref_id in valid_ids:
            G.add_edge(ref_id, agent.id)

    return G


def get_downline_subgraph_up_to_level(
    db: Session,
    root_id: int,
    max_level: int
) -> nx.DiGraph:
    
    full_graph = build_full_agent_graph(db)

    if root_id not in full_graph:
        return nx.DiGraph()

    visited = {root_id}
    downline_nodes = set()
    queue = deque([(root_id, 0)])

    while queue:
        current_node, depth = queue.popleft()
        if depth >= max_level:
            continue

        for child in full_graph.successors(current_node):
            if child not in visited:
                visited.add(child)
                downline_nodes.add(child)
                queue.append((child, depth + 1))

    nodes_to_include = {root_id} | downline_nodes

    subgraph = full_graph.subgraph(nodes_to_include).copy()

    return subgraph


@router.get("/degree_centrality")
def degree_centrality(db: Session = Depends(get_db)):
    graph = get_graph(db)
    
    total_nodes = len(graph) - 1 
    return {node: len(list(graph.neighbors(node))) / total_nodes for node in graph}


@router.get("/betweenness_centrality")
def betweenness_centrality(db: Session = Depends(get_db)):
    graph = get_graph(db)
    bc = {node: 0 for node in graph}
    
    for start in graph:
        for target in graph:
            if start != target:
                shortest_paths = []
                deq = deque([[start]])
                
                while deq:
                    path = deq.popleft()
                    node = path[-1]
                    
                    if node == target:
                        shortest_paths.append(path)
                        continue
                    
                    for neighbor in graph.neighbors(node):
                        if neighbor not in path:
                            deq.append(path + [neighbor])
                
                for path in shortest_paths:
                    for node in path[1:-1]:
                        bc[node] += 1 / len(shortest_paths)
    
    return bc   

def bfs(graph, start):
    queue = deque([(start, 0)]) 
    distances = {start: 0}
    
    while queue:
        node, dist = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in distances:
                distances[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))
    
    return distances
@router.get("/closeness_centrality")
def closeness_centrality(db: Session = Depends(get_db)):
    graph = get_graph(db)
    centrality = {}
    N = len(graph)
    for node in graph:
        distances = bfs(graph, node)
        total_distance = sum(distances.values())
        N_reached = len(distances)
        
        if total_distance > 0:
            centrality[node] = (N_reached / (N-1))/((N_reached - 1) / total_distance)
        else:
            centrality[node] = 0 
    
    return centrality

@router.get("/eigenvector_centrality")
def eigenvector_centrality(max_iter : int=100, tol : float=1e-6, db: Session = Depends(get_db)):
    graph = get_graph(db)
    nodes = list(graph.nodes())
    n = len(nodes)
    
    A = np.zeros((n, n)) #adj
    for i, node in enumerate(nodes):
        for neighbor in graph[node]:
            if neighbor in nodes:
                j = nodes.index(neighbor)
                A[i, j] = 1
    
    centrality = np.ones(n)
    
    for _ in range(max_iter):
        new_centrality = np.dot(A, centrality) 
        new_centrality /= np.linalg.norm(new_centrality, 2)
        centrality = new_centrality
    
    return {nodes[i]: centrality[i] for i in range(n)}
@router.get("/pagerank")
def pagerank(d : float=0.85, max_iter : int=100, tol:float=1e-6, db: Session = Depends(get_db)):
    graph = get_graph(db)
    nodes = list(graph.nodes())
    n = len(nodes)

    M = np.zeros((n, n))
    for i, node in enumerate(nodes):
        neighbors = graph[node]
        if neighbors:
            for neighbor in neighbors:
                if neighbor in nodes:
                    j = nodes.index(neighbor)
                    M[j, i] = 1 / len(neighbors)  
        else:
            M[:, i] = 1 / n  # Distribute uniformly if dangling node

    
    rank = np.ones(n) / n 
    
    for _ in range(max_iter):
        new_rank = (1 - d) / n + d * np.dot(M, rank) 
        
        if np.linalg.norm(new_rank - rank, 1) < tol:
            break
        
        rank = new_rank
    
    return {nodes[i]: rank[i] for i in range(n)}
def json_to_graph(response : JSONResponse):
    if not response:
        print("Cant decode jsonresponse to graph: not found")
        return None
    print(response.body)
    json_data = json.loads(response.body)
    G = json_graph.node_link_graph(json_data)
    return G
