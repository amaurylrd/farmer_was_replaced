from crop import *
from move import *
from item import *
from f0 import *
from maze import *
from drone import *
from farm_cactus import *
from wood import *
from farm_pumpkin import *
from carrot import *
from dino import *

# harvest()

clear()
go_home()
change_hat(Hats.Purple_Hat)
# farm_carrot()

farm_bones()

# move_grid(farm_cactus)
# farm_cactus()

# move_grid(farm_treasure)
# farm_wood()
# farm_pumpkin()

# solving_maze = True

# def harvest_strategy(x, y, n):
# 	harvest_crop()

# 	if x >= 16:
# 		plant_pumpkin(x, y, n)
# 	if x >= 7:
# 		plant_carrot(x, y, n)
# 	elif x >= 5:
# 		plant_wood(x, y, n)
# 		if solving_maze:
# 			solve_maze()
# 	else:
# 		if get_ground_type() != Grounds.Grassland:
# 			till()
# 	water_crop()

# if solving_maze:
# 	move_grid(harvest_strategy)
# else:
# 	world_size = get_world_size()
# 	half = world_size // 2
# 	half_half = half // 2

# 	spawn_drone(move_grid, harvest_strategy, (0, half_half), (0, half))
# 	spawn_drone(move_grid, harvest_strategy, (0, half_half), (half, world_size))
# 	spawn_drone(move_grid, harvest_strategy, (half_half, half), (0, half))
# 	spawn_drone(move_grid, harvest_strategy, (half_half, half), (half, world_size))

# 	spawn_horizontal_regions(replant_pumpkin, half, 0, half, world_size, 3)
	
# 	move_grid(harvest_strategy, (half, world_size), (0, world_size))

