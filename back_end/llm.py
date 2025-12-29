# back_end/llm.py
import requests
import json
import re
import subprocess
import sys
def call_llm(question: str) -> str:
    q = question.strip()
    if not q.endswith(('?', '？', '.', '。', '!', '！')):
        q += '？'

    full_prompt = f"问题：{q}\n回答："

    try:
        result = subprocess.run(
            ["ollama", "run", "qwen3:1.7b", full_prompt],
            capture_output=True,
            text=True,
            timeout=90,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        output = result.stdout.strip()

        # === 关键修复：不再取第一行，而是取最后一行非空行 ===
        lines = [line.strip() for line in output.split('\n') if line.strip()]

        # 移除 Ollama 的 Thinking... 和 done thinking 行
        cleaned_lines = []
        for line in lines:
            if line.startswith("Thinking...") or "...done thinking" in line:
                continue
            cleaned_lines.append(line)

        # 取最后一行作为答案
        if cleaned_lines:
            answer_line = cleaned_lines[-1]
        else:
            return "未知"

        # 清理可能的 markdown（如 **周杰伦**）
        answer_line = re.sub(r'\*+', '', answer_line)
        # 去掉句号、多余文字，只保留核心
        answer_line = answer_line.split('。')[0].split('！')[0].split('？')[0].strip()

        # 如果答案太长（像解释），或者包含“不知道”等词，视为无效
        if len(answer_line) > 30 or any(w in answer_line for w in ["不知道", "不确定", "可能", "需要确认"]):
            return "未知"

        return answer_line if answer_line else "未知"

    except Exception as e:
        print(f"【LLM ERROR】{e}")
        return "未知"