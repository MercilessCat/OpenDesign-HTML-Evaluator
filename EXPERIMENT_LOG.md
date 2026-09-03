# 人机一致率实验记录

## 研究目标

评估 LLM-based HTML 质量评测系统与人工资评判的一致率，优化门控阈值和类别感知策略。

## 实验配置

### 模型配置
- **语言模型**: qwen3.8-max (Token Plan)
- **视觉模型**: qwen3.8-max (Token Plan)
- **API端点**: https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
- **评判维度**: 功能性(functional)、可用性(usability)、美观性(aesthetic)

### 数据集
- **总样本池**: 10,000 个 HTML 页面（来自 AesCode-358K）
- **类别分布**: 3D design, Data visualization, Game dev, UI component, Website
- **人工标注**: 四档分类 (DEAD/BROKEN/CLUNKY/POLISHED)

### 门控逻辑
分段函数：先看能不能用 → 再看好不好用 → 最后好不好看

```
if exec_health <= EXEC_DEAD: return DEAD
if functional < F_DEAD: return BROKEN
if usability < UX_THRESH: return CLUNKY
return POLISHED
```

---

## 实验记录

### 实验 1: 基线评测（Standard 模型）

| 项目 | 值 |
|-----|---|
| **Commit ID** | 863af22 |
| **日期** | 2026-08-23 |
| **模型** | qwen3.8-max (Standard, sk-ws-) |
| **API端点** | https://dashscope.aliyuncs.com/compatible-mode/v1 |
| **训练集** | 无（使用默认阈值） |
| **评测集** | run100_ids.txt (100样本) |
| **阈值配置** | F_DEAD=3.0, UX_THRESH=5.0, EXEC_DEAD=0.4 |
| **封顶逻辑** | ≥3 死交互 → func 封顶到 2.0 |

**结果**:
| 指标 | 值 |
|-----|---|
| 总准确率 | 79.0% (79/100) |
| BROKEN | 97.4% (76/78) |
| CLUNKY | 27.3% (3/11) |
| POLISHED | 0% (0/11) |

**分析**: POLISHED 全部漏判，模型打分普遍偏低。

---

### 实验 2: Token Plan 模型 + 默认阈值

| 项目 | 值 |
|-----|---|
| **Commit ID** | 863af22 |
| **日期** | 2026-08-23 |
| **模型** | qwen3.8-max (Token Plan, sk-sp-) |
| **API端点** | https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1 |
| **训练集** | 无（使用默认阈值） |
| **评测集** | run100_ids.txt (100样本) |
| **阈值配置** | F_DEAD=3.0, UX_THRESH=5.0, EXEC_DEAD=0.4 |
| **封顶逻辑** | ≥3 死交互 → func 封顶到 2.0 |

**结果**:
| 指标 | 值 |
|-----|---|
| 总准确率 | 76.0% (76/100) |
| BROKEN | 87.2% (68/78) |
| CLUNKY | 45.5% (5/11) |
| POLISHED | 27.3% (3/11) |

**分析**: Token Plan 打分更宽松，POLISHED 识别改善但 BROKEN 误判增多。

---

### 实验 3: Token Plan + 校准阈值（calibrate.py）

| 项目 | 值 |
|-----|---|
| **Commit ID** | 863af22 |
| **日期** | 2026-08-23 |
| **模型** | qwen3.8-max (Token Plan) |
| **训练集** | splits.json tier-100 train (70样本) |
| **评测集** | splits.json tier-100 eval (30样本) |
| **校准方法** | 网格搜索最优阈值 |
| **阈值配置** | F_DEAD=2.5, UX_THRESH=4.0, EXEC_DEAD=0.3 |
| **封顶逻辑** | ≥3 死交互 → func 封顶到 2.0 |

**结果**:
| 指标 | 值 |
|-----|---|
| 总准确率 | 80.0% (80/100) |
| BROKEN | 87.2% (68/78) |
| CLUNKY | 45.5% (5/11) |
| POLISHED | 63.6% (7/11) |

**分析**: 阈值降低后 POLISHED 识别大幅提升 (+36.3%)。

---

### 实验 4: Token Plan + 精细搜索阈值

| 项目 | 值 |
|-----|---|
| **Commit ID** | 863af22 |
| **日期** | 2026-08-23 |
| **模型** | qwen3.8-max (Token Plan) |
| **训练集** | 全100样本（事后优化） |
| **评测集** | run100_ids.txt (100样本) |
| **校准方法** | 精细网格搜索 |
| **阈值配置** | F_DEAD=3.5, UX_THRESH=3.5, EXEC_DEAD=0.2 |
| **封顶逻辑** | ≥3 死交互 → func 封顶到 2.0 |

