import argparse
import numpy as np
import math


'''This script computes the overall score for the objective and subjective evaluations'''

parser = argparse.ArgumentParser()
parser.add_argument("--mode", help="must be obj or sub, representing the objective and subjective evaluation", default='obj')
parser.add_argument("--feedback_overall", help="the overall score of feedback dimension", default=math.inf, type=float)
parser.add_argument("--comp_feedback_overall", help="the overall score of comparison dimension", default=math.inf, type=float)
parser.add_argument("--correction_overall", help="the overall score of correction dimension", default=math.inf, type=float)
parser.add_argument("--meta_feedback_overall", help="the overall score of meta-feedback dimension", default=math.inf, type=float)
args = parser.parse_args()


def normalize(score):
    # normlize the corrections for objective evaluation
    return (score + 100) / 2


if __name__ == "__main__":
    scores = []
    for index, score in enumerate([
        args.feedback_overall,
        args.comp_feedback_overall,
        args.correction_overall,
        args.meta_feedback_overall
    ]):
        if score != math.inf:
            if args.mode == 'obj' and index in [0, 3]:
                score = normalize(score)
            scores.append(score)
    print(scores)

    assert len(scores) > 0, 'No valid scores'
    print('Overall Scores:', round(np.mean(scores), 4))
