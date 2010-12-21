import models
from badges import Badge, BadgeContextType, BadgeCategory

# All badges awarded for completing some subset of exercises inherit from ExerciseCompletionBadge
class ExerciseCompletionBadge(Badge):

    def is_satisfied_by(self, *args, **kwargs):
        user_data = kwargs.get("user_data", None)
        if user_data is None:
            return False

        if len(self.exercise_names_required) <= 0:
            return False

        user = user_data.user

        for exercise_name in self.exercise_names_required:
            if not user_data.is_proficient_at(exercise_name, user):
                return False

        return True

    def extended_description(self):
        s_exercises = ""
        for exercise_name in self.exercise_names_required:
            if len(s_exercises) > 0:
                s_exercises += ", "
            s_exercises += models.Exercise.to_display_name(exercise_name)
        return "Achieve proficiency in %s" % s_exercises

class ApprenticeArithmeticianBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['addition_1', 'subtraction_1', 'multiplication_1', 'division_1']
        self.description = "Apprentice Arithmetician"
        self.badge_category = BadgeCategory.SILVER
        self.points = 100
        ExerciseCompletionBadge.__init__(self)

class JourneymanArithmeticianBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['addition_4', 'subtraction_4', 'multiplication_4', 'division_4']
        self.description = "Journeyman Arithmetician"
        self.badge_category = BadgeCategory.SILVER
        self.points = 500
        ExerciseCompletionBadge.__init__(self)

class MasterArithmeticianBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['multiplying_decimals', 'dividing_decimals', 'multiplying_fractions', 'dividing_fractions']
        self.description = "Master Arithmetician"
        self.badge_category = BadgeCategory.SILVER
        self.points = 750
        ExerciseCompletionBadge.__init__(self)

class ApprenticeTrigonometricianBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['angles_2', 'distance_formula', 'pythagorean_theorem_1']
        self.description = "Apprentice Trigonometrician"
        self.badge_category = BadgeCategory.SILVER
        self.points = 100
        ExerciseCompletionBadge.__init__(self)

class JourneymanTrigonometricianBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['pythagorean_theorem_2', 'trigonometry_1']
        self.description = "Journeyman Trigonometrician"
        self.badge_category = BadgeCategory.SILVER
        self.points = 500
        ExerciseCompletionBadge.__init__(self)

class MasterTrigonometricianBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['trigonometry_2', 'graphs_of_sine_and_cosine', 'inverse_trig_identities', 'trig_identities_1']
        self.description = "Master Trigonometrician"
        self.badge_category = BadgeCategory.GOLD
        self.points = 750
        ExerciseCompletionBadge.__init__(self)

class ApprenticePrealgebraistBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['exponents_1', 'adding_and_subtracting_negative_numbers', 'adding_and_subtracting_fractions']
        self.description = "Apprentice Pre-algebraist"
        self.badge_category = BadgeCategory.SILVER
        self.points = 100
        ExerciseCompletionBadge.__init__(self)

class JourneymanPrealgebraistBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['exponents_2', 'multiplying_and_dividing_negative_numbers', 'multiplying_fractions', 'dividing_fractions']
        self.description = "Journeyman Pre-algebraist"
        self.badge_category = BadgeCategory.SILVER
        self.points = 500
        ExerciseCompletionBadge.__init__(self)

class MasterPrealgebraistBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['exponents_3', 'order_of_operations', 'ordering_numbers', 'scientific_notation', 'units', 'simplifying_radicals']
        self.description = "Master Pre-algebraist"
        self.badge_category = BadgeCategory.SILVER
        self.points = 750
        ExerciseCompletionBadge.__init__(self)

class ApprenticeAlgebraistBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['exponents_3', 'exponent_rules', 'logarithms_1', 'linear_equations_1', 'percentage_word_problems_1', 'functions_1']
        self.description = "Apprentice Algebraist"
        self.badge_category = BadgeCategory.SILVER
        self.points = 100
        ExerciseCompletionBadge.__init__(self)

class JourneymanAlgebraistBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['linear_equations_2', 'percentage_word_problems_2', 'functions_2', 'domain_of_a_function', 'even_and_odd_functions', 'shifting_and_reflecting_functions']
        self.description = "Journeyman Algebraist"
        self.badge_category = BadgeCategory.SILVER
        self.points = 500
        ExerciseCompletionBadge.__init__(self)

class MasterAlgebraistBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['linear_equations_3', 'systems_of_equations', 'multiplying_expressions_1', 'even_and_odd_functions', 'inverses_of_functions', 'slope_of_a_line']
        self.description = "Master Algebraist"
        self.badge_category = BadgeCategory.GOLD
        self.points = 750
        ExerciseCompletionBadge.__init__(self)

class SageAlgebraistBadge(ExerciseCompletionBadge):
    def __init__(self):
        self.exercise_names_required = ['linear_equations_4', 'linear_inequalities', 'average_word_problems', 'equation_of_a_line', 'solving_quadratics_by_factoring', 'quadratic_equation']
        self.description = "Sage Algebraist"
        self.badge_category = BadgeCategory.GOLD
        self.points = 1000
        ExerciseCompletionBadge.__init__(self)
