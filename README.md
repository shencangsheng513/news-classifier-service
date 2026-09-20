---
title: News Text Classifier
emoji: 📰
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

20newsgroups 文本分类模型（TF-IDF + LogisticRegression，测试集 87.7%）的生产级推理服务，来自 ml-tutorial 作品集的 ml-deploy 项目。

- 接口：`POST /v1/classify`，body `{"texts": ["...", "..."]}`（1–64 条），返回四类概率与置信度；短文本走护栏直接 `rejected`
- 探针：`GET /healthz`、`GET /ready`；交互文档：`/docs`
- 压测底数：本地单 worker ~565 条/秒零错误（免费 CPU 档预期 1/3–1/5）

私有 Space 期间，所有请求要带你的 HF token（Settings → Access Tokens 里那个）：

```bash
curl https://cangsheng345-news-classifier.hf.space/v1/classify \
  -H "Authorization: Bearer $HF_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"texts":["The goalie made a glove save in overtime"]}'
```
