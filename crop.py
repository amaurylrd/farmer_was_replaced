def can_till() -> bool:
	return get_ground_type() != Grounds.Soil

def untill_crop():
	if not can_till():
		return till()
	return False

def can_plant(crop):
	cost = get_cost(crop)

	for item in cost:
		if num_items(item) < cost[item]:
			return False
	return True

crop_needs_foil = {Entities.Carrot, Entities.Pumpkin, Entities.Sunflower, Entities.Cactus}

def plant_crop(crop):
	if crop in crop_needs_foil and can_till():
		till()

	return can_plant(crop) and plant(crop)

def harvest_crop():
	return can_harvest() and harvest()

def has_cost(crop):
	cost = get_cost(crop)

	if cost == None:
		return False

	for item in cost:
		if num_items(item) < cost[item]:
			return False
	return True
