from models import User
import tortoise.functions.functions as F

import matplotlib.pyplot as plt

from utils.tortoise_orm import flatten_tortoise_model


def analyse_user_language():
    """
    Creates bar chart for analysing languages overall by users
    """
    users_lst = list(flatten_tortoise_model(el) for el in User.all())

    lang_counts = {}
    for user in users_lst:
        lang = user.language_code
        if lang in lang_counts:
            lang[lang] += 1
        else:
            lang[lang] = 1

    # Sort the data by score
    sorted_scores = sorted(lang_counts.items())

    # Extract the scores and counts for the chart
    scores, counts = zip(*sorted_scores)

    # Create a bar chart
    plt.bar(scores, counts)
    plt.xlabel('Lang')
    plt.ylabel('Count')
    plt.title('User Score Distribution')

    # Display the chart
    plt.show()



