TCF_DEFAULT_FACTORS = [
    {"id": "T1", "name": "分布式系统", "weight": 2.0, "level": 0},
    {"id": "T2", "name": "响应时间或吞吐量性能", "weight": 1.0, "level": 0},
    {"id": "T3", "name": "终端用户效率", "weight": 1.0, "level": 0},
    {"id": "T4", "name": "复杂的内部处理", "weight": 1.0, "level": 0},
    {"id": "T5", "name": "代码必须重用", "weight": 1.0, "level": 0},
    {"id": "T6", "name": "易安装性", "weight": 0.5, "level": 0},
    {"id": "T7", "name": "易用性", "weight": 0.5, "level": 0},
    {"id": "T8", "name": "可移植性", "weight": 2.0, "level": 0},
    {"id": "T9", "name": "易更改性", "weight": 1.0, "level": 0},
    {"id": "T10", "name": "并发性", "weight": 1.0, "level": 0},
    {"id": "T11", "name": "特殊的安全性", "weight": 1.0, "level": 0},
    {"id": "T12", "name": "提供第三方接口", "weight": 1.0, "level": 0},
    {"id": "T13", "name": "需要特别的用户培训", "weight": 1.0, "level": 0},
]

EF_DEFAULT_FACTORS = [
    {"id": "F1", "name": "熟悉UML的程度", "weight": 1.5, "level": 0},
    {"id": "F2", "name": "开发应用程序的经验", "weight": 0.5, "level": 0},
    {"id": "F3", "name": "面向对象经验", "weight": 1.0, "level": 0},
    {"id": "F4", "name": "主分析师能力", "weight": 0.5, "level": 0},
    {"id": "F5", "name": "激励机制", "weight": 1.0, "level": 0},
    {"id": "F6", "name": "需求稳定度", "weight": 2.0, "level": 0},
    {"id": "F7", "name": "日程紧迫人员", "weight": -1.0, "level": 0},
    {"id": "F8", "name": "具有基础难度", "weight": -1.0, "level": 0},
]

USE_CASE_WEIGHTS = {"simple": 5, "average": 10, "complex": 15}
ACTOR_WEIGHTS = {"simple": 1, "average": 2, "complex": 3}
