import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='File "%(filename)s", line %(lineno)d, in %(funcName)s: %(message)s',
)


def main():
    logging.debug("This is a debug message")


if __name__ == "__main__":
    main()
