#!/usr/bin/env python3
"""
Filter module
"""

import logging
import re
import os
import mysql.connector


def filter_datum(fields, redaction, message, separator):
    pattern = '|'.join(f'{field}=[^\\{separator}]*' for field in fields)
    return re.sub(
        pattern, lambda m: f"{m.group().split('=')[0]}={redaction}", message
    )


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        original_message = super().format(record)
        return filter_datum(
            self.fields, self.REDACTION, original_message, self.SEPARATOR
        )


PII_FIELDS = ("name", "email", "ssn", "password", "phone_number")


def get_logger() -> logging.Logger:
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = RedactingFormatter(fields=PII_FIELDS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_db():
    username = os.getenv('PERSONAL_DATA_DB_USERNAME', 'root')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD', 'M!sasa12')
    host = os.getenv('PERSONAL_DATA_DB_HOST', 'localhost')
    database = os.getenv('PERSONAL_DATA_DB_NAME', 'my_db')

    print(f"Connecting to database: "
          f"USERNAME: {username}, "
          f"PASSWORD: {password}, "
          f"HOST: {host}, "
          f"DATABASE: {database}")

    return mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=database
    )


# Define the main function
def main():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users;")
    rows = cursor.fetchall()

    logger = get_logger()
    for row in rows:
        message = "; ".join(f"{key}={value}" for key, value in row.items())
        logger.info(message)

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