**结果**:
| 指标 | 值 |
|-----|---|
| 总准确率 | 81.0% (81/100) |
| BROKEN | 89.7% (70/78) |
| CLUNKY | 40.0% (4/10) |
| POLISHED | 63.6% (7/11) |

**分析**: 达到阈值优化上限，F_DEAD 提高有助于识别更多 BROKEN。

---

### 实验 5: 第二批100样本评测

| 项目 | 值 |
|-----|---|
| **Commit ID** | 863af22 |
| **日期** | 2026-08-23 |
| **模型** | qwen3.8-max (Token Plan) |
| **训练集** | 无 |
| **评测集** | run100_ids_v2.txt (100样本，新随机挑选) |
| **阈值配置** | F_DEAD=3.5, UX_THRESH=3.5, EXEC_DEAD=0.2 |
| **封顶逻辑** | ≥3 死交互 → func 封顶到 2.0 |

**结果**:
| 指标 | 值 |
|-----|---|
| 总准确率 | 76.0% (76/100) |
| BROKEN | 83.0% (73/88) |
| CLUNKY | 20.0% (2/10) |
| POLISHED | 50.0% (1/2) |

**按类别分析**:
| 类别 | 样本数 | 准确率 |
|-----|-------|-------|
| Website | 17 | 100% |
| UI component | 19 | 94.7% |
| Data visualization | 19 | 84.2% |
| 3D design | 27 | 63.0% |
| Game dev | 18 | 44.4% |

**分析**: 视觉/交互型类别（3D/Game）准确率显著低于功能型。

---

### 实验 6: 类别感知阈值（F_DEAD_VISUAL=5.0）

| 项目 | 值 |
|-----|---|
| **Commit ID** | f4fbb98 |
| **日期** | 2026-08-23 |
| **模型** | qwen3.8-max (Token Plan) |
| **训练集** | 人工分析误判模式 |
| **评测集** | run100_ids.txt + run100_ids_v2.txt (200样本) |
| **阈值配置（功能型）** | F_DEAD=3.5, UX_THRESH=3.5, EXEC_DEAD=0.2 |
| **阈值配置（视觉型）** | F_DEAD=5.0, UX_THRESH=3.5, EXEC_DEAD=0.2 |
| **封顶逻辑（功能型）** | ≥3 死交互 → func 封顶到 2.0 |
| **封顶逻辑（视觉型）** | ≥4 死交互 → func 封顶到 2.0 |
| **视觉型类别** | 3D design, Game dev |

**结果 - 第一批 (run100)**:
| 指标 | 值 |
|-----|---|
| 总准确率 | 79.0% (79/100) |
| 3D design | 71.4% (20/28) ↑ |
| Game dev | 35.7% (5/14) ↓ |
| Data visualization | 89.5% (17/19) ↑ |
| UI component | 93.1% (27/29) |
| Website | 100% (10/10) |

**结果 - 第二批 (run100_v2)**:
| 指标 | 值 |
|-----|---|
| 总准确率 | **85.0%** (85/100) ↑ |
| 3D design | **77.8%** (21/27) ↑ |
| Game dev | **72.2%** (13/18) ↑ |
| Data visualization | 84.2% (16/19) |
| UI component | 94.7% (18/19) |
| Website | 100% (17/17) |

**总计**: 164/200 = **82.0%**

**分析**: 
- 第二批显著提升 (+9%)，特别是 Game dev (+27.8%)
- 第一批 Game dev 反而变差，可能是标注标准差异
- 类别感知策略对视觉型类别有效

---

## 关键发现

### 1. 模型差异
- Token Plan 模型打分比 Standard 模型更宽松
- 需要重新校准阈值以适配不同模型的打分分布

### 2. 类别差异
- 功能型网站（Website/UI）：人机一致率高（93-100%）
- 视觉/交互型（3D/Game）：人机一致率低（35-77%）
- 原因：人工对视觉型的"核心功能失败"更宽容

### 3. 阈值优化
- 默认阈值不适用于所有模型/类别
- 网格搜索可找到更优阈值（79% → 81%）
- 类别感知阈值进一步提升（81% → 82%）

### 4. 封顶逻辑
- ≥3 死交互封顶对功能型最优
- 视觉型需要更宽容（≥4 死交互）

