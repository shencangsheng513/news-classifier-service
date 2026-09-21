# news-classifier-service — 已上线的文本分类推理服务

20newsgroups 文本分类模型（TF-IDF + LogisticRegression，测试集 87.0% / CV 88.1%）的生产级推理服务，来自 [ml-tutorial](https://github.com/shencangsheng513/ml-tutorial) 作品集的 ml-deploy 项目。本仓库是可直接被 Render/Docker 部署的自包含镜像配方：模型烤进镜像（`model/text_clf.joblib`），零卷挂载，`scikit-learn` 锁 `==1.9.1`（与训练工件同源，加载零告警）。

**Live demo：https://news-classifier-service-jsfq.onrender.com**（Render 免费档，空闲 15 分钟休眠，冷启动约 1 分钟）

## API

| 端点 | 方法 | 鉴权 |
|---|---|---|
| `/v1/classify` | POST | Bearer（`Authorization: Bearer <DEPLOY_API_TOKEN>`） |
| `/healthz` `/ready` | GET | 免钥匙（平台探活白名单） |
| `/docs` | GET | 免钥匙（Swagger 交互文档） |

```bash
curl https://news-classifier-service-jsfq.onrender.com/v1/classify \
  -H "Authorization: Bearer $API_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"texts":["The goalie made a glove save in overtime"]}'
```

返回四类（graphics/baseball/hockey/space）概率与置信度；短文本走护栏直接 `rejected`。

**`confidence` 口径（对接前必读）**：本服务返回的 `confidence` 是 **Top1 概率**。训练侧报告（`ml-tutorial/ml-text/models/report.json`）里的 `confidence_threshold: 0.207` 定义在 **Top1−Top2 差值**上，两者不是同一个量——四分类下 Top1 概率恒 ≥0.25，拿 0.207 去比本服务的 `confidence`，"低置信转人工"永远不会触发。要复刻拒答逻辑，请用响应里完整的 `probabilities` 自己算前两名差值。

## 上线实测记录（2026-09-20）

- 部署：Render Web Service / Docker runtime / 免费 cpu-basic，首次构建 2m01s
- 冒烟三查全绿：`/healthz` 无钥匙 200（`model_loaded: true`）→ `/v1/classify` 无钥匙 401 → 带钥匙 200 + 三条真实预测（latency ~183ms）
- 踩坑实录：Render 健康检查默认探 `HEAD /`，被 Bearer 中间件打成 401 → 平台误判服务不健康触发重启。修法：Settings → Health Check Path 设 `/healthz`。这正是鉴权中间件必须配免钥匙白名单（`OPEN_PATHS`）的实战理由
- **sklearn `InconsistentVersionWarning` 已本机修完，待重建生效**：根因是训练工件由 1.9.0 pickle、镜像按 `scikit-learn>=1.5` 装到了 1.9.1（先前记录误写成"模型存于 1.7.x"）。修法：`pyproject.toml` 锁 `==1.9.1` + 用 1.9.1 重跑训练生成 `model/text_clf.joblib`。本机验证：新旧工件对全部 1579 篇测试集 **0 条预测不一致、概率最大绝对差 0.0**，加载零告警，回环冒烟（healthz 200 / 无钥匙 401 / 带钥匙 200，单请求 23.6ms）全绿。**线上只剩一步：push 触发 Render 重建镜像**
- 原计划 HuggingFace Spaces，因 2026 起 Docker Space 免费档收费墙（402/PRO）改道 Render
