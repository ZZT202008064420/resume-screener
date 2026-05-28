# modules/extractor.py
import re
import json
import os
from openai import OpenAI



EXTRACT_PROMPT = """你是一个专业的简历解析引擎。请从以下简历文本中提取结构化信息，严格返回JSON，不要有任何解释或Markdown格式。

【提取规则】
- 手机号：中国大陆11位、带区号座机均可
- 邮箱：提取完整邮箱地址
- 工作年限：计算总年数，如"2020.3-2023.6"算3年，无法计算则填null
- 学历：统一为"博士/硕士/本科/大专/高中"之一
- 技能：提取编程语言、框架、工具、软件等技术关键词
- 项目经历：每项含 title/duration/tech_stack/description
- 工作经历：每项含 company/title/duration/description

【返回格式】
{{
  "basic_info": {{
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "address": "北京市朝阳区"
  }},
  "job_intention": {{
    "position": "后端开发工程师",
    "expected_salary": "20-30K"
  }},
  "background": {{
    "work_years": 3,
    "education": "本科",
    "school": "北京大学",
    "major": "计算机科学与技术",
    "skills": ["Python", "Redis", "MySQL", "Docker"],
    "work_experience": [
      {{
        "company": "某科技公司",
        "title": "后端工程师",
        "duration": "2021.07 - 2024.01",
        "description": "负责用户系统开发..."
      }}
    ],
    "projects": [
      {{
        "title": "电商推荐系统",
        "duration": "2023.01 - 2023.06",
        "tech_stack": ["Python", "Redis", "Kafka"],
        "description": "基于协同过滤算法..."
      }}
    ]
  }}
}}

简历文本如下：
---
{resume_text}
---

只返回JSON对象，不要任何其他内容。"""


class InfoExtractor:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def extract(self, cleaned_text: str) -> dict:
        truncated = cleaned_text[:6000]
        print("[DEBUG] 简历文本前500字:", truncated[:500])  # 加这行
        try:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[{
                    "role": "user",
                    "content": EXTRACT_PROMPT.format(resume_text=truncated)
                }],
                max_tokens=2000,
            )
            raw = response.choices[0].message.content.strip()
            return self._safe_parse(raw)

        except Exception as e:
            print(f"[Extractor] 异常: {e}")
            return self._empty_structure()

    def _safe_parse(self, raw: str) -> dict:
        """清洗AI返回内容并解析JSON"""
        # 去掉 ```json ... ``` 包裹
        print("[DEBUG] AI原始返回:", raw[:300])
        raw = re.sub(r'^```[a-z]*\s*', '', raw, flags=re.MULTILINE)
        raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)
        raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # 尝试提取第一个完整的 {...}
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            print(f"[Extractor] JSON parse failed, raw: {raw[:200]}")
            return self._empty_structure()

    def _empty_structure(self) -> dict:
        return {
            "basic_info": {"name": None, "phone": None, "email": None, "address": None},
            "job_intention": {"position": None, "expected_salary": None},
            "background": {
                "work_years": None, "education": None,
                "school": None, "major": None,
                "skills": [], "work_experience": [], "projects": []
            }
        }