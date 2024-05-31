#!/usr/bin/env python3
"""
Filter module
"""

import logging
import re
import os
import mysql.connector
from mysql.connector import errorcode


def filter_datum(fields, redaction, message, separator):
    """
    Redacts specified fields from a message.

    Args:
        fields (tuple): Fields to redact.
        redaction (str): String to use for redaction.
        message (str): Message to filter.
        separator (str): Separator used to separate fields in the message.

    Returns:
        str: Filtered message.
    """
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
        """
        Formats the log record with redaction of sensitive data.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: Formatted log message.
        """
        original_message = super().format(record)
        return filter_datum(
            self.fields, self.REDACTION, original_message, self.SEPARATOR
        )


PII_FIELDS = ("name", "email", "ssn", "password", "phone_number")


def get_logger() -> logging.Logger:
    """
    Retrieves a logger configured for redacting PII.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = RedactingFormatter(fields=PII_FIELDS)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_db():
    """
    Retrieves a connection to the database.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection.
    """
    try:
        db = mysql.connector.connect(
            user='root',
            password='M!sasa12',
            host='localhost',
            database='my_db'
        )
        return db
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied: Please check your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None


# Define the main function
def main():
    """
    Main function to retrieve data from database and log it with redacted PII.
    """
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
