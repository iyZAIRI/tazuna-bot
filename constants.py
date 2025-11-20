"""Constants for the Uma Musume Discord bot."""

# Stat Emojis
EMOJI_SPEED = "<:speed:1440769160182366259>"
EMOJI_STAMINA = "<:stamina:1440769173880832081>"
EMOJI_POWER = "<:power:1440769145707827382>"
EMOJI_GUTS = "<:guts:1440769099985719528>"
EMOJI_WIT = "<:wit:1440769186967326872>"

# Aptitude/Rank Emojis (A-G scale)
EMOJI_RANK_A = "<:Rank_A:1440798305717063842>"
EMOJI_RANK_B = "<:Rank_B:1440798321215148135>"
EMOJI_RANK_C = "<:Rank_C:1440798337719865444>"
EMOJI_RANK_D = "<:Rank_D:1440798351896608970>"
EMOJI_RANK_E = "<:Rank_E:1440798367805341796>"
EMOJI_RANK_F = "<:Rank_F:1440798384721104906>"
EMOJI_RANK_G = "<:Rank_G:1440798401267499221>"

# Rarity Emojis
EMOJI_SSR = "<:ssr:1441158280184467670>"
EMOJI_SR = "<:sr:1441158302435246281>"
EMOJI_R = "<:r_:1441158255995916319>"

# Support Card Type Emojis
EMOJI_PAL = "<:pal:1441157673008632099>"

# Running Style Emojis
EMOJI_FRONT_RUNNER = "🏃"
EMOJI_PACE_CHASER = "👑"
EMOJI_LATE = "🎯"
EMOJI_END_CLOSER = "⚡"

# Rank mapping for aptitude grades
RANK_EMOJIS = {
    "A": EMOJI_RANK_A,
    "B": EMOJI_RANK_B,
    "C": EMOJI_RANK_C,
    "D": EMOJI_RANK_D,
    "E": EMOJI_RANK_E,
    "F": EMOJI_RANK_F,
    "G": EMOJI_RANK_G,
    "?": "❓"
}

# Skill Ability Type Mapping
SKILL_ABILITY_TYPES = {
    1: "Speed Stat",
    2: "Stamina Stat",
    3: "Power Stat",
    4: "Guts Stat",
    5: "Wit Stat",
    6: "Strategy Change",
    8: "Vision",
    9: "Stamina Recovery",
    10: "Gate Start",
    13: "Rush Time",
    21: "Velocity",
    27: "Velocity",
    28: "Maneuverability",
    31: "Acceleration",
    35: "Surrounded Avoidance",
}

def get_ability_type_name(ability_type: int) -> str:
    """Get ability type name from ability_type number."""
    return SKILL_ABILITY_TYPES.get(ability_type, f"Unknown ({ability_type})")

