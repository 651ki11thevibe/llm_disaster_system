# app/core/llm_service.py
import os
import re
import requests
from app.models.disaster_info import DisasterInfo
from dotenv import load_dotenv

load_dotenv()
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_MODEL = os.getenv("LLM_MODEL_NAME")
TIMEOUT_SECS = 60

# 正则用于解析四元组
_QUADRUPLE_RE = re.compile(
    r"时间[:：](?P<time>[^\n]+?)\s*"
    r"地点[:：](?P<loc>[^\n]+?)\s*"
    r"事件[:：](?P<evt>[^\n]+?)\s*"
    r"受灾程度[:：](?P<level>[^\n]+?)\s*(?:$|\n)",
    re.S,
)


def _call_chat_llm(messages: list, max_tokens: int = 512, temperature: float = 0.7) -> str:
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = requests.post(LLM_API_URL, json=payload, timeout=TIMEOUT_SECS)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


def _parse_quadruples(raw: str) -> list[DisasterInfo]:
    """
    将 LLM 输出的四元组文本解析成 DisasterInfo ORM 对象列表
    """
    infos: list[DisasterInfo] = []
    for m in _QUADRUPLE_RE.finditer(raw):
        infos.append(
            DisasterInfo(
                time=m.group("time").strip(),
                location=m.group("loc").strip(),
                event=m.group("evt").strip(),
                level=m.group("level").strip(),
            )
        )
    return infos

def generate_report_info(raw_text: str) -> tuple[str, list[DisasterInfo]]:
    """
    两步推理：
    1. 生成摘要
    2. 从摘要提取四元组
    """
    # 第一步提示词
    summary_prompt = (
    "你是一个灾害信息处理专家，任务是把给定的灾情长文本，生成一段简短的结构化摘要，突出主要信息。\n\n"
    "请严格遵循以下处理步骤：\n"
    "1. 仔细阅读全文，判断文本中有多少个【独立的灾害事件】（灾害发生的时间、地点、类型、影响不同视为独立事件）。若原文中仅有一句简单事件描述，请直接保留原文内容，不需要改写或增加信息。\n"
    "2. 对每个独立事件，提取其对应的关键信息：【时间】、【地点】、【事件或处置结果】、【受灾程度】。\n"
    "3. 每个事件单独写一句话，句子顺序保持与原文一致，句子间用“。”结束，不换行，不添加其他解释或编号。\n"
    "4. 如果某些事件的内容缺失时间、地点，请保留已知信息，不得猜测或补充原文未出现的信息。\n"
    "5. 如果存在内容完全相同的事件信息，仅保留一条，避免重复。\n\n"
    "文本如下：\n" 
)
    
    summary_messages = [
        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": raw_text}
    ]
    summary = _call_chat_llm(summary_messages, max_tokens=512, temperature=0.7)

    # 第二步提示词
    quadruple_prompt = (
    "你是一名结构化信息提取专家，擅长将灾害类摘要内容准确拆分为【时间】-【地点】-【事件】-【受灾程度】四元组。请注意:\n\n"
    "1. 【事件】字段只填写精炼的灾害类型词汇（如：台风、洪水、地震、山体滑坡等）,不要添加其他描述。\n"
    "2. 【受灾程度】字段仅填写描述该事件影响程度的信息（如：多处电力中断、造成3人失联等），不要包含灾害名称\n"
    "3.  如果一段摘要包含多个独立的事件，请将其拆分成多条记录，每条记录对应一条独立事件，确保每个事件都有清晰的时间、地点、事件和受灾程度。\n"
    "4. 当同一句话中出现多个地点、多个时间或多个受灾描述时，请根据上下文判断并拆分，确保各记录之间对应正确。\n"
    "5. 如果原文缺失【时间】或【地点】等信息，请填写“未知”，不要留空，也不要自行补充未出现的内容。\n\n"
    "输出格式如下（每组四元组一段）：\n\n"
    "时间：<时间>\n"
    "地点：<地点>\n"
    "事件：<灾害类型>\n"
    "受灾程度：<受灾程度>\n\n"
    "以下是两个示例，供你参考：\n\n"
    "示例一：\n"
    "摘要：\n"
    "2023年2月6日，土耳其东南部发生强烈地震，为7.8级，造成重大人员伤亡。政府启动紧急状态并展开大规模救援。国际社会也积极援助。截至2月10日，死亡人数超过2万。\n\n"
    "思考过程：\n"
    "1. 摘要中描述的灾害类型为“地震”，发生时间为2023年2月6日，发生地点为土耳其东南部。\n"
    "2. 受灾程度为“重大人员伤亡”，未涉及多个地点或多次灾害，无需拆分多条记录。\n"
    "3. 因此只需提取一条完整的四元组记录，包含时间、地点、事件和受灾程度。\n\n"
    "最终应提取为如下记录：\n"
    "时间：2023年2月6日\n"
    "地点：土耳其东南部\n"
    "事件：地震\n"
    "受灾程度：重大人员伤亡\n\n"
    "示例二：\n"
    "摘要：\n"
    "2024年9月15日，广东省珠海市及中山市遭遇强台风“银海”正面袭击，带来强降雨和11级阵风。珠海市区多条道路积水严重，部分区域水深超过1.2米。中山市多处电力中断，超过20万人受影响。9月16日凌晨，惠州市突发山体滑坡，造成3人失联。省应急管理厅已派出工作组前往受灾地区指导救援。\n\n"
    "思考过程：\n"
    "1. 该摘要描述了多个地点（珠海市、中山市、惠州市）和多个事件（台风、山体滑坡）。\n"
    "2. 每个地点和事件对应的受灾影响不同，因此需要分别提取为多条记录。\n"
    "3. 【事件】字段应仅填写灾害类型，如“台风”或“山体滑坡”。\n"
    "4. 【受灾程度】字段应填写具体的受灾影响，如“多条道路积水严重”、“多处电力中断，超过20万人受影响”、“造成3人失联”。\n"
    "最终应拆分为如下记录：\n"
    "记录1：\n"
    "时间：2024年9月15日\n"  
    "地点：广东省珠海市\n"  
    "事件：台风\n"  
    "受灾程度：多条道路积水严重\n\n"
    "记录2：\n"
    "时间：2024年9月15日\n"  
    "地点：广东省中山市\n"  
    "事件：台风\n" 
    "受灾程度：多处电力中断，超过20万人受影响\n\n"  
    "记录3：\n"
    "时间：2024年9月16日凌晨\n"  
    "地点：惠州市\n"  
    "事件：山体滑坡\n"  
    "受灾程度：造成3人失联\n\n"
    "请按以上格式提取下列摘要内容的四元组：\n"
    )

    quadruple_messages = [
        {"role": "system", "content": quadruple_prompt},
        {"role": "user", "content": summary}
    ]
    quadruple_text = _call_chat_llm(quadruple_messages, max_tokens=512, temperature=0.7)
    disaster_infos = _parse_quadruples(quadruple_text)
    return summary, disaster_infos

