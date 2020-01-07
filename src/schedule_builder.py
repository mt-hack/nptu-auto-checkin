import logging

import jsonpickle

from models.Job import Job
from models.Schedule import Schedule

JSONFileName = "schedule.json"


def get_jobs():
    try:
        model = read_model()
    except FileNotFoundError:
        logging.critical("Schedule file not found. Writing a new schedule example file.")
        model = write_model(Schedule([
            Job(0, "13:00", "14:00", "彙整資料"),
            Job(3, "13:10", "15:00", "文書處理")
        ]))
    return model['Jobs']


def read_model():
    with open(JSONFileName, 'r') as schedule_content:
        content = schedule_content.read()
        return jsonpickle.decode(content)


def write_model(model):
    with open(JSONFileName, 'w') as schedule_content:
        content = jsonpickle.encode(model, unpicklable=False)
        schedule_content.write(content)
        return jsonpickle.decode(content)


if __name__ == '__main__':
    get_jobs()
