class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities):
        monster = self.owner
        results = []
        if fov_map.fov[monster.y][monster.x]:
            if monster.distance_to(target) >= 2: #Minimum distance 2, including the enemy's and its own square
                monster.move_astar(target, entities, game_map) #Moves with the A* algorithm

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target) #Automatically attacks the target
                results.extend(attack_results)

        return results