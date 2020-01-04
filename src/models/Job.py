from datetime import datetime


class Job:
    DayOfWeek = 0
    StartTime = datetime.strptime("00:00", "%H:%M").time()
    EndTime = datetime.strptime("00:00", "%H:%M").time()
    WorkDescription = ""

    def __init__(self, day_of_week, start_time, end_time, work_desc):
        parsed_start_time = datetime.strptime(start_time, "%H:%M").time()
        parsed_end_time = datetime.strptime(end_time, "%H:%M").time()
        if parsed_end_time > parsed_start_time:
            self.DayOfWeek = day_of_week
            self.StartTime = parsed_start_time
            self.EndTime = parsed_end_time
            self.WorkDescription = work_desc
        else:
            raise ArithmeticError('End time must be greater than start time.')
