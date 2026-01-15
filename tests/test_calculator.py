"""
Unit Tests for MISIC Calculator
===============================
Tests for age calculation, TQ lookup, and IQ scoring.
"""

import pytest
from datetime import date
from models import SubtestType, PatientProfile, TestSession, SubtestResult
from calculator import TQLookup, AgeCalculator, IQCalculator, check_discontinue


class TestAgeCalculator:
    """Tests for age calculation functionality."""
    
    def test_calculate_age_simple(self):
        """Test basic age calculation."""
        dob = date(2015, 6, 15)
        test_date = date(2024, 6, 15)
        
        months = AgeCalculator.calculate_age_in_months(dob, test_date)
        assert months == 108  # 9 years * 12 months
    
    def test_calculate_age_partial_year(self):
        """Test age calculation with partial year."""
        dob = date(2015, 6, 15)
        test_date = date(2024, 3, 15)
        
        months = AgeCalculator.calculate_age_in_months(dob, test_date)
        assert months == 105  # 8 years 9 months
    
    def test_table_age_rounds_up(self):
        """Test that table age rounds up when 6+ months."""
        dob = date(2015, 1, 1)
        test_date = date(2024, 7, 1)  # 9 years 6 months
        
        table_age = AgeCalculator.get_table_age(dob, test_date)
        assert table_age == 10  # Rounds up
    
    def test_table_age_rounds_down(self):
        """Test that table age rounds down when < 6 months."""
        dob = date(2015, 1, 1)
        test_date = date(2024, 5, 1)  # 9 years 4 months
        
        table_age = AgeCalculator.get_table_age(dob, test_date)
        assert table_age == 9  # Rounds down
    
    def test_table_age_clamps_minimum(self):
        """Test that table age clamps to minimum 6."""
        dob = date(2020, 1, 1)
        test_date = date(2024, 1, 1)  # 4 years
        
        table_age = AgeCalculator.get_table_age(dob, test_date)
        assert table_age == 6  # Clamped to 6
    
    def test_table_age_clamps_maximum(self):
        """Test that table age clamps to maximum 15."""
        dob = date(2005, 1, 1)
        test_date = date(2024, 1, 1)  # 19 years
        
        table_age = AgeCalculator.get_table_age(dob, test_date)
        assert table_age == 15  # Clamped to 15
    
    def test_valid_age_range(self):
        """Test is_valid_age for valid ages."""
        dob = date(2015, 1, 1)
        test_date = date(2024, 1, 1)  # 9 years
        
        assert AgeCalculator.is_valid_age(dob, test_date) is True
    
    def test_invalid_age_too_young(self):
        """Test is_valid_age for too young."""
        dob = date(2020, 1, 1)
        test_date = date(2024, 1, 1)  # 4 years
        
        assert AgeCalculator.is_valid_age(dob, test_date) is False


