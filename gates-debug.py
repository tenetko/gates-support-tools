#!/usr/bin/python
import sys
import csv
import base64
import json

csv.field_size_limit(sys.maxsize)


def open_csv_file(file):
    try:
        return csv.DictReader(file)
    except csv.Error as e:
        raise ValueError(e)


def decode_field(field):
    try:
        request_json = json.loads(field.replace("u'", '"').replace("'", '"'))
        return base64.b64decode(request_json[0]["body"]).decode("utf-8")
    except json.JSONDecodeError as e:
        print(e.msg)
        sys.exit()


def prepare_debug_files():
    try:
        input_file = open(sys.argv[1], "r", encoding="utf-8", newline="")
    except OSError:
        print('File "{0}" does not exist.'.format(sys.argv[1]))
        sys.exit()

    with input_file:
        csv_file = open_csv_file(input_file)
        for row in csv_file:
            try:
                output_file_name = "{0}-{1}.txt".format(
                    row["search_id"], row["gate_name"]
                )
            except KeyError:
                print(
                    "The CSV file does not have 'search_id' and/or 'gate_name' fields."
                )
                sys.exit()
            try:
                output_file = open(output_file_name, "w", encoding="utf-8")
            except IOError:
                print('Error creating file "{0}".'.format(output_file_name))

            with output_file:
                output_file.write(decode_field(row["request"]))
                output_file.write("\n\n=========================================\n\n")
                output_file.write(decode_field(row["response"]))
    print("Done.")


if __name__ == "__main__":
    prepare_debug_files()
