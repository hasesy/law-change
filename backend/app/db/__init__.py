from app.db.base import Base  # noqa

# 모델을 여기서 import 해서 Base.metadata에 등록
from app.models.law.law import Law  # noqa
from app.models.law.law_change_event import LawChangeEvent  # noqa
from app.models.law.law_old_new_info import LawOldNewInfo  # noqa
from app.models.law.law_article_diff import LawArticleDiff  # noqa
