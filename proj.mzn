% Domain Variables

int: max_timestep;
int: n_vertices;
int: n_agents;
array[1..n_agents] of int: goal_positions;
array[1..n_agents] of int: initial_positions;
array[1..n_vertices,1..n_vertices] of int: edges;

% Decision Variables

array[1..max_timestep,1..n_agents] of var 1..n_vertices: position_at_ts;

% Constraints

include "alldifferent.mzn";

% Limiting initial positions to the scenario ones.
constraint forall(agent in 1..n_agents)(
  position_at_ts[1,agent] = initial_positions[agent]);
  
% Limiting final/goal positions to the scenario ones.
constraint forall(agent in 1..n_agents)(
  position_at_ts[max_timestep,agent] = goal_positions[agent]);
  
% All different agent positions at each timestep.
constraint forall(ts in 1..max_timestep)(
  all_different([position_at_ts[ts,agent] | agent in 1..n_agents])); 

% Agent position at timestamp ts is empty at timestamp ts-1.
constraint forall(ts in 2..max_timestep,agent in 1..n_agents)(
  forall(other_agent in 1..n_agents)(
  if agent != other_agent then
    position_at_ts[ts-1,other_agent] != position_at_ts[ts,agent]
  else
    true
  endif
  ));
  
% Agent position at timestamp is adjacent or same as timestamp - 1.
constraint forall(ts in 2..max_timestep, agent in 1..n_agents)(
  if position_at_ts[ts-1,agent] = position_at_ts[ts,agent] then
    true
  else
    edges[position_at_ts[ts-1,agent],position_at_ts[ts,agent]] = 1 
  endif  
  );
  
solve satisfy;


 
