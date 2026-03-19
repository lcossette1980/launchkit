"""Schemas for the copy and messaging toolkit."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HeadlineSchema(BaseModel):
    """A hero headline variant with subheadline and CTA."""

    headline: str
    subheadline: str = ""
    cta: str = ""


class EmailTemplateSchema(BaseModel):
    """An email template with subject and body."""

    subject: str
    body: str


class LandingPageSectionsSchema(BaseModel):
    """Structured landing page copy sections."""

    problem: list[str] = Field(default_factory=list)
    solution: list[str] = Field(default_factory=list)
    benefits: list[str] = Field(default_factory=list)
    social_proof: list[str] = Field(default_factory=list)
    faq: list[str] = Field(default_factory=list)


class CopyKitSchema(BaseModel):
    """Complete copy and messaging toolkit."""

    headlines: list[HeadlineSchema] = Field(default_factory=list)
    value_propositions: list[str] = Field(default_factory=list)
    emails: dict[str, EmailTemplateSchema] = Field(default_factory=dict)
    linkedin_messages: dict[str, str] = Field(default_factory=dict)
    ads: dict[str, dict[str, str]] = Field(default_factory=dict)
    landing_page_sections: LandingPageSectionsSchema = Field(
        default_factory=LandingPageSectionsSchema
    )
