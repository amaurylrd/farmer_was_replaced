from crop import harvest_crop, plant_crop
from move import go_home, move_to
from drone import wait_until_harvestable


def plant_cactus():
	return plant_crop(Entities.Cactus)


def is_cactus_sorted(direction):
	return measure() <= measure(direction)


def plant_cactus_column(x_col):
	world_size = get_world_size()

	for y in range(world_size):
		move_to(x_col, y)

		if get_entity_type() != Entities.Cactus:
			plant_cactus()


def plant_cactus_subregion(x_start, x_end):
	for x in range(x_start, x_end):
		plant_cactus_column(x)


def parallel_plant_cactus():
	world_size = get_world_size()
	workers = min(max_drones(), world_size)
	strip_width = world_size // workers

	drones = []

	for i in range(1, workers - 1):
		drone = spawn_drone(plant_cactus_subregion, i * strip_width, (i + 1) * strip_width)
		if drone != None:
			append(drones, drone)

	if workers > 1:
		drone = spawn_drone(plant_cactus_subregion, (workers - 1) * strip_width, world_size)
		if drone != None:
			append(drones, drone)

	plant_cactus_subregion(0, strip_width)

	for drone in drones:
		wait_for(drone)


def sort_row(y):
	world_size = get_world_size()
	swapped = True

	while swapped:
		swapped = False
		move_to(0, y)

		for _ in range(world_size - 1):
			if not is_cactus_sorted(East):
				swap(East)
				swapped = True
			move(East)


def sort_column(x):
	world_size = get_world_size()
	swapped = True

	while swapped:
		swapped = False
		move_to(x, 0)

		for _ in range(world_size - 1):
			if not is_cactus_sorted(North):
				swap(North)
				swapped = True
			move(North)


def parallel_sort(sort_fn):
	world_size = get_world_size()
	drones = []
	main_indices = []

	for i in range(1, world_size):
		drone = spawn_drone(sort_fn, i)

		if drone != None:
			append(drones, drone)
		else:
			append(main_indices, i)

	sort_fn(0)

	for i in main_indices:
		sort_fn(i)

	for drone in drones:
		wait_for(drone)


def sort_cactus_field():
	parallel_sort(sort_row)
	parallel_sort(sort_column)


def farm_cactus():
	while True:
		parallel_plant_cactus()
		sort_cactus_field()

		go_home()
		wait_until_harvestable()
		harvest_crop()
  
if __name__ == "__main__":
	farm_cactus()