# Skill Icon Emojis (icon_id -> Discord emoji)
SKILL_ICON_EMOJIS = {
    10011: "<:utx_ico_skill_10011:1440849961867677820>",
    10012: "<:utx_ico_skill_10012:1440850073163399280>",
    10014: "<:utx_ico_skill_10014:1440850086836834334>",
    10021: "<:utx_ico_skill_10021:1440850102183788756>",
    10024: "<:utx_ico_skill_10024:1440850119846269119>",
    10031: "<:utx_ico_skill_10031:1440850151177715803>",
    10034: "<:utx_ico_skill_10034:1440850165740208128>",
    10041: "<:utx_ico_skill_10041:1440850231205040262>",
    10044: "<:utx_ico_skill_10044:1440850246979813507>",
    10051: "<:utx_ico_skill_10051:1440850260892319869>",
    10054: "<:utx_ico_skill_10054:1440850280345243741>",
    10061: "<:utx_ico_skill_10061:1440850298485870866>",
    10062: "<:utx_ico_skill_10062:1440850314206122167>",
    20011: "<:utx_ico_skill_20011:1440850328898768959>",
    20012: "<:utx_ico_skill_20012:1440850347525406751>",
    20013: "<:utx_ico_skill_20013:1440850364982366248>",
    20014: "<:utx_ico_skill_20014:1440850397731356724>",
    20021: "<:utx_ico_skill_20021:1440850417008250921>",
    20022: "<:utx_ico_skill_20022:1440850437841354942>",
    20023: "<:utx_ico_skill_20023:1440850453335244850>",
    20024: "<:utx_ico_skill_20024:1440850470209060904>",
    20041: "<:utx_ico_skill_20041:1440850493273538690>",
    20042: "<:utx_ico_skill_20042:1440850675863912599>",
    20043: "<:utx_ico_skill_20043:1440850828184518757>",
    20044: "<:utx_ico_skill_20044:1440851056874618995>",
    20051: "<:utx_ico_skill_20051:1440851080576630927>",
    20052: "<:utx_ico_skill_20052:1440851106426261517>",
    20061: "<:utx_ico_skill_20061:1440851129876480040>",
    20062: "<:utx_ico_skill_20062:1440851157173010452>",
    20064: "<:utx_ico_skill_20064:1440851179893555270>",
    20091: "<:utx_ico_skill_20091:1440851353634082966>",
    20092: "<:utx_ico_skill_20092:1440851391760302182>",
    20101: "<:utx_ico_skill_20101:1440851415902715914>",
    20102: "<:utx_ico_skill_20102:1440851442280960180>",
    20111: "<:utx_ico_skill_20111:1440851462023286906>",
    20112: "<:utx_ico_skill_20112:1440851502087540926>",
    20121: "<:utx_ico_skill_20121:1440853027488530586>",
    20122: "<:utx_ico_skill_20122:1440853060237791263>",
    20131: "<:utx_ico_skill_20131:1440853084212428941>",
    20132: "<:utx_ico_skill_20132:1440853099987341492>",
    30011: "<:utx_ico_skill_30011:1440853120652546159>",
    30012: "<:utx_ico_skill_30012:1440853271869788274>",
    30021: "<:utx_ico_skill_30021:1440853286587465869>",
    30022: "<:utx_ico_skill_30022:1440853344334778450>",
    30041: "<:utx_ico_skill_30041:1440853367596384329>",
    30051: "<:utx_ico_skill_30051:1440853385325576234>",
    30052: "<:utx_ico_skill_30052:1440853402182483998>",
    30071: "<:utx_ico_skill_30071:1440853416716013578>",
    30072: "<:utx_ico_skill_30072:1440853430867329034>",
    40012: "<:utx_ico_skill_40012:1440853446554030101>",
}


def get_skill_icon_emoji(icon_id: int) -> str:
    """Get Discord emoji for skill icon ID."""
    return SKILL_ICON_EMOJIS.get(icon_id, "🎯")  # Default to target emoji if not found

# Support Card Command ID Mapping (Training/Stat Types)
SUPPORT_CARD_TYPES = {
    101: "Speed",
    102: "Power",
    103: "Guts",
    105: "Stamina",
    106: "Wit",
    0: "Pal"  # Friendship/Group cards
}

def get_support_card_type_emoji(command_id: int) -> str:
    """Get emoji for support card training type."""
    emoji_map = {
        101: EMOJI_SPEED,
        102: EMOJI_POWER,
        103: EMOJI_GUTS,
        105: EMOJI_STAMINA,
        106: EMOJI_WIT,
        0: EMOJI_PAL
    }
    return emoji_map.get(command_id, "❓")

def get_rarity_emoji(rarity: int) -> str:
    """Get emoji for card rarity."""
    if rarity == 3:
        return EMOJI_SSR
    elif rarity == 2:
        return EMOJI_SR
    elif rarity == 1:
        return EMOJI_R
    return f"★{rarity}"  # Fallback for unexpected rarities
