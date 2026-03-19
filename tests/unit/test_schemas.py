"""Tests for Pydantic schema validation and defaults."""

import pytest
from pydantic import ValidationError

from gtm.schemas.analysis import PageAnalysisSchema, ScoresSchema, WebsiteAnalysisSchema
from gtm.schemas.competitor import CompetitorAnalysisSchema, CompetitorSchema
from gtm.schemas.config import AnalysisRequest
from gtm.schemas.copy_kit import CopyKitSchema, HeadlineSchema
from gtm.schemas.dashboard import AlertSchema, DashboardSpecSchema
from gtm.schemas.experiments import ExperimentSchema, ExperimentsBacklogSchema
from gtm.schemas.report import FullReportSchema
from gtm.schemas.strategy import GTMStrategySchema, RoadmapSchema


class TestScoresSchema:
    def test_defaults_to_zero(self):
        s = ScoresSchema()
        assert s.clarity == 0
        assert s.ux == 0

    def test_valid_range(self):
        s = ScoresSchema(clarity=100, seo=0)
        assert s.clarity == 100
        assert s.seo == 0

    def test_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            ScoresSchema(clarity=101)
        with pytest.raises(ValidationError):
            ScoresSchema(seo=-1)


class TestExperimentSchema:
    def test_ice_score_calculation(self):
        exp = ExperimentSchema(title="Test", impact=8, confidence=7, effort=2)
        score = exp.compute_ice()
        assert score == 28.0
        assert exp.ice_score == 28.0

    def test_min_effort(self):
        exp = ExperimentSchema(title="Test", impact=10, confidence=10, effort=1)
        score = exp.compute_ice()
        assert score == 100.0

    def test_zero_effort_rejected(self):
        with pytest.raises(ValidationError):
            ExperimentSchema(title="Test", impact=10, confidence=10, effort=0)


class TestExperimentsBacklog:
    def test_sort_by_ice(self):
        backlog = ExperimentsBacklogSchema(
            experiments=[
                ExperimentSchema(title="Low", impact=2, confidence=2, effort=8),
                ExperimentSchema(title="High", impact=9, confidence=9, effort=1),
                ExperimentSchema(title="Mid", impact=5, confidence=5, effort=5),
            ]
        )
        backlog.sort_by_ice()
        assert backlog.experiments[0].title == "High"
        assert backlog.experiments[-1].title == "Low"


class TestRoadmapSchema:
    def test_alias_serialization(self):
        rm = RoadmapSchema(day_30=["a"], day_60=["b"], day_90=["c"])
        dumped = rm.model_dump(by_alias=True)
        assert dumped["30_day"] == ["a"]
        assert dumped["60_day"] == ["b"]

    def test_alias_deserialization(self):
        rm = RoadmapSchema.model_validate({"30_day": ["x"], "60_day": ["y"], "90_day": ["z"]})
        assert rm.day_30 == ["x"]


class TestAnalysisRequest:
    def test_valid_request(self, sample_config):
        req = AnalysisRequest(**sample_config)
        assert req.brand == "TestBrand"
        assert req.max_pages_to_scan == 10

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(brand="X")  # missing site_url and audience_primary

    def test_max_pages_bounds(self):
        with pytest.raises(ValidationError):
            AnalysisRequest(
                site_url="https://example.com",
                brand="Test",
                audience_primary="devs",
                max_pages_to_scan=999,
            )


class TestFullReportSchema:
    def test_defaults_construct(self):
        report = FullReportSchema(
            brand_info={"brand": "Test", "url": "https://test.com"}
        )
        assert report.brand_info.brand == "Test"
        assert report.experiments.experiments == []
        assert report.executive_summary.overview == ""

    def test_round_trip(self, sample_report):
        report = FullReportSchema.model_validate(sample_report)
        dumped = report.model_dump(by_alias=True)
        assert dumped["brand_info"]["brand"] == "TestBrand"
        assert len(dumped["website_analysis"]["pages_analyzed"]) == 1
        assert dumped["experiments"]["experiments"][0]["title"] == "Homepage CTA test"

    def test_partial_data_fills_defaults(self):
        partial = {"brand_info": {"brand": "Partial", "url": "https://partial.com"}}
        report = FullReportSchema.model_validate(partial)
        assert report.brand_info.brand == "Partial"
        assert report.executive_summary.overview == ""
        assert report.website_analysis.overall_scores.clarity == 0
