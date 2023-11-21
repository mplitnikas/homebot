import datetime
import json
import os
import redis
import schedule

class TimePublisher:
    def __init__(self, redis_host, redis_port, redis_time_channel, weather_client):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)
        self.redis_time_channel = redis_time_channel
        self.weather_client = weather_client
        self.time_of_day_jobs = []

        self.schedule_jobs()
        self.update_time_of_day_jobs()

    def run(self):
        if len(self.time_of_day_jobs) == 0:
            raise Exception("TimePublisher: no time of day jobs scheduled!")

        while True:
            schedule.run_pending()
            time.sleep(60)

    def schedule_jobs(self):
        schedule.every().day.at("01:00").do(self.update_time_of_day_jobs)

    def update_time_of_day_jobs(self):
        for job in self.time_of_day_jobs:
            schedule.cancel_job(job)
        self.time_of_day_jobs = []

        self.weather_client.update_sun_times()
        sun_times = self.weather_client.get_sun_times()

        for time_of_day, event in sun_times.items():
            job = schedule.every().day.at(time_of_day).do(self.publish_time_of_day, event)
            self.time_of_day_jobs.append(job)

    def publish_time_of_day(self, time_of_day):
        self.redis_client.publish(self.redis_time_channel, time_of_day)
        self.redis_client.set('time_of_day', time_of_day)
