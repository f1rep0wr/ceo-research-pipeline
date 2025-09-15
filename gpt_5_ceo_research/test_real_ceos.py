"""
Integration test script for CEO research with real CEOs.

Tests the simple websearch system with 5 known CEOs to verify accuracy
and functionality using real API calls (not mocks).

This follows KISS principles:
- Simple test structure
- Clear success/failure indicators
- Direct API testing
- Readable output format
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any

# Add src directory to path for imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from src.ceo_websearch_simple import research_ceo_with_websearch
from src.config.settings import get_settings
from src.models.ceo_profile import CEOProfile


class CEOTestResult:
    """Simple container for test results."""

    def __init__(self, ceo_name: str, company_name: str, expected_type: str):
        self.ceo_name = ceo_name
        self.company_name = company_name
        self.expected_type = expected_type
        self.success = False
        self.profile: CEOProfile = None
        self.errors: List[str] = []
        self.checks_passed = 0
        self.total_checks = 0

    def add_check(self, condition: bool, description: str) -> None:
        """Add a test check and track results."""
        self.total_checks += 1
        if condition:
            self.checks_passed += 1
        else:
            self.errors.append(f"❌ {description}")

    def mark_success(self) -> None:
        """Mark test as successful."""
        self.success = True

    def get_score(self) -> str:
        """Get the test score as a string."""
        if self.total_checks == 0:
            return "0/0"
        return f"{self.checks_passed}/{self.total_checks}"


async def test_ceo_research(
    ceo_name: str,
    company_name: str,
    expected_type: str
) -> CEOTestResult:
    """
    Test CEO research for a single CEO using simple websearch.

    Args:
        ceo_name: Name of the CEO to test
        company_name: Company name
        expected_type: Expected insider/outsider classification

    Returns:
        CEOTestResult with test outcomes
    """
    result = CEOTestResult(ceo_name, company_name, expected_type)

    print(f"\n🔍 Testing: {ceo_name} ({company_name})")
    print("-" * 60)

    try:
        # Run the CEO research using simple websearch
        profile = await research_ceo_with_websearch(ceo_name, company_name)
        result.profile = profile

        # Check 1: CEO name exists and matches
        result.add_check(
            profile.ceo_name is not None and profile.ceo_name.strip() != "",
            f"CEO name populated: {profile.ceo_name}"
        )

        # Check 2: Company name matches
        result.add_check(
            profile.company_name is not None and company_name.lower() in profile.company_name.lower(),
            f"Company name matches: {profile.company_name}"
        )

        # Check 3: Insider/outsider classification exists
        classification_exists = profile.insider_outsider is not None and profile.insider_outsider.strip() != ""
        result.add_check(
            classification_exists,
            f"Insider/outsider classification: {profile.insider_outsider}"
        )

        # Check 4: Start date exists
        result.add_check(
            profile.start_date is not None and profile.start_date.strip() != "",
            f"Start date provided: {profile.start_date}"
        )

        # Check 5: Primary sources not empty
        has_sources = profile.primary_sources and len(profile.primary_sources) > 0
        result.add_check(
            has_sources,
            f"Primary sources found: {len(profile.primary_sources) if profile.primary_sources else 0} sources"
        )

        # Check 6: Confidence score reasonable
        confidence_ok = profile.confidence_score is not None and 0 <= profile.confidence_score <= 1
        result.add_check(
            confidence_ok,
            f"Confidence score valid: {profile.confidence_score}"
        )

        # Check 7: Data completeness assessment
        result.add_check(
            profile.data_completeness is not None and profile.data_completeness.strip() != "",
            f"Data completeness assessed: {profile.data_completeness}"
        )

        # Additional info checks (not failures if missing, but good to have)
        print(f"📊 Additional Info:")
        print(f"   • CEO Title: {profile.ceo_title or 'Not found'}")
        print(f"   • Age: {profile.age or 'Not found'}")
        print(f"   • Tenure: {profile.tenure_years or 'Not found'} years")
        print(f"   • Previous CEO Experience: {profile.previous_ceo_experience or 'Not found'}")
        print(f"   • Education: {', '.join(profile.education_schools) if profile.education_schools else 'Not found'}")

        # Mark as success if most checks passed
        if result.checks_passed >= 5:  # At least 5 out of 7 core checks
            result.mark_success()
            print(f"✅ Test PASSED: {result.get_score()} checks passed")
        else:
            print(f"❌ Test FAILED: {result.get_score()} checks passed")

        # Show any specific errors
        for error in result.errors:
            print(f"   {error}")

    except Exception as e:
        result.errors.append(f"Exception during research: {str(e)}")
        print(f"❌ Test FAILED with exception: {str(e)}")

    return result


async def run_ceo_integration_tests() -> None:
    """
    Run integration tests with 5 known CEOs.

    Tests real API functionality with well-known CEOs to verify
    the system can extract accurate information.
    """
    print("🚀 Starting CEO Research Integration Tests")
    print("=" * 60)
    print("Testing with 5 known CEOs using real API calls...")
    print("This will take a few minutes to complete.\n")

    # Test cases: (CEO Name, Company, Expected Classification)
    # Note: Satya Nadella was actually an outsider when hired
    test_cases = [
        ("Tim Cook", "Apple", "insider"),
        ("Satya Nadella", "Microsoft", "outsider"),  # Was outsider when hired
        ("Sundar Pichai", "Google", "insider"),
        ("Mary Barra", "General Motors", "insider"),
        ("Andy Jassy", "Amazon", "insider")
    ]

    # Initialize settings for simple websearch
    try:
        settings = get_settings()
        print(f"✅ Settings initialized successfully for simple websearch")
    except Exception as e:
        print(f"❌ Failed to initialize settings: {str(e)}")
        return

    # Run tests for each CEO
    results: List[CEOTestResult] = []

    for i, (ceo_name, company_name, expected_type) in enumerate(test_cases, 1):
        print(f"\n{'='*20} Test {i}/{len(test_cases)} {'='*20}")

        result = await test_ceo_research(ceo_name, company_name, expected_type)
        results.append(result)

        # Small delay between tests to be respectful to APIs
        if i < len(test_cases):
            print("⏳ Waiting 5 seconds before next test...")
            await asyncio.sleep(5)

    # Generate summary report
    print(f"\n{'='*60}")
    print("📋 INTEGRATION TEST SUMMARY REPORT")
    print(f"{'='*60}")

    successful_tests = [r for r in results if r.success]
    failed_tests = [r for r in results if not r.success]

    success_rate = len(successful_tests) / len(results) * 100

    print(f"🎯 Overall Success Rate: {len(successful_tests)}/{len(results)} ({success_rate:.1f}%)")
    print(f"✅ Passed Tests: {len(successful_tests)}")
    print(f"❌ Failed Tests: {len(failed_tests)}")

    # Show successful tests
    if successful_tests:
        print(f"\n✅ SUCCESSFUL TESTS:")
        for result in successful_tests:
            print(f"   • {result.ceo_name} ({result.company_name}) - {result.get_score()}")

    # Show failed tests with details
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for result in failed_tests:
            print(f"   • {result.ceo_name} ({result.company_name}) - {result.get_score()}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"     {error}")

    # Classification accuracy check
    print(f"\n🔍 CLASSIFICATION ACCURACY:")
    classification_correct = 0
    classification_total = 0

    for result in results:
        if result.profile and result.profile.insider_outsider:
            classification_total += 1
            expected = result.expected_type.lower()
            actual = result.profile.insider_outsider.lower()

            if expected == actual:
                classification_correct += 1
                print(f"   ✅ {result.ceo_name}: Expected {expected}, Got {actual}")
            else:
                print(f"   ❌ {result.ceo_name}: Expected {expected}, Got {actual}")

    if classification_total > 0:
        classification_accuracy = classification_correct / classification_total * 100
        print(f"📊 Classification Accuracy: {classification_correct}/{classification_total} ({classification_accuracy:.1f}%)")

    # Final assessment
    print(f"\n{'='*60}")
    if success_rate >= 80:
        print("🎉 INTEGRATION TESTS: EXCELLENT - System performing well!")
    elif success_rate >= 60:
        print("✅ INTEGRATION TESTS: GOOD - System mostly functional")
    elif success_rate >= 40:
        print("⚠️  INTEGRATION TESTS: FAIR - System needs improvement")
    else:
        print("❌ INTEGRATION TESTS: POOR - System requires attention")

    print(f"{'='*60}")
    print("🏁 Integration testing completed!")


def main():
    """Main entry point for the integration test script."""
    try:
        asyncio.run(run_ceo_integration_tests())
    except KeyboardInterrupt:
        print("\n⏹️  Integration tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Integration tests failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()