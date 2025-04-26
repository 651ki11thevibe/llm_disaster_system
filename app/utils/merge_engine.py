# app/utils/merge_engine.py

from collections import Counter, defaultdict
from sqlalchemy.orm import Session
from typing import List, Tuple

from app.models.disaster_info import DisasterInfo
from app.core.llm_service import merge_level_texts

class _DSU:
    """简单并查集，用来把相似对聚成簇"""
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if self.parent.get(x, x) != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent.get(x, x)

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def merge_duplicate_clusters(
    db: Session,
    similar_pairs: List[Tuple[int, int]],
) -> Tuple[int, int]:
    """
    接收 find_similar_disaster_infos 返回的相似对，
    聚簇后合并 & 删除，最后返回 (合并了多少簇, 删除了多少条记录)。
    """
    if not similar_pairs:
        return 0, 0, []

    # 构造 display_id 映射：{disaster_info.id: "3.1"}
    all_disasters = db.query(DisasterInfo).order_by(DisasterInfo.report_id, DisasterInfo.id).all()
    id_to_display = {}
    report_groups = defaultdict(list)
    for d in all_disasters:
        report_groups[d.report_id].append(d)
    for report_id, items in report_groups.items():
        for idx, d in enumerate(items, 1):
            id_to_display[d.id] = f"{report_id}.{idx}"

    # 1. 聚簇
    dsu = _DSU()
    for a, b in similar_pairs:
        dsu.union(a, b)

    clusters: dict[int, list[int]] = defaultdict(list)
    for rid in {i for pair in similar_pairs for i in pair}:
        clusters[dsu.find(rid)].append(rid)

    merged_clusters = 0
    deleted_records = 0
    cluster_details: List[dict] = []

    # 2. 对每个簇执行合并
    for id_list in clusters.values():
        recs = db.query(DisasterInfo).filter(DisasterInfo.id.in_(id_list)).all()
        if len(recs) <= 1:
            continue

        merged_clusters += 1
        deleted_records += len(recs) - 1

        main = max(recs, key=lambda r: (r.report_count, -r.id))
        to_delete = [r.id for r in recs if r.id != main.id]

        cluster_details.append({
            "main_display_id": id_to_display[main.id],
            "merged_display_ids": [id_to_display[i] for i in to_delete]
        })

        _merge_one_cluster(db, id_list)

    db.commit()
    return merged_clusters, deleted_records, cluster_details

def _choose_longest(values: List[str]) -> str:
    """取最长字符串，若并列则取字典序最小的"""
    return max(values, key=lambda s: (len(s), s or ""))


def _merge_one_cluster(db: Session, id_list: List[int]):
    recs = (
        db.query(DisasterInfo)
        .filter(DisasterInfo.id.in_(id_list))
        .all()
    )
    if len(recs) <= 1:
        return

    # 1. report_count 累加所有历史值 —— 
    total_count = sum(r.report_count for r in recs)

    # 2. time / location 取最长 —— 
    merged_time = _choose_longest([r.time or "" for r in recs])
    merged_loc  = _choose_longest([r.location or "" for r in recs])

    # 3. event 取众数，如并列再取最长 —— 
    cnt = Counter(r.event or "" for r in recs)
    top_freq = cnt.most_common(1)[0][1]
    merged_event = _choose_longest([e for e, f in cnt.items() if f == top_freq])

    # 4. level 是否相同，不同则调用 LLM 合并 —— 
    levels = [r.level or "" for r in recs]
    if len(set(levels)) == 1:
        merged_level = levels[0]
    else:
        merged_level = merge_level_texts(levels)

    # 5. 选主记录：当前 report_count 最大，其次 id 最小 —— 
    main = max(recs, key=lambda r: (r.report_count, -r.id))

    # 更新主记录
    main.time         = merged_time
    main.location     = merged_loc
    main.event        = merged_event
    main.level        = merged_level
    main.report_count = total_count

    # 补充 report_id，如果丢了
    if not main.report_id:
        for r in recs:
            if r.report_id:
                main.report_id = r.report_id
                break

    db.add(main)  #明确告诉 SQLAlchemy：main 有变动
    db.flush() 
    # 删除其他重复记录
    for r in recs:
        if r.id != main.id:
            db.delete(r)