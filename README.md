# wol-web

一个极简的基于 Flask 的 Wake-on-LAN Web 控制台，提供按钮一键发送魔术包，支持在 GitHub Actions 中构建并推送 arm64 Docker 镜像到 GHCR。

## 功能
- Web 界面（内联模板），输入/修改 MAC 与广播地址，一键唤醒
- API: `POST /api/wake`，请求体 `{ mac, broadcast? }`
- 极简依赖，使用多阶段构建生成 arm64 alpine 运行镜像
- GitHub Actions 工作流自动构建并推送镜像到 GHCR

## 本地运行

开发启动（非 Docker）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\wsgi.py
```

访问 http://127.0.0.1:8000

## Docker 构建与运行（arm64）

构建：

```powershell
docker build -t wol-web:local --platform linux/arm64 .
```

运行（推荐 host 网络，广播更直接）：

```powershell
docker run -d --name wol-web --network host --restart unless-stopped `
	-e DEFAULT_MAC=24:4B:FE:02:33:B9 `
	-e DEFAULT_BROADCAST=192.168.31.255 `
	wol-web:local
```

若使用 bridge 网络：

```powershell
docker run -d --name wol-web -p 8000:8000 --restart unless-stopped `
	-e DEFAULT_MAC=24:4B:FE:02:33:B9 `
	-e DEFAULT_BROADCAST=192.168.31.255 `
	wol-web:local
```

注意：容器需允许向局域网广播，默认使用 UDP 发送魔术包。如需自定义广播地址，请在页面中修改为你的网段广播地址（例如 `192.168.31.255`）。

## GHCR 推送

1. 将仓库可见性设为 `public`（或在私有仓库使用 GHCR 也可）。
2. 确保默认分支为 `main` 或 `master`，推送后将自动构建并推送 `latest` 标签到 `ghcr.io/<owner>/<repo>`。
3. 如推送 tag `v1.0.0`，则生成 `v1.0.0` 与 `arm64-v1.0.0` 标签。

拉取并运行：

```powershell
docker pull ghcr.io/<owner>/<repo>:latest
docker run -d --name wol-web --network host --restart unless-stopped `
	-e DEFAULT_MAC=24:4B:FE:02:33:B9 `
	-e DEFAULT_BROADCAST=192.168.31.255 `
	ghcr.io/<owner>/<repo>:latest
```

## 常见问题

- Windows 目标机器需在 BIOS 与网卡属性里启用 WOL，并允许通过 Magic Packet 唤醒。
- 建议确认子网广播地址，比如 192.168.31.255；若交换机做了广播限制，需放开。
- 容器或主机防火墙需允许 UDP 广播（端口通常 7/9）。

## 许可

MIT
