#!/usr/bin/python
import sys
import csv
import base64
import json

csv.field_size_limit(sys.maxsize)


class GatesDebugDecoder:
    def __init__(self):
        if len(sys.argv) > 1:
            try:
                self.input_file = open(sys.argv[1], "r", encoding="utf-8", newline="")
            except OSError as e:
                print("Failed to open file {}".format(e.filename))
                sys.exit()
        else:
            print("Please specify an input file.")
            sys.exit()

        self.records_number = 0
        self.output_file_name = "{}-{}{}{}.txt"

    def open_csv_file(self, file):
        try:
            return csv.DictReader(file)
        except csv.Error as e:
            raise ValueError(e)

    def convert_to_json(self, field):
        try:
            request_json = json.loads(field.replace("u'", '"').replace("'", '"'))
            return request_json
        except json.JSONDecodeError as e:
            print(e.msg)
            sys.exit()

    def decode_from_base64(self, string):
        return base64.b64decode(string).decode("utf-8")

    def dump_request_and_responce(self, params):
        record_number = params["record_number"]
        if self.records_number > 1:
            separator = "-"
            file_number = record_number + 1
        else:
            separator = ""
            file_number = ""

        output_file_name = self.output_file_name.format(
            params["search_id"], params["gate_name"], separator, file_number
        )

        try:
            output_file = open(output_file_name, "w", encoding="utf-8")
        except KeyError:
            print("The CSV file does not have 'search_id' and/or 'gate_name' fields.")
            sys.exit()
        except IOError:
            print('Error creating file "{0}".'.format(output_file_name))

        with output_file:
            request = self.decode_from_base64(
                json.dumps(params["requests"][record_number]["body"])
            )
            response = self.decode_from_base64(
                json.dumps(params["responses"][record_number]["body"])
            )

            output_file.write("{}\n".format(request))
            output_file.write("\n\n=========================================\n\n")
            output_file.write("{}\n".format(response))

    def decode_debug_info(self):
        with self.input_file:
            csv_file = self.open_csv_file(self.input_file)
            params = {}
            for row in csv_file:
                params["search_id"] = row["search_id"]
                params["gate_name"] = row["gate_name"]
                params["requests"] = self.convert_to_json(row["request"])
                params["responses"] = self.convert_to_json(row["response"])
                self.records_number = len(params["requests"])

                for record_number in range(self.records_number):
                    params["record_number"] = record_number
                    self.dump_request_and_responce(params)

            print("Done.")


if __name__ == "__main__":
    decoder = GatesDebugDecoder()
    decoder.decode_debug_info()
