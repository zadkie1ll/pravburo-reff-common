from pravburo_ref_common.contracts import LeadCreate, RewardCreate
from pravburo_ref_common.models import Agent, ReferralApplication, Reward


def test_owned_tables_use_referral_schema() -> None:
    assert Agent.__table__.schema == "referral"
    assert ReferralApplication.__table__.schema == "referral"
    assert Reward.__table__.schema == "referral"


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
