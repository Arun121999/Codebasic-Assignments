"""
Tests for the four money functions in pricing.py: member_price, add_gst,
delivery_fee, and loyalty_points.

specifically calls out:
  - a zero discount        -> price should stay unchanged
  - a full (100%) discount -> price should become 0
  - the delivery-fee threshold boundary -> exactly at the threshold vs.
    just below it, since the function uses >= (free AT or above the limit)
"""
import pytest
# Import the functions we're testing, straight from pricing.py
from pricing import member_price, add_gst, delivery_fee, loyalty_points


# ---------------------------------------------------------------------
# member_price(price, percent) -> price - (price * percent / 100)
# ---------------------------------------------------------------------

def test_member_price_normal_discount():
    # basic 10% off, this is the case that runs 99% of the time
    assert member_price(1000, 10) == 900.0


def test_member_price_zero_discount():
    # 0% off = price stays exactly the same, no discount applied
    assert member_price(1000, 0) == 1000.0


def test_member_price_full_discount_is_free():
    # 100% off should give 0, not something like 0.000000001 from float math
    assert member_price(1000, 100) == 0.0


def test_member_price_on_zero_price():
    # price is already 0, so any discount % should still land on 0
    assert member_price(0, 25) == 0.0


def test_member_price_fractional_percent():
    # percent doesn't have to be a whole number, e.g. 12.5% off
    assert member_price(200, 12.5) == pytest.approx(175.0)


# -------------------------------------------------------------------- add_gst

def test_add_gst_uses_five_percent_by_default():
    # not passing a rate at all -> should fall back to the 5% default for books
    assert add_gst(1000) == 1050.0


def test_add_gst_explicit_rate_matches_default():
    # same as above but rate passed explicitly, should match
    assert add_gst(1000, 5) == 1000 * 1.05


def test_add_gst_higher_rate():
    # non-book category, higher GST rate
    assert add_gst(1000, 18) == pytest.approx(1180.0)


def test_add_gst_zero_rate_leaves_price_unchanged():
    # tax-exempt case, rate = 0, price shouldn't move at all
    assert add_gst(1000, 0) == 1000.0


def test_add_gst_on_zero_price():
    assert add_gst(0) == 0.0


def test_add_gst_keeps_fractional_paise():
    # prices aren't always round numbers, check paise-level values hold up
    assert add_gst(199.99, 5) == pytest.approx(209.9895)


# --------------------------------------------------------------- delivery_fee

def test_delivery_fee_above_threshold_is_free():
    assert delivery_fee(600) == 0


def test_delivery_fee_below_threshold_is_flat():
    assert delivery_fee(300) == 40


def test_delivery_fee_exactly_at_threshold_is_free():
    # this is the important one - function uses >=, so exactly 500 must be free too
    assert delivery_fee(500) == 0


def test_delivery_fee_one_rupee_below_threshold_is_charged():
    # one rupee under the line and delivery isn't free anymore
    assert delivery_fee(499) == 40


def test_delivery_fee_just_above_threshold_is_free():
    assert delivery_fee(501) == 0


def test_delivery_fee_zero_order_is_charged():
    assert delivery_fee(0) == 40


# ------------------------------------------------------------- loyalty_points

def test_loyalty_points_normal():
    # 950 spent -> 9 full hundreds -> 9 points, the leftover 50 doesn't count
    assert loyalty_points(950) == 9


def test_loyalty_points_exact_multiple_of_hundred():
    assert loyalty_points(100) == 1
    assert loyalty_points(1000) == 10


def test_loyalty_points_below_one_hundred_earns_nothing():
    # under 100 spent = 0 points, and no rounding up for close numbers like 99.99
    assert loyalty_points(99) == 0
    assert loyalty_points(99.99) == 0


def test_loyalty_points_on_zero():
    assert loyalty_points(0) == 0


def test_loyalty_points_returns_an_int():
    # points should be a whole number type, not 9.0
    result = loyalty_points(950.75)
    assert isinstance(result, int)
    assert result == 9


# ------------------------------------------- a couple of functions in sequence

def test_member_discount_then_gst_then_delivery():
    """A 1000 order: 10% member discount, 5% GST, then the delivery rule."""
    discounted = member_price(1000, 10)          # 900.0
    with_gst = add_gst(discounted)               # 945.0
    assert with_gst == pytest.approx(945.0)
    assert delivery_fee(with_gst) == 0            # above 500 so free delivery
    assert loyalty_points(with_gst) == 9