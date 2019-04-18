import re
import logging


class ParserGeneric:

    def __init__(self, file):
        self.file = file

    def openfile(self):
        with open(self.file, mode='r') as fd:
            return fd.read()

    def parser(self):  # pragma: no cover
        pass


class ParserChannels(ParserGeneric):
    """
    Parser the frequencies/channels respect to each GLONASS PRNs. These values are essentials to the calculation
        of the selective factor
    """
    C = 299792458
    _regex = r'\d\/([\s\d]{3})\|([-\s\d]{6})'

    def __init__(self, file):
        """
        Initiate the parsing proceduring for GLONASS channels

        :param file: Absolute path to open the GLONASS channels file
        :return: The python Channels object, with all the information parsed
        """
        self.parsed = {}
        super().__init__(file)

    @property
    def pattern(self):
        return re.compile(self._regex)

    def find(self):
        data = self.openfile()
        self.put_in_parsed(data)
        return None

    def put_in_parsed(self, data):
        """
        :param data: The ASCII content from https://www.glonass-iac.ru/en/CUSGLONASS/getCUSMessage.php
        :return: The python channels object, with all the information (prn - value) parsed
        """
        for prn, channel in re.findall(self.pattern, data):
            new_channel = float(channel.strip())
            f1 = 1602.0e+6 + (new_channel * 562500.0)
            f2 = 1246.0e+6 + (new_channel * 437500.0)
            factor_1 = (f1 - f2) / (f1 + f2) / self.C
            factor_2 = (f1 * f2) / (f2 - f1) / self.C

            # self.parsed[prn.strip()] = pow(f1 * f2, 2) / (f1 + f2) / (f1 - f2) / self.A / self.TECU
            self.parsed[prn.strip()] = [f1, f2, factor_1, factor_2]

        return None

    def parser(self):
        logging.info(">> Starting GLONASS channels parsing...")
        self.find()
        return self.parsed


class ParserRinexChannels(ParserChannels):
    """
    Parser the frequencies/channels respect to each GLONASS PRNs. These values are essentials to the calculation
        of the selective factor
    """
    _regex = r'R(\d\d)([-\d\s]{4})'
    A = 40.3
    TECU = 1.0e16

    def __init__(self, content):
        """
        Initiate the parsing proceduring for GLONASS channels

        :param content: The ASCII content from https://www.glonass-iac.ru/en/CUSGLONASS/getCUSMessage.php, contenting the GLONASS channels
        """
        self.parsed = {}
        super().__init__(content)

    def find(self):
        data = self.file
        self.put_in_parsed(data)
        return self.parsed
