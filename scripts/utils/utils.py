# -*- coding: utf-8 -*-
import logging
import os
import sys

# output_file_handler = logging.handlers.RotatingFileHandler(filename='logs/logs.logger',
#                                                            mode='a')
# stdout_handler = logging.StreamHandler(sys.stdout)
#
# logging.basicConfig(
#   	#format="%(asctime)s %(name)-15s %(levelname)-6s %(message)s",
#     #datefmt="%y-%m-%d %H:%M:%S",
#     handlers=[
#     	output_file_handler,
#         stdout_handler
#     ]
# )

logger = logging.getLogger('Logger')
logger.setLevel(logging.DEBUG)

def spent_time(start_time, end_time):
    minutes = (end_time - start_time)//60
    seconds = (end_time - start_time) - (minutes*60)
    
    return ' {:.0f} min {:.2f} sec'.format(minutes,seconds)

def ensure_folder(folder):
    if not os.path.exists(folder):
        logger.info(f'> Creating folder at {folder}')
        os.makedirs(folder)
        return
    
def multiply_all_list_elements(input_list):
    
    result = 1
    
    for x in input_list:
        if(x > 0):
            result *= x
        elif(x < 0):
            result = -1
            break
        else:
            raise ValueError('Multiplication element')
        
    return result

def consecutive_numbers(number_list):

    nums = sorted(number_list)
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s + 1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])

    return list(zip(edges, edges))


        