def llm_check_similarity(text1: str, text2: str) -> bool:
    """
    判断两条灾情是否属于相同事件
    """
    sim_prompt = (
        "你是一个灾害信息比对助手。请判断用户输入的两段四元组文本是否语义相似，"
        "仅回答“是”或“否”，不要添加其他内容。"
    )

    user_prompt = ( 
        f"文本一：{text1}\n"
        f"文本二：{text2}\n"
        "这两段内容是否语义相似？请仅回答“是”或“否”。"
    )

    sim_messages = [
        {"role": "system", "content": sim_prompt},
        {"role": "user", "content": user_prompt}
    ]
    try:
        result = _call_chat_llm(sim_messages, max_tokens=10, temperature=0.0)
        return result.strip() == "是"
    except Exception as e:
        print(f"[LLM相似度判断异常] {e}")
        return False
    
def merge_level_texts(level_lines: list[str]) -> str:
    """
    将多行 level 文本传给 LLM，合并成一句短句。
    """

    COMBINE_LEVEL_PROMPT = (
    "你是一名文本合并助手，现有多条记录的信息需要整合成一句简短、清晰的描述。\n\n"
    "要求如下：\n"
    "1. 如果所有输入的 level 信息完全相同，则只输出一次该描述。\n"
    "2. 如果存在差异，则合并后输出一个包含所有不同描述的短句，逻辑通顺且准确,必要时可以使用连词或补充词使句子更加完整。\n"
    "3. 严禁添加任何未提供的内容或自行捏造的信息，输出结果必须严格基于提供的内容。\n"
    "注意:输入中每行代表一条独立的描述。\n"
    "例如，假设提供以下字段：\n"
    "出行不方便\n"
    "出行不方便\n"
    "大面积停电\n"
    "针对以上示例，合并后的结果可以是:出行不方便，同时存在大面积停电的情况。\n\n"
    "请按以上要求合并下列信息,整合成一句简短、清晰的描述。\n"
)
    # 构造对话
    combine_messages = [
        {"role": "system", "content": COMBINE_LEVEL_PROMPT},
        {"role": "user",   "content": "\n".join(level_lines)},
    ]
    try:
        merged = _call_chat_llm(messages=combine_messages, max_tokens=256, temperature=0.3)
        return merged.strip()
    except Exception as e:
        print(f"[LLM合并Level异常] {e}")
        # 出问题了就简单拼成一句
        return "；".join(dict.fromkeys(level_lines))
