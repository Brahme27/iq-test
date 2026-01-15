"""
MISIC Report Generator
======================
PDF report generation with visualizations for MISIC test results.
"""

import io
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from models import (
    PatientProfile, TestSession, SubtestType, 
    VERBAL_SUBTESTS, PERFORMANCE_SUBTESTS, IQClassification
)


class ReportGenerator:
    """
    Generate clinical reports for MISIC test results.
    """
    
    # Cultural context note from MISIC manual
    CULTURAL_DISPARITY_NOTE = """
    Note on Verbal-Performance Disparity:
    A significant difference between Verbal and Performance IQ scores (15+ points) 
    has been observed. When Verbal IQ exceeds Performance IQ, this may reflect:
    1. Strong language development and verbal learning environment
    2. Cultural emphasis on verbal/academic skills
    3. Less exposure to manipulative or constructional activities
    
    This pattern is common in Indian children and should be interpreted within 
    the cultural context. It does not necessarily indicate a specific deficit.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.fig_dpi = 100
    
    def create_tq_chart(
        self, 
        tqs: Dict[SubtestType, Optional[int]],
        save_path: Optional[str] = None
    ) -> bytes:
        """
        Create a bar chart visualization of Test Quotients.
        
        Args:
            tqs: Dictionary of subtest -> TQ
            save_path: Optional path to save the chart
            
        Returns:
            PNG image as bytes
        """
        # Prepare data
        verbal_labels = [st.value.replace('_', ' ').title() for st in VERBAL_SUBTESTS]
        performance_labels = [st.value.replace('_', ' ').title() for st in PERFORMANCE_SUBTESTS]
        
        verbal_scores = [tqs.get(st, 0) or 0 for st in VERBAL_SUBTESTS]
        performance_scores = [tqs.get(st, 0) or 0 for st in PERFORMANCE_SUBTESTS]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('MISIC Test Quotient Profile', fontsize=14, fontweight='bold')
        
        # Verbal chart
        bars1 = ax1.bar(verbal_labels, verbal_scores, color='#3498db', edgecolor='#2980b9')
        ax1.set_ylabel('Test Quotient (TQ)', fontsize=10)
        ax1.set_title('Verbal Scale', fontsize=12, fontweight='bold')
        ax1.set_ylim(50, 160)
        ax1.axhline(y=100, color='#27ae60', linestyle='--', linewidth=1, label='Average (100)')
        ax1.axhline(y=85, color='#f39c12', linestyle=':', linewidth=1, label='Low Average (85)')
        ax1.axhline(y=115, color='#f39c12', linestyle=':', linewidth=1, label='High Average (115)')
        ax1.tick_params(axis='x', rotation=45)
        ax1.legend(loc='upper right', fontsize=8)
        
        # Add value labels on bars
        for bar, score in zip(bars1, verbal_scores):
            if score > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                        str(score), ha='center', va='bottom', fontsize=9)
        
        # Performance chart
        bars2 = ax2.bar(performance_labels, performance_scores, color='#9b59b6', edgecolor='#8e44ad')
        ax2.set_ylabel('Test Quotient (TQ)', fontsize=10)
        ax2.set_title('Performance Scale', fontsize=12, fontweight='bold')
        ax2.set_ylim(50, 160)
        ax2.axhline(y=100, color='#27ae60', linestyle='--', linewidth=1, label='Average (100)')
        ax2.axhline(y=85, color='#f39c12', linestyle=':', linewidth=1, label='Low Average (85)')
        ax2.axhline(y=115, color='#f39c12', linestyle=':', linewidth=1, label='High Average (115)')
        ax2.tick_params(axis='x', rotation=45)
        ax2.legend(loc='upper right', fontsize=8)
        
        # Add value labels on bars
        for bar, score in zip(bars2, performance_scores):
            if score > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                        str(score), ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=self.fig_dpi, bbox_inches='tight')
        buf.seek(0)
        
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(buf.getvalue())
            buf.seek(0)
        
        plt.close(fig)
        return buf.getvalue()
    
    def create_iq_summary_chart(
        self,
        verbal_iq: float,
        performance_iq: float,
        full_scale_iq: float
    ) -> bytes:
        """
        Create a summary chart showing the three IQ scores.
        
        Args:
            verbal_iq: Verbal IQ score
            performance_iq: Performance IQ score
            full_scale_iq: Full Scale IQ score
            
        Returns:
            PNG image as bytes
        """
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = ['Verbal IQ', 'Performance IQ', 'Full Scale IQ']
        scores = [verbal_iq, performance_iq, full_scale_iq]
        colors = ['#3498db', '#9b59b6', '#2ecc71']
        
        bars = ax.barh(labels, scores, color=colors, edgecolor='#2c3e50', height=0.6)
        
        ax.set_xlim(50, 160)
        ax.set_xlabel('IQ Score', fontsize=11)
        ax.set_title('IQ Summary', fontsize=13, fontweight='bold')
        
        # Reference lines
        ax.axvline(x=100, color='#27ae60', linestyle='--', linewidth=2, label='Average')
        ax.axvline(x=85, color='#e74c3c', linestyle=':', linewidth=1)
        ax.axvline(x=115, color='#e74c3c', linestyle=':', linewidth=1)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            ax.text(score + 2, bar.get_y() + bar.get_height()/2,
                   f'{score:.1f}', ha='left', va='center', fontsize=11, fontweight='bold')
        
        # Add classification labels
        for i, (label, score) in enumerate(zip(labels, scores)):
            classification = IQClassification.classify(score)
            ax.text(55, i, classification, ha='left', va='center', 
                   fontsize=9, style='italic', color='#7f8c8d')
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=self.fig_dpi, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf.getvalue()
    
    def generate_pdf_report(
        self,
        session: TestSession,
        tqs: Dict[SubtestType, Optional[int]],
        verbal_iq: float,
        performance_iq: float,
        full_scale_iq: float,
        output_path: str
    ) -> str:
        """
        Generate a complete PDF report.
        
        Args:
            session: The test session data
            tqs: Dictionary of TQ scores
            verbal_iq: Calculated Verbal IQ
            performance_iq: Calculated Performance IQ
            full_scale_iq: Calculated Full Scale IQ
            output_path: Path to save the PDF
            
        Returns:
            Path to the generated PDF
        """
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Page 1: Header and Patient Info
        pdf.add_page()
        
        # Title
        pdf.set_font('Helvetica', 'B', 18)
        pdf.cell(0, 15, "MISIC Assessment Report", ln=True, align='C')
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 5, "Malin's Intelligence Scale for Indian Children", ln=True, align='C')
        pdf.ln(10)
        
        # Patient Information Box
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, 'Patient Information', ln=True)
        pdf.set_font('Helvetica', '', 10)
        
        patient = session.patient
        info_lines = [
            f"Patient ID: {patient.patient_id}",
            f"Name: {patient.name}",
            f"Date of Birth: {patient.date_of_birth.strftime('%d-%m-%Y')}",
            f"Test Date: {patient.test_date.strftime('%d-%m-%Y')}",
            f"Age at Testing: {patient.age_display}",
            f"Table Age Used: {patient.table_age} years",
        ]
        
        if patient.gender:
            info_lines.append(f"Gender: {patient.gender}")
        if patient.education:
            info_lines.append(f"Education: {patient.education}")
        if patient.examiner_name:
            info_lines.append(f"Examiner: {patient.examiner_name}")
        
        for line in info_lines:
            pdf.cell(0, 6, line, ln=True)
        
        pdf.ln(10)
        
        # IQ Summary Section
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, 'IQ Summary', ln=True)
        pdf.set_font('Helvetica', '', 10)
        
        pdf.cell(60, 7, 'Scale', border=1, align='C')
        pdf.cell(40, 7, 'IQ Score', border=1, align='C')
        pdf.cell(60, 7, 'Classification', border=1, align='C')
        pdf.ln()
        
        for scale, iq in [('Verbal IQ', verbal_iq), 
                          ('Performance IQ', performance_iq),
                          ('Full Scale IQ', full_scale_iq)]:
            pdf.cell(60, 7, scale, border=1)
            pdf.cell(40, 7, f'{iq:.1f}', border=1, align='C')
            pdf.cell(60, 7, IQClassification.classify(iq), border=1)
            pdf.ln()
        
        pdf.ln(5)
        
        # Disparity Analysis
        disparity = verbal_iq - performance_iq
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 7, f'Verbal-Performance Disparity: {disparity:+.1f} points', ln=True)
        
        if abs(disparity) >= 15:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.set_text_color(180, 0, 0)
            pdf.cell(0, 5, '* Significant disparity detected (15+ points)', ln=True)
            pdf.set_text_color(0, 0, 0)
        
        pdf.ln(10)
        
        # Subtest Scores Table
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, 'Subtest Scores', ln=True)
        
        # Verbal subtests
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 6, 'Verbal Scale:', ln=True)
        pdf.set_font('Helvetica', '', 9)
        
        pdf.cell(50, 6, 'Subtest', border=1, align='C')
        pdf.cell(30, 6, 'Raw Score', border=1, align='C')
        pdf.cell(30, 6, 'TQ', border=1, align='C')
        pdf.ln()
        
        for st in VERBAL_SUBTESTS:
            result = session.verbal_results.get(st)
            raw = result.raw_score if result else 0
            tq = tqs.get(st) or '--'
            
            pdf.cell(50, 6, st.value.replace('_', ' ').title(), border=1)
            pdf.cell(30, 6, str(raw), border=1, align='C')
            pdf.cell(30, 6, str(tq), border=1, align='C')
            pdf.ln()
        
        pdf.ln(5)
        
        # Performance subtests
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 6, 'Performance Scale:', ln=True)
        pdf.set_font('Helvetica', '', 9)
        
        pdf.cell(50, 6, 'Subtest', border=1, align='C')
        pdf.cell(30, 6, 'Raw Score', border=1, align='C')
        pdf.cell(30, 6, 'TQ', border=1, align='C')
        pdf.ln()
        
        for st in PERFORMANCE_SUBTESTS:
            result = session.performance_results.get(st)
            raw = result.raw_score if result else 0
            tq = tqs.get(st) or '--'
            
            pdf.cell(50, 6, st.value.replace('_', ' ').title(), border=1)
            pdf.cell(30, 6, str(raw), border=1, align='C')
            pdf.cell(30, 6, str(tq), border=1, align='C')
            pdf.ln()
        
        # Page 2: Charts and Notes
        pdf.add_page()
        
        # Generate and add TQ chart
        tq_chart = self.create_tq_chart(tqs)
        chart_path = Path(output_path).parent / "temp_tq_chart.png"
        with open(chart_path, 'wb') as f:
            f.write(tq_chart)
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, 'Test Quotient Profile', ln=True)
        pdf.image(str(chart_path), x=10, w=190)
        
        # Clean up temp file
        chart_path.unlink(missing_ok=True)
        
        pdf.ln(10)
        
        # Add cultural context note if significant disparity
        if disparity >= 15:  # Verbal > Performance by 15+
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, 'Clinical Notes', ln=True)
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 5, self.CULTURAL_DISPARITY_NOTE.strip())
        
        # Footer
        pdf.ln(15)
        pdf.set_font('Helvetica', 'I', 8)
        pdf.cell(0, 5, f'Report generated: {datetime.now().strftime("%d-%m-%Y %H:%M")}', ln=True)
        pdf.cell(0, 5, 'This report is confidential and intended for clinical use only.', ln=True)
        
        # Save PDF
        pdf.output(output_path)
        
        return output_path
    
    def generate_text_summary(
        self,
        session: TestSession,
        tqs: Dict[SubtestType, Optional[int]],
        verbal_iq: float,
        performance_iq: float,
        full_scale_iq: float
    ) -> str:
        """
        Generate a plain text summary for display.
        
        Returns:
            Formatted text summary
        """
        patient = session.patient
        disparity = verbal_iq - performance_iq
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║              MISIC ASSESSMENT SUMMARY                        ║
╠══════════════════════════════════════════════════════════════╣
║ Patient: {patient.name:<50} ║
║ ID: {patient.patient_id:<55} ║
║ Age: {patient.age_display:<54} ║
║ Test Date: {patient.test_date.strftime('%d-%m-%Y'):<48} ║
╠══════════════════════════════════════════════════════════════╣
║                    IQ SCORES                                  ║
╠══════════════════════════════════════════════════════════════╣
║ Verbal IQ:      {verbal_iq:>6.1f}  ({IQClassification.classify(verbal_iq):<20})    ║
║ Performance IQ: {performance_iq:>6.1f}  ({IQClassification.classify(performance_iq):<20})    ║
║ Full Scale IQ:  {full_scale_iq:>6.1f}  ({IQClassification.classify(full_scale_iq):<20})    ║
╠══════════════════════════════════════════════════════════════╣
║ V-P Disparity: {disparity:>+6.1f} points                               ║
"""
        
        if abs(disparity) >= 15:
            summary += "║ ⚠ SIGNIFICANT DISPARITY DETECTED                            ║\n"
        
        summary += "╚══════════════════════════════════════════════════════════════╝"
        
        return summary
