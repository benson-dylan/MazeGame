def check_collision(self, player_min, player_max, wall_min, wall_max):
        overlap_x = (wall_min[0] < player_max[0]) and (player_min[0] < wall_max[0])
        overlap_y = (wall_min[1] < player_max[1]) and (player_min[1] < wall_max[1])
        overlap_z = (wall_min[2] < player_max[2]) and (player_min[2] < wall_max[2])
        return overlap_x and overlap_y and overlap_z

    
    def move_player(self, dPos):
        dPos = np.array(dPos, dtype=np.float32)
        new_position = self.player.position + dPos
        player_min_corner, player_max_corner = self.player.get_bounding_box()
        player_min_corner += dPos
        player_max_corner += dPos
        collision = False
        for wall_box in self.mazeGenerator.wall_boxes:
            wall_min_corner = wall_box['position'] - wall_box['size'] / 2
            wall_max_corner = wall_box['position'] + wall_box['size'] / 2
            if self.check_collision(player_min_corner, player_max_corner, wall_min_corner, wall_max_corner):
                collision = True
                break
        if not collision:
            self.player.position = new_position
            current_time = time.time()
            if current_time - self.last_footstep_time >= self.footstep_delay:
                self.play(self.sound.player_move)
                self.last_footstep_time = current_time