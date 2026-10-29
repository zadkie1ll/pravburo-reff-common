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


class ProcessingStatus(StrEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


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


class PartnerLevel(StrEnum):
    START = "start"
    ACTIVE = "active"
    PRO = "pro"
    EXPERT = "expert"


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
    blocked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    display_name: Mapped[str] = mapped_column(String(200), default="", server_default="")
    employment_format: Mapped[EmploymentFormat | None] = mapped_column(
        enum_type(EmploymentFormat), nullable=True
    )
    payout_details: Mapped[str | None] = mapped_column(String(200), nullable=True)
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
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
        Index("ix_referral_applications_agent_created", "agent_id", "created_at"),
        Index("ix_referral_applications_phone_created", "phone_normalized", "created_at"),
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
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        enum_type(ProcessingStatus), default=ProcessingStatus.NEW
    )
    assigned_manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("referral.agents.id"), nullable=True
    )
    bitrix_deal_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deal_stage_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    agent: Mapped[Agent] = relationship(foreign_keys=[agent_id])
    assigned_manager: Mapped[Agent | None] = relationship(foreign_keys=[assigned_manager_id])


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
        CheckConstraint("network_level IN (1, 2, 3)", name="ck_rewards_network_level"),
        CheckConstraint(
            "(reward_type = 'quarterly_bonus' AND application_id IS NULL) "
            "OR (reward_type != 'quarterly_bonus' AND application_id IS NOT NULL)",
            name="ck_rewards_quarterly_bonus_no_application",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    deal_id: Mapped[str] = mapped_column(String(64), index=True)
    application_id: Mapped[int | None] = mapped_column(
        ForeignKey("referral.referral_applications.id"), index=True, nullable=True
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
    due_notice_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    overdue_notice_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class NetworkOverrideRate:
    """Flat sum paid to the upline per override level (1-3), regardless of the
    downline's own reward amount. Was a percent-of-reward rate; product
    switched to a flat amount per level instead.

    Level 3 only ever applies to a partner-type earner (self-registered) -
    a client-type earner (auto-created, never registered) caps at level 2.
    See bounty's _max_override_levels for that split.
    """

    __tablename__ = "network_override_rates"
    __table_args__ = (
        CheckConstraint("level IN (1, 2, 3)", name="ck_network_override_rates_level"),
        CheckConstraint("amount >= 0", name="ck_network_override_rates_amount_non_negative"),
    )

    level: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class RewardStageRate:
    """Flat amount paid to the referring agent when a deal crosses a
    specific Bitrix stage (advance on contract signing, main payout on
    deposit) - see pravburo-reff-crm's STAGE_REWARD_TRIGGERS for which
    stage maps to which reward_type. One row per (reward_type, level): the
    amount for `main` depends on the agent's partner level for the month the
    contract was signed (see PartnerLevelMonth); `advance` amounts are the
    same across all 4 levels by business rule (always 3000), kept per-level
    here only so the primary key doesn't need a nullable column. Admin-editable,
    same singleton-per-key pattern as NetworkOverrideRate.
    """

    __tablename__ = "reward_stage_rates"
    __table_args__ = (
        CheckConstraint(
            "reward_type IN ('advance', 'main')", name="ck_reward_stage_rates_type"
        ),
        CheckConstraint("amount >= 0", name="ck_reward_stage_rates_amount_non_negative"),
    )

    reward_type: Mapped[RewardType] = mapped_column(enum_type(RewardType), primary_key=True)
    level: Mapped[PartnerLevel] = mapped_column(enum_type(PartnerLevel), primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class PartnerLevelMonth:
    """One row per (agent, calendar month): the partner's level for that
    month, fixed by the number of non-rejected contracts (ADVANCE rewards)
    signed in it. `contracts_count` is denormalized here so the monthly
    recompute job (see project plan) doesn't need to recount rewards to show
    the level; `is_manual` freezes the row so that job skips it instead of
    overwriting an admin correction.
    """

    __tablename__ = "partner_level_months"
    __table_args__ = (
        UniqueConstraint("agent_id", "year", "month", name="uq_partner_level_months_agent_period"),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_partner_level_months_month"),
        CheckConstraint(
            "contracts_count >= 0", name="ck_partner_level_months_contracts_non_negative"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("referral.agents.id"), index=True)
    year: Mapped[int] = mapped_column()
    month: Mapped[int] = mapped_column()
    contracts_count: Mapped[int] = mapped_column(default=0)
    level: Mapped[PartnerLevel] = mapped_column(enum_type(PartnerLevel), default=PartnerLevel.START)
    is_manual: Mapped[bool] = mapped_column(default=False, server_default="false")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


@app_registry.mapped
class PayoutSettings:
    """Single-row settings for the admin "Выплаты" panel: how many days after
    a reward is approved (Reward.decided_at) it counts as overdue if still
    unpaid. Admin-editable, same singleton-row pattern as NetworkOverrideRate.
    """

    __tablename__ = "payout_settings"
    __table_args__ = (
        CheckConstraint("overdue_days > 0", name="ck_payout_settings_overdue_days_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    overdue_days: Mapped[int] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class FaqItem:
    """Editable FAQ entries shown on the public /faq page, managed from the
    admin "Материалы" panel. `position` controls display order (ascending).
    """

    __tablename__ = "faq_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(String(300))
    answer: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


@app_registry.mapped
class ReferralLinkVisit:
    """One row per visit to an agent's application link (/r/{referral_code})."""

    __tablename__ = "referral_link_visits"
    __table_args__ = (Index("ix_referral_link_visits_agent_created", "agent_id", "created_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("referral.agents.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


@app_registry.mapped
class PushSubscription:
    """One row per browser the agent granted Web Push permission in
    (navigator.pushManager.subscribe()). A partner may have several (phone +
    desktop); each is targeted independently when sending a notification.
    """

    __tablename__ = "push_subscriptions"
    __table_args__ = (UniqueConstraint("endpoint", name="uq_push_subscriptions_endpoint"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("referral.agents.id"), index=True)
    endpoint: Mapped[str] = mapped_column(Text)
    p256dh: Mapped[str] = mapped_column(String(200))
    auth: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
