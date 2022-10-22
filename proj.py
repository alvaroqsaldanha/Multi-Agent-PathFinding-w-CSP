# Search And Planning Project 2022/2023
# Alvaro Saldanha, 92416
# Vasco Cabral, 92568

import sys
from minizinc import Instance, Model, Solver

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

# Function to output found solution to text file
def build_solution(solution):
    for ts in range(0,len(solution)):
        line = "i=" + str(ts) + "   "
        for agent in range(len(solution[ts])):
            line += str(agent+1) + ":" + str(solution[ts][agent]) + " "
        print(line)

def build_minizinc(graph_file,scenario_file):
    graph = process_graph(graph_file)
    process_scenario(scenario_file,graph)
    mapf = Model("./proj.mzn")
    chuffed = Solver.lookup("chuffed")
    MAX_TIMESTEP = 60
    n_agents = graph.get_n_agents()
    ts = 2
    found_solution = None
    while ts < MAX_TIMESTEP + 1:
        instance = Instance(chuffed, mapf)
        instance["n_vertices"] = graph.get_n_vertices()
        instance["n_agents"] = n_agents
        instance["max_timestep"] = ts
        initial_positions = [0 for x in range(n_agents)]
        goal_positions = [0 for x in range(n_agents)]
        initial_scenario_positions = graph.get_start_positions()
        goal_scenario_positions = graph.get_goal_positions()
        for pos in range(n_agents):
            initial_positions[initial_scenario_positions[pos][0] - 1] = initial_scenario_positions[pos][1]
            goal_positions[goal_scenario_positions[pos][0] - 1] = goal_scenario_positions[pos][1]
        if initial_positions == goal_positions:
            build_solution([goal_positions])
            break
        instance["initial_positions"] = initial_positions
        instance["goal_positions"] = goal_positions
        instance["edges"] = graph.get_adj_matrix()
        result = instance.solve()
        if result.solution != None and found_solution == None:
            found_solution = result["position_at_ts"]
            #print("\nSolution found for timestep " + str(ts) + ".\n")
            ts -= 1
            if ts == 1:
                build_solution(found_solution)
                break
            continue
        elif result.solution == None and found_solution != None:
            build_solution(found_solution)
            return
        elif result.solution != None:
            #print("\nSolution found for timestep " + str(ts) + ".\n")
            build_solution(result["position_at_ts"])
            return
        else:
            #print("No solution found for timestep " + str(ts) + ".")
            ts += 2
            continue
    return graph

def main():
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
    build_minizinc(graph_file,scenario_file)

if __name__ == "__main__":
    main()
