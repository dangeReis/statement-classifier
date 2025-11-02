#!/usr/bin/env python3
"""
Comprehensive test suite for transaction classification.

Tests both v3 and v4 format rules with real-world examples.
"""

import sys
import unittest
from pathlib import Path

try:
    from .classifier import classify_transaction
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent))
    from classifier import classify_transaction


class TestClassification(unittest.TestCase):
    """Test transaction classification with real examples."""

    def test_business_bank_fees(self):
        """Test business bank fee classification."""
        desc = "STANDARD ACH PMNTS INITIAL FEE QTY = 2"
        purchase, cat, subcat, online = classify_transaction(desc, "FEE_TRANSACTION")
        self.assertEqual(purchase, "Business")
        self.assertIn("Bank Fees", cat)

    def test_business_payroll_fee(self):
        """Test business payroll fee classification."""
        desc = "Same-Day ACH Payroll Payment 11160449586"
        purchase, cat, subcat, online = classify_transaction(desc, "BASIC_PAYROLL")
        self.assertEqual(purchase, "Business")

    def test_personal_haircut(self):
        """Test personal haircut classification."""
        desc = "SAMS HAIR LLC"
        purchase, cat, subcat, online = classify_transaction(desc, "Miscellaneous")
        self.assertEqual(purchase, "Personal")
        self.assertIn("Personal Care", cat)

    def test_business_car_maintenance(self):
        """Test business car maintenance classification."""
        desc = "Riverside Nissan"
        purchase, cat, subcat, online = classify_transaction(desc, "Automotive")
        self.assertEqual(purchase, "Business")
        self.assertIn("Car", cat)

    def test_business_income_amazon_associates(self):
        """Test business income from Amazon Associates."""
        desc = "REAL TIME TRANSFER RECD FROM ABA/CONTR BNK-021000021  FROM: AMAZON.COM REF: 2DSNCRMDSKG5LOL"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        self.assertIn("Income", cat)

    def test_business_income_fba(self):
        """Test business income from FBA."""
        desc = "REAL TIME TRANSFER RECD FROM FROM: BNF-AMAZON.COM REF: 14NYITJFJGFQWC7"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        self.assertIn("Income", cat)

    def test_personal_income_moodys(self):
        """Test personal income from Moody's."""
        desc = "ACH Electronic Credit MOODY'S RISK PAYROLL"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")

    def test_personal_investment_ira(self):
        """Test personal IRA investment."""
        desc = "ACH Electronic Debit VANGUARD BUY   INVESTMENT 224208005001154"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")

    def test_business_property_tax(self):
        """Test business property tax."""
        desc = "Bill Payment BORO OF PALISADES PARK      010007 CBOL"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")

    def test_business_state_taxes(self):
        """Test business state taxes."""
        desc = "ACH Electronic Credit NY STATE     NYSTTAXRFD"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")

    def test_personal_recreation_soccer(self):
        """Test personal recreation soccer."""
        desc = "A-GAMESOCCER.COM FAIRFIELD NJ"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")
        self.assertTrue(online)

    def test_personal_grocery_amazon_fresh(self):
        """Test personal grocery from Amazon Fresh."""
        desc = "AMAZON FRESH*ZE3GA26U0 866-210-1072 WA"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")
        self.assertIn("Food", cat)

    def test_business_general_merchandise_amazon(self):
        """Test business general merchandise from Amazon."""
        desc = "AMAZON MARK* NH4S31RG1 SEATTLE WA"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        self.assertIn("General Merchandise", cat)

    def test_personal_entertainment_movies(self):
        """Test personal entertainment movies."""
        desc = "ATI*10415-02070010 8448386284 CA"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")

    def test_personal_financial_transfer(self):
        """Test personal financial transfer."""
        desc = "Autosave $30 to savings monthly 11456"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")
        self.assertIn("Financial", cat)

    def test_business_auto_tolls(self):
        """Test business auto tolls."""
        desc = "E-Z*PASSNY REBILL 800-333-8655 NY"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        self.assertIn("Auto", cat)

    def test_business_insurance_auto(self):
        """Test business auto insurance."""
        desc = "GEICO  *AUTO"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        # Category should contain "Insurance" or "Auto"
        self.assertTrue(
            "Insurance" in cat or "Auto" in cat,
            f"Expected Insurance/Auto category, got: {cat}"
        )

    def test_business_government_fees(self):
        """Test business government fees."""
        desc = "NJ ANNUAL REPORT SERVICES"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")

    def test_business_coupons(self):
        """Test business coupons."""
        desc = "PAYPAL *BOLTINC 4029357733 CA"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")

    def test_personal_medical_dental(self):
        """Test personal medical dental."""
        desc = "FORT LEE ORTHODONTICS"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")
        # Category should contain "Healthcare", "Medical", or "Health"
        self.assertTrue(
            "Healthcare" in cat or "Medical" in cat or "Health" in cat,
            f"Expected Healthcare/Medical/Health category, got: {cat}"
        )

    def test_personal_clothing(self):
        """Test personal clothing."""
        desc = "GAP OUTLET.COM 2679"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")
        self.assertIn("Clothing", cat)

    def test_personal_education_swimming(self):
        """Test personal education swimming."""
        desc = "ICP*Goldfish Swim School"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Personal")

    def test_business_shipping(self):
        """Test business shipping."""
        desc = "USPS PO 3323250227"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        self.assertIn("Shipping", cat)

    def test_business_professional_fees(self):
        """Test business professional fees."""
        desc = "UPWORK  -714055639"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        self.assertIn("Professional", cat)

    def test_business_education_certifications(self):
        """Test business education certifications."""
        desc = "WWW.WHIZLABS.COM"
        purchase, cat, subcat, online = classify_transaction(desc, "")
        self.assertEqual(purchase, "Business")
        self.assertTrue(online)


