import re
from dff.script import TRANSITIONS
from dff.script import RESPONSE
from dff.script import Message
import dff.script.conditions as cnd
from dff.pipeline import Pipeline

toy_script = {
    'greeting_flow': {
        'start_node': {
            RESPONSE: Message(),
            TRANSITIONS: {
                'node1': cnd.exact_match(Message(text='Hi')),
            },
        },
        'node1': {
            RESPONSE: Message(text='Hi, how are you?'),
            TRANSITIONS: {
                'node2': cnd.regexp('.*how are you', re.IGNORECASE),
            },
        },
        'node2': {
            RESPONSE: Message(text='Good. What do you want to talk about?'),
            TRANSITIONS: {
                'node3': cnd.all([cnd.regexp('talk'), cnd.regexp('about.*music')]),
            },
        },
        'node3': {
            RESPONSE: Message(text='Sorry, I can not talk about music now.'),
            TRANSITIONS: {
                'node4': cnd.regexp(re.compile('Ok, goodbye.')),
            },
        },
        'node4': {
            RESPONSE: Message(text='bye'),
            TRANSITIONS: {
                'node1': cnd.any([hi_lower_case_condition, cnd.exact_match(Message(text='hello'))]),
            },
        },
        'fallback_node': {
            RESPONSE: Message(text='Ooops'),
            TRANSITIONS: {
                'node1': complex_user_answer_condition,
                'fallback_node': predetermined_condition(True),
            },
        },
    },
}

pipeline = Pipeline.from_script(toy_script, start_label=('greeting_flow', 'start_node'), fallback_label=('greeting_flow', 'fallback_node'))
