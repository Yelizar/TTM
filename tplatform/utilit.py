"""This script for editing quiz questions"""

import json
import os

HELLO_STRING = """Hello! I am a bot designed to help you find out at which level of English you are.

You will receive a list of 120 multiple-choice questions, 20 at each level from Starter to Advanced (covering CEFR levels A1 to C1). Choose the best answer for each question.

The first HUNDRED (100) users to send their results to @talktome_agency will receive a gift from TalkToMe Ltd.

Are you ready? Push the "I am ready" button!"""

ADVERT_STRING = """Good job!

A gift from TalkToMe Ltd is a FREE online oral test for the first HUNDRED (100) users.

An oral placement test, designed to be used in conjunction with this test, is available via the TalkToMe Ltd. service.

Send your results to @talktome_agency and we will provide you with a native speaker for an online oral test."""


def check_answer(answer, right):
    if answer == right:
        return '1'
    else:
        return '0'


def make_a_query(question):
    query = '{id}. {question}'.format(id=question[0], question=question[1]["question"]),
                 [(question[1]["A"],
                   '*q{current}#*q{next}#{data}'.format(current=question[0],
                                                                        next=int(question[0]) + 1,
                                                                        data=check_answer(answer=question[1]["A"],
                                                                                          right=question[1]["right"]))),
                  (question[1]["B"],
                   '*q{current}#*q{next}#{data}'.format(current=question[0],
                                                                        next=int(question[0]) + 1,
                                                                        data=check_answer(answer=question[1]["B"],
                                                                                          right=question[1]["right"]))),
                  (question[1]["C"],
                   '*q{current}#*q{next}#{data}'.format(current=question[0],
                                                                        next=int(question[0]) + 1,
                                                                        data=check_answer(answer=question[1]["C"],
                                                                                          right=question[1]["right"])))]]
    if len(question[1]) == 6:
        query[1].append((question[1]["D"],
                   '*q{current}#*q{next}#{data}'.format(current=question[0],
                                                                        next=int(question[0]) + 1,
                                                                        data=check_answer(answer=question[1]["D"],
                                                                                          right=question[1]["right"]))))
    return tuple(query)


def add_questions():
    """Returns edited questions for a new format"""
    edited_questions = {'*placement': (None, [('Start Test', '*start_test'),
                                           ('Check result', '*check_result')]),
                        '*start_test': (HELLO_STRING, [('I am ready!', '*q1')])}

    # dictionary with data for quiz from JSON file
    with open(os.path.dirname(__file__)+"/quiz.json", "r") as read_file:
        quiz = json.load(read_file)
    #editing each question from quiz dictionary
    for question in quiz['questions'].items():
        edited_questions['*q{i}'.format(i=question[0])] = make_a_query(question)

    return edited_questions
