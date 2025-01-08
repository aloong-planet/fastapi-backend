import logging
# logging.basicConfig(level = logging.INFO)
# Create a custom logger
logger = logging.getLogger(__name__)
# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('server.log')
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
# c_format = logging.Formatter('%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s|%(lineno)s|%(message)s')
# f_format = logging.Formatter('%(asctime)s|%(levelname)s|%(filename)s|%(funcName)s|%(lineno)s|%(message)s')
# change format to json format

c_format = logging.Formatter('time="%(asctime)s" level=%(levelname)s filename=%(filename)s funcName=%(funcName)s lineno=%(lineno)s message="%(message)s"')
f_format = logging.Formatter('time="%(asctime)s" level=%(levelname)s filename=%(filename)s funcName=%(funcName)s lineno=%(lineno)s message="%(message)s"')

console_handler.setFormatter(c_format)
file_handler.setFormatter(f_format)


# fix issue (if not this line, log leve cannot take effect)
# https://blog.csdn.net/qq_34309753/article/details/84554259
logging.root.setLevel(logging.NOTSET)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)