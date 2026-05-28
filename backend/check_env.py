# check_env.py  ← 跑一遍确认所有依赖OK
import os
import sys

def check():
    errors = []

    # 1. API Key
    if not os.environ.get("DASHSCOPE_API_KEY"):
        errors.append("❌ DASHSCOPE_API_KEY 未设置")
    else:
        print("✅ DASHSCOPE_API_KEY 已设置")

    # 2. pdfplumber
    try:
        import pdfplumber
        print("✅ pdfplumber 可用")
    except ImportError:
        errors.append("❌ pdfplumber 未安装")

    # 3. jieba
    try:
        import jieba.analyse
        jieba.analyse.extract_tags("Python Redis MySQL开发工程师", topK=3)
        print("✅ jieba 可用")
    except Exception as e:
        errors.append(f"❌ jieba 异常: {e}")

    # 4. Redis
    try:
        import redis
        r = redis.Redis(
            host=os.environ.get("REDIS_HOST", "127.0.0.1"),
            port=int(os.environ.get("REDIS_PORT", 6379)),
            socket_connect_timeout=2
        )
        r.ping()
        print("✅ Redis 连接成功")
    except Exception as e:
        print(f"⚠️  Redis 不可用（将跳过缓存）: {e}")

    # 5. Anthropic SDK
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        print("✅ OpenAI SDK 初始化成功")
    except ImportError:
        errors.append("❌ openai 未安装，运行: pip install openai")
    except Exception as e:
        errors.append(f"❌ OpenAI SDK 异常: {e}")
    if errors:
        print("\n以下问题需要修复：")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("\n✅ 环境检查全部通过，可以启动！")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    check()