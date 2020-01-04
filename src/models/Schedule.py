class Schedule:
    Jobs = []

    def __init__(self, jobs):
        if type(jobs) is not list:
            raise TypeError("The given object is not a list.")
        self.Jobs = jobs
