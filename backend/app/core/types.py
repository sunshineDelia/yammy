"""共享列类型：兼顾 MySQL（BIGINT）与 SQLite 单测（INTEGER 自增）。

PRD §4.1 要求主键/外键使用 BIGINT；但单元测试使用 SQLite（PRD §5.1），
而 SQLite 仅当主键声明为 INTEGER 时才具备自增（rowid 别名）能力，
BIGINT 会触发 ``NOT NULL constraint failed``。
因此通过 ``with_variant`` 在 SQLite 上回退为 Integer，MySQL 保持 BIGINT。
"""

from sqlalchemy import BigInteger, Integer

BigIntType = BigInteger().with_variant(Integer, "sqlite")
