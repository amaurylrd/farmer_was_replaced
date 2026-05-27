from crop import plant_crop, harvest_crop
from move import go_home, move_to


def plant_pumpkin():
	return plant_crop(Entities.Pumpkin)


def replant_pumpkin():
	if get_entity_type() != Entities.Pumpkin:
		return plant_pumpkin()
	return False


def fill_column(x_col):
	world_size = get_world_size()
	all_ready = False

	while not all_ready:
		all_ready = True

		for y in range(world_size):
			move_to(x_col, y)

			if replant_pumpkin() or not can_harvest():
				all_ready = False


def fill_subregion(x_start, x_end):
	for x in range(x_start, x_end):
		fill_column(x)


def farm_pumpkin():
	world_size = get_world_size()
	workers = min(max_drones(), world_size)
	strip_width = world_size // workers

	while True:
		drones = []

		for i in range(1, workers - 1):
			drone = spawn_drone(fill_subregion, i * strip_width, (i + 1) * strip_width)

			if drone != None:
				append(drones, drone)

		if workers > 1:
			drone = spawn_drone(fill_subregion, (workers - 1) * strip_width, world_size)
			if drone != None:
				append(drones, drone)

		fill_subregion(0, strip_width)

		for drone in drones:
			wait_for(drone)

		go_home()
		harvest_crop()


if __name__ == "__main__":
	farm_pumpkin()