class TestTQLookup:
    """Tests for TQ lookup functionality."""
    
    @pytest.fixture
    def tq_lookup(self):
        """Create TQ lookup instance."""
        return TQLookup("tables.json")
    
    def test_lookup_direct_score(self, tq_lookup):
        """Test lookup for a direct score key."""
        # 6 years, Information, raw score 7 -> TQ 100
        tq = tq_lookup.get_tq(6, SubtestType.INFORMATION, 7)
        assert tq == 100
    
    def test_lookup_range_score(self, tq_lookup):
        """Test lookup for a range score key."""
        # 6 years, Coding, raw score 5 (in range_5_6) -> TQ 65
        tq = tq_lookup.get_tq(6, SubtestType.CODING, 5)
        assert tq == 65
    
    def test_lookup_null_value(self, tq_lookup):
        """Test lookup returns None for null values."""
        # 6 years, Picture Completion, raw score 14 is null
        tq = tq_lookup.get_tq(6, SubtestType.PICTURE_COMPLETION, 14)
        assert tq is None
    
    def test_lookup_clamps_age(self, tq_lookup):
        """Test that age is clamped to valid range."""
        # Age 5 should be clamped to 6
        tq = tq_lookup.get_tq(5, SubtestType.INFORMATION, 7)
        assert tq == 100  # Same as age 6
    
    def test_available_ages(self, tq_lookup):
        """Test getting available ages."""
        ages = tq_lookup.get_available_ages()
        assert ages == [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


class TestIQCalculator:
    """Tests for IQ calculation functionality."""
    
    @pytest.fixture
    def iq_calculator(self):
        """Create IQ calculator instance."""
        tq_lookup = TQLookup("tables.json")
        return IQCalculator(tq_lookup)
    
    def test_verbal_iq_calculation(self, iq_calculator):
        """Test Verbal IQ calculation."""
        tqs = {
            SubtestType.INFORMATION: 100,
            SubtestType.COMPREHENSION: 110,
            SubtestType.ARITHMETIC: 90,
            SubtestType.SIMILARITIES: 100,
            SubtestType.VOCABULARY: 100,
            SubtestType.DIGIT_SPAN: 100,
        }
        
        verbal_iq = iq_calculator.calculate_verbal_iq(tqs)
        assert verbal_iq == 100  # Average of all verbal TQs
    
    def test_performance_iq_calculation(self, iq_calculator):
        """Test Performance IQ calculation."""
        tqs = {
            SubtestType.PICTURE_COMPLETION: 100,
            SubtestType.BLOCK_DESIGN: 100,
            SubtestType.OBJECT_ASSEMBLY: 100,
            SubtestType.CODING: 100,
            SubtestType.MAZES: 100,
        }
        
        performance_iq = iq_calculator.calculate_performance_iq(tqs)
        assert performance_iq == 100
    
    def test_full_scale_iq_calculation(self, iq_calculator):
        """Test Full Scale IQ calculation."""
        tqs = {
            SubtestType.INFORMATION: 100,
            SubtestType.COMPREHENSION: 100,
            SubtestType.ARITHMETIC: 100,
            SubtestType.SIMILARITIES: 100,
            SubtestType.VOCABULARY: 100,
            SubtestType.DIGIT_SPAN: 100,
            SubtestType.PICTURE_COMPLETION: 100,
            SubtestType.BLOCK_DESIGN: 100,
            SubtestType.OBJECT_ASSEMBLY: 100,
            SubtestType.CODING: 100,
            SubtestType.MAZES: 100,
        }
        
        full_iq = iq_calculator.calculate_full_scale_iq(tqs)
        assert full_iq == 100
    
    def test_disparity_calculation(self):
        """Test disparity calculation."""
        disparity = IQCalculator.calculate_disparity(115, 100)
        assert disparity == 15
    
    def test_significant_disparity(self):
        """Test significant disparity detection."""
        assert IQCalculator.is_significant_disparity(15) is True
        assert IQCalculator.is_significant_disparity(14) is False
        assert IQCalculator.is_significant_disparity(-15) is True
    
    def test_iq_classification(self):
        """Test IQ classification."""
        assert IQCalculator.classify_iq(135) == "Very Superior"
        assert IQCalculator.classify_iq(125) == "Superior"
        assert IQCalculator.classify_iq(115) == "High Average"
        assert IQCalculator.classify_iq(100) == "Average"
        assert IQCalculator.classify_iq(85) == "Low Average"
        assert IQCalculator.classify_iq(75) == "Borderline"
        assert IQCalculator.classify_iq(65) == "Extremely Low"


class TestDiscontinuationRules:
    """Tests for discontinuation rule checking."""
    
    def test_discontinue_after_5_zeros(self):
        """Test discontinuation after 5 consecutive zeros."""
        scores = [1, 1, 0, 0, 0, 0, 0]
        should_stop, reason = check_discontinue(SubtestType.INFORMATION, scores)
        assert should_stop is True
    
    def test_no_discontinue_with_4_zeros(self):
        """Test no discontinuation with only 4 consecutive zeros."""
        scores = [1, 1, 0, 0, 0, 0]
        should_stop, reason = check_discontinue(SubtestType.INFORMATION, scores)
        assert should_stop is False
    
    def test_discontinue_breaks_on_pass(self):
        """Test that a pass resets the discontinuation counter."""
        scores = [0, 0, 0, 0, 1, 0, 0]
        should_stop, reason = check_discontinue(SubtestType.INFORMATION, scores)
        assert should_stop is False


class TestPatientProfile:
    """Tests for PatientProfile model."""
    
    def test_age_properties(self):
        """Test age calculation properties."""
        patient = PatientProfile(
            patient_id="TEST001",
            name="Test Patient",
            date_of_birth=date(2015, 6, 15),
            test_date=date(2024, 6, 15)
        )
        
        assert patient.age_years == 9
        assert patient.age_remaining_months == 0
        assert patient.table_age == 9
        assert patient.is_valid_age() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
