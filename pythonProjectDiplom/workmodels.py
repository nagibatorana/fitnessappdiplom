class Exercise:
    def __init__(self, name, description, muscle_group, sets=3, reps=10):
        self.name = name
        self.description = description
        self.muscle_group = muscle_group
        self.sets = sets
        self.reps = reps

class Training:
    def __init__(self, name, is_predefined=False):
        self.name = name
        self.exercises = []
        self.is_predefined = is_predefined

    def add_exercise(self, exercise):
        self.exercises.append(exercise)

    def remove_exercise(self, index):
        if 0 <= index < len(self.exercises):
            self.exercises.pop(index)