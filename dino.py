from move import best_step_toward, move_to
from farm_cactus import run_blocks


def hamilton_direction():
	world_size = get_world_size()
	x = get_pos_x()
	y = get_pos_y()

	if y == 0:
		if x > 0:
			return West
		return North

	if x % 2 == 0:
		if y < world_size - 1:
			return North
		return East

	if y > 1:
		return South

	if x < world_size - 1:
		return East

	return South

def hamilton_step():
	preferred = hamilton_direction()

	if can_move(preferred):
		return move(preferred)

	for d in [North, East, South, West]:
		if d != preferred and can_move(d):
			return move(d)

	return False

def farm_bones():
	world_size = get_world_size()

	while True:
		change_hat(Hats.Dinosaur_Hat)
		apple = [None, None]
		apples_eaten = 0
		use_hamilton = False

		while True:
			pos = measure()

			if pos != None:
				apple[0] = pos[0]
				apple[1] = pos[1]
				apples_eaten = apples_eaten + 1

				if apples_eaten >= world_size:
					use_hamilton = True

			if apple[0] != None:
				tx = apple[0]
				ty = apple[1]
				curr_x = get_pos_x()
				curr_y = get_pos_y()

				if not use_hamilton or curr_x == tx or curr_y == ty:
					if best_step_toward(tx, ty):
						continue

					use_hamilton = True

			if not hamilton_step():
				break

		change_hat(Hats.Straw_Hat)


# ---------------------------------------------------------------------------
# Optimized bone farming
#
# Rules that drive the design (docs/unlocks/dinosaurs.md):
#   - removing the hat pays tail_length ** 2 bones
#   - move() costs 400 ticks while the dinosaur hat is on, reduced by 3%
#     (floored) per apple eaten, so it bottoms out at 33 ticks
#   - measure() while standing on an apple returns the next apple position,
#     for 1 tick
#   - the border does not wrap while the hat is on
#   - an apple cannot spawn on a tile where something is planted
#
# Only the number of move() calls matters. The snake walks a hamiltonian cycle
# over the farm, so it can never trap itself and always ends up filling the
# field: length = size ** 2 and bones = size ** 4. Shortcuts jump forward along
# the cycle whenever the jump stays behind the tail, which is what makes the
# early game fast. Everything is O(1) per step, no path finding.
# ---------------------------------------------------------------------------

DINO_DIRS = [North, East, South, West]
DINO_DX = [0, 1, 0, -1]
DINO_DY = [1, 0, -1, 0]


def cycle_index(x, y, size):
	# Position of a tile along the cycle walked by cycle_step().
	if x == 0:
		return y

	if y == 0:
		return size + (size - 1) * (size - 1) + (size - 1 - x)

	base = size + (x - 1) * (size - 1)

	if x % 2 == 1:
		return base + (size - 1 - y)

	return base + (y - 1)


def cycle_step(x, y, size):
	# Column 0 upwards, then every column up and down, then row 0 back West.
	if y == 0:
		if x > 0:
			return 3
		return 0

	if x % 2 == 0:
		if y < size - 1:
			return 0
		return 1

	if y > 1:
		return 2

	if x < size - 1:
		return 1

	return 2


def clear_rows(y_start, y_end, size):
	for y in range(y_start, y_end):
		move_to(0, y)

		for _ in range(size):
			if get_entity_type() != None:
				clear()

			move(East)


def clear_field(size):
	# Apples do not spawn on planted tiles, so the farm must be empty first.
	run_blocks(clear_rows, size)