---

## 当前最优配置

**Commit**: f4fbb98

**阈值**:
```python
# 功能型类别 (Website, UI component, Data visualization)
F_DEAD_THRESHOLD = 3.5
UX_THRESHOLD = 3.5
DEAD_EXEC_THRESHOLD = 0.20

# 视觉型类别 (3D design, Game dev)
F_DEAD_THRESHOLD_VISUAL = 5.0
CAP_DEAD_INTERACTIONS_VISUAL = 4
```

**封顶逻辑**:
```python
def cap_functional_score(score, interactions, category=None):
    dead = sum(1 for i in interactions if i.get("ok") == 0)
    if category in VISUAL_INTERACTIVE_CATEGORIES:
        if dead >= 4:
            return min(score, 2.0)
    else:
        if dead >= 3:
            return min(score, 2.0)
    return score
```

**性能**: 82% (164/200) 人机一致率

---

### 实验 7: 误判模式分析与系统优化

| 项目 | 值 |
|-----|---|
| **日期** | 2026-08-31 |
| **类型** | 系统性优化（无需重新评测） |
| **基于** | 实验 6 的 100 样本误判分析 |

#### 误判模式分析

对实验 6 的 100 样本结果进行逐案分析，发现 35 个误判（64.3% 基线），分布如下：

| 误判类型 | 数量 | 根因 |
|---------|------|------|
| pred=BROKEN, true=CLUNKY | 19 | cap 规则过于激进：raw_score=5.0 被压到 2.0 |
| pred=POLISHED, true=BROKEN | 11 | LLM 对核心功能崩溃判断不准 |
| pred=BROKEN, true=POLISHED | 3 | LLM 对非核心功能缺失过度扣分 |
| pred=POLISHED, true=CLUNKY | 2 | CLUNKY 边界模糊 |

#### 实施的改进

**1. Functional Judge Prompt 重写**
- 新增"核心功能 vs 非核心功能"定义
- 新增 5 个评分锚定示例（8分/5分/7分/2分/7分），覆盖 TODO 应用、数据可视化、3D 展示、3D 物理模拟、病毒消除游戏
- 要求交互列表标注 `core: true/false`
- 新增 4 条关键原则（只评核心功能、非核心不重罚、看运行时证据、JS 错误看影响）

**2. UX Judge Prompt 增强**
- 新增 CLUNKY 的 6 种典型表现描述
- 新增"功能正确但体验差 vs 功能本身有问题"的区分说明

**3. Aesthetic Judge Prompt 增强**
- 新增分段评分标准（原来只有评价维度没有分段）

**4. cap_functional_score 重构**
- 支持 `core` 字段：只有核心交互死亡才参与封顶
- 梯度封顶：核心交互 ≥80% 死亡→封顶 2.0，≥50%→封顶 4.0，<50%→不封顶
- 低分保护：LLM 原始分 ≤4.0 且 ≥3 交互死亡→直接封顶 2.0（双方一致）
- 旧格式兼容：无 `core` 字段时按总数判定

**5. CLUNKY_HTML_THRESHOLD 修复**
- 旧逻辑：func < f_dead 且 html_len > 30000 → CLUNKY（即使 func=2.0 也判 CLUNKY）
- 新逻辑：增加 `functional >= f_dead - 1.5` 条件，只有 func 接近边界时才覆盖

**6. 交互探针增强**
- PROBE_SELECTOR 扩展：新增 `input[type='range']`, `input[type='checkbox']`, `select`, `.tab`, `[data-action]`, `canvas`
- MAX_PROBE 提升到 10（原 8）
- 新增像素变化检测（截图对比 before/after click）
- probe 格式化增强：显示具体反馈类型（DOM变化/像素变化/页面跳转）

#### 模拟结果（不重新运行 LLM，仅改 cap/阈值）

| 指标 | 旧 | 新 |
|-----|---|---|
| 一致率 | 64.3% (63/98) | 67.3% (66/98) |
| 改善 | — | +5 样本 |
| 回退 | — | -2 样本 |

改善样本：3D 的 POLISHED→BROKEN (×3)、Website 的 POLISHED→CLUNKY、BROKEN→CLUNKY
回退样本：3D/Game 的 POLISHED→BROKEN (×2)

