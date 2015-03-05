# Chip Fukuhara and Jacob Gile
# Zahorjan
# CSE 461
# Project 0

# Tor61Log.py
# Logging utility for the entire Tor61 project

import logging

#Set up the logger
FORMAT = '%(asctime)s %(module)s.%(funcName)s {%(thread)d} %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('Tor61')
logger.setLevel(logging.INFO)
		
#Allow modules acccess to the log
def getLog():
	return logger
