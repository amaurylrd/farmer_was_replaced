from farm_wood import plant_bush

directions = [North, East, South, West]
opposite_directions = {North: South, South: North, East: West, West: East}

def on_treasure():
	return get_entity_type() == Entities.Treasure

def next_pos(x, y, d):
	w = get_world_size()
	if d == North:
		return x, (y + 1) % w
	if d == South:
		return x, (y - 1) % w
	if d == East:
		return (x + 1) % w, y
	if d == West:
		return (x - 1) % w, y

def explore_maze(pos=(0, 0), came_from=None, visited=None, graph=None):
	if visited == None:
		visited = set()
  
	if graph == None:
		graph = {}

	if pos in visited:
		return graph, False

	visited.add(pos)
		
	if on_treasure():
		return graph, True

	if pos not in graph:
		graph[pos] = []

	x, y = pos

	for d in directions:
		if came_from and d == came_from:
			continue

		if move(d):
			neighbor = next_pos(x, y, d)
			opposite = opposite_directions[d]
			
			if (d, neighbor) not in graph[pos]:
				graph[pos].append((d, neighbor))

				if neighbor not in graph:
					graph[neighbor] = []

				graph[neighbor].append((opposite, pos))
			
			graph, found = explore_maze(neighbor, opposite, visited, graph)

			if found:
				return graph, True
			
			move(opposite)

	return graph, False

maze_state = {"visited": set(), "found": False, "gen": 0, "drones": []}

def is_active(gen):
	return gen == maze_state["gen"] and not maze_state["found"]

def explore_step(direction, gen):
	if not is_active(gen):
		return

	if not move(direction):
		return

	came_from = opposite_directions[direction]

	while is_active(gen):
		if on_treasure():
			maze_state["found"] = True
			harvest()
			return

		x = get_pos_x()
		y = get_pos_y()
		next_dir = None

		for d in directions:
			if d == came_from:
				continue
			if not can_move(d):
				continue
			target = next_pos(x, y, d)
			if target in maze_state["visited"]:
				continue
			add(maze_state["visited"], target)
			if next_dir == None:
				next_dir = d
			else:
				if not is_active(gen):
					return
				drone = spawn_drone(explore_step, d, gen)
				if drone != None:
					append(maze_state["drones"], drone)

		if next_dir == None:
			return

		if not is_active(gen):
			return

		if not move(next_dir):
			return

		came_from = opposite_directions[next_dir]

def parallel_explore_maze():
	maze_state["gen"] = maze_state["gen"] + 1
	maze_state["visited"] = set()
	maze_state["found"] = False
	maze_state["drones"] = []

	gen = maze_state["gen"]

	add(maze_state["visited"], (get_pos_x(), get_pos_y()))

	if on_treasure():
		maze_state["found"] = True
		harvest()
		return True

	start_x = get_pos_x()
	start_y = get_pos_y()

	for d in directions:
		if not can_move(d):
			continue
		target = next_pos(start_x, start_y, d)
		if target in maze_state["visited"]:
			continue
		add(maze_state["visited"], target)
		drone = spawn_drone(explore_step, d, gen)

		if drone != None:
			append(maze_state["drones"], drone)

	i = 0
	while i < len(maze_state["drones"]):
		wait_for(maze_state["drones"][i])
		i = i + 1

	return maze_state["found"]

def solve_maze(size=None):
	if get_entity_type() != Entities.Bush:
		return False

	substance = num_items(Items.Weird_Substance)

	if substance <= 0:
		return False

	max_size = get_world_size()

	if size == None:
		size = max_size
	else:
		size = min(size, max_size)

	substance_needed = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)

	if substance < substance_needed:
		return False

	use_item(Items.Weird_Substance, substance_needed)

	return parallel_explore_maze()

def farm_treasure_step():
	plant_bush()
	solve_maze()
 
def farm_treasure():
	harvest()	

	while True:
		farm_treasure_step()
 
if __name__ == "__main__":
	farm_treasure()