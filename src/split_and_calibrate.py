"""Train/test split experiment: calibrate thresholds on train, evaluate on test.

Stratified 80/20 split by category. Grid search on training set ONLY.
Test set is held out — never used during optimization.
"""

import json
import os
import random
import logging

import numpy as np

from piecewise import (
    classify_regime, cap_functional_score,
    VISUAL_INTERACTIVE_CATEGORIES,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

BASE = os.path.join(os.path.dirname(__file__), "..")
LABELS_PATH = os.path.join(BASE, "aescode_out", "human_scores_100.json")
RESULTS_DIR = os.path.join(BASE, "aescode_out", "results")
SPLIT_PATH = os.path.join(BASE, "aescode_out", "splits_train80_test20.json")

F_DEAD_RANGE = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0]
UX_RANGE = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
EXEC_DEAD_RANGE = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4]

SEED = 42
TRAIN_RATIO = 0.8


def load_labeled_data():
    with open(LABELS_PATH, encoding="utf-8") as f:
        labels_list = json.load(f)

    labels = {}
    categories = {}
    for item in labels_list:
        if item.get("regime") is None:
            continue
        labels[item["row_id"]] = item["regime"]
        categories[item["row_id"]] = item["category"]

    data = []
    for rid, human_label in labels.items():
        fpath = os.path.join(RESULTS_DIR, f"{rid}.json")
        if not os.path.exists(fpath):
            log.warning("No result file for %s, skipping", rid)
            continue
        with open(fpath, encoding="utf-8") as f:
            r = json.load(f)

        func_raw = r["functional"].get("raw_score", r["functional"]["score"])
        interactions = r["functional"].get("interactions", [])
        category = r.get("category", categories.get(rid, "unknown"))

        capped = cap_functional_score(func_raw, interactions, category)

        data.append({
            "row_id": rid,
            "category": category,
            "functional_raw": func_raw,
            "functional_capped": capped,
            "usability": r["usability"]["score"],
            "aesthetic": r["aesthetic"]["score"],
            "signals": r.get("signals", {}),
            "human_label": human_label,
            "interactions": interactions,
        })

    return data


def stratified_split(data, train_ratio=TRAIN_RATIO, seed=SEED):
    rng = random.Random(seed)

    by_cat = {}
    for d in data:
        cat = d["category"]
        by_cat.setdefault(cat, []).append(d)

    train, test = [], []
    for cat in sorted(by_cat):
        items = by_cat[cat]
        rng.shuffle(items)
        n_train = round(len(items) * train_ratio)
        train.extend(items[:n_train])
        test.extend(items[n_train:])

    rng.shuffle(train)
    rng.shuffle(test)
    return train, test


def predict(data, f_dead, ux_thresh, exec_dead):
    preds = []
    for d in data:
        regime = classify_regime(
            d["functional_capped"], d["usability"], d["signals"],
            f_dead=f_dead, ux_thresh=ux_thresh, exec_dead=exec_dead,
            category=d["category"],
        )
        preds.append(regime)
    return preds


def accuracy(preds, labels):
    correct = sum(1 for p, l in zip(preds, labels) if p == l)
    return correct / len(labels) if labels else 0.0


def grid_search_train(train_data):
    best_acc = 0
    best_config = None
    total = len(F_DEAD_RANGE) * len(UX_RANGE) * len(EXEC_DEAD_RANGE)
    tested = 0

    true_labels = [d["human_label"] for d in train_data]

    for f_dead in F_DEAD_RANGE:
        for ux_thresh in UX_RANGE:
            for exec_dead in EXEC_DEAD_RANGE:
                preds = predict(train_data, f_dead, ux_thresh, exec_dead)
                acc = accuracy(preds, true_labels)
                tested += 1

                if acc > best_acc:
                    best_acc = acc
                    best_config = {
                        "f_dead": f_dead,
                        "ux_thresh": ux_thresh,
                        "exec_dead": exec_dead,
                        "train_accuracy": round(best_acc, 4),
                        "train_correct": int(best_acc * len(train_data)),
                        "train_total": len(train_data),
                    }

    log.info("Grid search: %d configs tested, best train acc=%.4f", tested, best_acc)
    return best_config


