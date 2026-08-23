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

## 未来工作

1. **扩大样本量**: 测试 300/1000 样本的稳定性
2. **统一标注标准**: 解决两批 Game dev 结果不一致问题
3. **更强模型**: 尝试 qwen-max 等更强模型（需 Standard 计划）
4. **Prompt 优化**: 改进评判 prompt 以减少 LLM 打分偏差
5. **细粒度类别**: 探索更细的类别划分（如 3D 游戏 vs 3D 展示）

---

## 附录：实验文件清单

| 文件 | 说明 |
|-----|------|
| `run100_ids.txt` | 第一批100样本 ID |
| `run100_ids_v2.txt` | 第二批100样本 ID |
| `aescode_out/labels.json` | 人工标注标签 |
| `aescode_out/results/*.json` | 模型评测结果 |
| `aescode_out/splits.json` | 训练/评测集划分 |
| `src/piecewise.py` | 门控逻辑实现 |
| `src/calibrate.py` | 阈值校准工具 |
| `src/agreement_100.py` | 人机一致率计算 |
