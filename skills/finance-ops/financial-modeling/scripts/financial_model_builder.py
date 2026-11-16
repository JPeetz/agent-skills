#!/usr/bin/env python3
"""Build a driver-based three-statement financial model from a JSON spec.

Stdlib only. No network. Every output figure is derived from a named driver in
the input; the script never invents a value for a missing assumption, and it
exits non-zero on malformed or contradictory data.

What it produces, per month, for 1-60 months:

    * P&L            revenue -> COGS -> gross profit -> OPEX -> EBITDA -> EBIT
                     -> interest -> tax (with NOL carry-forward) -> net income
    * Cash flow      indirect method, CFO/CFI/CFF, ending cash
    * Balance sheet  cash, AR, prepaid, net PP&E, AP, deferred revenue, debt,
                     paid-in capital, retained earnings
    * Metrics        ARR, MRR growth, NRR, GRR, gross margin, EBITDA margin,
                     Rule of 40, burn, burn multiple, magic number, runway,
                     quick ratio, CAC payback and LTV/CAC when an ACV is given

Plus checks that must pass: the balance sheet balances every period (to the
cent), ending cash equals the cash-flow roll-forward, and ARR equals MRR x 12.

Usage:
    python3 financial_model_builder.py --input model.json --format markdown
    python3 financial_model_builder.py model.json --format json --pretty
    cat model.json | python3 financial_model_builder.py
    python3 financial_model_builder.py --self-test

Input schema (all money in one currency, all rates as decimals not percents):

    {
      "company": "Acme",
      "currency": "USD",
      "start_month": "2026-01",
      "months": 36,
      "revenue": {
        "starting_mrr": 180000,          # required, > 0
        "new_mrr_start": 22000,          # new-business MRR added in month 1
        "new_mrr_growth": 0.03,          # monthly growth of new-business adds
        "churn_rate": 0.014,             # monthly gross revenue churn
        "expansion_rate": 0.011,         # monthly expansion, applied to base
        "contraction_rate": 0.004,       # monthly downgrade, applied to base
        "one_time_revenue": 0,           # non-recurring revenue per month
        "seasonality": [1.0, ...],       # optional 12 multipliers, Jan..Dec
        "acv": 9000                      # optional, enables logo-level metrics
      },
      "cogs": {
        "hosting_pct": 0.09,             # % of revenue
        "support_pct": 0.05,             # % of revenue
        "payment_pct": 0.028,            # % of revenue (processor fees)
        "fixed_monthly": 4000            # fixed COGS floor
      },
      "headcount": {
        "departments": [
          {"name": "engineering", "start": 9, "cost_per_head": 16500,
           "additions": {"6": 2}, "bucket": "opex",
           "non_headcount_monthly": 0, "non_headcount_pct_revenue": 0.0,
           "variable_pct_revenue": 0.0}
        ]
      },
      "capex": {"pct_revenue": 0.02, "fixed_monthly": 0,
                "useful_life_months": 36},
      "working_capital": {"dso_days": 38, "dpo_days": 25,
                          "deferred_revenue_pct": 0.14,
                          "prepaid_pct_opex": 0.0,
                          "opening_ar": 0, "opening_ap": 0,
                          "opening_deferred_revenue": 0, "opening_ppe": 0},
      "cash": {"starting_cash": 3400000, "debt": 0,
               "debt_repayment_monthly": 0, "interest_rate_annual": 0.0,
               "tax_rate": 0.21, "year1_nol": 0,
               "equity_raised": {"month": 0, "amount": 0}},
      "scenario": "base"
    }

Design notes that matter for correctness:

    * Cash is derived from the cash flow statement, never plugged on the
      balance sheet. Opening equity is the only plug and it is computed once,
      from the opening balance sheet, so that period 0 balances by definition.
    * Tax is computed with a loss carry-forward (NOL), so a loss-making year
      does not produce a negative tax benefit that never arrives.
    * Depreciation is straight-line per capex vintage, not a single rate on
      closing PP&E, so the balance sheet ties while capex ramps.
    * Expansion, contraction and churn apply to beginning-of-period MRR only.
      Applying them to the same month's new business double-counts.
"""
from __future__ import annotations

import argparse
import calendar
import json
import math
import sys
from typing import Any

MONTHS_MIN = 1
MONTHS_MAX = 60
TOLERANCE = 0.01          # cents; balance residual must be below this
DEFAULT_MONTHS = 36


class InputError(Exception):
    """Raised on malformed, missing or contradictory input."""


# ---------------------------------------------------------------------------
# input helpers
# ---------------------------------------------------------------------------
def num(value, label, *, required=False, default=None, minimum=None,
        maximum=None) -> Any:
    """Coerce to float, rejecting booleans, strings, NaN and inf."""
    if value is None:
        if required:
            raise InputError("missing required field: {}".format(label))
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError("{} must be a number, got {!r}".format(label, value))
    value = float(value)
    if math.isnan(value) or math.isinf(value):
        raise InputError("{} must be finite, got {!r}".format(label, value))
    if minimum is not None and value < minimum:
        raise InputError("{} must be >= {}, got {}".format(label, minimum, value))
    if maximum is not None and value > maximum:
        raise InputError("{} must be <= {}, got {}".format(label, maximum, value))
    return value


def frac(value, label, *, required=False, default=None) -> Any:
    """A rate or share: 0 <= x <= 1."""
    return num(value, label, required=required, default=default,
               minimum=0.0, maximum=1.0)


def count(value, label, *, required=False, default=None) -> Any:
    """A non-negative whole number."""
    v = num(value, label, required=required, default=default, minimum=0.0)
    if v is not None and abs(v - round(v)) > 1e-9:
        raise InputError("{} must be a whole number, got {}".format(label, v))
    return None if v is None else int(round(v))


def mapping(value, label):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise InputError("{} must be an object, got {!r}".format(label, value))
    return value


def start_month(value):
    """Validate 'YYYY-MM' and return (year, month)."""
    if value is None:
        return (2026, 1)
    if not isinstance(value, str):
        raise InputError("start_month must be a string 'YYYY-MM'")
    try:
        year_s, month_s = value.split("-")
        year, month = int(year_s), int(month_s)
    except (ValueError, AttributeError):
        raise InputError("start_month must look like 'YYYY-MM', got {!r}"
                         .format(value))
    if not 1 <= month <= 12:
        raise InputError("start_month month must be 1-12, got {}".format(month))
    if not 1990 <= year <= 2100:
        raise InputError("start_month year out of range: {}".format(year))
    return (year, month)


