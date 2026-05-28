import re
import json
import os
from openai import OpenAI
import jieba.analyse


SCORE_PROMPT = """你是一位有10年经验的资深HR总监，请对以下候选人与岗位的匹配度进行专业打分。

【岗位需求】
{job_description}

【候选人信息】
{candidate_info}

【评分维度说明】
- skill_match（技能匹配）满分40分：技术栈、工具、语言与岗位要求的吻合程度
- experience_match（经验匹配）满分30分：工作年限、项目经历与岗位的相关性
- education_match（学历匹配）满分15分：学历层次与岗位要求
- overall_fit（综合评估）满分15分：候选人的成长性、稳定性、综合潜力

请严格返回如下JSON，不要有任何解释：
{{
  "skill_match": 32,
  "experience_match": 25,
  "education_match": 12,
  "overall_fit": 11,
  "total_score": 80,
  "matched_keywords": ["Python", "Redis", "微服务"],
  "missing_keywords": ["Kubernetes", "Go语言"],
  "recommendation": "候选人Python基础扎实，有微服务经验，建议进入技术面试进一步评估。",
  "hire_advice": "推荐"
}}

hire_advice 只能是"强烈推荐"(90+)/"推荐"(70-89)/"待定"(50-69)/"不推荐"(50以下)之一。
只返回JSON。"""


class ResumeScorer:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def score(self, extracted_info: dict, job_description: str) -> dict:
        keyword_result = self._keyword_match(extracted_info, job_description)
        ai_result = self._ai_score(extracted_info, job_description)
        return {
            "ai_score": ai_result,
            "keyword_analysis": keyword_result,
            "total_score": ai_result.get("total_score", 0),
            "hire_advice": ai_result.get("hire_advice", "待定"),
            "recommendation": ai_result.get("recommendation", ""),
        }

    def _keyword_match(self, info: dict, jd: str) -> dict:
        jd_keywords = set(jieba.analyse.extract_tags(jd, topK=20))
        bg = info.get("background", {})
        skills_text = " ".join(bg.get("skills", []))
        proj_text = " ".join([p.get("description", "") for p in bg.get("projects", [])])
        work_text = " ".join([w.get("description", "") for w in bg.get("work_experience", [])])
        resume_combined = f"{skills_text} {proj_text} {work_text}"
        resume_keywords = set(jieba.analyse.extract_tags(resume_combined, topK=30))
        matched = jd_keywords & resume_keywords
        missing = jd_keywords - resume_keywords
        return {
            "jd_keywords": list(jd_keywords),
            "resume_keywords": list(resume_keywords),
            "matched": list(matched),
            "missing": list(missing),
            "match_rate": round(len(matched) / max(len(jd_keywords), 1) * 100, 1)
        }

    def _ai_score(self, info: dict, jd: str) -> dict:
        candidate_str = json.dumps(info, ensure_ascii=False)
        try:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[{
                    "role": "user",
                    "content": SCORE_PROMPT.format(
                        job_description=jd[:2000],
                        candidate_info=candidate_str[:3000]
                    )
                }],
                max_tokens=1000,
            )
            raw = response.choices[0].message.content.strip()
            raw = re.sub(r'^```[a-z]*\s*|\s*```$', '', raw, flags=re.MULTILINE).strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[Scorer] AI score failed: {e}")
            kw = self._keyword_match(info, jd)
            estimated = int(kw["match_rate"] * 0.8)
            return {
                "skill_match": estimated,
                "experience_match": 0,
                "education_match": 0,
                "overall_fit": 0,
                "total_score": estimated,
                "matched_keywords": kw["matched"],
                "missing_keywords": kw["missing"],
                "recommendation": "AI评分服务暂时不可用，已使用关键词匹配估算。",
                "hire_advice": "待定"
            }