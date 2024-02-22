#!/bin/bash

echo "mode: $1"    # feedback, correction, comp_feedback, meta_feedback
echo "format: $2"    # sub, obj
echo "set: $3"    # test, dev
echo "save results into: $4"    # any name for saving the evaluation results
if [ $1 == 'feedback' ];
then
    if [ $2 == "obj" ]; 
    then  
        echo "Inference Objective Evaluation for Feedback Critique Task"
        python run_feedback.py --root_dir "../data/criticbench_v1.3" --prediction_dir "../example_data/prediction_v1.3" --batch_size 16 --split $3 --obj True
    else
        echo "Inference Subjective Evaluation for Feedback Critique Task"
        python run_feedback.py --root_dir "../data/criticbench_v1.3" --prediction_dir "../example_data/prediction_v1.3" --evaluation_dir "../example_data/evaluation_v1.3/" --batch_size 1 --split $3 --obj False
    fi
elif [ $1 == 'correction' ];
then
    if [ $2 == "obj" ]; 
    then  
        echo "Inference Objective Evaluation for Correction Critique Task"
        python run_correction.py --root_dir "../data/criticbench_v1.3" --prediction_dir "../example_data/prediction_v1.3" --batch_size 16 --split $3 --obj True
    else
        echo "Inference Subjective Evaluation for Correction Critique Task"
        python run_correction.py --root_dir "../data/criticbench_v1.3" --prediction_dir "../example_data/prediction_v1.3" --evaluation_dir "../example_data/evaluation_v1.3/" --batch_size 1 --split $3 --obj False
    fi
elif [ $1 == 'comp_feedback' ];
then
    if [ $2 == "obj" ]; 
    then  
        echo "Inference Objective Evaluation for Comparison-based Feedback Critique Task"
        python run_comp_feedback.py --root_dir "../data/criticbench_v1.3" --prediction_dir "../example_data/prediction_v1.3" --batch_size 16 --split $3 --obj True
    else
        echo "Inference Subjective Evaluation for Comparison-based Feedback Critique Task"
        python run_comp_feedback.py --root_dir "../data/criticbench_v1.3" --prediction_dir "../example_data/prediction_v1.3" --evaluation_dir "../example_data/evaluation_v1.3/" --batch_size 1 --split $3 --obj False
    fi
elif [ $1 == 'meta_feedback' ];
then
    echo "Inference Objective Evaluation for Meta-Feedback Critique Task"
    python run_meta_feedback.py --root_dir "../data/criticbench_v1.3" --prediction_dir "../example_data/prediction_v1.3" --batch_size 16 --split $3 --obj True
fi
