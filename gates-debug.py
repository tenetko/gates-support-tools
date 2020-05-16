#!/usr/bin/python
import sys
import csv
import base64
import json

csv.field_size_limit(sys.maxsize)


def open_csv_file(file):
    try:
        return csv.DictReader(file)
    except OSError:
        print('File "{0}" does not exist.'.format(file))
        sys.exit()
    except csv.Error as e:
        raise ValueError(e)


def retrieve_request(row):
    try:
        request_json = json.loads(row["request"].replace("u'", '"').replace("'", '"'))
        return base64.b64decode(request_json[0]["body"]).decode("utf-8")
    except json.JSONDecodeError as e:
        print(e.msg)
        sys.exit()


def retrieve_response(row):
    try:
        response_json = json.loads(row["response"].replace("u'", '"').replace("'", '"'))
        return base64.b64decode(response_json[0]["body"]).decode("utf-8")
    except json.JSONDecodeError as e:
        print("Decoding JSON has failed: {0}".format(e.msg))
        sys.exit()


if __name__ == "__main__":
    with open(sys.argv[1], "r", encoding="utf-8", newline="") as f:
        csv_file = open_csv_file(f)
        for row in csv_file:
            try:
                output_file_name = "{0}-{1}.txt".format(
                    row["search_id"], row["gate_name"]
                )
            except KeyError as e:
                print(
                    "The CSV file does not have 'search_id' and/or 'gate_name' fields."
                )
                sys.exit()
            try:
                with open(output_file_name, "w", encoding="utf-8") as output_file:
                    output_file.write(retrieve_request(row))
                    output_file.write(
                        "\n\n=========================================\n\n"
                    )
                    output_file.write(retrieve_response(row))
            except IOError:
                print('Error creating file "{0}".'.format(output_file_name))
    print("Done.")
