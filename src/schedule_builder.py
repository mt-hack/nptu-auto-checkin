import logging
from datetime import datetime

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
    # job_list = []
    # today = datetime.today()
    # for job in model['Jobs']:
    #     logging.info("Valid job(s) for today:")
    #     parsed_start_time = datetime.strptime(job['StartTime'], "%H:%M:%S")
    #     parsed_end_time = datetime.strptime(job['EndTime'], '%H:%M:%S')
    #     parsed_start_date = datetime.strptime(
    #         f'{today.year} {today.month} {today.day} {parsed_start_time.hour} {parsed_start_time.minute}',
    #         '%Y %m %d %H %S')
    #     parsed_end_date = datetime.strptime(
    #         f'{today.year} {today.month} {today.day} {parsed_end_time.hour} {parsed_end_time.minute}',
    #         '%Y %m %d %H %S')
    #     logging.info(parsed_start_date)
    #     logging.info(parsed_end_date)
    #     job_list.append([parsed_start_date, parsed_end_date])


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
