from unittest import TestCase

from models.Job import Job
from models.Schedule import Schedule
from schedule_builder import write_model


class Test(TestCase):
    def test_write_model(self):
        model = write_model(Schedule([
            Job(0, "13:00", "14:00", "Test Job on Monday"),
            Job(3, "13:10", "15:00", "Test Job on Thursday")
        ]))
        jobs = model['Jobs']
        self.assertIs(type(jobs), list)
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['DayOfWeek'], 0)
        self.assertEqual(jobs[0]['StartTime'], "13:00:00")
        self.assertEqual(jobs[0]['EndTime'], "14:00:00")
        self.assertEqual(jobs[0]['WorkDescription'], "Test Job on Monday")