class TestOnlineDetection(unittest.TestCase):
    """Test online purchase detection."""

    def test_amazon_fresh_online(self):
        """Amazon Fresh should be detected as online."""
        desc = "AMAZON FRESH*ZE3GA26U0"
        _, _, _, online = classify_transaction(desc, "")
        self.assertTrue(online)

    def test_amazon_mark_online(self):
        """Amazon marketplace should be detected as online."""
        desc = "AMAZON MARK* NH4S31RG1"
        _, _, _, online = classify_transaction(desc, "")
        self.assertTrue(online)

    def test_whizlabs_online(self):
        """Whizlabs should be detected as online."""
        desc = "WWW.WHIZLABS.COM"
        _, _, _, online = classify_transaction(desc, "")
        self.assertTrue(online)

    def test_ati_movies_online(self):
        """ATI movie tickets should be detected as online."""
        desc = "ATI*10415-02070010 8448386284"
        _, _, _, online = classify_transaction(desc, "")
        self.assertTrue(online)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def test_empty_description(self):
        """Test classification with empty description."""
        purchase, cat, subcat, online = classify_transaction("", "RESTAURANT")
        # Should fallback to category-based classification
        self.assertIn("Food", cat)

    def test_empty_category(self):
        """Test classification with empty category."""
        purchase, cat, subcat, online = classify_transaction("RIVERSIDE NISSAN", "")
        self.assertEqual(purchase, "Business")

    def test_unknown_merchant(self):
        """Test classification with unknown merchant."""
        purchase, cat, subcat, online = classify_transaction("UNKNOWN MERCHANT XYZ123", "")
        # Should return default (Personal with empty category or fallback)
        self.assertIsInstance(purchase, str)

    def test_case_insensitivity(self):
        """Test that classification is case-insensitive."""
        desc_upper = "RIVERSIDE NISSAN"
        desc_lower = "riverside nissan"
        desc_mixed = "Riverside Nissan"

        result_upper = classify_transaction(desc_upper, "")
        result_lower = classify_transaction(desc_lower, "")
        result_mixed = classify_transaction(desc_mixed, "")

        self.assertEqual(result_upper, result_lower)
        self.assertEqual(result_lower, result_mixed)


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestClassification))
    suite.addTests(loader.loadTestsFromTestCase(TestOnlineDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:       {result.testsRun}")
    print(f"Successes:       {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:        {len(result.failures)}")
    print(f"Errors:          {len(result.errors)}")
    print()

    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
