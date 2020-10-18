import re
from json import JSONDecoder

from bs4 import BeautifulSoup


class NoQuestionFound(Exception):
    pass


class ParseError(Exception):
    pass


QNUM_REGEX = re.compile(r"var qnum = .+;")
FIND_DIGIT_REGEX = re.compile(r"\d+")
AAID_REGEX = re.compile(r"aaid=.+")


class Parser:
    @staticmethod
    def parse(page: str):
        try:
            current_question_script = str(Parser.find_tags(page)[-4])
            _json = list(Parser.extract_json(current_question_script))[0]  # extract json and select first object
            
            qid = _json['id']
            
            type_ = _json['answer']['type']
            
            qnum = FIND_DIGIT_REGEX.findall(
                QNUM_REGEX.findall(current_question_script)[0])[0]  # extract question number
            #return {'qid': qid, 'qnum': qnum}, type_
            return {'qnum': qnum}, type_
        except (KeyError, IndexError) as e:
            raise NoQuestionFound(e)

    @staticmethod
    def find_tags(page: str):
        return BeautifulSoup(page, 'html.parser').find_all('script')

    @staticmethod
    def extract_json(string: str):
        pos = 0
        while True:
            match = string.find('{', pos)
            if match == -1:
                break
            try:
                result, index = JSONDecoder().raw_decode(string[match:])
                yield result
                pos = match + index
            except ValueError:
                pos = match + 1
