from decimal import Decimal

from pydantic import BaseModel, Field

from pravburo_ref_common.models import RewardType


class LeadCreate(BaseModel):
    application_id: int
    agent_id: int
    agent_name: str = ""
    full_name: str = Field(max_length=200)
    phone_normalized: str = Field(max_length=20)
    preferred_call_time_msk: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=120)
    debt_amount: str | None = Field(default=None, max_length=80)
    situation: str | None = Field(default=None, max_length=3000)


class RewardCreate(BaseModel):
    deal_id: str = Field(min_length=1, max_length=64)
    application_id: int
    agent_id: int
    reward_type: RewardType = RewardType.MAIN
    amount: Decimal | None = None
