import tcod as libtcod

def initialize_fov(game_map):
    fov_map = libtcod.map_new(game_map.width, game_map.height) #Makes a fov map of the entire game map

    for y in range(game_map.height):
        for x in range(game_map.width):
            fov_map.transparent[y][x] = not game_map.tiles[x][y].block_sight    #Makes a coordinate system of all the tiles that block sight
            fov_map.walkable[y][x] = not game_map.tiles[x][y].blocked           #Makes a coordinate system of all the tiles that block movement

    return fov_map

def recompute_fov(fov_map, x, y, radius, light_walls, algorithm=0):
    fov_map.compute_fov(x, y, radius, light_walls, algorithm) #Updates the map. Takes FOV center position (usually player), size of fov,
                                                              #whether it affects visibility, and the used algorithm - http://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds
