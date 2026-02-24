"""Spell slot calculation and management."""


class SpellSlotCalculator:
    """Calculates spell slots based on character levels and caster types."""
    
    # Caster classifications
    FULL_CASTERS = {'bard', 'cleric', 'druid', 'sorcerer', 'wizard', 'warlock'}
    HALF_CASTERS = {'paladin', 'ranger'}
    ONE_THIRD_CASTERS = {'eldritch knight', 'arcane trickster'}
    
    def __init__(self, spell_slot_data):
        """Initialize with spell slot progression data."""
        self.spell_slot_data = spell_slot_data
        self.progression_table = spell_slot_data['progression_tables']['full_casters']
    
    def get_caster_type(self, class_name):
        """Returns 'full', 'half', 'one_third', or None if not a caster."""
        class_lower = class_name.lower()
        if class_lower in self.FULL_CASTERS:
            return 'full'
        elif class_lower in self.HALF_CASTERS:
            return 'half'
        elif class_lower in self.ONE_THIRD_CASTERS:
            return 'one_third'
        return None
    
    def get_subclass_caster_type(self, subclass_name):
        """Returns caster type for subclasses like 'eldritch_knight' or 'arcane_trickster'."""
        subclass_lower = subclass_name.lower().replace('_', ' ')
        if subclass_lower in self.FULL_CASTERS:
            return 'full'
        elif subclass_lower in self.HALF_CASTERS:
            return 'half'
        elif subclass_lower in self.ONE_THIRD_CASTERS:
            return 'one_third'
        return None
    
    def calculate_effective_spell_level(self, character_levels, character_subclasses):
        """
        Calculate total Effective Spell Level (ESL) from multiclass levels.
        Formula: ESL = floor(full_levels/1 + half_levels/2 + one_third_levels/3)
        
        Returns the ESL capped at 20 (max D&D level).
        """
        esl = 0.0
        
        for class_name, level in character_levels.items():
            caster_type = self.get_caster_type(class_name)
            
            # Check subclass if it's a caster
            if caster_type:
                subclass_name = character_subclasses.get(class_name)
                if subclass_name:
                    subclass_type = self.get_subclass_caster_type(subclass_name)
                    if subclass_type:
                        caster_type = subclass_type
            
            if caster_type == 'full':
                esl += level / 1
            elif caster_type == 'half':
                esl += level / 2
            elif caster_type == 'one_third':
                esl += level / 3
        
        return min(int(esl), 20)
    
    def get_spell_slots_for_level(self, esl, spell_level):
        """
        Get the number of spell slots for a given spell level (1-6+).
        Returns the slot count based on ESL, or 0 if ESL is not high enough.
        """
        if esl == 0:
            return 0
        
        # Find the entry in progression table
        for entry in self.progression_table:
            if entry['level'] == esl:
                return entry['slots'].get(str(spell_level), 0)
        
        # If exact level not found, use highest available
        if esl > 12:
            return self.progression_table[-1]['slots'].get(str(spell_level), 0)
        
        return 0
    
    def get_all_spell_slots(self, esl):
        """
        Calculate all spell slots (levels 1-6) for the given ESL.
        Returns a dict: {1: count, 2: count, ..., 6: count}
        """
        result = {}
        
        if esl == 0:
            return {i: 0 for i in range(1, 7)}
        
        # Find the entry for current ESL
        spell_slots = None
        for entry in self.progression_table:
            if entry['level'] == esl:
                spell_slots = entry['slots']
                break
        
        # If not found and ESL > 12, use level 12 slots
        if not spell_slots and esl > 12:
            spell_slots = self.progression_table[-1]['slots']
        
        if spell_slots:
            for i in range(1, 7):
                result[i] = spell_slots.get(str(i), 0)
        else:
            result = {i: 0 for i in range(1, 7)}
        
        return result
