
from crop import plant_crop, harvest_crop
from move import move_grid


def plant_bush():
	return plant_crop(Entities.Bush)


def plant_wood(x, y):
	if (x + y) % 2 == 0:
		return plant_crop(Entities.Tree)
	return plant_bush()


def farm_wood_step(x, y, n):
	harvest_crop()
	plant_wood(x, y)


def farm_wood():
	world_size = get_world_size()
	workers = max_drones()

	if workers > world_size:
		workers = world_size

	strip_width = world_size // workers

	for i in range(workers - 1):
		x_start = i * strip_width
		x_end = (i + 1) * strip_width
		spawn_drone(move_grid, farm_wood_step, (x_start, x_end), (0, world_size))

	main_x_start = (workers - 1) * strip_width
	move_grid(farm_wood_step, (main_x_start, world_size), (0, world_size))


if __name__ == "__main__":
	farm_wood()
