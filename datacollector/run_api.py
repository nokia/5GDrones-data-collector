# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Script for running collector API."""
import datacollector.api.collector_api as c_api


def main():
    """Run the collector API."""
    c_api.run()


if __name__ == "__main__":
    main()