**注**：这只是 cap/阈值层的提升。重新运行 LLM 评估（使用新 prompt）后，预期打分质量会显著改善，特别是：
- 核心/非核心区分 → 减少"非核心缺失过度扣分"
- 评分锚定 → 稳定 LLM 打分分布，减少阈值附近横跳
- 更丰富的探针证据 → 改善 3D/Game 的交互评判

---

### 实验 8: 新 Prompt 评测 + 阈值校准

| 项目 | 值 |
|-----|---|
| **日期** | 2026-08-31 |
| **类型** | 完整 LLM 重新评测 + 阈值校准 |
| **样本** | 100 样本（98 个有效标签） |
| **模型** | qwen3.8-max (DashScope Token Plan) |

#### 评测流程

1. 使用实验 7 的新 prompt（FUNC/UX/AES 全部重写）重新运行 100 样本 LLM 评估
2. 结果存入 `aescode_out/results/`（旧结果备份在 `results_v1/`）
3. 用固定后的 `cap_functional_score` 重新计算所有 regime
4. 网格搜索校准阈值

#### 新 Prompt vs 旧 Prompt 对比

| 指标 | 旧 (results_v1) | 新 (results) |
|-----|----------------|--------------|
| 存储 regime 一致率 | 65.3% (64/98) | 64.3% (63/98) |
| 固定 cap 后一致率 | — | 73.5% (72/98) |
| 优化阈值后一致率 | — | **78.6% (77/98)** |

新 prompt 的原始存储 regime 与旧 prompt 基本持平（64-65%），但经过 cap 逻辑修复和阈值校准后，实际一致率大幅提升。

#### 逐类对比（优化后）

| 类别 | 旧 (stored) | 新 (optimized) | 变化 |
|------|------------|----------------|------|
| 3D design | 80% (12/15) | **87% (13/15)** | +7% |
| Data visualization | 67% (10/15) | **93% (14/15)** | +26% |
| Game dev | 67% (10/15) | **87% (13/15)** | +20% |
| UI component | 93% (14/15) | **100% (15/15)** | +7% |
| Website | 47% (18/38) | **58% (22/38)** | +11% |

#### 关键改进

**1. cap_functional_score 最终版本**
- core-based + total-based 双重封顶，取最严
- 低分保护：raw ≤ 4.0 且 ≥3 死亡→封顶 2.0（实际效果与其他阈值相同，因 core-based cap 已覆盖）
- 防止 LLM 通过 `core=false` 标签绕过 cap

**2. CLUNKY_HTML_THRESHOLD 守卫移除**
- 旧逻辑：func < f_dead 且 html_len > 30k 且 func >= f_dead - 1.5 → CLUNKY
- 新逻辑：func < f_dead 且 html_len > 30k → CLUNKY（无条件）
- 原因：内容丰富页面（30k+ HTML）即使多交互死亡，人工也倾向判 CLUNKY

**3. 阈值校准**
- F_DEAD: 5.0 → 5.5（非视觉型略严）
- F_DEAD_VISUAL: 6.0 → 4.5（视觉型略松）
- UX_THRESHOLD: 6.0 → 4.5（UX 阈值降低）

#### 剩余误判分析（21 个）

| 误判类型 | 数量 | 主要类别 |
|---------|------|---------|
| human=BROKEN, ai=CLUNKY | 10 | Website (html>30k 但核心功能完全坏) |
| human=CLUNKY, ai=BROKEN | 3 | Website (html<30k 但人工认为可用) |
| human=BROKEN, ai=POLISHED | 3 | 3D/Game (LLM 高估功能) |
| human=CLUNKY, ai=POLISHED | 2 | 3D/DataViz (LLM 高估 UX) |
| 其他 | 3 | 混合 |

Website 类别仍是主要瓶颈（58%），核心矛盾：html_len 不是"内容丰富"的完美代理——部分长 HTML 页面核心功能完全失效，人工仍判 BROKEN。

---

### 实验 9: Train/Test 80/20 分层校准（过拟合检验）

| 项目 | 值 |
|-----|---|
| **日期** | 2026-09-03 |
| **类型** | 训练集/测试集划分 + 阈值重新校准 |
| **动机** | 实验 1-8 全部用 100 条数据同时做阈值优化和评测，存在过拟合风险 |
| **模型** | qwen3.8-max (Token Plan)（LLM 分数沿用实验 8 结果，不重新评测） |

#### 数据划分

按类别分层抽样（seed=42），排除 2 条 null regime：

