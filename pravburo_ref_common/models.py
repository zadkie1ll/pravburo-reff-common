from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship
from sqlalchemy.sql import func, text

from pravburo_ref_common.database import app_metadata

app_registry = registry(metadata=app_metadata)


def enum_type(enum_class: type[StrEnum]) -> Enum:
    return Enum(
        enum_class,
        native_enum=False,
        values_callable=lambda members: [member.value for member in members],
    )


class AgentRole(StrEnum):
    AGENT = "agent"
    ADMIN = "admin"


class EmploymentFormat(StrEnum):
    SELF_EMPLOYED = "self_employed"
    INDIVIDUAL_ENTREPRENEUR = "individual_entrepreneur"
    INDIVIDUAL = "individual"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class RewardStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RewardType(StrEnum):
    ADVANCE = "advance"
    MAIN = "main"
    BONUS_FULL_PAYMENT = "bonus_full_payment"
    QUARTERLY_BONUS = "quarterly_bonus"
    OVERRIDE = "override"


@app_registry.mapped
class Agent:
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String(254), unique=True, index=True, nullable=True)
    phone_normalized: Mapped[str | None] = mapped_column(
        String(20), unique=True, index=True, nullable=True
    )
    display_name: Mapped[str] = mapped_column(String(200), default="")
    role: Mapped[AgentRole] = mapped_column(enum_type(AgentRole), default=AgentRole.AGENT)
    referral_code: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), default=uuid4, unique=True, index=True
    )
    legacy_client_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    invited_by_agent_id: Mapped[int | None] = mapped_column(
        ForeignKey("referral.agents.id"), index=True, nullable=True
    )
    employment_format: Mapped[EmploymentFormat | None] = mapped_column(
        enum_type(EmploymentFormat), nullable=True
    )
    payout_details: Mapped[str | None] = mapped_column(String(200), nullable=True)
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    totp_secret: Mapped[str | None] = mapped_column(String(32), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class AgentCredential:
    __tablename__ = "agent_credentials"

    agent_id: Mapped[int] = mapped_column(
        ForeignKey("referral.agents.id", ondelete="CASCADE"), primary_key=True
    )
    password_hash: Mapped[str] = mapped_column(String(256))


@app_registry.mapped
class AgentIdentity:
    __tablename__ = "agent_identities"
    __table_args__ = (
        UniqueConstraint("provider", "subject", name="uq_agent_identity_provider_subject"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("referral.agents.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(32))
    subject: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class PendingRegistration:
    __tablename__ = "pending_registrations"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    code_hash: Mapped[str] = mapped_column(String(64))
    attempts: Mapped[int] = mapped_column(default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class PendingPasswordReset:
    __tablename__ = "pending_password_resets"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("referral.agents.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(254), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    attempts: Mapped[int] = mapped_column(default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class ReferralApplication:
    __tablename__ = "referral_applications"
    __table_args__ = (
        UniqueConstraint("phone_normalized", name="uq_referral_application_phone"),
        Index("ix_referral_applications_agent_created", "agent_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("referral.agents.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    phone_normalized: Mapped[str] = mapped_column(String(20))
    preferred_call_time_msk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    debt_amount: Mapped[str | None] = mapped_column(String(80), nullable=True)
    situation: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        enum_type(DeliveryStatus), default=DeliveryStatus.PENDING
    )
    bitrix_lead_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    delivery_error: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    agent: Mapped[Agent] = relationship()


@app_registry.mapped
class Reward:
    __tablename__ = "rewards"
    __table_args__ = (
        Index(
            "uq_rewards_deal_id_reward_type_agent_id",
            "deal_id",
            "reward_type",
            "agent_id",
            unique=True,
            postgresql_where=text("source_reward_id IS NULL"),
        ),
        Index(
            "uq_rewards_source_reward_id_agent_id",
            "source_reward_id",
            "agent_id",
            unique=True,
            postgresql_where=text("source_reward_id IS NOT NULL"),
        ),
        CheckConstraint(
            "(reward_type = 'override' AND source_reward_id IS NOT NULL "
            "AND network_level IS NOT NULL) "
            "OR (reward_type != 'override' AND source_reward_id IS NULL "
            "AND network_level IS NULL)",
            name="ck_rewards_override_shape",
        ),
        CheckConstraint("network_level IN (1, 2)", name="ck_rewards_network_level"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    deal_id: Mapped[str] = mapped_column(String(64), index=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("referral.referral_applications.id"), index=True
    )
    agent_id: Mapped[int] = mapped_column(ForeignKey("referral.agents.id"), index=True)
    reward_type: Mapped[RewardType] = mapped_column(enum_type(RewardType), default=RewardType.MAIN)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[RewardStatus] = mapped_column(
        enum_type(RewardStatus), default=RewardStatus.PENDING
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_by_agent_id: Mapped[int | None] = mapped_column(
        ForeignKey("referral.agents.id"), nullable=True
    )
    network_level: Mapped[int | None] = mapped_column(nullable=True)
    source_reward_id: Mapped[int | None] = mapped_column(
        ForeignKey("referral.rewards.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class NetworkOverrideRate:
    """Percent of a downline partner's reward paid to the upline, per override level (1-2)."""

    __tablename__ = "network_override_rates"
    __table_args__ = (
        CheckConstraint("level IN (1, 2)", name="ck_network_override_rates_level"),
        CheckConstraint("percent >= 0", name="ck_network_override_rates_percent_non_negative"),
    )

    level: Mapped[int] = mapped_column(primary_key=True)
    percent: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class ReferralLinkVisit:
    """One row per visit to an agent's application link (/r/{referral_code})."""

    __tablename__ = "referral_link_visits"
    __table_args__ = (Index("ix_referral_link_visits_agent_created", "agent_id", "created_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("referral.agents.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
