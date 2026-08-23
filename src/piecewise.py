"""
分段门控（piecewise / gated）评价模型。

人工评价网页是分段函数：
    先看 能不能用   -> DEAD / BROKEN
    再看 是不是好用 -> CLUNKY
    最后 好不好看   -> POLISHED

分段逻辑必须放在确定性代码里（而不是 LLM prompt 里），否则模型会"妥协"，
允许好看救不能用。档与档之间不 trade-off：
    旧加权求和:  overall = mean(func, ux, aes)   （美观可抵消功能崩溃）
    分段门控:    DEAD∈[0,2]  BROKEN∈[0,4]  CLUNKY∈[0,6]  POLISHED∈[0,10]

维度分统一为 0-10。档内才是加权求和；档位判定 + 档内权重都由
calibrate.py 在训练集上网格搜索校准（这里的默认值只是起点）。
"""

REGIMES = ("DEAD", "BROKEN", "CLUNKY", "POLISHED")

# 默认阈值（Token Plan 模型优化后）
DEAD_EXEC_THRESHOLD = 0.20  # exec_health 低于此 -> DEAD
F_DEAD_THRESHOLD = 3.5      # functional 低于此 -> BROKEN
UX_THRESHOLD = 3.5          # usability 低于此 -> CLUNKY

# 视觉/交互型类别：对功能性失败更宽容（整体能跑，个别功能坏不算BROKEN）
VISUAL_INTERACTIVE_CATEGORIES = {"3D design", "Game dev"}
F_DEAD_THRESHOLD_VISUAL = 5.0  # 视觉型：functional 低于此 -> BROKEN（更宽松）
CAP_DEAD_INTERACTIONS_VISUAL = 4  # 视觉型：需要 4+ 死交互才封顶（而非 3）

# 各档上限：定义"不能 trade-off"性质
CAPS = {"DEAD": 2.0, "BROKEN": 4.0, "CLUNKY": 6.0, "POLISHED": 10.0}

# 各档档内权重（档内才是加权求和）
WEIGHTS = {
    "DEAD":     {"functional": 0.7, "usability": 0.0, "aesthetic": 0.3},
    "BROKEN":   {"functional": 0.6, "usability": 0.0, "aesthetic": 0.4},
    "CLUNKY":   {"functional": 0.3, "usability": 0.3, "aesthetic": 0.4},
    "POLISHED": {"functional": 0.25, "usability": 0.25, "aesthetic": 0.5},
}


def exec_health(signals):
    """把渲染运行时信号折叠成 0(完全坏) .. 1(干净)。

    信号是探针/渲染阶段的客观证据；这里把它们变成"页面能不能正常加载"
    的一个连续值。阈值故意宽松——只有渲染失败 / JS 大面积崩溃才算坏，
    普通 console 噪音不算。
    """
    if not signals:
        return 0.5  # 无信号：既不判死也不判完全健康
    if signals.get("render_error"):
        return 0.0
    # 错误按签名去重：同一特性的级联报错（如 3D 渲染器初始化失败）只算一次。
    # tier-50 复核：00_006164 页面能打开、但核心 3D 因页内 bug 崩溃，7 个
    # page_error 全是同一来源级联——按原始计数会误判全页崩溃(DEAD)，人工判
    # BROKEN（能打开但核心坏）。去重后同源级联只计 1 个签名；仍保留
    # "5+ 个不同签名 = 多处独立崩溃 -> 全页崩溃"的判定。
    page_errors = len({e for e in (signals.get("page_errors") or [])})
    console_errors = len({e for e in (signals.get("console_errors") or [])})
    if page_errors >= 5:
        return 0.0
    if page_errors >= 1:
        return 0.7
    if signals.get("load_timeout"):
        return 0.5
    if console_errors >= 5:
        return 0.8
    if console_errors >= 1:
        return 0.9
    return 1.0


def classify_regime(functional, usability, signals=None,
                    *, f_dead=None, ux_thresh=None, exec_dead=None,
                    category=None):
    """判定 4 档。顺序即人工的判断顺序：能不能用 -> 好不好用 -> 好不好看。
    
    对于视觉/交互型类别（3D design, Game dev），对功能性失败更宽容。
    """
    if f_dead is None:
        if category and category in VISUAL_INTERACTIVE_CATEGORIES:
            f_dead = F_DEAD_THRESHOLD_VISUAL
        else:
            f_dead = F_DEAD_THRESHOLD
    if ux_thresh is None:
        ux_thresh = UX_THRESHOLD
    if exec_dead is None:
        exec_dead = DEAD_EXEC_THRESHOLD

    if exec_health(signals) <= exec_dead:
        return "DEAD"
    if functional < f_dead:
        return "BROKEN"
    if usability < ux_thresh:
        return "CLUNKY"
    return "POLISHED"


def score_overall(functional, usability, aesthetic, signals=None,
                  *, f_dead=None, ux_thresh=None, exec_dead=None,
                  caps=None, weights=None, category=None):
    """分段组合 overall ∈ [0, 10]。返回 (regime, overall)。

    档内权重归一化到 0-10，再被档位上限截断——这就是"好看救不了不能用"。
    对于视觉/交互型类别，档位判定使用更宽松的功能性阈值。
    """
    regime = classify_regime(functional, usability, signals,
                             f_dead=f_dead, ux_thresh=ux_thresh,
                             exec_dead=exec_dead, category=category)
    w = (weights or WEIGHTS).get(regime, WEIGHTS[regime])
    cap = (caps or CAPS).get(regime, CAPS[regime])
    raw = 0.0
    for k in ("functional", "usability", "aesthetic"):
        if k in w and w.get(k):
            v = {"functional": functional, "usability": usability,
                 "aesthetic": aesthetic}.get(k, 0.0)
            if v is None:
                v = 0.0
            raw += w[k] * (v / 10.0)
    return regime, round(min(cap, raw * 10.0), 2)


def weighted_sum(functional, usability, aesthetic, weights=(0.4, 0.3, 0.3)):
    """旧模型的整体分（对照组）。默认 0.4/0.3/0.3；旧 300 页跑的是均值
    等价于 (1/3, 1/3, 1/3)。"""
    w = (weights[0], weights[1], weights[2])
    vals = (functional or 0.0, usability or 0.0, aesthetic or 0.0)
    return round(sum(a * b for a, b in zip(w, vals)), 2)


def cap_functional_score(score, interactions, category=None):
    """确定性 func 封顶：≥3 个关键交互判死 -> func 不高于 2。

    法官 prompt 要求列出真实用户会试的 3-6 个关键交互（ok=0/1/NA）。
    LLM 可能给死交互成片的页面仍打高分（如 func=4-8 但核心按钮全无反馈）。
    这是"核心交互死了，func 不能高"的分段规则，放确定性代码里，不依赖
    LLM 自觉。NA（需求里本就没有的入口）不算死交互。

    对于视觉/交互型类别（3D design, Game dev），更宽容：需要 4+ 死交互才封顶。
    阈值取 ≥3：tier-100 实测最优（功能型网站）。
    """
    if not interactions:
        return float(score)
    dead = sum(1 for i in interactions if i.get("ok") == 0)
    
    # 视觉/交互型类别更宽容
    if category and category in VISUAL_INTERACTIVE_CATEGORIES:
        if dead >= CAP_DEAD_INTERACTIONS_VISUAL:
            return min(float(score), 2.0)
    else:
        if dead >= 3:
            return min(float(score), 2.0)
    
    return float(score)
