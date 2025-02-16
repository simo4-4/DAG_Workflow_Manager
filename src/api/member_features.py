from pydantic import BaseModel
from typing import Optional


class MemberFeatures(BaseModel):
    AVG_POINTS_BOUGHT: Optional[float] = None
    AVG_REVENUE_USD: Optional[float] = None
    LAST_3_TRANSACTIONS_AVG_POINTS_BOUGHT: Optional[float] = None
    LAST_3_TRANSACTIONS_AVG_REVENUE_USD: Optional[float] = None
    PCT_BUY_TRANSACTIONS: Optional[float] = None
    PCT_GIFT_TRANSACTIONS: Optional[float] = None
    PCT_REDEEM_TRANSACTIONS: Optional[float] = None
    DAYS_SINCE_LAST_TRANSACTION: Optional[int] = None