def dino_game(size, deadline=None):
	# The cycle only closes on an even side.
	total = size * size

	change_hat(Hats.Dinosaur_Hat)

	x = get_pos_x()
	y = get_pos_y()
	head = cycle_index(x, y, size)
	cell = x * size + y

	occupied = set()
	add(occupied, cell)

	# Ring buffer of the tail cells, at most `total` of them.
	body = []
	for _ in range(total):
		append(body, 0)

	body[0] = cell
	head_at = 1 % total
	tail_at = 0

	length = 1
	grow = False
	moves = 0

	target = measure()
	tx = -1
	ty = -1

	if target != None:
		tx = target[0]
		ty = target[1]

	while True:
		if deadline != None and get_time() > deadline:
			break

		tail_cell = body[tail_at]
		tail_idx = cycle_index(tail_cell // size, tail_cell % size, size)

		room = tail_idx - head
		if room <= 0:
			room += total

		# room - 1 would let the head park right behind its own tail, which
		# kills the snake on the next apple. Two tiles of margin remove it.
		max_gain = room - 3

		# Near the end the cycle order is the only safe order.
		if total - length < 2 * size:
			max_gain = 1

		if tx >= 0:
			to_apple = cycle_index(tx, ty, size) - head
			if to_apple < 0:
				to_apple += total
			if to_apple > 0 and to_apple < max_gain:
				max_gain = to_apple

		step = -1
		best_gain = 0

		for i in range(4):
			nx = x + DINO_DX[i]
			ny = y + DINO_DY[i]

			if nx < 0 or ny < 0 or nx >= size or ny >= size:
				continue

			next_cell = nx * size + ny

			if next_cell in occupied:
				# The last segment moves out of the way, unless we just ate.
				if grow or next_cell != tail_cell:
					continue

			gain = cycle_index(nx, ny, size) - head
			if gain < 0:
				gain += total

			if gain < 1 or gain > max_gain:
				continue

			if gain > best_gain:
				best_gain = gain
				step = i

		if step < 0:
			step = cycle_step(x, y, size)

			# The cycle successor is free unless a shortcut left a segment
			# there. Take any free neighbour rather than dying.
			nx = x + DINO_DX[step]
			ny = y + DINO_DY[step]
			next_cell = nx * size + ny

			if next_cell in occupied:
				if grow or next_cell != tail_cell:
					for i in range(4):
						nx = x + DINO_DX[i]
						ny = y + DINO_DY[i]

						if nx < 0 or ny < 0 or nx >= size or ny >= size:
							continue

						next_cell = nx * size + ny

						if next_cell in occupied:
							if grow or next_cell != tail_cell:
								continue

						step = i
						break

		if not move(DINO_DIRS[step]):
			break

		moves += 1
		x += DINO_DX[step]
		y += DINO_DY[step]
		head = cycle_index(x, y, size)
		cell = x * size + y

		if grow:
			grow = False
			length += 1
		else:
			remove(occupied, body[tail_at])
			tail_at += 1
			if tail_at >= total:
				tail_at = 0

		add(occupied, cell)
		body[head_at] = cell
		head_at += 1
		if head_at >= total:
			head_at = 0

		if length >= total:
			break

		if x == tx and y == ty:
			grow = True
			target = measure()

			if target == None:
				break

			tx = target[0]
			ty = target[1]

	change_hat(Hats.Straw_Hat)

	return length, moves


def farm_bones_fast(size=None):
	if size != None:
		set_world_size(size)

	world = get_world_size()

	if world % 2 == 1:
		set_world_size(world - 1)
		world = get_world_size()

	clear_field(world)

	while True:
		dino_game(world)


def bench_bones(duration=60, size=None):
	if size != None:
		set_world_size(size)

	world = get_world_size()

	# The hamiltonian cycle needs an even side length.
	if world % 2 == 1:
		set_world_size(world - 1)
		world = get_world_size()

	set_execution_speed(1000000)
	clear_field(world)

	start = get_time()
	start_ticks = get_tick_count()
	before = num_items(Items.Bone)

	games = 0
	moves = 0
	best = 0
	elapsed = 0

	while elapsed < duration:
		length, game_moves = dino_game(world, start + duration)
		games += 1
		moves += game_moves

		if length > best:
			best = length

		elapsed = get_time() - start
		quick_print(num_items(Items.Bone) - before, "bones /", elapsed, "s")

	bones = num_items(Items.Bone) - before
	ticks = get_tick_count() - start_ticks

	quick_print("=== bench bones ===")
	quick_print("world size  :", world)
	quick_print("duration    :", elapsed, "s")
	quick_print("games       :", games)
	quick_print("best length :", best)
	quick_print("moves       :", moves)
	quick_print("bones       :", bones)
	quick_print("bones/min   :", bones * 60 / elapsed)
	quick_print("ticks       :", ticks)
	quick_print("ticks/move  :", ticks / moves)

	return bones


if __name__ == "__main__":
	bench_bones(60)
