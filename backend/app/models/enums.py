import enum


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class VerificationType(str, enum.Enum):
    MANUAL = "manual"
    CHANNEL_SUBSCRIPTION = "channel_subscription"
