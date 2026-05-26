import logging
# imports Python's built-in logging system


logging.basicConfig(
    level=logging.INFO,
    # shows INFO, WARNING, ERROR, and CRITICAL messages

    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    # controls how log lines look in terminal
)


logger = logging.getLogger("echelon")
# creates one named logger for the whole app