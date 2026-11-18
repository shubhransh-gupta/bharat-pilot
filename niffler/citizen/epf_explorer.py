"""
Employees' Provident Fund (EPF / EPFO) explorer, passbook analyzer, and retirement corpus projector.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import datetime


@dataclass
class EPFBalanceSummary:
    uan: str
    member_id: str
    establishment_name: str
    employee_share_balance_inr: int
    employer_share_balance_inr: int
    pension_scheme_balance_inr: int
    total_epf_balance_inr: int
    current_interest_rate_pct: float
    last_updated_financial_year: str


@dataclass
class EPFWithdrawalEligibility:
    form_31_medical: Dict[str, Any]
    form_31_housing: Dict[str, Any]
    form_31_marriage: Dict[str, Any]
    form_19_full_settlement: Dict[str, Any]
    form_10c_pension: Dict[str, Any]


@dataclass
class RetirementProjection:
    current_age: int
    retirement_age: int
    years_to_grow: int
    monthly_contribution: int
    projected_corpus_at_58_inr: int
    total_interest_earned_inr: int


class EPFExplorer:
    """Analyzes EPF passbook, explains government withdrawal rules, and models compounding growth."""

    CURRENT_EPF_RATE = 8.25  # Govt approved rate for FY 2024-25 / 2025-26

    def parse_or_simulate_account(
        self,
        uan: str = "101234567890",
        monthly_basic_da: int = 50000,
        years_of_service: float = 4.5,
        starting_epf_balance: int = 340000,
    ) -> EPFBalanceSummary:
        """Calculates current EPF breakdown based on salary and tenure."""
        # 12% employee share
        emp_contrib = int(monthly_basic_da * 0.12)
        # 3.67% employer share to EPF
        empr_contrib = int(monthly_basic_da * 0.0367)
        # 8.33% to EPS (capped at 15,000 wage ceiling in standard rules: 1250/mo, or full if un-capped)
        eps_contrib = min(1250, int(monthly_basic_da * 0.0833))

        total_emp_share = starting_epf_balance + int(emp_contrib * 12 * 1.5)
        total_empr_share = int(total_emp_share * (0.0367 / 0.12))
        total_eps = int(eps_contrib * years_of_service * 12)

        return EPFBalanceSummary(
            uan=uan,
            member_id=f"DLCPM{uan[-7:]}000",
            establishment_name="Technology Solutions India Pvt Ltd",
            employee_share_balance_inr=total_emp_share,
            employer_share_balance_inr=total_empr_share,
            pension_scheme_balance_inr=total_eps,
            total_epf_balance_inr=total_emp_share + total_empr_share,
            current_interest_rate_pct=self.CURRENT_EPF_RATE,
            last_updated_financial_year="2024-25",
        )

    def check_withdrawal_eligibility(
        self,
        years_of_service: float,
        employee_balance: int,
        is_employed: bool = True
    ) -> EPFWithdrawalEligibility:
        """Determines eligibility under Form 31, Form 19, and Form 10C."""
        # Medical: No minimum service required
        medical = {
            "eligible": True,
            "max_withdrawal": employee_balance,
            "rule": "Eligible for self/family medical emergencies. No minimum service duration required."
        }

        # Housing: Requires 5 years service
        housing = {
            "eligible": years_of_service >= 5.0,
            "max_withdrawal": int(employee_balance * 0.90) if years_of_service >= 5.0 else 0,
            "rule": "Requires min 5 years of continuous service. Up to 90% of total balance for home purchase/construction."
        }

        # Marriage: Requires 7 years service
        marriage = {
            "eligible": years_of_service >= 7.0,
            "max_withdrawal": int(employee_balance * 0.50) if years_of_service >= 7.0 else 0,
            "rule": "Requires min 7 years of service. Up to 50% of employee contribution for self/children/sibling marriage."
        }

        # Form 19: Full withdrawal
        form_19 = {
            "eligible": not is_employed or years_of_service >= 58,
            "rule": "Full PF settlement can be withdrawn after 2 months of non-employment or upon reaching retirement age (58)."
        }

        # Form 10C: Pension
        form_10c = {
            "eligible": years_of_service < 9.5,
            "rule": "If service is less than 9.5 years, lump-sum pension withdrawal via Form 10C is permitted. After 10 years, Scheme Certificate is issued for regular pension at 58."
        }

        return EPFWithdrawalEligibility(
            form_31_medical=medical,
            form_31_housing=housing,
            form_31_marriage=marriage,
            form_19_full_settlement=form_19,
            form_10c_pension=form_10c,
        )

    def project_retirement_corpus(
        self,
        current_age: int = 28,
        current_balance: int = 450000,
        monthly_basic_da: int = 50000,
        annual_increment_pct: float = 7.0,
        retirement_age: int = 58,
    ) -> RetirementProjection:
        """Projects compounding wealth at retirement age 58 with 8.25% interest rate."""
        years = max(1, retirement_age - current_age)
        balance = float(current_balance)
        wage = float(monthly_basic_da)
        total_contributed = 0.0

        r = self.CURRENT_EPF_RATE / 100.0

        for year in range(years):
            annual_emp_contrib = wage * 0.12 * 12
            annual_empr_contrib = wage * 0.0367 * 12
            total_annual_addition = annual_emp_contrib + annual_empr_contrib

            balance = (balance + total_annual_addition) * (1.0 + r)
            total_contributed += total_annual_addition
            wage *= (1.0 + (annual_increment_pct / 100.0))

        projected = int(balance)
        interest_earned = int(projected - current_balance - total_contributed)

        return RetirementProjection(
            current_age=current_age,
            retirement_age=retirement_age,
            years_to_grow=years,
            monthly_contribution=int(monthly_basic_da * 0.1567),
            projected_corpus_at_58_inr=projected,
            total_interest_earned_inr=interest_earned,
        )
