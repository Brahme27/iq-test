"""
MISIC Scoring Calculator
========================
Core scoring engine for the Malin's Intelligence Scale for Indian Children.

This module provides:
- TQ (Test Quotient) lookup from scoring tables
- Age calculation utilities
- IQ calculation algorithms

All scoring logic follows the MISIC manual strictly. No AI is used for scoring.
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import date

from models import SubtestType, VERBAL_SUBTESTS, PERFORMANCE_SUBTESTS


class TQLookup:
    """
    Test Quotient lookup utility for MISIC scoring tables.
    
    Loads and queries the tables.json file to convert raw scores to TQs.
    Handles range-based keys (e.g., 'range_1_2') and null values.
    """
    
    def __init__(self, tables_path: str = "tables.json"):
        """
        Initialize the TQ lookup with scoring tables.
        
        Args:
            tables_path: Path to the tables.json file
        """
        self.tables_path = Path(tables_path)
        self.tables: Dict[str, Any] = {}
        self._load_tables()
    
    def _load_tables(self) -> None:
        """Load scoring tables from JSON file."""
        if not self.tables_path.exists():
            raise FileNotFoundError(f"Scoring tables not found: {self.tables_path}")
        
        with open(self.tables_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.tables = data.get("tables", {})
        self.meta = data.get("meta", {})
    
    def _get_age_key(self, age: int) -> str:
        """Convert age to table key format."""
        return f"{age}_years"
    
    def _get_scale_key(self, subtest: SubtestType) -> str:
        """Determine if subtest is verbal or performance."""
        if subtest in VERBAL_SUBTESTS:
            return "verbal"
        elif subtest in PERFORMANCE_SUBTESTS:
            return "performance"
        else:
            raise ValueError(f"Unknown subtest type: {subtest}")
    
    def _parse_range_key(self, key: str) -> Optional[Tuple[int, int]]:
        """
        Parse a range key like 'range_1_2' or 'range_10_13' into (start, end).
        
        Args:
            key: The key string to parse
            
        Returns:
            Tuple of (start, end) integers, or None if not a range key
        """
        if not key.startswith("range_"):
            return None
        
        # Handle formats like: range_1_2, range_10_13, range_1_6
        match = re.match(r'range_(\d+)_(\d+)', key)
        if match:
            return int(match.group(1)), int(match.group(2))
        
        return None
    
    def _find_tq_in_dict(self, score_dict: Dict[str, Any], raw_score: int) -> Optional[int]:
        """
        Find TQ for a raw score in a subtest dictionary.
        Handles both direct keys and range keys.
        
        Args:
            score_dict: Dictionary mapping scores/ranges to TQs
            raw_score: The raw score to look up
            
        Returns:
            The TQ value, or None if not found or null
        """
        # First, try direct key lookup
        str_score = str(raw_score)
        if str_score in score_dict:
            value = score_dict[str_score]
            if value == "null" or value is None:
                return None
            return int(value)
        
        # Check range keys
        for key, value in score_dict.items():
            range_bounds = self._parse_range_key(key)
            if range_bounds:
                start, end = range_bounds
                if start <= raw_score <= end:
                    if value == "null" or value is None:
                        return None
                    return int(value)
        
        return None
    
    def get_tq(self, age: int, subtest: SubtestType, raw_score: int) -> Optional[int]:
        """
        Look up the Test Quotient for a given age, subtest, and raw score.
        
        Args:
            age: Patient's age (6-15, will be clamped)
            subtest: The subtest type
            raw_score: The raw score achieved
            
        Returns:
            The TQ value, or None if not found in tables
        """
        # Clamp age to valid range
        age = max(6, min(15, age))
        
        age_key = self._get_age_key(age)
        scale_key = self._get_scale_key(subtest)
        subtest_key = subtest.value
        
        # Navigate to the correct table
        if age_key not in self.tables:
            return None
        
        age_table = self.tables[age_key]
        if scale_key not in age_table:
            return None
        
        scale_table = age_table[scale_key]
        if subtest_key not in scale_table:
            return None
        
        subtest_table = scale_table[subtest_key]
        return self._find_tq_in_dict(subtest_table, raw_score)
    
    def get_max_raw_score(self, age: int, subtest: SubtestType) -> int:
        """
        Get the maximum raw score defined for a subtest at a given age.
        
        Args:
            age: Patient's age (6-15)
            subtest: The subtest type
            
        Returns:
            The maximum raw score, or 0 if not found
        """
        age = max(6, min(15, age))
        age_key = self._get_age_key(age)
        scale_key = self._get_scale_key(subtest)
        subtest_key = subtest.value
        
        try:
            subtest_table = self.tables[age_key][scale_key][subtest_key]
            max_score = 0
            
            for key in subtest_table.keys():
                range_bounds = self._parse_range_key(key)
                if range_bounds:
                    max_score = max(max_score, range_bounds[1])
                else:
                    try:
                        max_score = max(max_score, int(key))
                    except ValueError:
                        continue
            
            return max_score
        except KeyError:
            return 0
    
    def get_available_ages(self) -> list:
        """Get list of available age groups in the tables."""
        ages = []
        for key in self.tables.keys():
            match = re.match(r'(\d+)_years', key)
            if match:
                ages.append(int(match.group(1)))
        return sorted(ages)


class AgeCalculator:
    """
    Age calculation utilities following MISIC manual specifications.
    
    Uses 12-month intervals (not calendar months) for age calculation.
    """
    
    @staticmethod
    def calculate_age_in_months(dob: date, test_date: date) -> int:
        """
        Calculate age in complete months using 12-month intervals.
        
        Args:
            dob: Date of birth
            test_date: Date of testing
            
        Returns:
            Age in complete months
        """
        years = test_date.year - dob.year
        months = test_date.month - dob.month
        
        # Adjust for day of month
        if test_date.day < dob.day:
            months -= 1
        
        total_months = years * 12 + months
        return max(0, total_months)
    
    @staticmethod
    def get_table_age(dob: date, test_date: date) -> int:
        """
        Get the age to use for table lookup.
        
        Rounds to nearest year as per MISIC manual.
        Clamps result to valid range 6-15.
        
        Args:
            dob: Date of birth
            test_date: Date of testing
            
        Returns:
            Age in years for table lookup (6-15)
        """
        total_months = AgeCalculator.calculate_age_in_months(dob, test_date)
        years = total_months // 12
        remaining_months = total_months % 12
        
        # Round to nearest year (6+ months rounds up)
        if remaining_months >= 6:
            years += 1
        
        # Clamp to valid test range
        return max(6, min(15, years))
    
    @staticmethod
    def format_age(dob: date, test_date: date) -> str:
        """
        Format age as a human-readable string.
        
        Args:
            dob: Date of birth
            test_date: Date of testing
            
        Returns:
            String like "8 years, 4 months"
        """
        total_months = AgeCalculator.calculate_age_in_months(dob, test_date)
        years = total_months // 12
        months = total_months % 12
        return f"{years} years, {months} months"
    
    @staticmethod
    def is_valid_age(dob: date, test_date: date) -> bool:
        """
        Check if the patient's age is within valid MISIC range.
        
        Args:
            dob: Date of birth
            test_date: Date of testing
            
        Returns:
            True if age is between 6 and 15 years
        """
        total_months = AgeCalculator.calculate_age_in_months(dob, test_date)
        years = total_months // 12
        return 6 <= years <= 15


class IQCalculator:
    """
    IQ calculation engine for MISIC.
    
    Calculates Verbal IQ, Performance IQ, and Full Scale IQ
    based on Test Quotients from subtests.
    """
    
    def __init__(self, tq_lookup: TQLookup):
        """
        Initialize the IQ calculator.
        
        Args:
            tq_lookup: TQLookup instance for score conversion
        """
        self.tq_lookup = tq_lookup
    
    def calculate_tqs(
        self, 
        age: int, 
        raw_scores: Dict[SubtestType, int]
    ) -> Dict[SubtestType, Optional[int]]:
        """
        Convert all raw scores to TQs.
        
        Args:
            age: Patient's table age (6-15)
            raw_scores: Dictionary of subtest -> raw score
            
        Returns:
            Dictionary of subtest -> TQ (None if lookup failed)
        """
        tqs = {}
        for subtest, raw_score in raw_scores.items():
            tqs[subtest] = self.tq_lookup.get_tq(age, subtest, raw_score)
        return tqs
    
    @staticmethod
    def calculate_verbal_iq(tqs: Dict[SubtestType, Optional[int]]) -> Optional[float]:
        """
        Calculate Verbal IQ from verbal subtest TQs.
        
        Args:
            tqs: Dictionary of subtest -> TQ
            
        Returns:
            Verbal IQ (average of verbal TQs), or None if insufficient data
        """
        verbal_tqs = [
            tqs[st] for st in VERBAL_SUBTESTS 
            if st in tqs and tqs[st] is not None
        ]
        
        if not verbal_tqs:
            return None
        
        return sum(verbal_tqs) / len(verbal_tqs)
    
    @staticmethod
    def calculate_performance_iq(tqs: Dict[SubtestType, Optional[int]]) -> Optional[float]:
        """
        Calculate Performance IQ from performance subtest TQs.
        
        Args:
            tqs: Dictionary of subtest -> TQ
            
        Returns:
            Performance IQ (average of performance TQs), or None if insufficient data
        """
        performance_tqs = [
            tqs[st] for st in PERFORMANCE_SUBTESTS 
            if st in tqs and tqs[st] is not None
        ]
        
        if not performance_tqs:
            return None
        
        return sum(performance_tqs) / len(performance_tqs)
    
    @staticmethod
    def calculate_full_scale_iq(tqs: Dict[SubtestType, Optional[int]]) -> Optional[float]:
        """
        Calculate Full Scale IQ from all subtest TQs.
        
        Args:
            tqs: Dictionary of subtest -> TQ
            
        Returns:
            Full Scale IQ (average of all TQs), or None if insufficient data
        """
        all_tqs = [
            tq for tq in tqs.values() 
            if tq is not None
        ]
        
        if not all_tqs:
            return None
        
        return sum(all_tqs) / len(all_tqs)
    
    @staticmethod
    def calculate_disparity(verbal_iq: float, performance_iq: float) -> float:
        """
        Calculate Verbal-Performance disparity.
        
        Args:
            verbal_iq: Calculated Verbal IQ
            performance_iq: Calculated Performance IQ
            
        Returns:
            Disparity value (Verbal - Performance)
        """
        return verbal_iq - performance_iq
    
    @staticmethod
    def is_significant_disparity(disparity: float, threshold: float = 15.0) -> bool:
        """
        Check if disparity is clinically significant.
        
        Args:
            disparity: The V-P disparity value
            threshold: Significance threshold (default 15 points)
            
        Returns:
            True if disparity exceeds threshold
        """
        return abs(disparity) >= threshold
    
    @staticmethod
    def classify_iq(iq_score: float) -> str:
        """
        Classify IQ score into clinical category.
        
        Args:
            iq_score: The IQ score to classify
            
        Returns:
            Classification label
        """
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
    
    def generate_summary(
        self,
        age: int,
        raw_scores: Dict[SubtestType, int]
    ) -> Dict[str, Any]:
        """
        Generate a complete scoring summary.
        
        Args:
            age: Patient's table age
            raw_scores: All raw scores by subtest
            
        Returns:
            Dictionary containing all calculated scores and classifications
        """
        # Calculate TQs
        tqs = self.calculate_tqs(age, raw_scores)
        
        # Calculate IQs
        verbal_iq = self.calculate_verbal_iq(tqs)
        performance_iq = self.calculate_performance_iq(tqs)
        full_scale_iq = self.calculate_full_scale_iq(tqs)
        
        # Calculate disparity
        disparity = None
        significant_disparity = False
        if verbal_iq is not None and performance_iq is not None:
            disparity = self.calculate_disparity(verbal_iq, performance_iq)
            significant_disparity = self.is_significant_disparity(disparity)
        
        return {
            "raw_scores": raw_scores,
            "test_quotients": tqs,
            "verbal_iq": verbal_iq,
            "performance_iq": performance_iq,
            "full_scale_iq": full_scale_iq,
            "verbal_iq_classification": self.classify_iq(verbal_iq) if verbal_iq else None,
            "performance_iq_classification": self.classify_iq(performance_iq) if performance_iq else None,
            "full_scale_iq_classification": self.classify_iq(full_scale_iq) if full_scale_iq else None,
            "verbal_performance_disparity": disparity,
            "significant_disparity": significant_disparity,
        }


# Discontinuation rules per MISIC manual
DISCONTINUE_RULES = {
    SubtestType.INFORMATION: {
        "consecutive_failures": 5,
        "description": "Discontinue after 5 consecutive failures (0 scores)"
    },
    SubtestType.COMPREHENSION: {
        "consecutive_failures": 4,
        "description": "Discontinue after 4 consecutive failures (0 scores)"
    },
    SubtestType.ARITHMETIC: {
        "consecutive_failures": 4,
        "description": "Discontinue after 4 consecutive failures"
    },
    SubtestType.SIMILARITIES: {
        "consecutive_failures": 4,
        "description": "Discontinue after 4 consecutive failures (0 scores)"
    },
    SubtestType.VOCABULARY: {
        "consecutive_failures": 5,
        "description": "Discontinue after 5 consecutive failures (0 scores)"
    },
    SubtestType.DIGIT_SPAN: {
        "consecutive_failures": 2,
        "description": "Discontinue after failure on both trials of any item"
    },
    SubtestType.PICTURE_COMPLETION: {
        "consecutive_failures": 4,
        "description": "Discontinue after 4 consecutive failures"
    },
    SubtestType.BLOCK_DESIGN: {
        "consecutive_failures": 3,
        "description": "Discontinue after 3 consecutive failures"
    },
    SubtestType.OBJECT_ASSEMBLY: {
        "all_items": True,
        "description": "Administer all items"
    },
    SubtestType.CODING: {
        "timed": True,
        "time_limit": 120,
        "description": "Timed test - 120 seconds"
    },
    SubtestType.MAZES: {
        "consecutive_failures": 2,
        "description": "Discontinue after 2 consecutive failures"
    },
}


def check_discontinue(
    subtest: SubtestType, 
    item_scores: list
) -> Tuple[bool, Optional[str]]:
    """
    Check if a subtest should be discontinued based on scoring pattern.
    
    Args:
        subtest: The subtest type
        item_scores: List of scores in order administered
        
    Returns:
        Tuple of (should_discontinue, reason)
    """
    rule = DISCONTINUE_RULES.get(subtest)
    if not rule:
        return False, None
    
    if rule.get("all_items"):
        return False, None
    
    if rule.get("timed"):
        return False, None
    
    consecutive_needed = rule.get("consecutive_failures", 0)
    if consecutive_needed <= 0:
        return False, None
    
    # Count consecutive zeros at end
    consecutive_zeros = 0
    for score in reversed(item_scores):
        if score == 0:
            consecutive_zeros += 1
        else:
            break
    
    if consecutive_zeros >= consecutive_needed:
        return True, rule["description"]
    
    return False, None
