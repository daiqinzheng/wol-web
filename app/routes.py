from flask import Blueprint, jsonify, render_template_string, request
import os
import socket

bp = Blueprint('main', __name__)

# Inline minimal template to avoid separate template files
INDEX_HTML = """
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Wake on LAN 控制台</title>
    <style>
      :root { color-scheme: light dark; }
      body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, 'Apple Color Emoji', 'Segoe UI Emoji'; margin: 0; padding: 2rem; }
      .card { max-width: 520px; margin: 10vh auto; padding: 1.5rem; border-radius: 12px; border: 1px solid #8883; backdrop-filter: blur(10px); }
      h1 { margin-top: 0; }
      button { font-size: 1.1rem; padding: 0.8rem 1.2rem; border-radius: 10px; border: 1px solid #4443; cursor: pointer; }
      button:disabled { opacity: 0.6; cursor: not-allowed; }
      .row { display: flex; gap: .75rem; align-items: center; }
      .status { margin-top: 1rem; min-height: 1.4rem; }
      input { padding: .6rem .7rem; border-radius: 8px; border: 1px solid #4443; font-size: 1rem; width: 100%; }
      label { font-size: .9rem; color: #666; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Wake on LAN 控制台</h1>
      <p>点击下方按钮向目标电脑发送魔术包（Magic Packet）。</p>
      <div class="row">
        <div style="flex:1">
          <label for="mac">MAC 地址</label>
          <input id="mac" value="{{ default_mac }}" placeholder="例如: 24:4B:FE:02:33:B9" />
        </div>
      </div>
      <div class="row" style="margin-top: .75rem;">
        <div style="flex:1">
          <label for="bcast">广播地址</label>
          <input id="bcast" value="{{ default_broadcast }}" placeholder="例如: 192.168.31.255" />
        </div>
        <div>
          <label>&nbsp;</label>
          <button id="wake">唤醒</button>
        </div>
      </div>
      <div class="status" id="status"></div>
    </div>

    <script>
      const btn = document.getElementById('wake');
      const statusDiv = document.getElementById('status');
      btn.addEventListener('click', async () => {
        btn.disabled = true;
        statusDiv.textContent = '正在发送魔术包…';
        try {
          const resp = await fetch('/api/wake', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mac: document.getElementById('mac').value.trim(), broadcast: document.getElementById('bcast').value.trim() })
          });
          const data = await resp.json();
          statusDiv.textContent = data.message || JSON.stringify(data);
        } catch (e) {
          statusDiv.textContent = '请求失败: ' + e;
        } finally {
          btn.disabled = false;
        }
      });
    </script>
  </body>
</html>
"""


def _clean_mac(mac: str) -> bytes:
    mac = mac.replace("-", "").replace(":", "").replace(".", "").strip().lower()
    if len(mac) != 12 or any(c not in '0123456789abcdef' for c in mac):
        raise ValueError("无效的 MAC 地址格式")
    return bytes.fromhex(mac)


def send_magic_packet(mac: str, broadcast: str = "255.255.255.255", port: int = 9) -> None:
    hw = _clean_mac(mac)
    payload = b"\xff" * 6 + hw * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(payload, (broadcast, port))


@bp.get("/")
def index():
  return render_template_string(
    INDEX_HTML,
    default_mac=os.getenv("DEFAULT_MAC", "24:4B:FE:02:33:B9"),
    default_broadcast=os.getenv("DEFAULT_BROADCAST", "192.168.31.255"),
  )


@bp.post("/api/wake")
def api_wake():
    data = request.get_json(silent=True) or {}
    mac = data.get("mac")
    broadcast = data.get("broadcast") or "255.255.255.255"
    if not mac:
        return jsonify({"ok": False, "message": "缺少 mac"}), 400
    try:
        send_magic_packet(mac, broadcast)
        return jsonify({"ok": True, "message": f"已发送魔术包到 {mac}（广播 {broadcast}）"})
    except Exception as e:
        return jsonify({"ok": False, "message": f"失败: {e}"}), 400
