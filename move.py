def get_pos():
	return get_pos_x(), get_pos_y()

def min_distance_with_direction(x1, y1, x2, y2):
	world_size = get_world_size()

	dx = (x2 - x1) % world_size

	if dx <= world_size // 2:
		dist_x, dir_x = dx, East
	else:
		dist_x, dir_x = world_size - dx, West

	dy = (y2 - y1) % world_size

	if dy <= world_size // 2:
		dist_y, dir_y = dy, North
	else:
		dist_y, dir_y = world_size - dy, South
	
	return dist_x, dir_x, dist_y, dir_y

def step_toward(target_x, target_y):
	curr_x, curr_y = get_pos()

	dx = target_x - curr_x
	dy = target_y - curr_y

	if dx > 0 and move(East):
		return True
	if dx < 0 and move(West):
		return True
	if dy > 0 and move(North):
		return True
	if dy < 0 and move(South):
		return True

	return False

def predict_pos(d, x, y):
	if d == North:
		return x, y + 1
	if d == South:
		return x, y - 1
	if d == East:
		return x + 1, y
	return x - 1, y

def axis_distance(a, b, wrap):
	d = abs(a - b)

	if not wrap:
		return d

	world_size = get_world_size()

	return min(d, world_size - d)

def best_step_toward(target_x, target_y, wrap=False):
	world_size = get_world_size()
	curr_x, curr_y = get_pos()

	best_dir = None
	best_dist = -1

	for d in [North, East, South, West]:
		if not can_move(d):
			continue

		new_x, new_y = predict_pos(d, curr_x, curr_y)

		if wrap:
			new_x = new_x % world_size
			new_y = new_y % world_size

		dist = axis_distance(target_x, new_x, wrap) + axis_distance(target_y, new_y, wrap)

		if best_dist == -1 or dist < best_dist:
			best_dist = dist
			best_dir = d

	if best_dir == None:
		return False

	return move(best_dir)

def move_to(target_x, target_y):
	dist_x, dir_x, dist_y, dir_y = min_distance_with_direction(
		get_pos_x(), get_pos_y(), target_x, target_y
	)

	for _ in range(dist_x):
		move(dir_x)
	
	for _ in range(dist_y):
		move(dir_y)

def go_home():
	move_to(0, 0)

def move_grid(fn, x_range=None, y_range=None):
	world_size = get_world_size()
	
	if x_range == None:
		x_range = (0, world_size)
	if y_range == None:
		y_range = (0, world_size)
	
	n = 0
	while True:
		for x in range(x_range[0], x_range[1]):
			for y in range(y_range[0], y_range[1]):
				move_to(x, y)
				fn(x, y, n)
		n += 1
		

	