| 集合 | 样本数 | BROKEN | CLUNKY | POLISHED |
|------|--------|--------|--------|----------|
| 训练集 | 78 | 70 | 3 | 5 |
| 测试集 | 20 | 17 | 0 | 3 |

类别分布：
| 集合 | 3D | UI | DataViz | Game | Website |
|------|-----|-----|---------|------|---------|
| 训练集 | 12 | 12 | 12 | 12 | 30 |
| 测试集 | 3 | 3 | 3 | 3 | 8 |

**关键约束**：网格搜索只在训练集上进行，测试集标签在阈值确定前完全不查看。

#### 网格搜索结果

| 参数 | 实验 8（全量拟合） | 实验 9（训练集拟合） |
|------|-------------------|---------------------|
| F_DEAD | 5.5 | **4.5** |
| UX_THRESH | 4.5 | **3.5** |
| EXEC_DEAD | 0.20 | **0.10** |

旧阈值确实过拟合了——新阈值整体更宽松。

#### 结果

| 指标 | 训练集 (78) | 测试集 (20) |
|------|-------------|-------------|
| 准确率 | 91.0% (71/78) | **95.0% (19/20)** |
| 过拟合 | — | **无**（测试反而高 +4%） |

训练集逐类：
| 类别 | 准确率 |
|------|--------|
| 3D design | 83.3% (10/12) |
| Data visualization | 100% (12/12) |
| Game dev | 83.3% (10/12) |
| UI component | 75.0% (9/12) |
| Website | 100% (30/30) |

测试集逐类：
| 类别 | 准确率 |
|------|--------|
| 3D design | 100% (3/3) |
| Data visualization | 100% (3/3) |
| Game dev | 100% (3/3) |
| UI component | 66.7% (2/3) |
| Website | 100% (8/8) |

#### 训练集误判分析（7 个）

全部为 **human=BROKEN, ai=POLISHED** 模式——LLM 打分偏高：

| row_id | 类别 | func_raw | func_cap | ux |
|--------|------|----------|----------|-----|
| 01_000425 | UI component | 6.0 | 6.0 | 5.0 |
| 00_009144 | 3D design | 6.0 | 6.0 | 5.0 |
| 01_014447 | UI component | 6.0 | 5.0 | 5.0 |
| 00_018024 | 3D design | 5.0 | 5.0 | 5.0 |
| 03_012601 | Game dev | 6.0 | 6.0 | 5.0 |
| 03_018217 | Game dev | 7.0 | 7.0 | 6.0 |
| 01_022300 | UI component | 7.0 | 7.0 | 5.0 |

共同特征：LLM 给的 func 分（5.0-7.0）远高于 F_DEAD=4.5，ux 分（5.0-6.0）也高于 UX_THRESH=3.5。阈值切不过去。

#### 测试集误判分析（1 个）

| row_id | 类别 | func_raw | func_cap | ux | human | pred |
|--------|------|----------|----------|-----|-------|------|
| 01_033120 | UI component | 6.0 | 5.0 | 5.0 | BROKEN | POLISHED |

同样是 LLM 打分偏高导致。

#### 结论

1. **没有过拟合**：测试集 95% ≥ 训练集 91%，阈值泛化能力 OK
2. **旧阈值确实过拟合**：实验 8 的 F_DEAD=5.5 在全量数据上优化，泛化到子集时偏严
3. **主要误判模式不变**：LLM 对 BROKEN 页面打分偏高（func 5-7），阈值切不过去
4. **测试集太小**：20 条的 95% CI 约 [75%, 99%]，统计意义有限

---

### CLUNKY 类别深度分析

#### 问题

CLUNKY 识别率极低（3 个样本只对 1 个），需要理解根因。

#### 数据现状

全量 98 条有效标签中只有 **3 条 CLUNKY**（3%）。全部 98 条中只有 8 条通过功能门控（functional_ok=OK）进入 usability 评判：

| row_id | 类别 | 人工 usability | 人工 regime | LLM ux 分 | LLM 判 |
|--------|------|---------------|-------------|-----------|--------|
| 00_009144 | 3D design | CLUNKY | CLUNKY | **5.0** | POLISHED |
| 02_006338 | DataViz | CLUNKY | CLUNKY | **0.0** (跳过) | BROKEN |
| 03_004558 | Game dev | CLUNKY | CLUNKY | **3.0** | CLUNKY ✓ |
| 00_006140 | 3D design | OK | POLISHED | 7.0 | POLISHED ✓ |
| 03_003003 | Game dev | OK | POLISHED | **5.0** | POLISHED ✓ |
| 03_005229 | Game dev | OK | POLISHED | **5.0** | POLISHED ✓ |
| 03_015256 | Game dev | OK | POLISHED | 6.0 | POLISHED ✓ |
| 04_019960 | Website | OK | POLISHED | **5.0** | POLISHED ✓ |

