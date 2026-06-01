"""The cinestyle theme catalog and film-look definitions.

Each :class:`~cinestyle.theme.Theme` is defined from a small set of sourced
"hero" colors; the categorical palette and colormaps are derived from them. Where
an authoritative, openly-licensed palette exists it is used verbatim (Wes
Anderson via the ``wesanderson`` R package; Ghibli via the ``ghibli`` R
package); the rest are sourced from documented color analyses and credited in
each theme's ``note``. Film titles are used descriptively for inspired-by
tributes and are trademarks of their respective owners; cinestyle is not
affiliated with or endorsed by any rights holder.
"""

from __future__ import annotations

from .luts import Look
from .theme import Theme

# --------------------------------------------------------------------- looks
# Original, hand-built grades (no third-party film-emulation LUTs redistributed).
LOOKS: dict[str, Look] = {
    "neon_night": Look(
        "neon_night",
        gamma=0.95,
        gain=1.05,
        saturation=1.25,
        shadow_tint="#0A0030",
        highlight_tint="#00E5FF",
        tint_strength=0.25,
    ),
    "teal_orange": Look(
        "teal_orange",
        saturation=1.15,
        shadow_tint="#0E4D64",
        highlight_tint="#E0531F",
        tint_strength=0.30,
    ),
    "warm_amber": Look(
        "warm_amber",
        gain=1.05,
        saturation=0.92,
        shadow_tint="#2C1A0A",
        highlight_tint="#F8C457",
        tint_strength=0.28,
    ),
    "noir_contrast": Look(
        "noir_contrast",
        gamma=0.85,
        saturation=0.15,
        shadow_tint="#000000",
        highlight_tint="#FFFFFF",
        tint_strength=0.10,
    ),
    "verdant": Look(
        "verdant",
        saturation=1.10,
        shadow_tint="#001100",
        highlight_tint="#00FF41",
        tint_strength=0.30,
    ),
}


def get_look(name: str) -> Look:
    """Return the named film-look grade."""
    return LOOKS[name]


