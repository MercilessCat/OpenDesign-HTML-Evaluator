# OpenDesign HTML Evaluator

A Large Language Model based HTML Quality Verifier for evaluating
generated web pages.

## Overview

This project implements an HTML verifier that evaluates generated
webpages from three dimensions:

-   Functional correctness
-   Usability
-   Visual aesthetics

Pipeline:

HTML + Requirement → Verifier → Multi-dimensional Scores

## Features

### Functional Evaluation

Evaluates whether HTML pages satisfy functional requirements.

Implementation:

    functional_judge.py

### Usability Evaluation

Evaluates user experience, information organization, and interaction
flow.

Implementation:

    usability_checker.py

### Aesthetic Evaluation

Evaluates webpage visual quality using browser rendering.

Pipeline:

    HTML
     |
     v
    Playwright Chromium
     |
     v
    Screenshot
     |
     v
    Visual Analysis
     |
     v
    Aesthetic Score

Implementation:

    html_renderer.py
    image_analyzer.py
    aesthetic_judge.py

## Architecture

    HTML + Requirement

            |
            v

        verifier.py

            |
      -----------------
      |       |       |
      v       v       v

    Functional Usability Aesthetic

            |
            v

        Final Score

## Project Structure

    OpenDesign-HTML-Evaluator

    ├── dataset.json
    ├── samples
    ├── results
    ├── screenshot
    ├── report
    └── src
        ├── config.py
        ├── verifier.py
        ├── functional_judge.py
        ├── usability_checker.py
        ├── aesthetic_judge.py
        ├── html_renderer.py
        ├── image_analyzer.py
        ├── batch_evaluate.py
        ├── agreement_evaluator.py
        └── report_generator.py

## Installation

Install dependencies:

``` bash
pip install openai playwright pillow scipy numpy
```

Install browser:

``` bash
playwright install chromium
```

## Configuration

Create:

    src/config.py

Example:

``` python
API_KEY = "your_api_key"

BASE_URL = "https://api.deepseek.com"

MODEL = "deepseek-chat"
```

## Usage

Single evaluation:

``` python
from verifier import verify_html

result = verify_html(
    html,
    requirement
)

print(result)
```

Batch evaluation:

``` bash
python batch_evaluate.py
```

Human agreement evaluation:

``` bash
python agreement_evaluator.py
```

Report generation:

``` bash
python report_generator.py
```

## Human Agreement Evaluation

The verifier is evaluated by comparing:

    Human Annotation

            VS

    Verifier Prediction

Metrics:

-   MAE
-   Accuracy
-   Pearson correlation
-   Spearman correlation

## Methodology

The project follows an LLM-as-a-Judge framework:

1.  Input HTML and user requirements.
2.  Evaluate webpage quality using an LLM.
3.  Generate structured scores.
4.  Compare with human annotations.

## Improvements Compared With Basic Baselines

Implemented improvements:

-   Three-dimensional evaluation instead of single score.
-   Browser rendering based aesthetic evaluation.
-   Automated batch evaluation pipeline.
-   Human agreement measurement.

## Future Work

Possible improvements:

-   Vision-language model integration.
-   Larger HTML benchmark datasets.
-   Better human agreement rate.
-   More advanced interaction testing.

## License

This project is for research and educational purposes.
