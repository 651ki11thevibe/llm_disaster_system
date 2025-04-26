# app/utils/full_dedup_engine.py

from sqlalchemy.orm import Session
from app.models.disaster_info import DisasterInfo
from app.utils.embedder import encode_disaster_fields
import faiss
import numpy as np
from app.core.llm_service import llm_check_similarity  

def find_similar_disaster_infos(db: Session, threshold=0.9, fuzzy_lower=0.6):
    """
    在数据库中查找相似的灾情记录。
    
    1. 先将记录分为“新记录”（has_been_checked=False）和“历史记录”（has_been_checked=True）。
    2. 对新记录内部进行比对（新-新），以及新记录与历史记录间的比对（新-旧）。
       对于模糊匹配（相似度在 [fuzzy_lower, threshold) 范围内）时，调用 llm_check_similarity 进行复核。
    3. 当判断为重复时，取 ID 较小的记录为主记录.
    4. 比对结束后，将所有新记录的 has_been_checked 设为 True，并提交更新。
    
    返回一个包含重复对的列表，每个元素为 (id1, id2) 的元组。
    """
    # 查询所有记录
    all_records = db.query(DisasterInfo).all()
    # 分组：新记录和历史记录
    new_records = [r for r in all_records if not r.has_been_checked]
    old_records = [r for r in all_records if r.has_been_checked]
    
    seen = set()  # 用于去重的记录对（存储排序后的 (id1, id2)）
    similar_pairs = []

    # 为方便 llm 检查，构造文本表示列表
    new_text_list = [
        f"时间：{r.time}，地点：{r.location}，事件：{r.event}，受灾程度：{r.level}"
        for r in new_records
    ]
    old_text_list = [
        f"时间：{r.time}，地点：{r.location}，事件：{r.event}，受灾程度：{r.level}"
        for r in old_records
    ]
    
    # 新记录之间（新-新）的比对
    if new_records:
        vectors_new = np.array([encode_disaster_fields(r) for r in new_records])
        faiss.normalize_L2(vectors_new)
        index_new = faiss.IndexFlatIP(vectors_new.shape[1])
        index_new.add(vectors_new)
        top_k = 5
        scores_new, neighbors_new = index_new.search(vectors_new, top_k)
        
        for i, (score_row, neighbor_row) in enumerate(zip(scores_new, neighbors_new)):
            for j, score in enumerate(score_row):
                target_idx = neighbor_row[j]
                if i == target_idx or target_idx < 0 or target_idx >= len(new_records):
                    continue  # 加索引保护
                pair = tuple(sorted([new_records[i].id, new_records[target_idx].id]))
                if pair in seen:
                    continue
                seen.add(pair)
                if score >= threshold:
                    similar_pairs.append(pair)
                    # 较小 id 为主记录
                    main_id, _ = sorted([new_records[i].id, new_records[target_idx].id])
                    main_record = db.query(DisasterInfo).filter(DisasterInfo.id == main_id).first()
                elif fuzzy_lower <= score < threshold:
                    print(f"Invoking LLM for fuzzy new-new comparison: Record {new_records[i].id} vs Record {new_records[target_idx].id}")
                    if llm_check_similarity(new_text_list[i], new_text_list[target_idx]):
                        similar_pairs.append(pair)
                        main_id, _ = sorted([new_records[i].id, new_records[target_idx].id])
                        main_record = db.query(DisasterInfo).filter(DisasterInfo.id == main_id).first()

    # 新记录与历史记录之间（新-旧）的比对
    if new_records and old_records:
        vectors_old = np.array([encode_disaster_fields(r) for r in old_records])
        faiss.normalize_L2(vectors_old)
        index_old = faiss.IndexFlatIP(vectors_old.shape[1])
        index_old.add(vectors_old)
        top_k = 5
        for i, record in enumerate(new_records):
            vec_new = encode_disaster_fields(record)
            vec_new = vec_new.reshape(1, -1)
            faiss.normalize_L2(vec_new)
            scores_old, neighbors_old = index_old.search(vec_new, top_k)
            for score, target_idx in zip(scores_old[0], neighbors_old[0]):
                if target_idx < 0 or target_idx >= len(old_records):
                    continue  # 加索引保护
                pair = tuple(sorted([record.id, old_records[target_idx].id]))
                if pair in seen:
                    continue
                seen.add(pair)
                if score >= threshold:
                    similar_pairs.append(pair)
                    main_id, _ = sorted([record.id, old_records[target_idx].id])
                    main_record = db.query(DisasterInfo).filter(DisasterInfo.id == main_id).first()
                elif fuzzy_lower <= score < threshold:
                    print(f"Invoking LLM for fuzzy new-new comparison: Record {record.id} vs Record {old_records[target_idx].id}")
                    text_new = f"时间：{record.time}，地点：{record.location}，事件：{record.event}，受灾程度：{record.level}"
                    text_old = f"时间：{old_records[target_idx].time}，地点：{old_records[target_idx].location}，事件：{old_records[target_idx].event}，受灾程度：{old_records[target_idx].level}"
                    if llm_check_similarity(text_new, text_old):
                        similar_pairs.append(pair)
                        main_id, _ = sorted([record.id, old_records[target_idx].id])
                        main_record = db.query(DisasterInfo).filter(DisasterInfo.id == main_id).first()
                        
    # ---------------------------
    # 将所有新记录标记为已比对
    for rec in new_records:
        rec.has_been_checked = True
    
    db.commit()
    return similar_pairs
