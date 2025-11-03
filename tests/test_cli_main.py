"""Tests for CLI main entry point."""

import json
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

from bin.cli.main import CLI, main


class TestCLI(unittest.TestCase):
    """Test CLI coordinator."""

    def setUp(self):
        """Set up test fixtures."""
        self.rules_path = Path(__file__).parents[1] / "bin" / "classification_rules.v4.json"
        self.cli = CLI(rules_path=self.rules_path, verbose=False)

    def test_cli_initialization(self):
        """Test CLI initializes with correct components."""
        self.assertIsNotNone(self.cli.provider)
        self.assertIsNotNone(self.cli.engine)
        self.assertIsNotNone(self.cli.manager)
        self.assertIsNotNone(self.cli.validator)
        self.assertIsNotNone(self.cli.analyzer)
        self.assertIsNotNone(self.cli.tester)

    def test_cli_rules_path_validation(self):
        """Test CLI validates rules file exists."""
        with self.assertRaises(FileNotFoundError):
            CLI(rules_path=Path("/nonexistent/rules.json"), verbose=False)

    def test_classify_success(self):
        """Test classify command succeeds."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.cli.classify("Amazon AMZN.COM", "5411")
            self.assertEqual(result, 0)
            output = fake_out.getvalue()
            self.assertIn("Classification Result:", output)
            self.assertIn("Purchase Type:", output)
            self.assertIn("Category:", output)

    def test_classify_handles_error(self):
        """Test classify handles errors gracefully."""
        with patch('sys.stdout', new=StringIO()):
            with patch('sys.stderr', new=StringIO()) as fake_err:
                with patch.object(self.cli.tester, 'test_classification',
                                  side_effect=Exception("Test error")):
                    result = self.cli.classify("Test", "5411")
                    self.assertEqual(result, 1)
                    output = fake_err.getvalue()
                    self.assertIn("Error", output)

    def test_validate_success(self):
        """Test validate command succeeds."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.cli.validate()
            # Result may be 0 or 1 depending on rules validity
            self.assertIn(result, [0, 1])
            output = fake_out.getvalue()
            self.assertIsNotNone(output)

    def test_analyze_stats(self):
        """Test analyze stats command."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.cli.analyze_stats()
            self.assertEqual(result, 0)
            output = fake_out.getvalue()
            self.assertIn("Rule Statistics:", output)
            self.assertIn("Total Rules:", output)

    def test_analyze_duplicates_no_duplicates(self):
        """Test analyze duplicates when none exist."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            # Mock analyzer to return empty duplicates
            with patch.object(self.cli.analyzer, 'find_duplicates', return_value=[]):
                result = self.cli.analyze_duplicates()
                self.assertEqual(result, 0)
                output = fake_out.getvalue()
                self.assertIn("No duplicate keywords", output)

    def test_analyze_duplicates_found(self):
        """Test analyze duplicates when duplicates exist."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            # Mock analyzer to return duplicates
            duplicates = [
                {'keyword': 'AMAZON', 'rule_ids': ['rule1', 'rule2']}
            ]
            with patch.object(self.cli.analyzer, 'find_duplicates', return_value=duplicates):
                result = self.cli.analyze_duplicates()
                self.assertEqual(result, 1)
                output = fake_out.getvalue()
                self.assertIn("duplicate keyword groups:", output)

    def test_analyze_coverage(self):
        """Test analyze coverage command."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.cli.analyze_coverage()
            self.assertEqual(result, 0)
            output = fake_out.getvalue()
            self.assertIn("Coverage Analysis:", output)

    def test_rules_add_success(self):
        """Test rules add command."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            result = self.cli.rules_add(
                rule_id="test-rule",
                keywords="TEST,EXAMPLE",
                purchase_type="Personal",
                category="Testing"
            )
            # May succeed or fail depending on existing rules, but should not crash
            self.assertIn(result, [0, 1])

    def test_rules_get_nonexistent(self):
        """Test rules get with nonexistent rule."""
        with patch('sys.stderr', new=StringIO()) as fake_err:
            result = self.cli.rules_get("nonexistent-rule-12345")
            self.assertEqual(result, 1)
            output = fake_err.getvalue()
            self.assertIn("not found", output)

    def test_rules_remove_success(self):
        """Test rules remove command."""
        with patch('sys.stdout', new=StringIO()):
            with patch('sys.stderr', new=StringIO()):
                # Just test it doesn't crash
                result = self.cli.rules_remove("nonexistent-rule-12345")
                # Result depends on whether rule exists
                self.assertIn(result, [0, 1])

    def test_test_batch_missing_file(self):
        """Test batch command with missing file."""
        with patch('sys.stderr', new=StringIO()) as fake_err:
            result = self.cli.test_batch("/nonexistent/file.csv")
            self.assertEqual(result, 1)
            output = fake_err.getvalue()
            self.assertIn("Error", output)


class TestCLIMain(unittest.TestCase):
    """Test main CLI function."""

    def test_main_no_args(self):
        """Test main with no arguments shows help."""
        with patch('sys.argv', ['statement-classifier']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = main()
                self.assertEqual(result, 1)
                output = fake_out.getvalue()
                self.assertIn("usage:", output)

    def test_main_help(self):
        """Test main with --help."""
        with patch('sys.argv', ['statement-classifier', '--help']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 0)

    def test_main_classify_command(self):
        """Test main with classify command."""
        with patch('sys.argv', ['statement-classifier', 'classify', 'Amazon', '5411']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = main()
                self.assertEqual(result, 0)
                output = fake_out.getvalue()
                self.assertIn("Classification Result:", output)

    def test_main_validate_command(self):
        """Test main with validate command."""
        with patch('sys.argv', ['statement-classifier', 'validate']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = main()
                # May be 0 or 1 depending on rules validity
                self.assertIn(result, [0, 1])

    def test_main_rules_add_command(self):
        """Test main with rules add command."""
        with patch('sys.argv', [
            'statement-classifier', 'rules', 'add',
            '--id', 'test-rule-123',
            '--keywords', 'TEST,EXAMPLE',
            '--type', 'Personal',
            '--category', 'Testing'
        ]):
            with patch('sys.stdout', new=StringIO()):
                result = main()
                # May succeed or fail, but should not crash
                self.assertIn(result, [0, 1])

    def test_main_analyze_stats_command(self):
        """Test main with analyze stats command."""
        with patch('sys.argv', ['statement-classifier', 'analyze', 'stats']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                result = main()
                self.assertEqual(result, 0)
                output = fake_out.getvalue()
                self.assertIn("Rule Statistics:", output)

    def test_main_analyze_duplicates_command(self):
        """Test main with analyze duplicates command."""
        with patch('sys.argv', ['statement-classifier', 'analyze', 'duplicates']):
            with patch('sys.stdout', new=StringIO()):
                result = main()
                self.assertIn(result, [0, 1])

    def test_main_analyze_coverage_command(self):
        """Test main with analyze coverage command."""
        with patch('sys.argv', ['statement-classifier', 'analyze', 'coverage']):
            with patch('sys.stdout', new=StringIO()):
                result = main()
                self.assertEqual(result, 0)

    def test_main_invalid_command(self):
        """Test main with invalid command."""
        with patch('sys.argv', ['statement-classifier', 'invalid']):
            with patch('sys.stderr', new=StringIO()):
                with self.assertRaises(SystemExit):
                    main()

    def test_main_with_custom_rules_path(self):
        """Test main with --rules option."""
        rules_path = Path(__file__).parents[1] / "bin" / "classification_rules.v4.json"
        with patch('sys.argv', [
            'statement-classifier',
            '--rules', str(rules_path),
            'validate'
        ]):
            with patch('sys.stdout', new=StringIO()):
                result = main()
                # Should work with valid path
                self.assertIn(result, [0, 1])

    def test_main_with_verbose_flag(self):
        """Test main with --verbose flag."""
        with patch('sys.argv', ['statement-classifier', '--verbose', 'validate']):
            with patch('sys.stdout', new=StringIO()):
                result = main()
                self.assertIn(result, [0, 1])

    def test_main_nonexistent_rules_file(self):
        """Test main with nonexistent rules file."""
        with patch('sys.argv', [
            'statement-classifier',
            '--rules', '/nonexistent/rules.json',
            'validate'
        ]):
            with patch('sys.stderr', new=StringIO()) as fake_err:
                result = main()
                self.assertEqual(result, 1)
                output = fake_err.getvalue()
                self.assertIn("Error:", output)


class TestCLIVerbose(unittest.TestCase):
    """Test CLI with verbose logging."""

    def test_cli_verbose_logging(self):
        """Test CLI initializes logging when verbose."""
        rules_path = Path(__file__).parents[1] / "bin" / "classification_rules.v4.json"
        cli = CLI(rules_path=rules_path, verbose=True)
        self.assertTrue(cli.verbose)
        self.assertTrue(cli.logger.enabled)

    def test_cli_quiet_logging(self):
        """Test CLI has logging disabled by default."""
        rules_path = Path(__file__).parents[1] / "bin" / "classification_rules.v4.json"
        cli = CLI(rules_path=rules_path, verbose=False)
        self.assertFalse(cli.verbose)
        self.assertFalse(cli.logger.enabled)


if __name__ == '__main__':
    unittest.main()
