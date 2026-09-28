from pravburo_ref_common.contracts import LeadCreate, RewardCreate
from pravburo_ref_common.models import (
    Agent,
    PartnerLevelMonth,
    ReferralApplication,
    Reward,
    RewardStageRate,
)


def test_owned_tables_use_referral_schema() -> None:
    assert Agent.__table__.schema == "referral"
    assert ReferralApplication.__table__.schema == "referral"
    assert Reward.__table__.schema == "referral"
    assert PartnerLevelMonth.__table__.schema == "referral"


def test_reward_stage_rate_key_includes_level() -> None:
    assert {col.name for col in RewardStageRate.__table__.primary_key.columns} == {
        "reward_type",
        "level",
    }


def test_reward_application_id_is_nullable() -> None:
    assert Reward.__table__.c.application_id.nullable is True


def test_internal_contracts_preserve_attribution() -> None:
    lead = LeadCreate(
        application_id=10,
        agent_id=20,
        full_name="Тестовый Клиент",
        phone_normalized="+79990000000",
    )
    reward = RewardCreate(deal_id="30", application_id=10, agent_id=20)

    assert lead.application_id == reward.application_id
    assert lead.agent_id == reward.agent_id
