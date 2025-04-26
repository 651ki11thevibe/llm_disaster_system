# app/utils/embedder.py
from text2vec import SentenceModel
from app.models.disaster_info import DisasterInfo
import numpy as np

#加载本地轻量级别模型计算embedding
model = SentenceModel("./sim_model/text2vec-base-chinese")

def encode_disaster_fields(item: DisasterInfo):
    """
    对单个灾情记录的各字段分别编码，再加权融合生成最终向量。防止其他噪声影响小模型判别
    """
    vec_time = model.encode(item.time or "")
    vec_loc = model.encode(item.location or "")
    vec_event = model.encode(item.event or "")
    vec_level = model.encode(item.level or "")
    final_vector = (
        0.3 * vec_time +
        0.25 * vec_loc +
        0.2 * vec_event +
        0.25 * vec_level
    )
    return final_vector
