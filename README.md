# 合并代理

我有两份代理文件，一份买了月卡，一份买了年卡。前者便宜，每天都用；后者比较贵，只有在访问香港也不可以访问的网站时候才用。

我将一些规则进行整理合并，本质上是对yaml文件的处理。

我将其使用 docker-compose 进行部署，方便使用过 clash 更新

实际合并的时候不算优雅...应该是有包给我掉的啊...

# 启动命令
```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

# docker部署
```
docker build -t proxy_merge .
docker network create --driver=bridge --subnet=172.23.1.0/24 proxy_merge
docker compose up -d
```

# Kubernetes部署
使用K8s进行部署，fleet进行持续集成