def evaluate(data, config, label=""):
    preds = predict(data, config["f_dead"], config["ux_thresh"], config["exec_dead"])
    true_labels = [d["human_label"] for d in data]
    acc = accuracy(preds, true_labels)
    correct = sum(1 for p, l in zip(preds, true_labels) if p == l)

    print(f"\n{'=' * 50}")
    print(f"  {label}")
    print(f"{'=' * 50}")
    print(f"  Accuracy: {acc:.1%} ({correct}/{len(data)})")

    by_cat = {}
    for d, p in zip(data, preds):
        cat = d["category"]
        by_cat.setdefault(cat, {"correct": 0, "total": 0})
        by_cat[cat]["total"] += 1
        if p == d["human_label"]:
            by_cat[cat]["correct"] += 1

    print(f"\n  Per-category:")
    for cat in sorted(by_cat):
        info = by_cat[cat]
        cat_acc = info["correct"] / info["total"] if info["total"] else 0
        print(f"    {cat:25s} {cat_acc:.1%} ({info['correct']}/{info['total']})")

    by_regime = {}
    for d, p in zip(data, preds):
        h = d["human_label"]
        by_regime.setdefault(h, {"correct": 0, "total": 0})
        by_regime[h]["total"] += 1
        if p == h:
            by_regime[h]["correct"] += 1

    print(f"\n  Per-regime:")
    for regime in ["DEAD", "BROKEN", "CLUNKY", "POLISHED"]:
        if regime in by_regime:
            info = by_regime[regime]
            r_acc = info["correct"] / info["total"] if info["total"] else 0
            print(f"    {regime:10s} {r_acc:.1%} ({info['correct']}/{info['total']})")

    from piecewise import REGIMES
    confusion = {p: {h: 0 for h in REGIMES} for p in REGIMES}
    for d, p in zip(data, preds):
        h = d["human_label"]
        if p in confusion and h in confusion[p]:
            confusion[p][h] += 1

    print(f"\n  Confusion matrix (rows=pred, cols=human):")
    header = "           " + "  ".join(f"{r:>10}" for r in REGIMES)
    print(header)
    for pred in REGIMES:
        row = f"  {pred:>10}"
        for human in REGIMES:
            row += f"  {confusion[pred][human]:>10}"
        print(row)

    mismatches = [(d, p) for d, p in zip(data, preds) if p != d["human_label"]]
    if mismatches:
        print(f"\n  Mismatches ({len(mismatches)}):")
        for d, p in mismatches:
            print(f"    {d['row_id']:12s} cat={d['category']:25s} "
                  f"human={d['human_label']:10s} pred={p:10s} "
                  f"func_raw={d['functional_raw']:.1f} func_cap={d['functional_capped']:.1f} "
                  f"ux={d['usability']:.1f}")

    return {
        "accuracy": round(acc, 4),
        "correct": correct,
        "total": len(data),
        "by_category": {cat: {"correct": info["correct"], "total": info["total"],
                              "accuracy": round(info["correct"] / info["total"], 4)}
                        for cat, info in by_cat.items()},
    }


def main():
    print("Loading labeled data...")
    data = load_labeled_data()
    print(f"Loaded {len(data)} samples with valid labels")

    from collections import Counter
    regime_dist = Counter(d["human_label"] for d in data)
    cat_dist = Counter(d["category"] for d in data)
    print(f"Regime distribution: {dict(regime_dist)}")
    print(f"Category distribution: {dict(cat_dist)}")

    print(f"\nSplitting {len(data)} samples: {TRAIN_RATIO:.0%} train / {1-TRAIN_RATIO:.0%} test (seed={SEED})...")
    train_data, test_data = stratified_split(data)

    train_regimes = Counter(d["human_label"] for d in train_data)
    test_regimes = Counter(d["human_label"] for d in test_data)
    print(f"Train: {len(train_data)} samples, regimes: {dict(train_regimes)}")
    print(f"Test:  {len(test_data)} samples, regimes: {dict(test_regimes)}")

    train_cats = Counter(d["category"] for d in train_data)
    test_cats = Counter(d["category"] for d in test_data)
    print(f"\nTrain categories: {dict(train_cats)}")
    print(f"Test  categories: {dict(test_cats)}")

    split_info = {
        "seed": SEED,
        "train_ratio": TRAIN_RATIO,
        "train_ids": [d["row_id"] for d in train_data],
        "test_ids": [d["row_id"] for d in test_data],
        "train_regimes": dict(train_regimes),
        "test_regimes": dict(test_regimes),
    }
    with open(SPLIT_PATH, "w", encoding="utf-8") as f:
        json.dump(split_info, f, indent=2, ensure_ascii=False)
    print(f"\nSplit saved to {SPLIT_PATH}")

    print(f"\n{'=' * 50}")
    print(f"  GRID SEARCH on training set ({len(train_data)} samples)")
    print(f"  (test set is NOT used during this step)")
    print(f"{'=' * 50}")
    best_config = grid_search_train(train_data)
    print(f"\nBest thresholds:")
    print(f"  F_DEAD:     {best_config['f_dead']}")
    print(f"  UX_THRESH:  {best_config['ux_thresh']}")
    print(f"  EXEC_DEAD:  {best_config['exec_dead']}")
    print(f"  Train acc:  {best_config['train_accuracy']:.1%} "
          f"({best_config['train_correct']}/{best_config['train_total']})")

    evaluate(train_data, best_config, label="TRAINING SET")
    evaluate(test_data, best_config, label="TEST SET (held out)")

    print(f"\n{'=' * 50}")
    print(f"  SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Train: {best_config['train_accuracy']:.1%} ({best_config['train_correct']}/{best_config['train_total']})")
    test_preds = predict(test_data, best_config["f_dead"], best_config["ux_thresh"], best_config["exec_dead"])
    test_acc = accuracy(test_preds, [d["human_label"] for d in test_data])
    test_correct = sum(1 for p, d in zip(test_preds, test_data) if p == d["human_label"])
    print(f"  Test:  {test_acc:.1%} ({test_correct}/{len(test_data)})")
    print(f"\n  Gap (train - test): {best_config['train_accuracy'] - test_acc:+.1%}")
    if best_config['train_accuracy'] - test_acc > 0.1:
        print(f"  WARNING: Train significantly outperforms test — possible overfitting")
    else:
        print(f"  OK: No significant overfitting detected")


if __name__ == "__main__":
    main()
