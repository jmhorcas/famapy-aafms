import os
import logging 
import requests

import telebot 

from famapy.metamodels.fm_metamodel.transformations.featureide_parser import FeatureIDEParser
from famapy.metamodels.fm_metamodel.operations.metrics import Metrics
from famapy.metamodels.fm_metamodel.operations import get_core_features, average_branching_factor, max_depth_tree, count_configurations


HTTP_API_TOKEN = ''


def int_to_scientific_notation(n: int, precision: int = 2) -> str:
    """Convert a large int into scientific notation.
    
    It is required for large numbers that Python cannot convert to float,
    solving the error `OverflowError: int too large to convert to float`.
    """
    str_n = str(n)
    decimal = str_n[1:precision+1]
    exponent = str(len(str_n) - 1)
    return str_n[0] + '.' + decimal + 'e' + exponent


def analyze_model(file_name: str) -> str:
    fm = FeatureIDEParser(file_name).transform() 
    metrics = Metrics(fm)
    response = f"*Root:* {fm.root.name}\n"
    response += f"*Features:* {metrics.nof_features()}\n"
    response += f"*Cross-tree constraints:* {metrics.nof_cross_tree_constraints()}\n"
    nof_configs = count_configurations(fm)
    response += f"*Configurations:* {'≤' if metrics.nof_cross_tree_constraints() > 0 else ''} {int_to_scientific_notation(nof_configs) if nof_configs > 1e6 else nof_configs}\n"
    response += f"*Group-features:* {metrics.nof_group_features()}\n"
    response += f"*Alternative-groups:* {metrics.nof_alternative_groups()}\n"
    response += f"*Or-groups:* {metrics.nof_or_groups()}\n"
    response += f"*Abstract features:* {metrics.nof_abstract_features()}\n"
    response += f"*Leaf features:* {metrics.nof_leaf_features()}\n"
    response += f"*Core features:* {len(get_core_features(fm))}\n"
    response += f"*Max depth tree:* {max_depth_tree(fm)}\n"
    response += f"*Branching factor:* {average_branching_factor(fm)}\n"

    print(fm)
    print(fm.root.get_relations())
    for r in fm.root.get_relations():
        print([f for f in r.children])
    return response


if __name__ == "__main__":
    logging.basicConfig(filename='famapybot.log', filemode='a+', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',)
    logging.info("FaMaPyBot is running...")

    bot = telebot.TeleBot(HTTP_API_TOKEN, parse_mode='MARKDOWN')

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
	    bot.reply_to(message, "Send me a feature model to analyze (in FeatureIDE .xml format).")

    @bot.message_handler(content_types=['document'])
    def analyze_feature_model(message):
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name
        content = requests.get(f'https://api.telegram.org/file/bot{HTTP_API_TOKEN}/{file_info.file_path}')

        if content.ok:
            with open(file_name, 'w+') as file:
                file.write(content.text)

            response = analyze_model(file_name)

            if os.path.exists(file_name):
                os.remove(file_name)      
            
            bot.reply_to(message, response)
            #bot.reply_to(message, "Error processing the file.")
        else:
            bot.reply_to(message, "Error getting the file.")

    bot.polling()

    logging.info("FaMaPyBot has finished!")



