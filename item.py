def can_use_item(item, n=1):
	return num_items(item) >= n

def water_crop(threshold=0.5, n=1):
	if get_entity_type() != None and get_water() < threshold and can_use_item(Items.Water, n):
		return use_item(Items.Water, n)
	return False

def fertilize_crop(n=1):
	entity_type = get_entity_type()

	if entity_type == None:
		return False

	if entity_type != Entities.Bush and can_harvest():
		return False

	return can_use_item(Items.Fertilizer, n) and use_item(Items.Fertilizer, n)

def cure_crop():
	if get_entity_type() != None and can_use_item(Items.Weird_Substance):
		return use_item(Items.Weird_Substance)
	return False


