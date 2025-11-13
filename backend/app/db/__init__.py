from app.db.base import Base  # noqa

# 모델을 여기서 import 해서 Base.metadata에 등록
from app.models.law import Law  # noqa
from app.models.law_change_event import LawChangeEvent  # noqa
from app.models.old_new_info import OldNewInfo  # noqa
from app.models.article_diff import ArticleDiff  # noqa
