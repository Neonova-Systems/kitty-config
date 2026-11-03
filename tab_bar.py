# tab_bar.py — custom kitty tab bar: the built-in fade tabs stay on the left
# and the active session (workspace) name is right-aligned in the tab palette
# colors. Loaded by kitty when tab_bar_style is "custom"; if draw_tab raises,
# kitty logs the error and falls back to the built-in fade style.
from kitty.fast_data_types import Screen, wcswidth
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    as_rgb,
    draw_tab_with_fade,
)
from kitty.utils import color_as_int


def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_tab_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:
    x = draw_tab_with_fade(draw_data, screen, tab, before, max_tab_length, index, is_last, extra_data)
    # for_layout is the measuring pass: move the cursor only, draw nothing.
    if not is_last or extra_data.for_layout:
        return x
    name = (tab.active_session_name or '').strip()
    if not name:
        return x
    name = f' {name} '
    width = max(0, wcswidth(name))
    space = screen.columns - screen.cursor.x
    if space <= width:
        # Not enough room: keep the tail of the name and mark the cut.
        while name and width + 1 > space:
            name = name[:-1]
            width = max(0, wcswidth(name))
        if not name:
            return x
        name = f'{name}…'
        width += 1
    # Fill the gap with the bare bar background, then the name block in the
    # inactive tab colors (dark bg, blue text).
    bar_bg = as_rgb(color_as_int(draw_data.default_bg))
    screen.cursor.fg = bar_bg
    screen.cursor.bg = bar_bg
    screen.draw(' ' * (space - width))
    screen.cursor.fg = as_rgb(color_as_int(draw_data.inactive_fg))
    screen.cursor.bg = as_rgb(color_as_int(draw_data.inactive_bg))
    screen.draw(name)
    return screen.cursor.x
