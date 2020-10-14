import functools
import json
import sys
from statistics import mean

from parser_utils import Parser, NoQuestionFound, AAID_REGEX, FIND_DIGIT_REGEX


class InvalidURLException(BaseException):
    def __init__(self, url, *args):
        self.__url = url
        super().__init__(*args)

    def __str__(self):
        return f"Invalid URL {self.__url}"


def catch(func):
    @functools.wraps(func)
    def stub(self, *args, **kwargs):
        try:
            return func(self, *args, *kwargs)
        except NoQuestionFound:  # raised in parser, questions finished
            return True, True
        except KeyboardInterrupt:
            sys.exit()  # quits script
        except BaseException as e:
            return None, e

    return stub


class AnswerHandler:
    def __init__(self, session):
        self.sesh = session
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                                      ' Chrome/71.0.3578.98 Safari/537.36'}
        self.process_ans_url = 'https://www.drfrostmaths.com/process-answer-new.php'
        self.process_skip_url = 'https://www.drfrostmaths.com/process-skipquestion2.php'
        self.answer_functions = {}

    def find_answer(self, data: dict, type_: str):
        data = dict(data)
        data[f'{type_}-answer-1'] = '1'  # prepare incorrect  answer
        print(f'Question number: {data["qnum"]}', '|', f'Question type: {type_}')
        r = self.sesh.post(self.process_ans_url, data=data, headers=self.headers)  # submit incorrect answer
        _json = json.loads(r.text)
        return _json['answer']  # parse correct answer

    def submit(self, data: dict):
        # noinspection PyBroadException
##        try:
##            r = self.sesh.post(self.process_ans_url, data=data, timeout=3)
##        except BaseException:
##            return False
##
##        _json = json.loads(r.text)
##        if not _json['isCorrect']:
##            self.wrong_answer(_json, data)
##            return False
        return True

    @staticmethod
    def new_type(answer: dict, type_: str):
        print(f'Type:{type_})'
              f'\n {answer}')

    @staticmethod
    def wrong_answer(response, data: dict):
        print('-- The wrong answer was submitted --')
        print('The following data if for debugging:')
        print(f'Request: {data}')
        print(f'Response: {response}')

    @catch
    def answer_questions_V2(self, url: str):

        try:
            aaid = FIND_DIGIT_REGEX.findall(AAID_REGEX.findall(url)[0])[0]
            print(aaid)
        except IndexError:
            raise InvalidURLException(url)

        while True:  
            url = "".join(url.split("&qnum=")[:1])
            try:
                url = url + "&qnum=" + data['qnum']
            except:
                url = url + "&qnum=" + '1'
            page = self.sesh.get(url, headers=self.headers).text  
            data, type_ = Parser.parse(page)  
            answer = self.find_answer(data, type_)
            data['aaid'] = aaid

            self.new_type(answer, type_) 

            data = dict(data)
            del data['qid']
            data['qnum'] = str(int(data['qnum']) + 1)
            


            




