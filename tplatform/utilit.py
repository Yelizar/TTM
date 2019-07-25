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


def make_a_query(question):
    query = ['{id}. {question}'.format(id=question[0], question=question[1]["question"]),
                 [('a. ' + question[1]["A"], '*q{current}#{data}'.format(current=question[0], data=question[1]["A"])),
                  ('b. ' + question[1]["B"], '*q{current}#{data}'.format(current=question[0], data=question[1]["B"])),
                  ('c. ' + question[1]["C"], '*q{current}#{data}'.format(current=question[0], data=question[1]["C"]))]]
    if len(question[1]) == 6:
        query[1].append(
            ('d. ' + question[1]["D"], '*q{current}#{data}'.format(current=question[0], data=question[1]["D"]))
        )
    return tuple(query)


def add_questions():
    """Returns edited questions for a new format"""
    # dictionary with data for quiz from JSON file
    with open(os.path.dirname(__file__)+"/quiz.json", "r") as read_file:
        quiz = json.load(read_file)
    # editing each question from quiz dictionary
    edited_questions = {}
    answers = {}
    for question in quiz['questions'].items():
        edited_questions['*q{i}'.format(i=question[0])] = make_a_query(question)
        answers['{i}'.format(i=question[0])] = question[1]['right']
    return edited_questions, answers
