from farm_wood import plant_bush

directions = [North, East, South, West]
opposite_directions = {North: South, South: North, East: West, West: East}

def on_treasure():
	return get_entity_type() == Entities.Treasure

def next_pos(x, y, d):
	if d == North:
		return x, y + 1
	if d == South:
		return x, y - 1
	if d == East:
		return x + 1, y
	if d == West:
		return x - 1, y

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

maze_state = {"visited": set(), "found": False, "gen": 0}

def is_active(gen):
	return gen == maze_state["gen"] and not maze_state["found"]

def explore_step(direction, gen):
	if not is_active(gen):
		# Arrêt immédiat du drone si le labyrinthe n'est plus actif
		return

	if not move(direction):
		# Arrêt immédiat si le mouvement n'est pas possible ou labyrinthe fini
		return

	if not is_active(gen):
		# Arrêt immédiat du drone si le labyrinthe a disparu entre temps
		return

	came_from = opposite_directions[direction]

	if on_treasure():
		maze_state["found"] = True
		harvest()
		return

	x = get_pos_x()
	y = get_pos_y()
	branches = []

	for d in directions:
		if d != came_from and can_move(d):
			target = next_pos(x, y, d)
			if target not in maze_state["visited"]:
				add(maze_state["visited"], target)
				append(branches, d)

	if len(branches) == 0:
		if is_active(gen):
			move(came_from)
		return

	main_branches = []

	for i in range(1, len(branches)):
		if not is_active(gen):
			break

		drone = spawn_drone(explore_step, branches[i], gen)

		if drone == None:
			append(main_branches, branches[i])

	if is_active(gen):
		explore_step(branches[0], gen)

	for branch in main_branches:
		if not is_active(gen):
			break

		explore_step(branch, gen)

	if is_active(gen):
		move(came_from)

def parallel_explore_maze():
	maze_state["gen"] = maze_state["gen"] + 1
	maze_state["visited"] = set()
	maze_state["found"] = False

	gen = maze_state["gen"]

	add(maze_state["visited"], (get_pos_x(), get_pos_y()))

	if on_treasure():
		maze_state["found"] = True
		harvest()
		return True

	start_x = get_pos_x()
	start_y = get_pos_y()
	valid_dirs = []

	for d in directions:
		if can_move(d):
			target = next_pos(start_x, start_y, d)
			if target not in maze_state["visited"]:
				add(maze_state["visited"], target)
				append(valid_dirs, d)

	if len(valid_dirs) == 0:
		return False

	main_dirs = []

	for i in range(1, len(valid_dirs)):
		if not is_active(gen):
			break

		drone = spawn_drone(explore_step, valid_dirs[i], gen)

		if drone == None:
			append(main_dirs, valid_dirs[i])

	if is_active(gen):
		explore_step(valid_dirs[0], gen)

	for d in main_dirs:
		if not is_active(gen):
			break

		explore_step(d, gen)

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

def farm_treasure(x, y, n):
	plant_bush()
	solve_maze()