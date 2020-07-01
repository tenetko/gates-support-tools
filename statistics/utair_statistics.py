import os
import sys
import hashlib
import json
import requests
import re
import datetime


class UtairRawStatisticsFetcher:

    DEFAULT_DATE_FORMAT = "%Y-%m-%d"

    SESSION_TEMPLATE = """<?xml version="1.0"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tais="http://www.tais.ru/">
        <soapenv:Body>
            <tais:StartSessionInput>
            <tais:login>{login}</tais:login>
            <tais:password>{password}</tais:password>
            <tais:hash>{hash}</tais:hash>
            <tais:disable_hash>false</tais:disable_hash>
            </tais:StartSessionInput>
        </soapenv:Body>
    </soapenv:Envelope>"""

    REQUEST_TEMPLATE = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tais="http://www.tais.ru/">
    <soapenv:Header/>
       <soapenv:Body>
          <tais:GetOrderListInput>
             <tais:session_token>{session}</tais:session_token>
             <tais:hash>{hash}</tais:hash>
             <tais:timestamp_from>{start_date}</tais:timestamp_from>
             <tais:timestamp_to>{end_date}</tais:timestamp_to>
          </tais:GetOrderListInput>
       </soapenv:Body>
    </soapenv:Envelope>"""

    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        self.config["secret"] = sys.argv[1]
        self.config["login"] = sys.argv[2]
        self.config["password"] = sys.argv[3]
        self.config["start"] = sys.argv[4]
        self.config["end"] = sys.argv[5]
        self.config["url"] = "https://tais-api.utair.ru//bitrix/components/travelshop/ibe.soap/travelshop_booking.php"

    def build_hash(self, config):
        return hashlib.md5("".join(config).encode("utf8")).hexdigest()

    def get_session_token(self):
        params = {
            "login": self.config["login"],
            "password": self.config["password"],
            "secret": self.config["secret"],
        }
        params["hash"] = self.build_hash(
            [params[x] for x in ("login", "password", "secret")]
        )

        payload = self.SESSION_TEMPLATE.format(**params)
        print("{}\n\n".format(payload))

        response = requests.post(self.config["url"], payload)

        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                "Stats api responded with %s status code (%s)"
                % (response.status_code, response.reason)
            )

        return re.search("session_token>(.*?)<", response.text).groups(1)[0]

    def get_results(self, start, end):
        params = {
            "session": self.get_session_token(),
            "start_date": ".".join(reversed(start.split("-"))) + " 00:00:00",
            "end_date": ".".join(reversed(end.split("-"))) + " 23:59:59",
            "secret": self.config["secret"],
        }
        params["hash"] = self.build_hash(
            [params[x] for x in ("session", "start_date", "end_date", "secret")]
        )

        payload = self.REQUEST_TEMPLATE.format(**params)
        print("{}\n\n".format(payload))

        response = requests.post(self.config["url"], payload)
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                "Stats api responded with %s status code (%s)"
                % (response.status_code, response.reason)
            )

        print("{}\n\n".format(response.text))

    def get_results_by_chunks(self, start, end):
        chunk_step = 3

        chunk_start_date = datetime.datetime.strptime(start, self.DEFAULT_DATE_FORMAT)
        chunk_end_date = chunk_start_date + datetime.timedelta(days=chunk_step)

        report_end_date = datetime.datetime.strptime(end, self.DEFAULT_DATE_FORMAT)

        while chunk_start_date <= report_end_date:
            self.get_results(
                chunk_start_date.strftime(self.DEFAULT_DATE_FORMAT),
                chunk_end_date.strftime(self.DEFAULT_DATE_FORMAT),
            )
            chunk_start_date += datetime.timedelta(days=chunk_step)
            chunk_end_date += datetime.timedelta(days=chunk_step)


f = UtairRawStatisticsFetcher()
f.get_results_by_chunks(f.config["start"], f.config["end"])
