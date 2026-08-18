# Experiment Report

## Objective

Evaluate whether the HTML verifier can replace part of human evaluation.

The key metric is Human-AI Agreement.

## Dataset

Current experiments use HTML samples from the project benchmark.

## Evaluation Process

    HTML Samples
     |
     v
    Human Evaluation
     |
     v
    Verifier Evaluation
     |
     v
    Agreement Calculation

## Human Evaluation

Humans score three dimensions:

-   Usability
-   Functionality
-   Aesthetics

## Verifier Evaluation

The verifier outputs structured scores for the same dimensions.

## Metrics

-   Pearson Correlation
-   Spearman Correlation
-   Ranking Accuracy

## Current Progress

Completed:

-   HTML rendering pipeline
-   Batch evaluation framework
-   LLM evaluation interface
-   Three-dimensional evaluation design

Not completed:

-   Large-scale human annotation
-   Human-AI agreement calculation
-   Reward model training

## Future Work

-   Collect human evaluation data
-   Improve agreement rate
-   Build specialized HTML quality reward models
