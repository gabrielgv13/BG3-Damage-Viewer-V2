"""Character state and level management."""


class Character:
    """Manages character state including levels, subclasses, and ability scores."""
    
    MAX_LEVEL = 12
    
    def __init__(self):
        # Class levels: {class_name: level}
        self.levels = {}
        
        # Subclass selections: {class_name: subclass_name}
        self.subclasses = {}
        
        # Pending subclass selection: (class_name, level) when waiting for selection
        self.pending_subclass = ("", 0)
        
        # Ability scores
        self.ability_scores = {
            "Strength": 8,
            "Dexterity": 8,
            "Constitution": 8,
            "Intelligence": 8,
            "Wisdom": 8,
            "Charisma": 8
        }
    
    def get_total_level(self):
        """Calculate total character level across all classes."""
        return sum(self.levels.values())
    
    def can_add_level(self):
        """Check if character can add another level."""
        return self.get_total_level() < self.MAX_LEVEL
    
    def add_level(self, class_name):
        """Add a level to a class."""
        if not self.can_add_level():
            return False
        
        if class_name in self.levels:
            self.levels[class_name] += 1
        else:
            self.levels[class_name] = 1
        
        return True
    
    def set_subclass(self, class_name, subclass_name):
        """Set the subclass for a class."""
        self.subclasses[class_name] = subclass_name
    
    def get_class_level(self, class_name):
        """Get the level in a specific class."""
        return self.levels.get(class_name, 0)
    
    def get_subclass(self, class_name):
        """Get the subclass for a class."""
        return self.subclasses.get(class_name)
    
    def reset(self):
        """Reset all character data."""
        self.levels.clear()
        self.subclasses.clear()
        self.pending_subclass = ("", 0)
    
    def get_class_breakdown(self):
        """Get formatted class breakdown string."""
        if not self.levels:
            return "No levels assigned"
        
        breakdown = []
        for class_name in sorted(self.levels.keys()):
            if self.levels[class_name] > 0:
                breakdown.append(f"{class_name} {self.levels[class_name]}")
        
        return " / ".join(breakdown) if breakdown else "No levels assigned"
    
    def get_ability_modifier(self, ability_name):
        """Calculate ability modifier from score."""
        score = self.ability_scores.get(ability_name, 10)
        return (score - 10) // 2
    
    def get_points_spent(self, base_costs):
        """Calculate total ability score points spent."""
        total = 0
        for score in self.ability_scores.values():
            total += base_costs.get(score, 0)
        return total
