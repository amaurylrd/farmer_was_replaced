from move import best_step_toward


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

if __name__ == "__main__":
	farm_bones()
