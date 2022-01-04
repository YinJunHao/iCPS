import logging
from nltk.corpus import stopwords
import json
import bson
import nltk
nltk.download('stopwords')

logger = logging.getLogger(__name__)


def string2func_name(sentence):
    """
    Converts a translated sentence into a variable name in snake case (i.e. snake_case)
    """
    words = tokenize_sentence(sentence)
    out = ""
    for word in words:
        out += "_"+word
    return out[1:]


def check_none(list):
    """
    Check if item in a list if None. Returns a list of boolean where False elements represent None entry in the original list.
    """
    out = []
    for item in list:
        if item is None:
            out.append(False)
        else:
            out.append(True)
    return out


def to_form_list(sentence_list, as_tuple=True):
    """
    Converts a translated sentence list into a list variables.  \n
    Result can be returned as a list of tuple in the form (variable, sentence) or only as a list of variables.
    """
    out = []
    for sentence in sentence_list:
        var_name = string2func_name(sentence)
        if as_tuple:
            tuple_out = (var_name, sentence)
            out.append(tuple_out)
        else:
            out.append(var_name)
    return out


def tokenize_sentence(sentence):
    """
    Splits the inputted sentence into separate words. Then stopwords as defined in NLTK is removed. \n
    Result is returned as a list. \n
    \n
    For more info: https://pythonspot.com/nltk-stop-words/
    """
    word_list = sentence.lower().split(" ")
    filtered_words = [
        word for word in word_list if word not in stopwords.words('english')]
    return filtered_words
