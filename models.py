"""
MISIC Data Models
================
Data structures for the Malin's Intelligence Scale for Indian Children.

This module defines all data models used throughout the application,
including patient profiles, test sessions, and subtest results.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Dict, List
from enum import Enum


class TestStage(Enum):
    """Current stage of the testing workflow."""
    REGISTRATION = "registration"
    VERBAL = "verbal"
    PERFORMANCE = "performance"
    REPORT = "report"


class SubtestType(Enum):
    """Types of subtests in MISIC."""
    # Verbal subtests
    INFORMATION = "information"
    COMPREHENSION = "comprehension"
    ARITHMETIC = "arithmetic"
    SIMILARITIES = "similarities"
    VOCABULARY = "vocabulary"
    DIGIT_SPAN = "digit_span"
    
    # Performance subtests
    PICTURE_COMPLETION = "picture_completion"
    BLOCK_DESIGN = "block_design"
    OBJECT_ASSEMBLY = "object_assembly"
    CODING = "coding"
    MAZES = "mazes"


# Define which subtests belong to which scale
VERBAL_SUBTESTS = [
    SubtestType.INFORMATION,
    SubtestType.COMPREHENSION,
    SubtestType.ARITHMETIC,
    SubtestType.SIMILARITIES,
    SubtestType.VOCABULARY,
    SubtestType.DIGIT_SPAN,
]

PERFORMANCE_SUBTESTS = [
    SubtestType.PICTURE_COMPLETION,
    SubtestType.BLOCK_DESIGN,
    SubtestType.OBJECT_ASSEMBLY,
    SubtestType.CODING,
    SubtestType.MAZES,
]


@dataclass
class PatientProfile:
    """
    Patient information and demographics.
    
    Attributes:
        patient_id: Unique identifier for the patient
        name: Patient's full name
        date_of_birth: Patient's date of birth
        test_date: Date when the test is administered
        gender: Patient's gender (optional)
        education: Education level/grade (optional)
        examiner_name: Name of the examiner (optional)
        notes: Additional clinical notes (optional)
    """
    patient_id: str
    name: str
    date_of_birth: date
    test_date: date
    gender: Optional[str] = None
    education: Optional[str] = None
    examiner_name: Optional[str] = None
    notes: Optional[str] = None
    
    @property
    def age_in_months(self) -> int:
        """Calculate age in complete months using 12-month intervals."""
        years = self.test_date.year - self.date_of_birth.year
        months = self.test_date.month - self.date_of_birth.month
        
        # Adjust for day of month
        if self.test_date.day < self.date_of_birth.day:
            months -= 1
        
        total_months = years * 12 + months
        return max(0, total_months)
    
    @property
    def age_years(self) -> int:
        """Get age in complete years."""
        return self.age_in_months // 12
    
    @property
    def age_remaining_months(self) -> int:
        """Get remaining months after complete years."""
        return self.age_in_months % 12
    
    @property
    def age_display(self) -> str:
        """Human-readable age display."""
        years = self.age_years
        months = self.age_remaining_months
        return f"{years} years, {months} months"
    
    @property
    def table_age(self) -> int:
        """
        Get the age to use for table lookup.
        Rounds to nearest year, clamped to valid range 6-15.
        
        Per MISIC manual: Use 12-month intervals, round to nearest year.
        """
        total_months = self.age_in_months
        years = total_months // 12
        remaining_months = total_months % 12
        
        # Round to nearest year (6+ months rounds up)
        if remaining_months >= 6:
            years += 1
        
        # Clamp to valid test range
        return max(6, min(15, years))
    
    def is_valid_age(self) -> bool:
        """Check if patient age is within valid MISIC range (6-15 years)."""
        years = self.age_years
        return 6 <= years <= 15


@dataclass
class SubtestResult:
    """
    Result of a single subtest.
    
    Attributes:
        subtest_type: The type of subtest
        raw_score: The raw score achieved
        test_quotient: The TQ derived from tables (calculated after scoring)
        time_taken_seconds: Time taken to complete (for timed tests)
        items_attempted: Number of items attempted
        items_correct: Number of items answered correctly
        discontinued: Whether the test was discontinued early
        discontinue_reason: Reason for discontinuation (if applicable)
        ai_suggestions: AI grader's suggested scores (for verbal subtests)
        examiner_confirmed: Whether examiner confirmed AI suggestions
        notes: Additional notes from examiner
    """
    subtest_type: SubtestType
    raw_score: int = 0
    test_quotient: Optional[int] = None
    time_taken_seconds: Optional[int] = None
    items_attempted: int = 0
    items_correct: int = 0
    discontinued: bool = False
    discontinue_reason: Optional[str] = None
    ai_suggestions: Optional[Dict] = None
    examiner_confirmed: bool = False
    notes: Optional[str] = None
    
    # Per-item scores for detailed tracking
    item_scores: Dict[int, int] = field(default_factory=dict)
    
    def add_item_score(self, item_number: int, score: int) -> None:
        """Add a score for a specific item."""
        self.item_scores[item_number] = score
        self.items_attempted = len(self.item_scores)
        self.items_correct = sum(1 for s in self.item_scores.values() if s > 0)
        self.raw_score = sum(self.item_scores.values())


@dataclass
class TestSession:
    """
    Complete test session containing all results.
    
    Attributes:
        patient: Patient profile
        verbal_results: Results for all verbal subtests
        performance_results: Results for all performance subtests
        current_stage: Current stage of testing
        current_subtest_index: Index of current subtest within stage
        session_start: When the session started
        session_end: When the session ended (if complete)
    """
    patient: PatientProfile
    verbal_results: Dict[SubtestType, SubtestResult] = field(default_factory=dict)
    performance_results: Dict[SubtestType, SubtestResult] = field(default_factory=dict)
    current_stage: TestStage = TestStage.REGISTRATION
    current_subtest_index: int = 0
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize session start time."""
        if self.session_start is None:
            self.session_start = datetime.now()
    
    def get_verbal_raw_total(self) -> int:
        """Sum of all verbal subtest raw scores."""
        return sum(r.raw_score for r in self.verbal_results.values())
    
    def get_performance_raw_total(self) -> int:
        """Sum of all performance subtest raw scores."""
        return sum(r.raw_score for r in self.performance_results.values())
    
    def get_verbal_tq_list(self) -> List[int]:
        """Get list of TQs for verbal subtests."""
        return [r.test_quotient for r in self.verbal_results.values() 
                if r.test_quotient is not None]
    
    def get_performance_tq_list(self) -> List[int]:
        """Get list of TQs for performance subtests."""
        return [r.test_quotient for r in self.performance_results.values() 
                if r.test_quotient is not None]
    
    def get_all_tq_list(self) -> List[int]:
        """Get list of all TQs."""
        return self.get_verbal_tq_list() + self.get_performance_tq_list()
    
    @property
    def verbal_iq(self) -> Optional[float]:
        """Calculate Verbal IQ (average of verbal TQs)."""
        tqs = self.get_verbal_tq_list()
        if not tqs:
            return None
        return sum(tqs) / len(tqs)
    
    @property
    def performance_iq(self) -> Optional[float]:
        """Calculate Performance IQ (average of performance TQs)."""
        tqs = self.get_performance_tq_list()
        if not tqs:
            return None
        return sum(tqs) / len(tqs)
    
    @property
    def full_scale_iq(self) -> Optional[float]:
        """Calculate Full Scale IQ (average of all TQs)."""
        tqs = self.get_all_tq_list()
        if not tqs:
            return None
        return sum(tqs) / len(tqs)
    
    @property
    def verbal_performance_disparity(self) -> Optional[float]:
        """Calculate Verbal - Performance disparity."""
        v_iq = self.verbal_iq
        p_iq = self.performance_iq
        if v_iq is None or p_iq is None:
            return None
        return v_iq - p_iq
    
    @property
    def has_significant_disparity(self) -> bool:
        """Check if V-P disparity is clinically significant (15+ points)."""
        disparity = self.verbal_performance_disparity
        if disparity is None:
            return False
        return abs(disparity) >= 15
    
    def is_complete(self) -> bool:
        """Check if all subtests are completed."""
        verbal_complete = len(self.verbal_results) == len(VERBAL_SUBTESTS)
        performance_complete = len(self.performance_results) == len(PERFORMANCE_SUBTESTS)
        return verbal_complete and performance_complete
    
    def mark_complete(self) -> None:
        """Mark the session as complete."""
        self.session_end = datetime.now()
        self.current_stage = TestStage.REPORT


@dataclass
class IQClassification:
    """
    IQ classification categories per standard clinical guidelines.
    """
    VERY_SUPERIOR = (130, float('inf'), "Very Superior")
    SUPERIOR = (120, 129, "Superior")
    HIGH_AVERAGE = (110, 119, "High Average")
    AVERAGE = (90, 109, "Average")
    LOW_AVERAGE = (80, 89, "Low Average")
    BORDERLINE = (70, 79, "Borderline")
    EXTREMELY_LOW = (0, 69, "Extremely Low")
    
    @staticmethod
    def classify(iq_score: float) -> str:
        """Get the classification label for an IQ score."""
        if iq_score >= 130:
            return "Very Superior"
        elif iq_score >= 120:
            return "Superior"
        elif iq_score >= 110:
            return "High Average"
        elif iq_score >= 90:
            return "Average"
        elif iq_score >= 80:
            return "Low Average"
        elif iq_score >= 70:
            return "Borderline"
        else:
            return "Extremely Low"
