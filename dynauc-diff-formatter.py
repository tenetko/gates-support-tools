#!/usr/bin/python

import sys
import re

regex = re.compile(
    r"\[WARNING\] Booking (?P<booking_number>[\d\w]+) from (?P<gate_name>[\d\w]+) has commission diff \((?P<received_comm>\d+) instead of (?P<expected_comm>\d+), std: (?P<standard_comm>\d+), diff: (?P<comm_diff>\d+)\)."
)

try:
    if len(sys.argv) > 1:
        input_file = open(sys.argv[1], "r", encoding="utf-8")
    else:
        print("Please specify an input file.")
        sys.exit()
    output_file = open("output.txt", "w", encoding="utf-8")
except OSError as e:
    print("Failed to open file {}.".format(e.filename))

with input_file, output_file:
    for line in input_file:
        try:
            match = regex.match(line)
        except re.error as e:
            print("Invalid regex:\n{}".format(e.msg))
        if match:
            output_file.write("Заказ {}\n".format(match.group("booking_number")))
            output_file.write("Комиссия {}\n".format(match.group("received_comm")))
            output_file.write(
                "Ожидаемая Комиссия {}\n".format(match.group("expected_comm"))
            )
            output_file.write(
                "Стандартная Комиссия {}\n\n".format(match.group("standard_comm"))
            )
