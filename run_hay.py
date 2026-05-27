from move import move_to, go_home
from crop import untill_crop, harvest_crop

TARGET = 100000000

go_home()
size = get_world_size()

while num_items(Items.Hay) < TARGET:
	for x in range(size):
		if num_items(Items.Hay) >= TARGET:
			break
		for y in range(size):
			move_to(x, y)
			untill_crop()
			harvest_crop()
