import unittest

from theme_design import THEMES, validate_all_themes


REQUIRED_TOKENS = {
    'background',
    'surface',
    'surface_alt',
    'text',
    'text_muted',
    'border',
    'input_border',
    'primary',
    'primary_hover',
    'primary_text',
    'secondary_hover',
    'focus',
    'comparison_border',
    'comparison_hover',
    'done_surface',
    'done_border',
    'index_bg',
    'drag_handle',
}


class ThemeDesignTests(unittest.TestCase):
    def test_light_and_dark_themes_exist(self):
        self.assertEqual(set(THEMES), {'light', 'dark'})

    def test_themes_have_required_tokens(self):
        for theme in THEMES.values():
            with self.subTest(theme=theme.key):
                self.assertEqual(set(theme.colors), REQUIRED_TOKENS)

    def test_themes_pass_validation(self):
        self.assertEqual(validate_all_themes(), [])


if __name__ == '__main__':
    unittest.main()