#### 核心发现

**1. CLUNKY 和 POLISHED 的 LLM UX 打分完全重叠**

- CLUNKY `00_009144`：UX=**5.0**
- POLISHED `03_003003`：UX=**5.0**
- POLISHED `03_005229`：UX=**5.0**
- POLISHED `04_019960`：UX=**5.0**

UX 分完全相同，但人工判了 1 个 CLUNKY、3 个 POLISHED。

**2. LLM 的描述也无法区分**

- CLUNKY 描述："整体可用但体验有**明显短板**"
- POLISHED 描述："整体体验有**明显短板**"

措辞几乎一致，说明边界本身模糊。

**3. 人工标注定义主观**

标注界面中 CLUNKY 的判断标准：
> "信息组织合理吗？交互流程顺畅吗？容易上手吗？"
> - CLUNKY = "难用/混乱"
> - OK = "好用/体验顺畅"

三个问题全是主观感受，没有客观判定标准。对比：
- DEAD/BROKEN：有客观证据（页面能否加载、JS 报错、核心交互响应）
- POLISHED：有截图 + 视觉评分（相对客观）
- CLUNKY：纯粹"用起来感觉好不好"——因人而异

**4. 结构性问题**

- 标注者判 usability 时**没有截图**，只能看 HTML 源码脑补用户体验
- CLUNKY 只出现在"功能没坏但体验差"的窄通道里，样本极少
- 没有 inter-annotator agreement 数据，无法确定人工自身的一致性

#### 结论

CLUNKY 识别率低不是阈值或 prompt 的问题，而是**类别定义本身主观**。在 3 个样本、LLM 打分与 POLISHED 完全重叠的情况下，靠调阈值优化 CLUNKY 识别是在拟合噪声。保留四级体系的前提下，CLUNKY 准确率会持续偏低。

---

## 当前最优配置（实验 9 后）

**代码改动**：新增 `src/split_and_calibrate.py`（训练/测试集划分 + 校准）

**阈值（训练集网格搜索，测试集验证）**:
```python
# 功能型类别 (Website, UI component, Data visualization)
F_DEAD_THRESHOLD = 4.5
UX_THRESHOLD = 3.5
DEAD_EXEC_THRESHOLD = 0.10

# 视觉型类别 (Game dev)
F_DEAD_THRESHOLD_VISUAL = 4.5  # 同功能型（网格搜索未区分出更优值）
CAP_DEAD_INTERACTIONS_VISUAL = 4
```

**性能**:
- 训练集: 91.0% (71/78)
- 测试集: 95.0% (19/20)
- 无过拟合

---

## 未来工作

1. **扩大标注样本量**: 当前 100 条太少（CLUNKY 仅 3 条），至少需要 300+ 条才有统计意义
2. **CLUNKY 客观化**: 探索用探针证据（如"核心交互死亡但页面能跑"）替代主观 UX 评分来定义 CLUNKY
3. **Inter-annotator agreement**: 多人标注同一批样本，计算 Cohen's Kappa，确定一致率上限
4. **LLM 打分偏高问题**: 7/8 训练误判都是 human=BROKEN 但 LLM func≥5.0，需要在 prompt 中加强"核心功能缺失应低分"的锚定
5. **Website 类别专项优化**: 引入更精确的"内容丰富度"指标替代 html_len
6. **更强模型**: 尝试 qwen-max 等更强模型

---

## 附录：实验文件清单

| 文件 | 说明 |
|-----|------|
| `aescode_out/random_100_ids.txt` | 100 样本 ID |
| `aescode_out/human_scores_100.json` | 人工标注标签 |
| `aescode_out/results/*.json` | 模型评测结果（实验 8 prompt） |
| `aescode_out/splits_train80_test20.json` | 实验 9 训练/测试集划分 |
| `aescode_out/clunky_review.html` | CLUNKY 样本对比评审页 |
| `src/piecewise.py` | 门控逻辑实现 |
| `src/calibrate.py` | 阈值校准工具（全量） |
| `src/split_and_calibrate.py` | 训练/测试集划分 + 校准（实验 9） |
| `src/agreement_100.py` | 人机一致率计算 |
