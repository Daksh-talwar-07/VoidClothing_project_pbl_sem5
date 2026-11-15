def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(ch * 2 for ch in hex_color)
    return ", ".join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


# =====================================================================
# STORE BRANDING
# =====================================================================
STORE_NAME = "VOID CLOTHING"
STORE_LOGO = "/static/images/logo.png"

STORE_PHONE = "919193469637"
STORE_INSTAGRAM = "https://www.instagram.com/syco_dkzz/"
STORE_ADDRESS = ""

# Product categories. Single source of truth: the homepage rail, the
# collection filter and both admin forms all read this list.
# name = label shown to customers, slug = value stored in DB / used in URLs,
# image = file in static/images/categories/  (replace these with your own photos)
CATEGORIES = [
    {"name": "T-Shirts",        "slug": "Tshirt",      "image": "tshirt.jpg"},
    {"name": "Shirts",          "slug": "Shirt",       "image": "shirt.jpg"},
    {"name": "Jeans & Cargos",  "slug": "Jeans",       "image": "jeans.jpg"},
    {"name": "Hoodies",         "slug": "Hoodie",      "image": "hoodie.jpg"},
    {"name": "Accessories",     "slug": "Accessories", "image": "hat.jpg"},
]


# =====================================================================
# COLOR PALETTE
# This is the ONLY place that needs to change per-client. Every color
# used anywhere on the site (storefront + admin) is generated from
# these values. To onboard a new client, copy this file, swap the
# hex codes below to their brand colors, and nothing else needs to
# be touched (no template or CSS edits required).
# =====================================================================

# ---- Backgrounds (page -> elevated surfaces, lightest to darkest) ----
BG_COLOR = "#FAFAF8"          # page background
BG_ALT_COLOR = "#F3F4F6"      # secondary background / gradients
SURFACE_COLOR = "#FFFFFF"     # card / panel background
SURFACE_2_COLOR = "#F9FAFB"   # recessed surface (inputs, table stripes)
SURFACE_3_COLOR = "#F3F4F6"   # hover surface
SURFACE_4_COLOR = "#E5E7EB"   # active/disabled surface

# ---- Text ----
TEXT_COLOR = "#111827"        # primary text
TEXT_SECONDARY_COLOR = "#374151"  # secondary text
TEXT_SOFT_COLOR = "#6B7280"   # tertiary text
MUTED_COLOR = "#9CA3AF"       # most muted text / placeholders / icons

# ---- Borders ----
BORDER_COLOR = "#E5E7EB"          # standard hairline border
BORDER_STRONG_COLOR = "#D1D5DB"   # emphasized border

# ---- Brand / buttons ----
PRIMARY_COLOR = "#111827"     # primary buttons, CTAs, meta theme-color
SECONDARY_COLOR = "#F3F4F6"   # secondary buttons / chips
ACCENT_COLOR = "#111827"      # highlighted price/link color
ACCENT_2_COLOR = "#374151"    # accent hover / secondary accent
ACCENT_SOFT_COLOR = "rgba(17, 24, 39, 0.06)"  # tinted accent background

# ---- Status colors (order/customer state indicators) ----
# These are intentionally independent of the brand palette above so
# that "pending", "success", "error" etc. stay visually consistent
# and recognizable across every client's theme.
SUCCESS_COLOR = "#16A34A"
DANGER_COLOR = "#DC2626"
WARNING_COLOR = "#B45309"
INFO_COLOR = "#2563EB"
HIGHLIGHT_COLOR = "#7C3AED"

SHADOW_COLOR = "rgba(17, 24, 39, 0.08)"


# =====================================================================
# Derived values (do not edit below this line)
# =====================================================================
ACCENT_COLOR_RGB = hex_to_rgb(ACCENT_COLOR)
SUCCESS_COLOR_RGB = hex_to_rgb(SUCCESS_COLOR)
DANGER_COLOR_RGB = hex_to_rgb(DANGER_COLOR)
WARNING_COLOR_RGB = hex_to_rgb(WARNING_COLOR)
INFO_COLOR_RGB = hex_to_rgb(INFO_COLOR)
HIGHLIGHT_COLOR_RGB = hex_to_rgb(HIGHLIGHT_COLOR)
