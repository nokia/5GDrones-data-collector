# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Script for running Datacollector from console."""
import argparse
import logging
import pathlib
import sys
import time
import uuid

from datetime import datetime, timedelta
from threading import Thread

from datacollector.collector.agent import Agent


def create_run_id():
    """Create a run id for the collector (agent-level)."""
    date = datetime.utcnow()
    run_id = "Datacollector_" + str(uuid.uuid4())[:3] + '_' + datetime.strftime(date, "%Y-%m-%dT%H-%M-%S")
    return run_id


def set_logging(run_id):
    """Initialize logging."""
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s',
                                  datefmt="%Y-%m-%dT%H:%M:%S%z")

    # Create logging handler for logging to file
    absp = pathlib.Path(__file__).parent.absolute()
    abspath = absp.__str__()
    file_handler = logging.FileHandler(abspath + '/collector/log/' + run_id + '.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)

    # Create logging handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        format=formatter,
        handlers=[
            file_handler,
            console_handler
        ]
    )


def time_interval(arg):
    """Function for checking validity of command line arguments."""
    if int(arg) < 0:
        raise argparse.ArgumentTypeError
    return arg


def parse_arguments():
    """Parse given folder path from command line argument."""
    try:
        parser = argparse.ArgumentParser(description='Set start, end, and collection interval values for collector.')
        parser.add_argument('-s', '--start', type=time_interval, help='Time interval to start the collector. In '
                                                                      'seconds. Must be a positive integer.')
        parser.add_argument('-e', '--end', type=time_interval, help='Time interval to stop the collector. In seconds. '
                                                                    'Must be a positive integer.')
        parser.add_argument('-i', '--interval', type=time_interval, help='Time interval between individual collection '
                                                                         'events. In seconds. Must be a positive integer.')

        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)
        else:
            args = parser.parse_args()
            return args
    except Exception as e:
        print("Exception caught: ", str(e))
        sys.exit(1)


def run():
    """Run collector without any external interface."""
    args = parse_arguments()
    collect_start_time = datetime.utcnow() + timedelta(seconds=int(args.start))
    collect_stop_time = collect_start_time + timedelta(seconds=int(args.end))
    collect_interval = int(args.interval)

    # Create test id for the agent.
    run_id = create_run_id()

    # Set up logging
    set_logging(run_id)

    # This spawns a new thread. Use these to wrap the agent in your own program.
    # The last loop is blocking, and you need to implement your own solution or just ignore it.
    agent = Agent(collect_start_time, collect_stop_time, collect_interval, run_id)
    agent_thread = Thread(target=run_agent, args=[agent])
    agent_thread.start()
    while agent.is_alive():
        time.sleep(1)


def run_agent(agent):
    """Run agent thread."""
    agent.start()


if __name__ == "__main__":
    run()
