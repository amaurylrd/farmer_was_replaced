from crop import untill_crop, harvest_crop
from move import move_to, go_home
from drone import wait_until_harvestable
from farm_carrot import farm_carrot_step
from farm_cactus import parallel_plant_cactus, sort_cactus_field
from farm_wood import farm_wood_step
from farm_maze import farm_treasure


companions = {}

def set_companion(x, y):
	companion = get_companion()

	if companion:
		target_entity, target_pos = companion
		companions[target_pos] = (x, y)


M = 1000000
B = M * 1000

objectives = {
	Items.Hay: B,
	Items.Wood: 10 * B,
	Items.Carrot: B,
	Items.Cactus: B,
	Items.Gold: 100 * M,
}


def farm_hay(x, y, n):
	untill_crop()
	harvest_crop()


def sweep_strip(step_fn, x_start, x_end, n):
	world_size = get_world_size()

	for x in range(x_start, x_end):
		for y in range(world_size):
			move_to(x, y)
			step_fn(x, y, n)


def parallel_sweep(step_fn, n):
	world_size = get_world_size()
	workers = min(max_drones(), world_size)
	strip_width = world_size // workers

	drones = []

	for i in range(1, workers - 1):
		d = spawn_drone(sweep_strip, step_fn, i * strip_width, (i + 1) * strip_width, n)
		if d != None:
			append(drones, d)

	if workers > 1:
		d = spawn_drone(sweep_strip, step_fn, (workers - 1) * strip_width, world_size, n)
		if d != None:
			append(drones, d)

	sweep_strip(step_fn, 0, strip_width, n)

	for d in drones:
		wait_for(d)


def farm_hay_round(n):
	parallel_sweep(farm_hay, n)


def farm_wood_round(n):
	parallel_sweep(farm_wood_step, n)


def farm_carrot_round(n):
	parallel_sweep(farm_carrot_step, n)


def farm_cactus_round(n):
	parallel_plant_cactus()
	sort_cactus_field()
	go_home()
	wait_until_harvestable()
	harvest_crop()


def farm_gold_round(n):
	farm_treasure()


rounds = {
	Items.Hay: farm_hay_round,
	Items.Wood: farm_wood_round,
	Items.Carrot: farm_carrot_round,
	Items.Cactus: farm_cactus_round,
	Items.Gold: farm_gold_round,
}


def farm_until_top_hat():
	while num_unlocked(Unlocks.Top_Hat) == 0:
		for item in objectives:
			n = 0

			while num_items(item) < objectives[item]:
				rounds[item](n)
				n += 1

				if num_unlocked(Unlocks.Top_Hat) > 0:
					return

		if not unlock(Unlocks.Top_Hat):
			print("objectifs atteints mais unlock a échoué — ajuste le dict objectives")
			return


if __name__ == "__main__":
	farm_until_top_hat()