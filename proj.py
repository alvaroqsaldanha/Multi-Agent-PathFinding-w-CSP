import sys
from minizinc import Instance, Model, Solver

if len(sys.argv) != 3:
    print("Wrong number of command line arguments!")
    exit()

graph_file_name = sys.argv[1]
scenario_file_name = sys.argv[2]

try:
    graph_file = open(graph_file_name,"r")
    scenario_file = open(scenario_file_name,"r")
except FileNotFoundError:
    print("Error processing input file(s).")

# Class for graph implementation
class Graph:

    def __init__(self,n_vertices,n_edges,edges):
        self.n_vertices = n_vertices
        self.n_edges = n_edges
        self.edges = edges
        self.build_adj_matrix()

    # Method for setting up a specific given scenario for the graph
    def set_scenario(self,n_agents,agent_start_positions,agent_goal_positions):
        self.n_agents = n_agents
        self.agent_start_positions = agent_start_positions
        self.agent_goal_positions = agent_goal_positions

    # Getters
    def get_n_vertices(self):
        return self.n_vertices

    def get_n_agents(self):
        return self.n_agents

    def get_start_positions(self):
        return self.agent_start_positions

    def get_goal_positions(self):
        return self.agent_goal_positions

    def get_adj_matrix(self):
        return self.adj_matrix

    # Method to return Adjacency Matrix for minizinc initialization
    def build_adj_matrix(self):
        adj_matrix = [[0] * self.n_vertices for x in range(self.n_vertices)]
        for edge in self.edges:
            adj_matrix[edge[0]-1][edge[1]-1] = 1
            adj_matrix[edge[1]-1][edge[0]-1] = 1
        self.adj_matrix = adj_matrix

    # Method to print adjacency matrix for graph
    def __str__(self):
        graph_repr = "\nAdjacency Matrix:\n\n"
        found_edge = 0
        for i in range(1,self.n_vertices+1):
            for j in range(1,self.n_vertices+1):
                for edge in self.edges:
                    if i in edge and j in edge and i != j:
                        graph_repr += "1 "
                        found_edge = 1
                        break
                if found_edge == 0:
                    graph_repr += "0 "
                found_edge = 0
            graph_repr += "\n"
        return graph_repr

# Function to read graph_file and create respective graph
def process_graph(graph_file):
    lines = list(filter(lambda line: line[0] != '#',graph_file.readlines()))
    n_vertices = int(lines[0])
    n_edges = int(lines[1])
    edges = []
    for edge in range(2,len(lines)):
        vertices = lines[edge].split(' ')
        edges.append((int(vertices[0]),int(vertices[1])))
    graph_file.close()
    return Graph(n_vertices,n_edges,edges)

# Function to read scenario_file and set up scenario on respective graph
def process_scenario(scenario_file,graph):
    lines = list(filter(lambda line: line[0] != '#',scenario_file.readlines()))
    n_agents = int(lines[0])
    agent_start_positions = []
    agent_goal_positions = []
    for i in range(2,len(lines) - n_agents - 1):
        pos = lines[i].split(' ')
        agent_start_positions.append((int(pos[0]),int(pos[1])))
    for i in range(len(lines) - n_agents,len(lines)):
        pos = lines[i].split(' ')
        agent_goal_positions.append((int(pos[0]),int(pos[1])))
    graph.set_scenario(n_agents,agent_start_positions,agent_goal_positions)
    scenario_file.close()

def build_minizinc(graph_file,scenario_file):
    graph = process_graph(graph_file)
    process_scenario(scenario_file,graph)
    mapf = Model("./proj.mzn")
    gecode = Solver.lookup("gecode") # GECODE ??
    MAX_TIMESTEP = 1
    n_agents = graph.get_n_agents()
    # SERÁ QUE DÁ PARA INICIALIZAR A INSTANCIA ANTES DO CICLO E A CADA ITERAÇÃO MUDAR SÓ O MAX_TIMETSTEP?
    for ts in range(0,MAX_TIMESTEP):
        instance = Instance(gecode, mapf)
        instance["n_vertices"] = 4
        instance["n_agents"] = 1
        instance["max_timestep"] = 2
        initial_positions = [0 for x in range(n_agents)]
        goal_positions = [0 for x in range(n_agents)]
        initial_scenario_positions = graph.get_start_positions()
        goal_scenario_positions = graph.get_goal_positions()
        for pos in range(n_agents):
            initial_positions[initial_scenario_positions[pos][0] - 1] = initial_scenario_positions[pos][1]
            goal_positions[goal_scenario_positions[pos][0] - 1] = goal_scenario_positions[pos][1]
        instance["initial_positions"] = [1]
        instance["goal_positions"] = [4]
        instance["edges"] = [[1,1,1,1], [1,1,1,1], [1,1,1,1], [1,1,1,1]]
        result = instance.solve()
        print(result)
    return graph

def main():
    graph = build_minizinc(graph_file,scenario_file)
    print(graph)

if __name__ == "__main__":
    main()

