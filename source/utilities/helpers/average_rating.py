#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the MIT License.
## You may obtain a copy of the License at:
##     https://opensource.org/licenses/MIT
##
## This software is provided "as is," without warranty of any kind.
##
#############################################################################


def calculate_average_rating(ratings, target_scale=5):
    """
    Calculate the average rating on a target scale (default is 5), rounded to one decimal place.

    Parameters:
    - ratings: List of tuples where each tuple contains (score, scale).
    - target_scale: The scale to which all scores will be converted (default is 5).

    Returns:
    - The overall average rating on the target scale, rounded to one decimal place.
    """
    scaled_ratings = [(score / scale) * target_scale for score, scale in ratings]
    average = sum(scaled_ratings) / len(scaled_ratings)

    return round(average, 1)


# Example usage
if __name__ == "__main__":
    ratings = [
        (50, 100),  # metacritic
        (8.1, 10),  # metacritic
        (4.8, 10),  # gamespot
        (7.7, 10),  # imdb
        (5.5, 10),  # ign
        (7.7, 10),  # ign
        (4.1, 5),  # gog
        (4.7, 5),  # fanatical
    ]

    average_rating = calculate_average_rating(ratings)
    print(average_rating)
