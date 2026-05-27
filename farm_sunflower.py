from crop import plant_crop, harvest_crop
from move import move_grid
from item import water_crop, fertilize_crop


def plant_sunflower():
	return plant_crop(Entities.Sunflower)


def sunflower_step(x, y, n):
	harvest_crop()
	if get_entity_type() == None:
		plant_sunflower()
	water_crop(0.75)
	fertilize_crop()


def farm_sunflower():
	world_size = get_world_size()
	workers = min(max_drones(), world_size)
	strip_width = world_size // workers

	for i in range(workers - 1):
		x_start = i * strip_width
		x_end = (i + 1) * strip_width
		spawn_drone(move_grid, sunflower_step, (x_start, x_end), (0, world_size))

	main_x_start = (workers - 1) * strip_width
	move_grid(sunflower_step, (main_x_start, world_size), (0, world_size))


if __name__ == "__main__":
	change_hat(Hats.Sunflower_Hat)
	farm_sunflower()
