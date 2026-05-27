from move import move_grid


def can_spawn_drone():
	return num_drones() < max_drones()


def wait_until_harvestable():
	while not can_harvest():
		pass


def spawn_horizontal_regions(fn, start_x, start_y, width, height, num_drones):
	region_width = width // num_drones

	for i in range(num_drones):
		region_x = start_x + region_width * i
		region_y = region_x + region_width
	
		if can_spawn_drone():
			spawn_drone(move_grid, fn, (region_x, region_y), (start_y, start_y + height))

	