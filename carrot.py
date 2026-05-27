from crop import plant_crop, harvest_crop, untill_crop
from item import water_crop
from move import move_grid
from farm_wood import plant_wood


def plant_carrot():
	return plant_crop(Entities.Carrot)

def farm_carrot_step(x, y, n):
	harvest_crop()

 # TODO replace with get_cost
	if num_items(Items.Hay) < 512:
		untill_crop()
		water_crop()
	elif num_items(Items.Wood) < 512:
		plant_wood(x, y, n)
		water_crop()
	else:
		plant_carrot()
		water_crop()

def farm_carrot():
	world_size = get_world_size()
	workers = min(max_drones(), world_size)
	strip_width = world_size // workers

	for i in range(workers - 1):
		x_start = i * strip_width
		x_end = (i + 1) * strip_width
		spawn_drone(move_grid, farm_carrot_step, (x_start, x_end), (0, world_size))

	main_x_start = (workers - 1) * strip_width
	move_grid(farm_carrot_step, (main_x_start, world_size), (0, world_size))
