import praw
import configparser

config = configparser.ConfigParser()
config.optionxform = str
config.read('config.ini')

account_info = config['Account']

reddit = praw.Reddit(
    client_id=account_info['client_id'],
    client_secret=account_info['client_secret'],
    user_agent=account_info['user_agent'],
    username=account_info['username'],
    password=account_info['password'],
)


def get_thread_ticker(title, body):
    capitalized_words = set()

    def helper(string):
        tokenized_string = string.split()
        for word in tokenized_string:
            if word.isupper():
                capitalized_words.add(word)
    helper(title)
    helper(body)
    return capitalized_words


def funcname(parameter_list):
    """
    docstring
    """
    pass


def get_posts():
    """get all posts from the last 24 hours
    """
    pass