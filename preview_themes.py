"""Terminal preview for the proposed light and dark palettes."""

from __future__ import annotations

import argparse
import sys

from theme_design import THEMES, ThemePalette, contrast_results, validate_theme


def _rgb_from_hex(value: str) -> tuple[int, int, int]:
    return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)


def color_swatch(hex_color: str, enabled: bool) -> str:
    if not enabled:
        return '      '

    red, green, blue = _rgb_from_hex(hex_color)
    return f'\x1b[48;2;{red};{green};{blue}m      \x1b[0m'


def print_theme(theme: ThemePalette, use_color: bool) -> None:
    print(f'\nTheme: {theme.label} ({theme.key})')
    print('Palette:')
    longest_token = max(len(token) for token in theme.colors)
    for token, hex_color in theme.colors.items():
        print(f'  {token:<{longest_token}}  {color_swatch(hex_color, use_color)}  {hex_color}')

    print('\nContrast checks:')
    for check, ratio, passed in contrast_results(theme):
        status = 'PASS' if passed else 'FAIL'
        pair = f'{check.foreground} on {check.background}'
        print(f'  {pair:<28} {ratio:>5.2f}:1  {status}')

    errors = validate_theme(theme)
    if errors:
        print('\nValidation errors:')
        for error in errors:
            print(f'  - {error}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Preview proposed light/dark theme tokens in the terminal.'
    )
    parser.add_argument(
        '--theme',
        choices=['all', *THEMES.keys()],
        default='all',
        help='Theme to preview. Defaults to all.',
    )
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable ANSI color swatches.',
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selected_themes = THEMES.values() if args.theme == 'all' else [THEMES[args.theme]]
    has_errors = False

    for theme in selected_themes:
        print_theme(theme, use_color=not args.no_color)
        has_errors = has_errors or bool(validate_theme(theme))

    return 1 if has_errors else 0


if __name__ == '__main__':
    sys.exit(main())
