#!/usr/bin/env python3

"""
Write from Kafka stream to ratings and views files
"""

from kafka import KafkaConsumer, TopicPartition
import pandas as pd
from datetime import datetime, timedelta
import re


def parse_message(message, ratings_file):
    """Parse a Kafka `message` and save rating to `ratings_file`."""
    m = re.search(
        r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}),(\d+),GET /rate/(.*?\d{4})=(\d{1})$', message.value)
    if m:
        time, userid, movieid, rating = m.groups()
        ratings_file.write(f"{time},{userid},{movieid},{rating}\n")


if __name__ == "__main__":
    consumer = KafkaConsumer(
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda x: x.decode('utf-8'),
        auto_offset_reset='earliest',
        group_id='group3',
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )

    topic_part = TopicPartition('movielog3', 0)
    consumer.assign([topic_part])

    begin_datetime = datetime.now() - timedelta(hours=0.25)
    end_datetime = datetime.now()

    start_offset = consumer.offsets_for_times(
        {topic_part: begin_datetime.timestamp() * 1000})

    consumer.seek(topic_part, start_offset[topic_part].offset)

    end_offset = consumer.end_offsets([topic_part])[topic_part]
    # consumer.seek_to_end(topic_part)

    raw_ratings = open(
        '/home/teamtitanic/datasets/kafka_raw_ratings_new.csv', 'w')
    raw_ratings.write(f"time,userid,movieid,rating\n")

    iterate = True
    while iterate:
        response = consumer.poll(timeout_ms=5000)
        for message in response[topic_part]:
            parse_message(message, raw_ratings)
        pos = consumer.position(topic_part)
        if pos >= end_offset:
            iterate = False
    consumer.close()
    raw_ratings.close()
