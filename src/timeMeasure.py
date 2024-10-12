import time
from functools import wraps

# @time_measure

## Utiliser dans le fichier souhaité :
# L'import
# from timeMeasure import TimeMeasure
# Instancié :
# self.time_measure = TimeMeasure()
# Ajouté un décorateur pour voir le temps de la fonction
# @TimeMeasure()

class TimeMeasure:
    def __init__(self):
        self.execution_times = {}
        self.last_display_time = time.time()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time

            method_name = func.__name__
            if method_name not in self.execution_times:
                self.execution_times[method_name] = 0
            self.execution_times[method_name] += elapsed_time

            if time.time() - self.last_display_time >= 2:  # Affiche toutes les secondes
                for fct in list(self.execution_times):
                    print(f"Time in {fct}: {self.execution_times[fct]} secondes")
                self.last_display_time = time.time()

            return result
        return wrapper