# -------------------------------------------------------------------- themes
_THEME_LIST: list[Theme] = [
    Theme(
        name="noir",
        heroes=("#FFFFFF", "#8B0000", "#9A9A9A", "#C0392B", "#5A5A5A"),
        cycle_length=5,
        background="#0A0A0A",
        surface="#141414",
        foreground="#F5F5F5",
        muted="#333333",
        grid=False,
        font_family="Oswald",
        seq_anchor="#8B0000",
        div_pair=("#1E6F8C", "#8B0000"),
        look="noir_contrast",
        film="Film noir / chiaroscuro (1940s-50s, neo-noir)",
        note="Chiaroscuro greyscale plus a blood-red accent; hex by construction.",
    ),
    Theme(
        name="ghibli",
        heroes=("#3C989B", "#7D9B5F", "#E3BBA1", "#F0A3B0", "#A3C5E0", "#D2CF39"),
        background="#FBF7EC",
        surface="#FBF7EC",
        foreground="#3A3A2E",
        muted="#D8D2C0",
        grid=True,
        font_family="EB Garamond",
        seq_anchor="#7D9B5F",
        div_pair=("#3C989B", "#E3BBA1"),
        film="Studio Ghibli (Hayao Miyazaki)",
        note="Derived from the ghibli R package (ewenme) / Movies in Color.",
    ),
    Theme(
        name="wes_anderson",
        heroes=("#F1BB7B", "#FD6467", "#5B1A18", "#D67236", "#3B9AB2", "#EBCC2A"),
        background="#F3E9D2",
        surface="#F3E9D2",
        foreground="#5B1A18",
        muted="#CBB99A",
        grid=False,
        framed=True,
        font_family="Jost",
        seq_anchor="#D67236",
        div_pair=("#3B9AB2", "#FD6467"),
        film="Wes Anderson (The Grand Budapest Hotel, The Life Aquatic)",
        note="Grand Budapest + Zissou, from the wesanderson R package (karthik).",
    ),
    Theme(
        name="blade_runner",
        heroes=("#08F7FE", "#FE53BB", "#F5D300", "#09FBD3", "#B537F2"),
        background="#05060A",
        surface="#0A0C12",
        foreground="#08F7FE",
        muted="#2E2150",
        grid=True,
        font_family="Orbitron",
        glow=0.7,
        seq_anchor="#08F7FE",
        div_pair=("#FE53BB", "#08F7FE"),
        look="neon_night",
        film="Blade Runner (1982) -- neon-noir / synthwave reading",
        note="Neon reading of the 1982 film; BR2049's grade is muted amber/teal.",
    ),
    Theme(
        name="star_wars",
        heroes=("#FFD700", "#1E90FF", "#C0392B", "#D2B48C", "#C0C0C0", "#4A6FA5"),
        cycle_length=6,
        background="#000000",
        surface="#0E0E12",
        foreground="#FFD700",
        muted="#2A2A33",
        grid=False,
        font_family="Oswald",
        title_weight="bold",
        seq_anchor="#FFD700",
        div_pair=("#1E90FF", "#C0392B"),
        film="Star Wars (original-trilogy-leaning)",
        note="Saber blue/Sith red, gold, Tatooine sand; hex by construction.",
    ),
    Theme(
        name="matrix",
        heroes=("#00FF41", "#03A062", "#008F11", "#003B00"),
        cycle_length=6,
        background="#0D0208",
        surface="#04120A",
        foreground="#00FF41",
        muted="#0A3315",
        grid=True,
        font_family="Share Tech Mono",
        glow=0.5,
        seq_anchor="#00FF41",
        film="The Matrix (Wachowskis)",
        note="Monochrome 'digital rain' green ramp; SchemeColor Matrix Code Green.",
    ),
    Theme(
        name="dune",
        heroes=("#E79B07", "#D5C0A1", "#6E6253", "#B07A43"),
        background="#EAD9BE",
        surface="#EAD9BE",
        foreground="#3A2C1C",
        muted="#C9B594",
        grid=True,
        font_family="Space Grotesk",
        seq_anchor="#E79B07",
        div_pair=("#0E4D64", "#E79B07"),
        look="warm_amber",
        film="Dune (Villeneuve, 2021)",
        note="Monochrome spice-amber / dune-sand; SchemeColor Dune + colorswall.",
    ),
    Theme(
        name="fury_road",
        heroes=("#E0531F", "#F2A900", "#0E4D64", "#1B6A8C"),
        cycle_length=6,
        background="#171210",
        surface="#211712",
        foreground="#F2A900",
        muted="#3A4A52",
        grid=False,
        font_family="Anton",
        seq_anchor="#E0531F",
        div_pair=("#0E4D64", "#E0531F"),
        look="teal_orange",
        film="Mad Max: Fury Road (colorist Eric Whipp)",
        note="Saturated teal-and-orange at the extreme; hex from documented intent.",
    ),
    Theme(
        name="kill_bill",
        heroes=("#FCD612", "#D61A1F", "#7A0A0A", "#E08A00"),
        cycle_length=5,
        background="#0A0A0A",
        surface="#161616",
        foreground="#FCD612",
        muted="#3A2A00",
        grid=False,
        font_family="Bebas Neue",
        seq_anchor="#FCD612",
        div_pair=("#FCD612", "#D61A1F"),
        film="Kill Bill (Tarantino)",
        note="Bride-yellow, black and blood-red; SchemeColor Kill Bill.",
    ),
    Theme(
        name="in_the_mood",
        heroes=("#CC0000", "#D58D29", "#F1C232", "#660000", "#2E5A4A"),
        background="#140A0A",
        surface="#1C1010",
        foreground="#F1C232",
        muted="#3A2420",
        grid=False,
        font_family="EB Garamond",
        seq_anchor="#CC0000",
        div_pair=("#2E5A4A", "#CC0000"),
        look="warm_amber",
        film="In the Mood for Love (Wong Kar-wai)",
        note="Smoldering reds/golds against cool green; color-hex 1061098.",
    ),
]

THEMES: dict[str, Theme] = {theme.name: theme for theme in _THEME_LIST}


def get_theme(name: str) -> Theme:
    """Return a theme by name (e.g. ``"blade_runner"``)."""
    try:
        return THEMES[name]
    except KeyError:
        raise KeyError(
            f"Unknown theme {name!r}. Available: {', '.join(sorted(THEMES))}"
        ) from None


def list_themes() -> list[str]:
    """Return the names of all built-in themes, in catalog order."""
    return [theme.name for theme in _THEME_LIST]


def register(prefix: str = "cinestyle") -> list[str]:
    """Register every built-in theme as a named matplotlib style sheet.

    Also registers each theme's colormaps and named colors, so the styles are
    fully usable via ``plt.style.use(...)`` afterwards.

    Args:
        prefix: Style-sheet name prefix; themes register as ``<prefix>-<name>``.

    Returns:
        The registered style-sheet names.
    """
    return [theme.register(f"{prefix}-{theme.name}") for theme in _THEME_LIST]
