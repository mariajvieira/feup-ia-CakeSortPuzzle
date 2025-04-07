import random
import copy


class AvailablePlates:
    
    def __init__(self, level=1, plate_count=None):
        self.max_plates = 3 
        
        if plate_count is not None:
            self.total_plate_limit = plate_count
        elif level == 1:
            self.total_plate_limit = 5 
        else:
            self.total_plate_limit = 18 
            
        self.plates_used = 0  
        
        self.slice_types = self._get_slice_types(level)
        
        self.visible_plates = []
        self.plates_queue = []
        
        self._generate_all_plates(level)
        
        self._refill_visible_plates()
    
    def _get_slice_types(self, level):
        basic_types = [1, 2, 3, 4, 5]
        
        if level >= 3:
            basic_types.extend([6, 7])
        if level >= 5:
            basic_types.extend([8, 9])
        
        return basic_types
    
    def _generate_all_plates(self, level):
        self.plates_queue = []
        
        for _ in range(self.total_plate_limit):
            plate = self._generate_single_plate(level)
            self.plates_queue.append(plate)
    
    def _generate_single_plate(self, level):
        num_slices = random.randint(1, min(5, level + 2))
        
        plate = [None] * 8
        
        for _ in range(num_slices):
            slice_type = random.choice(self.slice_types)
            
            empty_indices = [i for i, slice_val in enumerate(plate) if slice_val is None]
            if empty_indices: 
                index = random.choice(empty_indices)
                plate[index] = slice_type
        
        return plate
    
    def _refill_visible_plates(self):
        while len(self.visible_plates) < self.max_plates and self.plates_queue:
            self.visible_plates.append(self.plates_queue.pop(0))
    
    def get_plate(self, index):
        if 0 <= index < len(self.visible_plates):
            return copy.deepcopy(self.visible_plates[index])
        return None
    
    def remove_plate(self, index):
        if 0 <= index < len(self.visible_plates):
            self.visible_plates.pop(index)
            
            self.plates_used += 1
            
            self._refill_visible_plates()
            
            return True
        return False
    
    def has_plates(self):
        return len(self.visible_plates) > 0 or len(self.plates_queue) > 0
    
    def is_exhausted(self):
        return self.plates_used >= self.total_plate_limit
    
    def get_remaining_plates(self):
        return self.total_plate_limit - self.plates_used
    
    def get_visible_plate_count(self):
        return len(self.visible_plates)
    
    def get_representation(self):
        return {
            'visible_plates': copy.deepcopy(self.visible_plates),
            'plates_used': self.plates_used,
            'total_limit': self.total_plate_limit,
            'queue_size': len(self.plates_queue)
        }
    
    def clone(self):
        new_avl_plates = AvailablePlates(1)  
        new_avl_plates.visible_plates = copy.deepcopy(self.visible_plates)
        new_avl_plates.plates_queue = copy.deepcopy(self.plates_queue)
        new_avl_plates.max_plates = self.max_plates
        new_avl_plates.slice_types = copy.deepcopy(self.slice_types)
        new_avl_plates.plates_used = self.plates_used
        new_avl_plates.total_plate_limit = self.total_plate_limit
        
        return new_avl_plates