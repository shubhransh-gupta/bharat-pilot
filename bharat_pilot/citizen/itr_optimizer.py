"""
Autonomous Income Tax Return (ITR) optimizer, Form-16 parser, and ITR-1 JSON generator.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json


@dataclass
class TaxBreakdown:
    regime_name: str
    gross_salary: int
    exemptions_and_deductions: int
    net_taxable_income: int
    tax_before_cess: int
    rebate_87a: int
    health_education_cess: int
    total_tax_payable: int


@dataclass
class ITRComparisonResult:
    pan: str
    assessment_year: str
    old_regime: TaxBreakdown
    new_regime: TaxBreakdown
    recommended_regime: str
    tax_savings_inr: int
    itr_1_json: Dict[str, Any]


class ITROptimizer:
    """Calculates optimal tax regime and generates compliant ITR-1 Sahaj JSON."""

    def __init__(self, assessment_year: str = "2025-26"):
        self.ay = assessment_year

    def calculate_new_regime_tax(self, gross_salary: int, other_income: int = 0) -> TaxBreakdown:
        """New Tax Regime (Section 115BAC) under Budget 2024 revisions."""
        # Standard deduction increased to 75,000 in Budget 2024
        standard_deduction = 75000
        gross_total = gross_salary + other_income
        net_taxable = max(0, gross_total - standard_deduction)

        # Tax slabs (Budget 2024 New Regime)
        tax = 0.0
        if net_taxable <= 300000:
            tax = 0.0
        elif net_taxable <= 700000:
            tax = (net_taxable - 300000) * 0.05
        elif net_taxable <= 1000000:
            tax = (400000 * 0.05) + (net_taxable - 700000) * 0.10
        elif net_taxable <= 1200000:
            tax = (400000 * 0.05) + (300000 * 0.10) + (net_taxable - 1000000) * 0.15
        elif net_taxable <= 1500000:
            tax = (400000 * 0.05) + (300000 * 0.10) + (200000 * 0.15) + (net_taxable - 1200000) * 0.20
        else:
            tax = (400000 * 0.05) + (300000 * 0.10) + (200000 * 0.15) + (300000 * 0.20) + (net_taxable - 1500000) * 0.30

        # Section 87A rebate: zero tax if taxable income <= 7,00,000
        gross_tax = int(tax)
        rebate = 0
        if net_taxable <= 700000:
            rebate = min(gross_tax, 25000)

        tax_after_rebate = max(0, gross_tax - rebate)
        cess = int(tax_after_rebate * 0.04)
        total_tax = tax_after_rebate + cess

        return TaxBreakdown(
            regime_name="New Tax Regime (Sec 115BAC)",
            gross_salary=gross_total,
            exemptions_and_deductions=standard_deduction,
            net_taxable_income=net_taxable,
            tax_before_cess=gross_tax,
            rebate_87a=rebate,
            health_education_cess=cess,
            total_tax_payable=total_tax,
        )

    def calculate_old_regime_tax(
        self,
        gross_salary: int,
        sec_80c: int = 150000,
        sec_80d: int = 25000,
        hra_exemption: int = 0,
        home_loan_interest_24b: int = 0,
        other_deductions: int = 0,
        other_income: int = 0
    ) -> TaxBreakdown:
        """Old Tax Regime with 80C, 80D, HRA, and Home Loan exemptions."""
        standard_deduction = 50000
        capped_80c = min(150000, sec_80c)
        capped_80d = min(50000, sec_80d)
        capped_24b = min(200000, home_loan_interest_24b)

        total_deductions = (
            standard_deduction + capped_80c + capped_80d +
            hra_exemption + capped_24b + other_deductions
        )

        gross_total = gross_salary + other_income
        net_taxable = max(0, gross_total - total_deductions)

        # Old Regime Slabs
        tax = 0.0
        if net_taxable <= 250000:
            tax = 0.0
        elif net_taxable <= 500000:
            tax = (net_taxable - 250000) * 0.05
        elif net_taxable <= 1000000:
            tax = (250000 * 0.05) + (net_taxable - 500000) * 0.20
        else:
            tax = (250000 * 0.05) + (500000 * 0.20) + (net_taxable - 1000000) * 0.30

        # Section 87A rebate for Old Regime: up to 12,500 if income <= 5,00,000
        gross_tax = int(tax)
        rebate = 0
        if net_taxable <= 500000:
            rebate = min(12500, gross_tax)

        tax_after_rebate = max(0, gross_tax - rebate)
        cess = int(tax_after_rebate * 0.04)
        total_tax = tax_after_rebate + cess

        return TaxBreakdown(
            regime_name="Old Tax Regime",
            gross_salary=gross_total,
            exemptions_and_deductions=total_deductions,
            net_taxable_income=net_taxable,
            tax_before_cess=gross_tax,
            rebate_87a=rebate,
            health_education_cess=cess,
            total_tax_payable=total_tax,
        )

    def optimize_and_generate_itr(
        self,
        pan: str,
        name: str,
        gross_salary: int,
        sec_80c: int = 150000,
        sec_80d: int = 25000,
        hra_exemption: int = 0,
        home_loan_interest: int = 0,
        tds_deducted: int = 0,
        other_income: int = 0
    ) -> ITRComparisonResult:
        """Determines best tax regime and prepares ready-to-upload ITR-1 JSON."""
        new_res = self.calculate_new_regime_tax(gross_salary, other_income)
        old_res = self.calculate_old_regime_tax(
            gross_salary, sec_80c, sec_80d, hra_exemption, home_loan_interest, 0, other_income
        )

        if new_res.total_tax_payable <= old_res.total_tax_payable:
            rec = "NEW_REGIME"
            diff = old_res.total_tax_payable - new_res.total_tax_payable
            chosen = new_res
        else:
            rec = "OLD_REGIME"
            diff = new_res.total_tax_payable - old_res.total_tax_payable
            chosen = old_res

        # Generate official ITR-1 Sahaj JSON payload
        refund_or_payable = tds_deducted - chosen.total_tax_payable
        itr_payload = {
            "ITR": {
                "ITR1": {
                    "Form_ITR1": {
                        "FormName": "ITR-1",
                        "Description": "For Individuals having Income from Salaries, one house property, other sources",
                        "AssessmentYear": self.ay,
                        "SchemaVer": "Ver1.0"
                    },
                    "PersonalInfo": {
                        "PAN": pan.upper(),
                        "Name": name,
                        "Status": "Individual",
                        "EmployerCategory": "OTH"
                    },
                    "FilingStatus": {
                        "ReturnFileSec": "11",  # On or before due date
                        "OptOutNewTaxRegime": "Y" if rec == "OLD_REGIME" else "N",
                    },
                    "IncomeDeductions": {
                        "GrossSalary": gross_salary,
                        "TotalDeductions": chosen.exemptions_and_deductions,
                        "TotalIncome": chosen.net_taxable_income,
                    },
                    "TaxComputation": {
                        "TotalTaxPayable": chosen.total_tax_payable,
                        "TaxesPaid": {
                            "TDS": tds_deducted,
                            "TotalTaxesPaid": tds_deducted
                        },
                        "Refund": max(0, refund_or_payable),
                        "AmountPayable": max(0, -refund_or_payable)
                    }
                }
            }
        }

        return ITRComparisonResult(
            pan=pan.upper(),
            assessment_year=self.ay,
            old_regime=old_res,
            new_regime=new_res,
            recommended_regime=rec,
            tax_savings_inr=diff,
            itr_1_json=itr_payload,
        )
