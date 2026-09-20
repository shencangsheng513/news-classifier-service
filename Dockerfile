FROM python:3.12-slim

WORKDIR /srv/app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY model/text_clf.joblib /models/text_clf.joblib

ENV DEPLOY_MODEL_PATH=/models/text_clf.joblib \
    DEPLOY_PORT=7860 \
    DEPLOY_WORKERS=1

EXPOSE 7860
CMD ["deploy-serve"]
