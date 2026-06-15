"""Theme tokens and validation helpers for terminal review.

This module is intentionally not wired into the PyQt UI yet. It lets the
palette be reviewed and tested from the terminal before the app stylesheet is
updated.
"""

from dataclasses import dataclass


MIN_TEXT_CONTRAST = 4.5


@dataclass(frozen=True)
class ContrastCheck:
    foreground: str
    background: str
    minimum: float = MIN_TEXT_CONTRAST


@dataclass(frozen=True)
class ThemePalette:
    key: str
    label: str
    colors: dict[str, str]
    contrast_checks: tuple[ContrastCheck, ...]


LIGHT_THEME = ThemePalette(
    key='light',
    label='Light',
    colors={
        'background': '#f7f8fa',
        'surface': '#ffffff',
        'surface_alt': '#f8fafc',
        'text': '#111827',
        'text_muted': '#4b5563',
        'border': '#d1d5db',
        'input_border': '#e2e8f0',
        'primary': '#2563eb',
        'primary_hover': '#1d4ed8',
        'primary_text': '#ffffff',
        'secondary_hover': '#f8fbff',
        'focus': '#16a34a',
        'comparison_border': '#dc2626',
        'comparison_hover': '#f87171',
        'done_surface': '#d1fae5',
        'done_border': '#10b981',
        'index_bg': '#eff6ff',
        'drag_handle': '#64748b',
    },
    contrast_checks=(
        ContrastCheck('text', 'background'),
        ContrastCheck('text', 'surface'),
        ContrastCheck('text_muted', 'background'),
        ContrastCheck('text_muted', 'surface'),
        ContrastCheck('primary_text', 'primary'),
        ContrastCheck('text', 'done_surface'),
        ContrastCheck('primary', 'index_bg'),
    ),
)


DARK_THEME = ThemePalette(
    key='dark',
    label='Dark',
    colors={
        'background': '#111315',
        'surface': '#1b1f23',
        'surface_alt': '#23272e',
        'text': '#f4f6f8',
        'text_muted': '#b7c0cc',
        'border': '#38414a',
        'input_border': '#46515c',
        'primary': '#60a5fa',
        'primary_hover': '#93c5fd',
        'primary_text': '#0b1020',
        'secondary_hover': '#252b32',
        'focus': '#4ade80',
        'comparison_border': '#fb7185',
        'comparison_hover': '#fda4af',
        'done_surface': '#143b2c',
        'done_border': '#34d399',
        'index_bg': '#172b45',
        'drag_handle': '#94a3b8',
    },
    contrast_checks=(
        ContrastCheck('text', 'background'),
        ContrastCheck('text', 'surface'),
        ContrastCheck('text_muted', 'background'),
        ContrastCheck('text_muted', 'surface'),
        ContrastCheck('primary_text', 'primary'),
        ContrastCheck('text', 'done_surface'),
        ContrastCheck('primary', 'index_bg'),
    ),
)


THEMES = {
    LIGHT_THEME.key: LIGHT_THEME,
    DARK_THEME.key: DARK_THEME,
}


def normalize_hex_color(value: str) -> str:
    candidate = value.strip().lower()
    if not candidate.startswith('#'):
        raise ValueError(f'Color must start with #: {value!r}')
    if len(candidate) != 7:
        raise ValueError(f'Color must use 6 hex digits: {value!r}')

    int(candidate[1:], 16)
    return candidate


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    color = normalize_hex_color(value)
    return (
        int(color[1:3], 16),
        int(color[3:5], 16),
        int(color[5:7], 16),
    )


def _linearize_channel(channel: int) -> float:
    value = channel / 255
    if value <= 0.03928:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    red, green, blue = hex_to_rgb(hex_color)
    return (
        0.2126 * _linearize_channel(red)
        + 0.7152 * _linearize_channel(green)
        + 0.0722 * _linearize_channel(blue)
    )


def contrast_ratio(foreground: str, background: str) -> float:
    foreground_luminance = relative_luminance(foreground)
    background_luminance = relative_luminance(background)
    lighter = max(foreground_luminance, background_luminance)
    darker = min(foreground_luminance, background_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def contrast_results(theme: ThemePalette) -> list[tuple[ContrastCheck, float, bool]]:
    results = []
    for check in theme.contrast_checks:
        ratio = contrast_ratio(
            theme.colors[check.foreground],
            theme.colors[check.background],
        )
        results.append((check, ratio, ratio >= check.minimum))
    return results


def validate_theme(theme: ThemePalette) -> list[str]:
    errors = []
    for token, color in theme.colors.items():
        try:
            normalize_hex_color(color)
        except ValueError as exc:
            errors.append(f'{theme.key}.{token}: {exc}')

    for check, ratio, passed in contrast_results(theme):
        if not passed:
            errors.append(
                f'{theme.key}.{check.foreground} on {check.background}: '
                f'{ratio:.2f} contrast, expected >= {check.minimum:.2f}'
            )

    return errors


def validate_all_themes() -> list[str]:
    errors = []
    for theme in THEMES.values():
        errors.extend(validate_theme(theme))
    return errors
