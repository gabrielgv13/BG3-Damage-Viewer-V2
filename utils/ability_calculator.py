"""Ability score calculation utilities for point buy system."""


class AbilityScoreCalculator:
    """Manages ability score calculations using point buy system."""
    
    # Point buy costs from D&D 5e
    BASE_COSTS = {
        8: 0, 
        9: 1, 
        10: 2, 
        11: 3, 
        12: 4, 
        13: 5, 
        14: 7, 
        15: 9
    }
    
    TOTAL_POINTS = 27
    ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
    
    @staticmethod
    def calculate_modifier(score):
        """Calculate ability modifier from ability score."""
        return (score - 10) // 2
    
    @staticmethod
    def calculate_point_cost(base_score):
        """Get point buy cost for a base score."""
        return AbilityScoreCalculator.BASE_COSTS.get(base_score, 0)
    
    @staticmethod
    def calculate_total_points_used(base_scores):
        """
        Calculate total points used in point buy.
        
        Args:
            base_scores: Dict of ability -> base score (before racial bonuses)
        
        Returns:
            Total points used
        """
        total = 0
        for ability in AbilityScoreCalculator.ABILITIES:
            base_val = base_scores.get(ability, 8)
            total += AbilityScoreCalculator.calculate_point_cost(base_val)
        return total
    
    @staticmethod
    def is_valid_point_buy(base_scores):
        """
        Check if point buy is valid (doesn't exceed TOTAL_POINTS).
        
        Args:
            base_scores: Dict of ability -> base score
        
        Returns:
            True if valid, False otherwise
        """
        used = AbilityScoreCalculator.calculate_total_points_used(base_scores)
        return used <= AbilityScoreCalculator.TOTAL_POINTS
    
    @staticmethod
    def calculate_final_scores(base_scores, racial_bonuses):
        """
        Calculate final ability scores with racial bonuses applied.
        
        Args:
            base_scores: Dict of ability -> base score
            racial_bonuses: Dict of ability -> bonus (e.g., {"Strength": 2, "Dexterity": 1})
        
        Returns:
            Dict of ability -> final score
        """
        final_scores = {}
        for ability in AbilityScoreCalculator.ABILITIES:
            base = base_scores.get(ability, 8)
            bonus = racial_bonuses.get(ability, 0)
            final_scores[ability] = base + bonus
        return final_scores
    
    @staticmethod
    def calculate_all_modifiers(ability_scores):
        """
        Calculate modifiers for all abilities.
        
        Args:
            ability_scores: Dict of ability -> score
        
        Returns:
            Dict of ability -> modifier
        """
        modifiers = {}
        for ability in AbilityScoreCalculator.ABILITIES:
            score = ability_scores.get(ability, 10)
            modifiers[ability] = AbilityScoreCalculator.calculate_modifier(score)
        return modifiers
    
    @staticmethod
    def format_modifier(modifier):
        """Format modifier with sign (+3, -1, etc.)."""
        sign = "+" if modifier >= 0 else ""
        return f"{sign}{modifier}"
