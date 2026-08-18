# System Design

## Overview

This project builds an automatic HTML quality verifier for LLM generated
webpages.

The verifier evaluates three dimensions:

1.  Usability
2.  Functionality
3.  Aesthetics

## Pipeline

    HTML Input
        |
        v
    HTML Renderer
        |
        v
    Screenshot + Runtime Information
        |
        v
    Multi-dimensional Evaluation
        |
        v
    Quality Score

## Components

### HTML Renderer

Responsible for loading HTML, rendering pages, capturing screenshots,
and collecting runtime information.

Technology: Playwright.

### Usability Checker

Checks whether HTML pages run correctly, including rendering errors and
resource failures.

### Functionality Judge

Uses LLM evaluation to determine whether the webpage satisfies user
requirements.

### Aesthetic Judge

Evaluates layout, color, typography, and visual quality.

## Future Improvements

-   Human annotation dataset
-   Human-AI agreement measurement
-   Reward model training
-   Interactive agent evaluation
