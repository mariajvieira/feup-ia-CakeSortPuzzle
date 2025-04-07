import copy


class Board:
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
    
    def is_valid_position(self, x, y):
        return 0 <= x < self.rows and 0 <= y < self.cols
    
    def is_empty(self, x, y):
        if not self.is_valid_position(x, y):
            return False
        return self.grid[x][y] is None
    
    def place_plate(self, x, y, plate):
        if not self.is_valid_position(x, y) or not self.is_empty(x, y):
            return False
        
        self.grid[x][y] = plate
        return True
    
    def optimize_plates(self, x1, y1, x2, y2):
        if not self.is_valid_position(x1, y1) or not self.is_valid_position(x2, y2):
            return False, []
        
        if self.is_empty(x1, y1) or self.is_empty(x2, y2):
            return False, []
        
        plate1 = self.grid[x1][y1]
        plate2 = self.grid[x2][y2]
        
        count1 = self._count_slice_types(plate1)
        count2 = self._count_slice_types(plate2)
        
        common_types = set(count1.keys()) & set(count2.keys())
        if not common_types:
            return False, []
        
        optimized = False
        movements = []
        
        for slice_type in common_types:
            if count1[slice_type] > 0 and count2[slice_type] > 0:
                if count1[slice_type] >= count2[slice_type]:
                    moved, count = self._move_slices(plate2, plate1, slice_type)
                    if moved:
                        optimized = True
                        movements.append((x2, y2, x1, y1, slice_type, count))
                else:
                    moved, count = self._move_slices(plate1, plate2, slice_type)
                    if moved:
                        optimized = True
                        movements.append((x1, y1, x2, y2, slice_type, count))
        
        return optimized, movements
    
    def _count_slice_types(self, plate):
        count = {}
        for slice_type in plate:
            if slice_type is not None:  
                count[slice_type] = count.get(slice_type, 0) + 1
        return count
    
    def _move_slices(self, source_plate, target_plate, slice_type):
        slices_to_move = source_plate.count(slice_type)
        if slices_to_move == 0:
            return False, 0
        
        empty_slots = target_plate.count(None)
        
        if empty_slots == 0:
            target_slices_of_type = target_plate.count(slice_type)
            if target_slices_of_type > 0:
                other_types = {}
                for s in target_plate:
                    if s is not None and s != slice_type:
                        other_types[s] = other_types.get(s, 0) + 1
                
                source_empty_slots = source_plate.count(None)
                
                if other_types and source_empty_slots >= min(other_types.values()):
                    other_type = min(other_types, key=other_types.get)
                    
                    moved = False
                    slices_moved = 0
                    
                    for i in range(len(target_plate)):
                        if target_plate[i] == other_type and source_empty_slots > 0:
                            target_plate[i] = None
                            
                            for j in range(len(source_plate)):
                                if source_plate[j] is None:
                                    source_plate[j] = other_type
                                    break
                            
                            source_empty_slots -= 1
                            moved = True
                    
                    empty_slots = target_plate.count(None)
                    slices_to_move = min(slices_to_move, empty_slots)
                    
                    for i in range(len(source_plate)):
                        if source_plate[i] == slice_type and slices_to_move > 0:
                            source_plate[i] = None
                            
                            for j in range(len(target_plate)):
                                if target_plate[j] is None:
                                    target_plate[j] = slice_type
                                    break
                            
                            slices_to_move -= 1
                            slices_moved += 1
                            moved = True
                    
                    return moved, slices_moved
            
            return False, 0
        
        slices_to_move = min(slices_to_move, empty_slots)
        
        moved = False
        slices_moved = 0
        for i in range(len(source_plate)):
            if source_plate[i] == slice_type and slices_to_move > 0:
                source_plate[i] = None
                
                for j in range(len(target_plate)):
                    if target_plate[j] is None:
                        target_plate[j] = slice_type
                        break
                
                slices_to_move -= 1
                slices_moved += 1
                moved = True
        
        return moved, slices_moved
        
    def is_plate_empty(self, x, y):
        if not self.is_valid_position(x, y) or self.is_empty(x, y):
            return False
            
        plate = self.grid[x][y]
        return all(slice_type is None for slice_type in plate)
    
    def check_completed_cakes(self):
        completed_cakes = 0
        
        for x in range(self.rows):
            for y in range(self.cols):
                if not self.is_empty(x, y):
                    plate = self.grid[x][y]
                    
                    count = self._count_slice_types(plate)
                    
                    for slice_type, num in count.items():
                        if num == 8: 
                            self.grid[x][y] = None
                            completed_cakes += 1
                            break
        
        self.remove_empty_plates()
        
        return completed_cakes
        
    def remove_empty_plates(self):
        removed_plates = 0
        
        for x in range(self.rows):
            for y in range(self.cols):
                if not self.is_empty(x, y) and self.is_plate_empty(x, y):
                    self.grid[x][y] = None
                    removed_plates += 1
        
        return removed_plates
        
    def is_full(self):
        for x in range(self.rows):
            for y in range(self.cols):
                if self.is_empty(x, y):
                    return False
        return True
    
    def get_representation(self):
        return copy.deepcopy(self.grid)
    
    def clone(self):
        new_board = Board(self.rows, self.cols)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board
    
    def count_occupied_cells(self):
        count = 0
        for x in range(self.rows):
            for y in range(self.cols):
                if not self.is_empty(x, y):
                    count += 1
        return count