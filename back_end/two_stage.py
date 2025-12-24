# back_end/two_stage.py
from llm import call_llm
from handler import query_handler


def two_stage_qa(question: str):
    # === 第一阶段：LLM 生成 ===
    llm_ans = call_llm(question)
    print(f"【第一阶段】已接入千问3 1.7B，大模型的回答是：{llm_ans}")  # ← 新增这行！

    # === 第二阶段：尝试用 KG 验证 ===
    kg_res = query_handler(question)

    if kg_res["state"] == 0 and kg_res["data"]:
        kg_set = set(kg_res["data"])
        if llm_ans in kg_set:
            return {
                "final_answer": llm_ans,
                "source": "verified_by_kg",
                "llm_answer": llm_ans,
                "kg_answers": kg_res["data"],
                "is_hallucination": False
            }
        else:
            correct = kg_res["data"][0]
            print(f"【修正】LLM 回答，已用图谱答案 '{correct}' 修正")  # 可选
            return {
                "final_answer": correct,
                "source": "corrected_by_kg",
                "llm_answer": llm_ans,
                "kg_answers": kg_res["data"],
                "is_hallucination": True
            }
    else:
        return {
            "final_answer": llm_ans,
            "source": "unverified_llm",
            "llm_answer": llm_ans,
            "kg_answers": [],
            "is_hallucination": None
        }