def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(ch * 2 for ch in hex_color)
    return ", ".join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


STORE_NAME = "VOID CLOTHING"
STORE_LOGO = "/static/images/logo.png"

STORE_PHONE = "919193469637"
STORE_INSTAGRAM = "https://www.instagram.com/syco_dkzz/"
STORE_ADDRESS = ""

CATEGORIES = [
    {"name": "T-Shirts",        "slug": "Tshirt",      "image": "tshirt.jpg"},
    {"name": "Shirts",          "slug": "Shirt",       "image": "shirt.jpg"},
    {"name": "Jeans & Cargos",  "slug": "Jeans",       "image": "jeans.jpg"},
    {"name": "Hoodies",         "slug": "Hoodie",      "image": "hoodie.jpg"},
    {"name": "Accessories",     "slug": "Accessories", "image": "hat.jpg"},
]


BG_COLOR = "#FAFAF8"         
BG_ALT_COLOR = "#F3F4F6"     
SURFACE_COLOR = "#FFFFFF"   
SURFACE_2_COLOR = "#F9FAFB"  
SURFACE_3_COLOR = "#F3F4F6"  
SURFACE_4_COLOR = "#E5E7EB"   

TEXT_COLOR = "#111827"       
TEXT_SECONDARY_COLOR = "#374151" 
TEXT_SOFT_COLOR = "#6B7280"   
MUTED_COLOR = "#9CA3AF"      
BORDER_COLOR = "#E5E7EB"          

PRIMARY_COLOR = "#111827"     
SECONDARY_COLOR = "#F3F4F6"  
ACCENT_COLOR = "#111827"     
ACCENT_2_COLOR = "#374151"   
ACCENT_SOFT_COLOR = "rgba(17, 24, 39, 0.06)" 

SUCCESS_COLOR = "#16A34A"
DANGER_COLOR = "#DC2626"
WARNING_COLOR = "#B45309"
INFO_COLOR = "#2563EB"
HIGHLIGHT_COLOR = "#7C3AED"

SHADOW_COLOR = "rgba(17, 24, 39, 0.08)"


ACCENT_COLOR_RGB = hex_to_rgb(ACCENT_COLOR)
SUCCESS_COLOR_RGB = hex_to_rgb(SUCCESS_COLOR)
DANGER_COLOR_RGB = hex_to_rgb(DANGER_COLOR)
WARNING_COLOR_RGB = hex_to_rgb(WARNING_COLOR)
INFO_COLOR_RGB = hex_to_rgb(INFO_COLOR)
HIGHLIGHT_COLOR_RGB = hex_to_rgb(HIGHLIGHT_COLOR)
