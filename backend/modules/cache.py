# modules/cache.py
import json
import os
import redis


class CacheManager:

    TTL_PARSED = 60 * 60 * 24      # 解析结果缓存24小时
    TTL_SCORED = 60 * 60 * 6       # 评分缓存6小时

    def __init__(self):
        self._client = None
        self._init_redis()

    def _init_redis(self):
        try:
            self._client = redis.Redis(
                host=os.environ.get("REDIS_HOST", "127.0.0.1"),
                port=int(os.environ.get("REDIS_PORT", 6379)),
                password=os.environ.get("REDIS_PASSWORD") or None,
                db=0,
                socket_connect_timeout=2,   # 连接超时2秒，不卡主流程
                decode_responses=True
            )
            self._client.ping()  # 验证连接
            print("[Cache] Redis connected")
        except Exception as e:
            print(f"[Cache] Redis unavailable, running without cache: {e}")
            self._client = None  # 降级：无缓存模式

    # ── 解析缓存 ──────────────────────────────────────────────

    def get_parsed(self, file_hash: str):
        return self._get(f"resume:parsed:{file_hash}")

    def set_parsed(self, file_hash: str, data: dict):
        self._set(f"resume:parsed:{file_hash}", data, self.TTL_PARSED)

    # ── 评分缓存 ──────────────────────────────────────────────

    def get_scored(self, file_hash: str, jd_hash: str):
        return self._get(f"resume:scored:{file_hash}:{jd_hash}")

    def set_scored(self, file_hash: str, jd_hash: str, data: dict):
        self._set(f"resume:scored:{file_hash}:{jd_hash}", data, self.TTL_SCORED)

    # ── 底层操作 ──────────────────────────────────────────────

    def _get(self, key: str):
        if not self._client:
            return None
        try:
            raw = self._client.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            print(f"[Cache] GET error {key}: {e}")
            return None

    def _set(self, key: str, data: dict, ttl: int):
        if not self._client:
            return
        try:
            self._client.setex(key, ttl, json.dumps(data, ensure_ascii=False))
        except Exception as e:
            print(f"[Cache] SET error {key}: {e}")