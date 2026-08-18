# Difference With Reference Work

## Reference

This project is inspired by Code Aesthetics with Agentic Reward
Feedback.

The reference work studies HTML/code generation improvement through
aesthetic reward feedback.

## Comparison

  Component               Reference Work   Current Project
  ----------------------- ---------------- -----------------
  HTML evaluation         Yes              Yes
  Rendering               Yes              Yes
  LLM evaluation          Yes              Yes
  Reward model training   Yes              No
  Human benchmark         Yes              Planned
  Human-AI agreement      Yes              Planned

## Main Differences

### Reward Model

The reference work trains reward models using human preference data.

The current project uses an LLM-as-a-Judge approach.

### Human-AI Agreement

Future experiments will compare verifier scores with human scores using
correlation metrics.

### Interactive Evaluation

The reference includes webpage interaction evaluation. The current
version focuses on static HTML evaluation.

## Summary

The current project reproduces the basic verifier pipeline and extends
it into a lightweight HTML quality evaluation framework.