def month_label(year, month, offset):
    """Label for model month `offset` (0-based) starting at (year, month)."""
    total = (year * 12 + (month - 1)) + offset
    return "{:04d}-{:02d}".format(total // 12, total % 12 + 1)


# ---------------------------------------------------------------------------
# normalisation / validation
# ---------------------------------------------------------------------------
def normalise(data: Any) -> dict:
    """Validate the raw JSON and return a fully-defaulted model spec."""
    if not isinstance(data, dict):
        raise InputError("top-level input must be a JSON object")

    months = count(data.get("months"), "months", default=DEFAULT_MONTHS)
    if not MONTHS_MIN <= months <= MONTHS_MAX:
        raise InputError("months must be between {} and {}, got {}"
                         .format(MONTHS_MIN, MONTHS_MAX, months))

    rev = mapping(data.get("revenue"), "revenue")
    starting_mrr = num(rev.get("starting_mrr"), "revenue.starting_mrr",
                       required=True, minimum=0.0)

    new_mrr_start = num(rev.get("new_mrr_start"), "revenue.new_mrr_start",
                        default=0.0, minimum=0.0)
    new_mrr_growth = num(rev.get("new_mrr_growth"), "revenue.new_mrr_growth",
                         default=0.0, minimum=-0.95, maximum=2.0)
    churn = frac(rev.get("churn_rate"), "revenue.churn_rate", default=0.0)
    expansion = frac(rev.get("expansion_rate"), "revenue.expansion_rate",
                     default=0.0)
    contraction = frac(rev.get("contraction_rate"), "revenue.contraction_rate",
                       default=0.0)
    if churn + contraction >= 1.0:
        raise InputError("revenue.churn_rate + revenue.contraction_rate must be "
                         "below 1.0 (currently {:.3f})".format(churn + contraction))
    one_time = num(rev.get("one_time_revenue"), "revenue.one_time_revenue",
                   default=0.0, minimum=0.0)
    acv = num(rev.get("acv"), "revenue.acv", default=None, minimum=0.0)
    if acv is not None and acv == 0:
        raise InputError("revenue.acv must be > 0 when supplied")

    season = rev.get("seasonality")
    if season is not None:
        if not isinstance(season, list) or len(season) != 12:
            raise InputError("revenue.seasonality must be a list of 12 numbers")
        season = [num(v, "revenue.seasonality[{}]".format(i), minimum=0.0,
                      maximum=5.0) for i, v in enumerate(season)]
        if not any(season):
            raise InputError("revenue.seasonality must not be all zeros")

    cogs = mapping(data.get("cogs"), "cogs")
    cogs_spec = {
        "hosting_pct": frac(cogs.get("hosting_pct"), "cogs.hosting_pct", default=0.0),
        "support_pct": frac(cogs.get("support_pct"), "cogs.support_pct", default=0.0),
        "payment_pct": frac(cogs.get("payment_pct"), "cogs.payment_pct", default=0.0),
        "fixed_monthly": num(cogs.get("fixed_monthly"), "cogs.fixed_monthly",
                             default=0.0, minimum=0.0),
    }
    if sum(cogs_spec[k] for k in ("hosting_pct", "support_pct",
                                  "payment_pct")) >= 1.0:
        raise InputError("cogs percentage drivers sum to >= 100% of revenue; "
                         "gross margin would be zero or negative")

    hc = mapping(data.get("headcount"), "headcount")
    raw_depts = hc.get("departments") or []
    if not isinstance(raw_depts, list):
        raise InputError("headcount.departments must be a list")
    departments = []
    for i, d in enumerate(raw_depts):
        label = "headcount.departments[{}]".format(i)
        if not isinstance(d, dict):
            raise InputError("{} must be an object".format(label))
        name = d.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InputError("{}.name is required and must be a string".format(label))
        bucket = d.get("bucket", "opex")
        if bucket not in ("opex", "cogs"):
            raise InputError("{}.bucket must be 'opex' or 'cogs', got {!r}"
                             .format(label, bucket))
        additions = mapping(d.get("additions"), label + ".additions")
        clean_additions = {}
        for k, v in additions.items():
            try:
                m = int(k)
            except (TypeError, ValueError):
                raise InputError("{}.additions keys must be model month numbers "
                                 "(1-based), got {!r}".format(label, k))
            if not 1 <= m <= months:
                raise InputError("{}.additions month {} is outside the model "
                                 "horizon (1-{})".format(label, m, months))
            clean_additions[m] = count(v, "{}.additions[{}]".format(label, k))
        departments.append({
            "name": name.strip(),
            "start": count(d.get("start"), label + ".start", default=0),
            "cost_per_head": num(d.get("cost_per_head"), label + ".cost_per_head",
                                 default=0.0, minimum=0.0),
            "additions": clean_additions,
            "bucket": bucket,
            "non_headcount_monthly": num(d.get("non_headcount_monthly"),
                                         label + ".non_headcount_monthly",
                                         default=0.0, minimum=0.0),
            "non_headcount_pct_revenue": frac(d.get("non_headcount_pct_revenue"),
                                              label + ".non_headcount_pct_revenue",
                                              default=0.0),
            "variable_pct_revenue": frac(d.get("variable_pct_revenue"),
                                         label + ".variable_pct_revenue",
                                         default=0.0),
        })

    capex = mapping(data.get("capex"), "capex")
    capex_spec = {
        "pct_revenue": frac(capex.get("pct_revenue"), "capex.pct_revenue", default=0.0),
        "fixed_monthly": num(capex.get("fixed_monthly"), "capex.fixed_monthly",
                             default=0.0, minimum=0.0),
        "useful_life_months": count(capex.get("useful_life_months"),
                                    "capex.useful_life_months", default=36),
    }
    if capex_spec["useful_life_months"] < 1:
        raise InputError("capex.useful_life_months must be >= 1")

    wc = mapping(data.get("working_capital"), "working_capital")
    wc_spec = {
        "dso_days": num(wc.get("dso_days"), "working_capital.dso_days",
                        default=0.0, minimum=0.0, maximum=365.0),
        "dpo_days": num(wc.get("dpo_days"), "working_capital.dpo_days",
                        default=0.0, minimum=0.0, maximum=365.0),
        "deferred_revenue_pct": frac(wc.get("deferred_revenue_pct"),
                                     "working_capital.deferred_revenue_pct",
                                     default=0.0),
        "prepaid_pct_opex": frac(wc.get("prepaid_pct_opex"),
                                 "working_capital.prepaid_pct_opex", default=0.0),
        "opening_ar": num(wc.get("opening_ar"), "working_capital.opening_ar",
                          default=0.0, minimum=0.0),
        "opening_ap": num(wc.get("opening_ap"), "working_capital.opening_ap",
                          default=0.0, minimum=0.0),
        "opening_deferred_revenue": num(wc.get("opening_deferred_revenue"),
                                        "working_capital.opening_deferred_revenue",
                                        default=0.0, minimum=0.0),
        "opening_ppe": num(wc.get("opening_ppe"), "working_capital.opening_ppe",
                           default=0.0, minimum=0.0),
    }

    cash_in = mapping(data.get("cash"), "cash")
    equity_raised = mapping(cash_in.get("equity_raised"), "cash.equity_raised")
    eq_amount = num(equity_raised.get("amount"), "cash.equity_raised.amount",
                    default=0.0, minimum=0.0)
    eq_month = count(equity_raised.get("month"), "cash.equity_raised.month", default=1)
    if eq_amount and not 1 <= eq_month <= months:
        raise InputError("cash.equity_raised.month must be within 1-{}".format(months))
    cash_spec = {
        "starting_cash": num(cash_in.get("starting_cash"), "cash.starting_cash",
                             required=True, minimum=0.0),
        "debt": num(cash_in.get("debt"), "cash.debt", default=0.0, minimum=0.0),
        "debt_repayment_monthly": num(cash_in.get("debt_repayment_monthly"),
                                      "cash.debt_repayment_monthly", default=0.0,
                                      minimum=0.0),
        "interest_rate_annual": frac(cash_in.get("interest_rate_annual"),
                                     "cash.interest_rate_annual", default=0.0),
        "tax_rate": frac(cash_in.get("tax_rate"), "cash.tax_rate", default=0.0),
        "year1_nol": num(cash_in.get("year1_nol"), "cash.year1_nol",
                         default=0.0, minimum=0.0),  # opening loss balance, positive
        "equity_raised": {"month": eq_month if eq_amount else 0,
                          "amount": eq_amount},
    }
    if cash_spec["debt_repayment_monthly"] * months > cash_spec["debt"] + 1e-9:
        raise InputError("cash.debt_repayment_monthly x months exceeds cash.debt; "
                         "the debt would be repaid below zero")

    company = data.get("company") or "Untitled model"
    if not isinstance(company, str):
        raise InputError("company must be a string")
    currency = data.get("currency") or "USD"
    if not isinstance(currency, str) or len(currency) > 8:
        raise InputError("currency must be a short string, e.g. 'USD'")

    scenario = data.get("scenario") or "base"
    if not isinstance(scenario, str):
        raise InputError("scenario must be a string")

    return {
        "company": company,
        "currency": currency.upper(),
        "start": start_month(data.get("start_month")),
        "months": months,
        "scenario": scenario,
        "revenue": {
            "starting_mrr": starting_mrr,
            "new_mrr_start": new_mrr_start,
            "new_mrr_growth": new_mrr_growth,
            "churn_rate": churn,
            "expansion_rate": expansion,
            "contraction_rate": contraction,
            "one_time_revenue": one_time,
            "seasonality": season,
            "acv": acv,
        },
        "cogs": cogs_spec,
        "departments": departments,
        "capex": capex_spec,
        "working_capital": wc_spec,
        "cash": cash_spec,
    }


# ---------------------------------------------------------------------------
# the model
# ---------------------------------------------------------------------------
def build(spec: dict) -> dict:
    """Run the month loop and return periods, summary, checks and flags."""
    r = spec["revenue"]
    c = spec["cogs"]
    capex_spec = spec["capex"]
    wc = spec["working_capital"]
    cash_spec = spec["cash"]
    months = spec["months"]
    year, month = spec["start"]

    # opening balance sheet -- the single legitimate plug in the model
    opening_assets = (cash_spec["starting_cash"] + wc["opening_ar"]
                      + wc["opening_ppe"])
    opening_liabs = (wc["opening_ap"] + wc["opening_deferred_revenue"]
                     + cash_spec["debt"])
    opening_equity = opening_assets - opening_liabs

    mrr = r["starting_mrr"]
    prev_ar = wc["opening_ar"]
    prev_ap = wc["opening_ap"]
    prev_deferred = wc["opening_deferred_revenue"]
    prev_prepaid = 0.0
    prev_ppe_gross = wc["opening_ppe"]
    prev_cash = cash_spec["starting_cash"]
    debt = cash_spec["debt"]
    paid_in = opening_equity
    retained = 0.0
    nol = cash_spec["year1_nol"]

    capex_vintages = []          # (month_index, amount)
    periods = []
    prev_mrr_for_growth = mrr
    mrr_history = [mrr]

    for t in range(months):
        offset = t + 1
        label = month_label(year, month, t)
        cal_month = int(label.split("-")[1])

        # ---- revenue: MRR roll-forward -----------------------------------
        season = 1.0
        if r["seasonality"]:
            season = r["seasonality"][cal_month - 1]
        new_mrr = r["new_mrr_start"] * ((1 + r["new_mrr_growth"]) ** t) * season
        expansion_mrr = mrr * r["expansion_rate"]
        contraction_mrr = mrr * r["contraction_rate"]
        churn_mrr = mrr * r["churn_rate"]
        begin_mrr = mrr
        mrr = max(0.0, begin_mrr + new_mrr + expansion_mrr
                  - contraction_mrr - churn_mrr)
        revenue = mrr + r["one_time_revenue"]

        # ---- headcount-driven cost ---------------------------------------
        hc_total = 0
        opex_total = 0.0
        cogs_people = 0.0
        dept_detail = {}
        for d in spec["departments"]:
            heads = d["start"] + sum(v for m, v in d["additions"].items() if m <= offset)
            cost = heads * d["cost_per_head"]
            cost += d["non_headcount_monthly"]
            cost += revenue * d["non_headcount_pct_revenue"]
            cost += revenue * d["variable_pct_revenue"]
            hc_total += heads
            dept_detail[d["name"]] = {"heads": heads, "cost": cost,
                                      "bucket": d["bucket"]}
            if d["bucket"] == "cogs":
                cogs_people += cost
            else:
                opex_total += cost

        # ---- P&L ---------------------------------------------------------
        cogs_variable = revenue * (c["hosting_pct"] + c["support_pct"]
                                   + c["payment_pct"])
        cogs_total = cogs_variable + c["fixed_monthly"] + cogs_people
        gross_profit = revenue - cogs_total
        ebitda = gross_profit - opex_total

        # depreciation: straight-line per vintage
        capex = revenue * capex_spec["pct_revenue"] + capex_spec["fixed_monthly"]
        capex_vintages.append((t, capex))
        depreciation = 0.0
        for (vt, vamount) in capex_vintages:
            age = t - vt
            if age < capex_spec["useful_life_months"]:
                depreciation += vamount / capex_spec["useful_life_months"]
        # opening PP&E depreciates over the same life
        if wc["opening_ppe"]:
            depreciation += wc["opening_ppe"] / capex_spec["useful_life_months"]

        ebit = ebitda - depreciation
        interest = debt * cash_spec["interest_rate_annual"] / 12.0
        pretax = ebit - interest

        # tax with NOL carry-forward
        if pretax < 0:
            nol += -pretax
            taxable = 0.0
        else:
            used = min(nol, pretax)
            nol -= used
            taxable = pretax - used
        tax = taxable * cash_spec["tax_rate"]
        net_income = pretax - tax

        # ---- working capital --------------------------------------------
        ar = revenue * wc["dso_days"] / 365.0 if wc["dso_days"] else 0.0
        ap = cogs_total * wc["dpo_days"] / 365.0 if wc["dpo_days"] else 0.0
        deferred = revenue * wc["deferred_revenue_pct"]
        prepaid = opex_total * wc["prepaid_pct_opex"]
        ppe_gross = prev_ppe_gross + capex

        # ---- cash flow ---------------------------------------------------
        equity_this_month = (cash_spec["equity_raised"]["amount"]
                             if cash_spec["equity_raised"]["month"] == offset else 0.0)
        repay = min(cash_spec["debt_repayment_monthly"], debt)
        delta_ar = ar - prev_ar
        delta_ap = ap - prev_ap
        delta_deferred = deferred - prev_deferred
        delta_prepaid = prepaid - prev_prepaid
        cfo = net_income + depreciation - delta_ar - delta_prepaid + delta_ap + delta_deferred
        cfi = -capex
        cff = equity_this_month - repay
        net_change = cfo + cfi + cff
        cash = prev_cash + net_change
        debt = debt - repay
        paid_in += equity_this_month
        retained += net_income

        # ---- balance sheet ----------------------------------------------
        assets = cash + ar + prepaid + (ppe_gross - _accum_dep(periods, t, depreciation))
        liabs = ap + deferred + debt
        equity = paid_in + retained
        residual = assets - (liabs + equity)

        # ---- metrics -----------------------------------------------------
        mrr_history.append(mrr)
        arr = mrr * 12.0
        prev_arr = mrr_history[t] * 12.0
        growth_mom = (mrr / prev_mrr_for_growth - 1.0) if prev_mrr_for_growth else 0.0
        nrr = ((begin_mrr + expansion_mrr - contraction_mrr - churn_mrr)
               / begin_mrr) if begin_mrr else 0.0
        grr = ((begin_mrr - contraction_mrr - churn_mrr) / begin_mrr
               if begin_mrr else 0.0)
        gross_margin = gross_profit / revenue if revenue else 0.0
        ebitda_margin = ebitda / revenue if revenue else 0.0
        annual_growth = ((mrr / mrr_history[max(0, t - 11)] - 1.0)
                         if t >= 11 and mrr_history[max(0, t - 11)] else growth_mom * 12)
        rule40 = annual_growth * 100.0 + ebitda_margin * 100.0

        net_burn = max(0.0, -net_change)
        prior_cash = prev_cash
        runway = (cash / _avg_burn(periods, net_burn)) if _avg_burn(periods, net_burn) > 0 else None
        if runway is not None and runway < 0:
            runway = 0.0
        # trailing 3-month net new ARR and burn for burn multiple
        idx = max(0, t - 3)
        arr_3ago = mrr_history[idx] * 12.0
        net_new_arr = arr - arr_3ago
        burn_3 = sum(p["cash_flow"]["net_change"] for p in periods[-2:]) + net_change
        burn_3 = max(0.0, -burn_3)
        burn_multiple = (burn_3 / net_new_arr) if net_new_arr > 0 and burn_3 > 0 else None

        sm_cost = dept_detail.get("sales", {}).get("cost", 0.0) + \
            dept_detail.get("marketing", {}).get("cost", 0.0)
        magic_number = (net_new_arr / (sm_cost * 3.0)) if sm_cost > 0 and t >= 3 else None

        customers = None
        cac_payback = None
        ltv_cac = None
        if r["acv"]:
            customers = arr / r["acv"] if r["acv"] else None
            if customers and sm_cost > 0:
                new_customers = (new_mrr * 12.0 / r["acv"]) if r["acv"] else 0.0
                if new_customers > 0:
                    cac = sm_cost / new_customers
                    arpa_monthly = (arr / customers) / 12.0 if customers else 0.0
                    contribution = arpa_monthly * gross_margin
                    if contribution > 0:
                        cac_payback = cac / contribution
                        life_months = (1.0 / (churn_mrr / begin_mrr)) if begin_mrr and churn_mrr else None
                        if life_months:
                            ltv = contribution * life_months
                            ltv_cac = ltv / cac

        periods.append({
            "month": label,
            "index": offset,
            "headcount": hc_total,
            "departments": dept_detail,
            "pl": {
                "revenue": revenue,
                "mrr_begin": begin_mrr,
                "new_mrr": new_mrr,
                "expansion_mrr": expansion_mrr,
                "contraction_mrr": contraction_mrr,
                "churn_mrr": churn_mrr,
                "mrr_end": mrr,
                "cogs_variable": cogs_variable,
                "cogs_people": cogs_people,
                "cogs_fixed": c["fixed_monthly"],
                "cogs": cogs_total,
                "gross_profit": gross_profit,
                "opex": opex_total,
                "ebitda": ebitda,
                "depreciation": depreciation,
                "ebit": ebit,
                "interest": interest,
                "pretax": pretax,
                "tax": tax,
                "net_income": net_income,
            },
            "cash_flow": {
                "net_income": net_income,
                "depreciation": depreciation,
                "delta_ar": -delta_ar,
                "delta_prepaid": -delta_prepaid,
                "delta_ap": delta_ap,
                "delta_deferred": delta_deferred,
                "cfo": cfo,
                "capex": -capex,
                "cfi": cfi,
                "equity": equity_this_month,
                "debt_repayment": -repay,
                "cff": cff,
                "net_change": net_change,
                "ending_cash": cash,
            },
            "balance_sheet": {
                "cash": cash,
                "accounts_receivable": ar,
                "prepaid": prepaid,
                "ppe_gross": ppe_gross,
                "accumulated_depreciation": _accum_dep(periods, t, depreciation),
                "ppe_net": ppe_gross - _accum_dep(periods, t, depreciation),
                "total_assets": assets,
                "accounts_payable": ap,
                "deferred_revenue": deferred,
                "debt": debt,
                "total_liabilities": liabs,
                "paid_in_capital": paid_in,
                "retained_earnings": retained,
                "total_equity": equity,
                "balance_check": residual,
            },
            "metrics": {
                "arr": arr,
                "arr_prior": prev_arr,
                "mrr_growth_mom": growth_mom,
                "nrr": nrr,
                "grr": grr,
                "gross_margin": gross_margin,
                "ebitda_margin": ebitda_margin,
                "rule_of_40": rule40,
                "net_burn": net_burn,
                "runway_months": runway,
                "burn_multiple": burn_multiple,
                "magic_number": magic_number,
                "customers": customers,
                "cac_payback_months": cac_payback,
                "ltv_cac": ltv_cac,
                "quick_ratio": ((new_mrr + expansion_mrr) /
                                (churn_mrr + contraction_mrr))
                                if (churn_mrr + contraction_mrr) else None,
            },
        })
        prev_mrr_for_growth = begin_mrr
        prev_ar, prev_ap, prev_deferred, prev_prepaid = ar, ap, deferred, prepaid
        prev_ppe_gross = ppe_gross
        prev_cash = cash

    summary = summarise(spec, periods)
    checks = run_checks(spec, periods)
    flags = raise_flags(spec, periods, checks)

    return {
        "meta": {
            "company": spec["company"],
            "currency": spec["currency"],
            "start_month": month_label(spec["start"][0], spec["start"][1], 0),
            "end_month": periods[-1]["month"],
            "months": spec["months"],
            "scenario": spec["scenario"],
            "generator": "financial_model_builder.py",
            "version": "1.0.0",
        },
        "assumptions": _echo(spec),
        "checks": checks,
        "summary": summary,
        "periods": periods,
        "flags": flags,
    }


def _accum_dep(periods, t, current_dep):
    prior = periods[-1]["balance_sheet"]["accumulated_depreciation"] if periods else 0.0
    return prior + current_dep


def _avg_burn(periods, current_burn):
    """Trailing 3-month average net burn, including the current month."""
    values = [p["metrics"]["net_burn"] for p in periods[-2:]] + [current_burn]
    return sum(values) / len(values)


def _echo(spec):
    """Assumptions actually used, echoed for the reader of the output."""
    return {
        "revenue": spec["revenue"],
        "cogs": spec["cogs"],
        "capex": spec["capex"],
        "working_capital": spec["working_capital"],
        "cash": spec["cash"],
        "departments": [
            {"name": d["name"], "start": d["start"],
             "cost_per_head": d["cost_per_head"], "bucket": d["bucket"],
             "additions": d["additions"]}
            for d in spec["departments"]
        ],
    }


def summarise(spec: dict, periods: list) -> dict:
    """Annual roll-up plus the totals a reader asks for first."""
    years = {}
    for p in periods:
        y = p["month"][:4]
        agg = years.setdefault(y, {
            "revenue": 0.0, "cogs": 0.0, "gross_profit": 0.0, "opex": 0.0,
            "ebitda": 0.0, "net_income": 0.0, "capex": 0.0, "net_change": 0.0,
            "months": 0, "headcount_end": 0, "arr_end": 0.0, "mrr_end": 0.0,
            "interest": 0.0, "tax": 0.0, "depreciation": 0.0,
        })
        agg["revenue"] += p["pl"]["revenue"]
        agg["cogs"] += p["pl"]["cogs"]
        agg["gross_profit"] += p["pl"]["gross_profit"]
        agg["opex"] += p["pl"]["opex"]
        agg["ebitda"] += p["pl"]["ebitda"]
        agg["net_income"] += p["pl"]["net_income"]
        agg["capex"] += p["cash_flow"]["capex"] * -1
        agg["net_change"] += p["cash_flow"]["net_change"]
        agg["interest"] += p["pl"]["interest"]
        agg["tax"] += p["pl"]["tax"]
        agg["depreciation"] += p["pl"]["depreciation"]
        agg["months"] += 1
        agg["headcount_end"] = p["headcount"]
        agg["arr_end"] = p["metrics"]["arr"]
        agg["mrr_end"] = p["pl"]["mrr_end"]

    annual = []
    for y in sorted(years):
        a = years[y]
        a["year"] = y
        a["gross_margin"] = a["gross_profit"] / a["revenue"] if a["revenue"] else 0.0
        a["ebitda_margin"] = a["ebitda"] / a["revenue"] if a["revenue"] else 0.0
        annual.append(a)

    first = periods[0]
    last = periods[-1]
    burn_months = [p for p in periods if p["metrics"]["net_burn"] > 0]
    peak_burn = max((p["metrics"]["net_burn"] for p in periods), default=0.0)
    cash_out = next((p["month"] for p in periods
                     if p["balance_sheet"]["cash"] < 0), None)
    breakeven = next((p["month"] for p in periods if p["pl"]["ebitda"] > 0), None)
    starting_arr = spec["revenue"]["starting_mrr"] * 12.0
    total_revenue = sum(p["pl"]["revenue"] for p in periods)
    total_net_income = sum(p["pl"]["net_income"] for p in periods)

    return {
        "annual": annual,
        "starting_mrr": spec["revenue"]["starting_mrr"],
        "starting_arr": starting_arr,
        "ending_mrr": last["pl"]["mrr_end"],
        "ending_arr": last["metrics"]["arr"],
        "arr_cagr": _cagr(starting_arr, last["metrics"]["arr"], spec["months"]),
        "total_revenue": total_revenue,
        "total_net_income": total_net_income,
        "ending_cash": last["balance_sheet"]["cash"],
        "peak_cash": max(p["balance_sheet"]["cash"] for p in periods),
        "lowest_cash": min(p["balance_sheet"]["cash"] for p in periods),
        "peak_monthly_burn": peak_burn,
        "burn_months": len(burn_months),
        "months_to_cash_out": cash_out,
        "ebitda_breakeven_month": breakeven,
        "ending_headcount": last["headcount"],
        "ending_nrr": last["metrics"]["nrr"],
        "ending_gross_margin": last["metrics"]["gross_margin"],
        "total_raised": spec["cash"]["equity_raised"]["amount"],
        "ending_runway_months": last["metrics"]["runway_months"],
        "first_month_revenue": first["pl"]["revenue"],
    }


def _cagr(begin, end, months):
    """Annualised growth from monthly-compounded endpoints."""
    if begin <= 0 or months <= 0:
        return None
    years = months / 12.0
    if years <= 0:
        return None
    return (end / begin) ** (1.0 / years) - 1.0


def run_checks(spec: dict, periods: list) -> dict:
    """The checks that decide whether the model is usable at all."""
    max_residual = max((abs(p["balance_sheet"]["balance_check"]) for p in periods),
                       default=0.0)
    cash_ties = all(
        abs(p["balance_sheet"]["cash"] - p["cash_flow"]["ending_cash"]) < TOLERANCE
        for p in periods)
    arr_ties = all(
        abs(p["metrics"]["arr"] - p["pl"]["mrr_end"] * 12.0) < TOLERANCE
        for p in periods)
    retained_ties = abs(
        periods[-1]["balance_sheet"]["retained_earnings"]
        - sum(p["pl"]["net_income"] for p in periods)) < TOLERANCE
    cfo_ties = all(
        abs(p["cash_flow"]["cfo"]
            - (p["pl"]["net_income"] + p["pl"]["depreciation"]
               + p["cash_flow"]["delta_ar"] + p["cash_flow"]["delta_prepaid"]
               + p["cash_flow"]["delta_ap"] + p["cash_flow"]["delta_deferred"]))
        < TOLERANCE for p in periods)
    return {
        "balance_sheet_balances": max_residual < TOLERANCE,
        "max_balance_residual": max_residual,
        "cash_ties_to_statement": cash_ties,
        "arr_ties_to_mrr": arr_ties,
        "retained_earnings_ties": retained_ties,
        "cfo_ties_to_components": cfo_ties,
        "all_passed": all([max_residual < TOLERANCE, cash_ties, arr_ties,
                           retained_ties, cfo_ties]),
        "revenue_positive": all(p["pl"]["revenue"] > 0 for p in periods),
        "gross_margin_valid": all(-1.0 < p["metrics"]["gross_margin"] <= 1.0
                                  for p in periods),
    }


def raise_flags(spec: dict, periods: list, checks: dict) -> list:
    """Severity-tagged observations a human should read before the numbers."""
    flags = []

    def add(severity, code, message):
        flags.append({"severity": severity, "code": code, "message": message})

    if not checks["all_passed"]:
        add("error", "model_does_not_foot",
            "Model checks failed (max balance residual {:.4f}); fix before "
            "showing anyone.".format(checks["max_balance_residual"]))

    cash_out = next((p for p in periods if p["balance_sheet"]["cash"] < 0), None)
    if cash_out:
        add("critical", "cash_negative",
            "Cash goes negative in {} — the plan is unfunded from that month."
            .format(cash_out["month"]))

    last = periods[-1]
    runway = last["metrics"]["runway_months"]
    if runway is not None and runway < 12:
        add("critical", "runway_short",
            "Ending runway {:.1f} months at trailing burn — below the 12-month "
            "floor; raise or cut.".format(runway))
    elif runway is not None and runway < 18:
        add("warning", "runway_thin",
            "Ending runway {:.1f} months — inside the 18-month comfort band."
            .format(runway))

    gm = last["metrics"]["gross_margin"]
    if gm < 0.5:
        add("warning", "gross_margin_low",
            "Gross margin {:.1%} — below 50%; check COGS drivers before "
            "claiming a software model.".format(gm))

    nrr = last["metrics"]["nrr"]
    if nrr < 1.0:
        add("warning", "nrr_below_100",
            "NRR {:.1%} in the final month — growth must come from new logos; "
            "a leaky base makes the growth plan more expensive.".format(nrr))

    bm = last["metrics"]["burn_multiple"]
    if bm is not None and bm > 2.5:
        add("warning", "burn_multiple_high",
            "Burn multiple {:.2f} — above 2.5 means roughly $2.50 of burn per $1 "
            "of net new ARR.".format(bm))
    if bm is not None and bm < 0:
        add("warning", "burn_multiple_negative", "Net new ARR is negative.")

    if last["metrics"]["rule_of_40"] < 40:
        add("info", "rule_of_40_below",
            "Rule of 40 is {:.0f} — below the 40 threshold at the end of the "
            "horizon.".format(last["metrics"]["rule_of_40"]))

    if spec["revenue"]["acv"] and last["metrics"]["cac_payback_months"]:
        pb = last["metrics"]["cac_payback_months"]
        if pb > 24:
            add("warning", "cac_payback_long",
                "CAC payback {:.0f} months — above 24 months; every new logo "
                "consumes cash for two years.".format(pb))

    if not spec["departments"]:
        add("info", "no_headcount_plan",
            "No headcount departments supplied: OPEX contains no people cost, "
            "which is rarely true.")

    if spec["cash"]["equity_raised"]["amount"] == 0:
        add("info", "no_funding",
            "No equity raise modelled; ensure starting cash covers the plan.")

    if spec["cash"]["tax_rate"] == 0:
        add("info", "no_tax",
            "Tax rate is zero — acceptable for a loss-making plan, wrong for a "
            "profitable one.")

    growth = spec["revenue"]["new_mrr_growth"]
    if growth > 0.10:
        add("warning", "growth_extrapolation",
            "New-business MRR grows {:.1%}/month — that is {:.0f}% annualised "
            "and compounds to an implausible scale; glide to a terminal rate."
            .format(growth, ((1 + growth) ** 12 - 1) * 100))
    return flags


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------
def money(value, currency=""):
    if value is None:
        return "n/a"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000:
        body = "{:.2f}B".format(value / 1_000_000_000)
    elif value >= 1_000_000:
        body = "{:.2f}M".format(value / 1_000_000)
    elif value >= 1_000:
        body = "{:,.0f}k".format(value / 1_000)
    else:
        body = "{:,.0f}".format(value)
    return "{}{}".format(sign, body)


def pct(value, digits=1):
    if value is None:
        return "n/a"
    return "{:.{}f}%".format(value * 100, digits)


def render_markdown(result: dict) -> str:
    meta = result["meta"]
    s = result["summary"]
    cur = meta["currency"]
    out = []
    add = out.append

    add("# {} — {} financial model".format(meta["company"], meta["scenario"]))
    add("")
    add("{} to {} · {} months · all figures in {}".format(
        meta["start_month"], meta["end_month"], meta["months"], cur))
    add("")

    add("## Headline")
    add("")
    add("| Metric | Value |")
    add("|---|---|")
    add("| Starting ARR | {} |".format(money(s["starting_arr"])))
    add("| Ending ARR | {} |".format(money(s["ending_arr"])))
    add("| ARR CAGR | {} |".format(pct(s["arr_cagr"])))
    add("| Total revenue | {} |".format(money(s["total_revenue"])))
    add("| Total net income | {} |".format(money(s["total_net_income"])))
    add("| Ending cash | {} |".format(money(s["ending_cash"])))
    add("| Lowest cash | {} |".format(money(s["lowest_cash"])))
    add("| Peak monthly burn | {} |".format(money(s["peak_monthly_burn"])))
    add("| EBITDA breakeven | {} |".format(s["ebitda_breakeven_month"] or "not reached"))
    add("| Cash-out month | {} |".format(s["months_to_cash_out"] or "none"))
    add("| Ending headcount | {} |".format(s["ending_headcount"]))
    add("| Ending gross margin | {} |".format(pct(s["ending_gross_margin"])))
    add("| Ending NRR | {} |".format(pct(s["ending_nrr"])))
    add("")

    add("## Annual roll-up")
    add("")
    add("| Year | Revenue | Gross profit | GM% | OPEX | EBITDA | EBITDA% | Net income | Capex | Net cash change | ARR (end) | HC (end) |")
    add("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for a in s["annual"]:
        add("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            a["year"], money(a["revenue"]), money(a["gross_profit"]),
            pct(a["gross_margin"]), money(a["opex"]), money(a["ebitda"]),
            pct(a["ebitda_margin"]), money(a["net_income"]), money(a["capex"]),
            money(a["net_change"]), money(a["arr_end"]), a["headcount_end"]))
    add("")

    add("## Monthly detail")
    add("")
    detail = result["periods"] if len(result["periods"]) <= 24 else result["periods"][-24:]
    if len(result["periods"]) > 24:
        add("_Showing the final 24 of {} months._".format(len(result["periods"])))
        add("")
    add("| Month | Revenue | COGS | GM% | OPEX | EBITDA | Net income | Cash | ARR | Burn | Runway | HC |")
    add("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for p in detail:
        m = p["metrics"]
        add("| {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |".format(
            p["month"], money(p["pl"]["revenue"]), money(p["pl"]["cogs"]),
            pct(m["gross_margin"]), money(p["pl"]["opex"]), money(p["pl"]["ebitda"]),
            money(p["pl"]["net_income"]), money(p["balance_sheet"]["cash"]),
            money(m["arr"]), money(m["net_burn"]),
            "{:.1f}".format(m["runway_months"]) if m["runway_months"] is not None else "n/a",
            p["headcount"]))
    add("")

    add("## Unit economics (final month)")
    add("")
    last = result["periods"][-1]["metrics"]
    add("| Metric | Value |")
    add("|---|---|")
    add("| NRR (monthly) | {} |".format(pct(last["nrr"], 2)))
    add("| GRR (monthly) | {} |".format(pct(last["grr"], 2)))
    add("| Quick ratio | {} |".format(
        "{:.2f}".format(last["quick_ratio"]) if last["quick_ratio"] is not None else "n/a"))
    add("| Burn multiple | {} |".format(
        "{:.2f}".format(last["burn_multiple"]) if last["burn_multiple"] is not None else "n/a"))
    add("| Magic number | {} |".format(
        "{:.2f}".format(last["magic_number"]) if last["magic_number"] is not None else "n/a"))
    add("| Rule of 40 | {:.0f} |".format(last["rule_of_40"]))
    add("| Customers | {} |".format(
        "{:,.0f}".format(last["customers"]) if last["customers"] else "n/a (no ACV)"))
    add("| CAC payback (months) | {} |".format(
        "{:.1f}".format(last["cac_payback_months"])
        if last["cac_payback_months"] is not None else "n/a"))
    add("| LTV/CAC | {} |".format(
        "{:.2f}".format(last["ltv_cac"]) if last["ltv_cac"] is not None else "n/a"))
    add("")

    add("## Checks")
    add("")
    add("| Check | Result |")
    add("|---|---|")
    for k, v in result["checks"].items():
        if isinstance(v, bool):
            add("| {} | {} |".format(k, "PASS" if v else "FAIL"))
    add("| max_balance_residual | {:.6f} |".format(result["checks"]["max_balance_residual"]))
    add("")

    if result["flags"]:
        add("## Flags")
        add("")
        for f in result["flags"]:
            add("- **{}** `{}` — {}".format(f["severity"].upper(), f["code"],
                                            f["message"]))
        add("")

    add("## Method notes")
    add("")
    add("- Cash is derived from the cash flow statement; the balance sheet is not "
        "plugged. Opening equity is set from the opening balance sheet.")
    add("- Expansion, contraction and churn apply to beginning-of-period MRR only.")
    add("- Tax carries losses forward (NOL); a loss produces no tax benefit.")
    add("- Depreciation is straight-line per capex vintage over the useful life.")
    add("- Runway uses the trailing 3-month average net burn, not the current month.")
    add("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# demo data + self test
# ---------------------------------------------------------------------------
DEMO = {
    "company": "Acme Cloud",
    "currency": "USD",
    "start_month": "2026-01",
    "months": 36,
    "revenue": {
        "starting_mrr": 180000,
        "new_mrr_start": 22000,
        "new_mrr_growth": 0.02,
        "churn_rate": 0.014,
        "expansion_rate": 0.011,
        "contraction_rate": 0.004,
        "one_time_revenue": 6000,
        "seasonality": [0.92, 0.95, 1.02, 1.0, 1.0, 1.05, 0.95, 0.85, 1.02,
                        1.05, 1.05, 1.2],
        "acv": 9000,
    },
    "cogs": {"hosting_pct": 0.09, "support_pct": 0.05,
             "payment_pct": 0.028, "fixed_monthly": 4000},
    "headcount": {
        "departments": [
            {"name": "engineering", "start": 9, "cost_per_head": 16500,
             "additions": {"6": 2, "15": 2, "27": 2}, "bucket": "opex"},
            {"name": "sales", "start": 4, "cost_per_head": 14500,
             "additions": {"4": 1, "10": 2, "18": 3},
             "variable_pct_revenue": 0.05},
            {"name": "marketing", "start": 2, "cost_per_head": 12000,
             "additions": {"3": 1, "20": 1},
             "non_headcount_pct_revenue": 0.08},
            {"name": "cs", "start": 3, "cost_per_head": 9500,
             "additions": {"9": 1, "21": 2}, "bucket": "opex"},
            {"name": "ga", "start": 2, "cost_per_head": 11000,
             "non_headcount_monthly": 9000},
        ]
    },
    "capex": {"pct_revenue": 0.02, "fixed_monthly": 1500,
              "useful_life_months": 36},
    "working_capital": {"dso_days": 38, "dpo_days": 25,
                        "deferred_revenue_pct": 0.14,
                        "prepaid_pct_opex": 0.02},
    "cash": {"starting_cash": 3400000, "debt": 0,
             "debt_repayment_monthly": 0, "interest_rate_annual": 0.0,
             "tax_rate": 0.21,
             "equity_raised": {"month": 0, "amount": 0}},
    "scenario": "base",
}


def self_test() -> int:
    """Run the demo and assert the invariants. Returns an exit code."""
    checks = []

    def check(name, condition, detail=""):
        checks.append((name, bool(condition), detail))

    try:
        spec = normalise(DEMO)
        result = build(spec)
    except InputError as exc:
        print("FAIL: demo input rejected: {}".format(exc), file=sys.stderr)
        return 1

    periods = result["periods"]
    check("period count", len(periods) == DEMO["months"],
          "got {}".format(len(periods)))
    check("balance sheet balances",
          result["checks"]["balance_sheet_balances"],
          "max residual {:.6f}".format(result["checks"]["max_balance_residual"]))
    check("cash ties to statement", result["checks"]["cash_ties_to_statement"])
    check("ARR = MRR x 12", result["checks"]["arr_ties_to_mrr"])
    check("retained earnings ties", result["checks"]["retained_earnings_ties"])
    check("CFO ties to components", result["checks"]["cfo_ties_to_components"])
    check("revenue positive", all(p["pl"]["revenue"] > 0 for p in periods))
    check("gross margin sane",
          all(0.4 < p["metrics"]["gross_margin"] < 1.0 for p in periods),
          "range {:.2f}-{:.2f}".format(
              min(p["metrics"]["gross_margin"] for p in periods),
              max(p["metrics"]["gross_margin"] for p in periods)))
    check("MRR rolls forward",
          abs(periods[0]["pl"]["mrr_begin"] - DEMO["revenue"]["starting_mrr"]) < 0.01)
    check("ending cash = start + sum(net change)",
          abs(result["summary"]["ending_cash"]
              - (DEMO["cash"]["starting_cash"]
                 + sum(p["cash_flow"]["net_change"] for p in periods))) < 0.01)
    check("headcount only grows",
          all(periods[i]["headcount"] <= periods[i + 1]["headcount"]
              for i in range(len(periods) - 1)))
    check("annual revenue == monthly sum",
          abs(sum(a["revenue"] for a in result["summary"]["annual"])
              - sum(p["pl"]["revenue"] for p in periods)) < 0.01)
    check("flags produced", isinstance(result["flags"], list))

    # negative tests: the validator must reject bad input
    bad_cases = [
        ("missing starting_mrr", {"months": 12, "cash": {"starting_cash": 1}}),
        ("months out of range", {"months": 120, "revenue": {"starting_mrr": 1},
                                 "cash": {"starting_cash": 1}}),
        ("negative churn", {"months": 12,
                            "revenue": {"starting_mrr": 1, "churn_rate": -0.1},
                            "cash": {"starting_cash": 1}}),
        ("additions beyond horizon", {"months": 12,
                                      "revenue": {"starting_mrr": 1},
                                      "cash": {"starting_cash": 1},
                                      "headcount": {"departments": [
                                          {"name": "eng", "start": 1,
                                           "additions": {"24": 2}}]}}),
        ("cogs over 100%", {"months": 12, "revenue": {"starting_mrr": 1},
                            "cash": {"starting_cash": 1},
                            "cogs": {"hosting_pct": 0.8, "support_pct": 0.3}}),
        ("over-repayment", {"months": 12, "revenue": {"starting_mrr": 1},
                            "cash": {"starting_cash": 1, "debt": 100,
                                     "debt_repayment_monthly": 50}}),
    ]
    for name, payload in bad_cases:
        rejected = False
        try:
            normalise(payload)
        except InputError:
            rejected = True
        check("rejects {}".format(name), rejected)

    width = max(len(n) for n, _, _ in checks)
    failed = 0
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print("{:<6} {:<{w}} {}".format(status, name, detail, w=width))

    print("")
    print("self-test: {} passed, {} failed".format(len(checks) - failed, failed))
    if failed == 0:
        print("\n--- demo model (markdown, first 40 lines) ---\n")
        print("\n".join(render_markdown(result).splitlines()[:40]))
    return 0 if failed == 0 else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a driver-based three-statement financial model from "
                    "a JSON spec. Stdlib only, no network.",
        epilog="Example: python3 financial_model_builder.py --input model.json "
               "--format markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", nargs="?", default=None,
                        help="path to the JSON model spec (omit to read stdin)")
    parser.add_argument("--input", "-i", dest="input_opt", default=None,
                        help="path to the JSON model spec (same as positional)")
    parser.add_argument("--format", "-f", choices=["json", "markdown"],
                        default="markdown", help="output format (default: markdown)")
    parser.add_argument("--output", "-o", choices=["json", "markdown"],
                        dest="output", default=None,
                        help="alias for --format, kept for symmetry with other skills")
    parser.add_argument("--pretty", action="store_true",
                        help="pretty-print JSON output")
    parser.add_argument("--self-test", action="store_true",
                        help="run the built-in demo and verify model invariants")
    args = parser.parse_args(argv) if argv is not None else parser.parse_args()

    if args.self_test:
        return self_test()

    path = args.input_opt or args.input
    raw = None
    if path:
        try:
            with open(path, encoding="utf-8") as fh:
                raw = fh.read()
        except FileNotFoundError:
            print("error: no such file: {}".format(path), file=sys.stderr)
            return 2
        except OSError as exc:
            print("error: cannot read {}: {}".format(path, exc), file=sys.stderr)
            return 2
    else:
        if sys.stdin.isatty():
            parser.print_help(sys.stderr)
            print("\nerror: no input file and stdin is empty", file=sys.stderr)
            return 2
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print("error: input is not valid JSON: {}".format(exc), file=sys.stderr)
        return 2

    try:
        spec = normalise(data)
        result = build(spec)
    except InputError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2
    except (ZeroDivisionError, OverflowError, ValueError) as exc:
        print("error: model could not be computed: {}".format(exc), file=sys.stderr)
        return 2

    fmt = args.output or args.format
    if fmt == "json":
        print(json.dumps(result, indent=2 if args.pretty else None,
                         sort_keys=args.pretty, default=str))
    else:
        print(render_markdown(result))

    # a model that does not foot must not exit clean
    if not result["checks"]["all_passed"]:
        print("warning: model checks failed; see the 'checks' block",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
