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
	n_cactus = num_items(Items.Cactus)
	start = get_time()

	# while True:
	set_execution_speed(1000000)
	parallel_plant_cactus()
	sort_cactus_field()

	# go_home()
	wait_until_harvestable()
	harvest_crop()

	n_cactus -= num_items(Items.Cactus)
	dt = get_time() - start

	print(n_cactus + " en " + dt)


# ---------------------------------------------------------------------------
# Optimized cactus farm
#
# Principle: a cactus field sorted on both axes (sizes non-decreasing towards
# East and towards North) is harvested in a single harvest() call with the
# sorted bonus.
#
# Tick economics that drive every choice below:
#   move / swap / plant / till / harvest / spawn_drone : 200 ticks
#   measure / get_* / can_harvest / append             : 1 tick
#   arithmetic, comparisons, indexing                  : free
#
# So the cost of a cycle is "number of moves + swaps", and reading the field
# is practically free. The strategy is therefore: measure once, plan the whole
# sort offline on a local list, then walk the row only where a swap is really
# needed.
#
# Versus the naive bubble sort:
#   - the sizes are recorded while planting, so the sort starts with the full
#     row already known and never measures again
#   - the swap schedule is computed offline (cocktail sort with shrinking
#     bounds), so there is no verification pass and no walking past the last
#     swap of a sweep
#   - work is split in contiguous blocks over max_drones() - num_drones() + 1
#     workers, instead of one drone per line with every refused spawn dumped
#     on the main thread
#   - contiguous blocks mean one single move between two consecutive lines
# ---------------------------------------------------------------------------


def plan_sort(values, size):
	plan = []
	low = 0
	high = size - 1

	while low < high:
		last = low

		for i in range(low, high):
			if values[i] > values[i + 1]:
				v = values[i]
				values[i] = values[i + 1]
				values[i + 1] = v
				append(plan, i)
				last = i

		high = last

		if low >= high:
			break

		last = high

		for i in range(high - 1, low - 1, -1):
			if values[i] > values[i + 1]:
				v = values[i]
				values[i] = values[i + 1]
				values[i + 1] = v
				append(plan, i)
				last = i

		low = last

	return plan


def apply_plan(plan, forward, backward):
	pos = 0

	for target in plan:
		while pos < target:
			move(forward)
			pos += 1

		while pos > target:
			move(backward)
			pos -= 1

		swap(forward)

	return pos


def plant_and_read_row(y, size):
	move_to(0, y)
	values = []

	for _ in range(size):
		if get_ground_type() != Grounds.Soil:
			till()

		plant(Entities.Cactus)
		append(values, measure())
		move(East)

	return values


def read_column(x, size):
	move_to(x, 0)
	values = []

	for _ in range(size):
		append(values, measure())
		move(North)

	return values


def plant_sort_rows(y_start, y_end, size):
	for y in range(y_start, y_end):
		values = plant_and_read_row(y, size)
		plan = plan_sort(values, size)

		if len(plan) > 0:
			pos = apply_plan(plan, East, West)

			# Leave the drone on x = 0 so the next row costs one single move.
			while pos > 0:
				move(West)
				pos -= 1


def sort_columns(x_start, x_end, size):
	for x in range(x_start, x_end):
		values = read_column(x, size)
		plan = plan_sort(values, size)

		if len(plan) > 0:
			pos = apply_plan(plan, North, South)

			while pos > 0:
				move(South)
				pos -= 1


def split_blocks(size, workers):
	blocks = []
	start = 0
	base = size // workers
	extra = size % workers

	for w in range(workers):
		length = base

		if w < extra:
			length += 1

		if length > 0:
			append(blocks, (start, start + length))
			start += length

	return blocks


def run_blocks(block_fn, size):
	workers = max_drones() - num_drones() + 1

	if workers > size:
		workers = size
	if workers < 1:
		workers = 1

	blocks = split_blocks(size, workers)
	drones = []
	leftover = []

	for i in range(1, len(blocks)):
		block = blocks[i]
		drone = spawn_drone(block_fn, block[0], block[1], size)

		if drone == None:
			append(leftover, block)
		else:
			append(drones, drone)

	first = blocks[0]
	block_fn(first[0], first[1], size)

	for block in leftover:
		block_fn(block[0], block[1], size)

	for drone in drones:
		wait_for(drone)


# Ticks spent in the last cycle, per phase. get_tick_count() costs 0 tick, so
# the instrumentation is free.
rows_ticks = 0
cols_ticks = 0
harvest_ticks = 0


def fast_cactus_cycle(size):
	global rows_ticks
	global cols_ticks
	global harvest_ticks

	# Rows first: sorting the columns afterwards keeps the rows sorted, so the
	# field ends up non-decreasing on both axes.
	t0 = get_tick_count()
	run_blocks(plant_sort_rows, size)

	t1 = get_tick_count()
	run_blocks(sort_columns, size)

	t2 = get_tick_count()

	while not can_harvest():
		pass

	harvest()

	t3 = get_tick_count()
	rows_ticks = t1 - t0
	cols_ticks = t2 - t1
	harvest_ticks = t3 - t2




def bench_cactus(duration=60):
	size = get_world_size()
	set_execution_speed(1000000)

	start = get_time()
	start_ticks = get_tick_count()
	before = num_items(Items.Cactus)

	cycles = 0
	elapsed = 0

	while elapsed < duration:
		fast_cactus_cycle(size)
		cycles += 1
		elapsed = get_time() - start

		quick_print(num_items(Items.Cactus) - before, "cactus /", elapsed, "s")

	harvested = num_items(Items.Cactus) - before
	ticks = get_tick_count() - start_ticks

	quick_print("=== bench cactus ===")
	quick_print("world size  :", size)
	quick_print("max drones  :", max_drones())
	quick_print("plant+rows  :", rows_ticks, "ticks (last cycle)")
	quick_print("columns     :", cols_ticks, "ticks (last cycle)")
	quick_print("wait+harvest:", harvest_ticks, "ticks (last cycle)")
	quick_print("duration    :", elapsed, "s")
	quick_print("cycles      :", cycles)
	quick_print("harvested   :", harvested)
	quick_print("cactus/s    :", harvested / elapsed)
	quick_print("cactus/cycle:", harvested / cycles)
	quick_print("ticks       :", ticks)
	quick_print("cactus/tick :", harvested / ticks)

	return harvested


def fast_farm_cactus(target=20000000):
	size = get_world_size()
	set_execution_speed(1000000)

	start = get_time()
	before = num_items(Items.Cactus)
	harvested = 0

	while harvested < target:
		fast_cactus_cycle(size)

		harvested = num_items(Items.Cactus) - before
		quick_print(harvested, "cactus in", get_time() - start)

	return harvested


if __name__ == "__main__":
	bench_cactus(60)
