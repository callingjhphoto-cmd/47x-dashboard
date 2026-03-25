#!/usr/bin/env python3
"""
Reads SWF research profiles and generates a JavaScript deepProfiles object
for swf.html. Extracts executive summary, mandate, timeline, macro context
from each research markdown file.
"""

import os
import re
import json
import glob

PROFILE_DIR = os.path.expanduser("~/Documents/Claude/research/swf_profiles")

# Map fund ranks (from swf.html) to research file names
# This mapping connects the fund table entries to their research files
FUND_MAP = {
    1: "pif_saudi",
    2: "adia_abudhabi",
    3: "kia_kuwait",
    4: "qia_qatar",
    5: "icd_dubai",
    6: "gosi_saudi",
    7: "mubadala_abudhabi",
    8: "hassana_saudi",
    9: "royal_group_abudhabi",
    10: "adq_abudhabi",
    11: "lunate_abudhabi",
    12: "snb_capital_saudi",
    13: "oia_oman",
    14: "dubai_holding",
    15: "al_rajhi_capital",
    16: "jadwa_saudi",
    17: "gfh_bahrain",
    18: "nbk_wealth_kuwait",
    19: "adcg_abudhabi",
    20: "yba_kanoo",
    21: "mumtalakat_bahrain",
    22: "al_qasimi_sharjah",
    23: "eia_uae",
    24: "aramco_ventures",
    25: "landmark_group",
    26: "future_fund_oman",
    27: "waha_capital",
    28: "gulf_capital_inv_kuwait",
    29: "wafra_international",
    30: "majid_al_futtaim",
    31: "al_gurg_group",
    32: "gulf_capital_abudhabi",
    33: "svc_saudi",
    34: "stv_saudi",
    35: "jada_pif",
    36: "riyad_capital",
    37: "sanabil_pif",
    38: "tvm_capital",
    39: "shorooq_abudhabi",
    40: "wamda_dubai",
    41: "neom_fund",
    42: "adcg_abudhabi",  # Abu Dhabi Developmental Holding
    43: "stc_ventures",
    44: "taqnia_saudi",
    45: "hub71_abudhabi",
    46: "beco_capital",
    47: "global_ventures",
    48: "nuwa_capital",
    49: "mevp_dubai",
    50: "investcorp_bahrain",
}


def find_profile(name):
    """Find the best research file for a fund, checking all loops."""
    # Check loop5 first (most refined), then loop4, loop3, loop2, then root
    for loop in ["loop5", "loop4", "loop3", "loop2", ""]:
        if loop:
            path = os.path.join(PROFILE_DIR, loop, f"{name}.md")
        else:
            path = os.path.join(PROFILE_DIR, f"{name}.md")
        if os.path.exists(path):
            return path
    return None


def extract_section(text, heading_pattern, max_chars=2000):
    """Extract content under a heading pattern."""
    # Try to find the section
    match = re.search(heading_pattern, text, re.IGNORECASE | re.MULTILINE)
    if not match:
        return None

    start = match.end()
    # Find next heading of same or higher level
    next_heading = re.search(r'\n#{1,3}\s', text[start:])
    if next_heading:
        content = text[start:start + next_heading.start()]
    else:
        content = text[start:start + max_chars]

    # Clean up markdown formatting for HTML
    content = content.strip()

    # Remove metadata tables (| Field | Value | patterns)
    content = re.sub(r'\|[^\n]*\|[^\n]*\n?', '', content)
    content = re.sub(r'---+', '', content)

    # Remove citation markers
    content = re.sub(r'\[cite:\s*[\d,\s]+\]', '', content)

    # Remove markdown list bullets that are just formatting
    content = re.sub(r'^\s*\*\s+', '', content, flags=re.MULTILINE)

    # Convert markdown formatting to HTML
    content = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', content)
    content = re.sub(r'\n\n+', '</p><p>', content)
    content = re.sub(r'\n', ' ', content)

    # Clean up empty paragraphs and extra spaces
    content = re.sub(r'<p>\s*</p>', '', content)
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()

    # Skip if content is too short after cleanup (likely just metadata)
    if len(content) < 50:
        return None

    if not content.startswith('<p>'):
        content = '<p>' + content
    if not content.endswith('</p>'):
        content += '</p>'

    return content[:max_chars]


def extract_executive(text):
    """Extract executive summary / key points."""
    # Try Key Points section first
    patterns = [
        r'#{1,3}\s*Key Points.*?\n',
        r'#{1,3}\s*Executive Summary.*?\n',
        r'#{1,3}\s*Leading Paragraph.*?\n',
        r'#{1,3}\s*Overview.*?\n',
        r'#{1,3}\s*Introduction.*?\n',
    ]
    for p in patterns:
        result = extract_section(text, p, 1500)
        if result and len(result) > 100:
            return result

    # Fallback: first substantial paragraph after the metadata table
    match = re.search(r'\n---\n\n?#', text)
    if match:
        after = text[match.end():]
        # Skip the heading
        newline = after.find('\n')
        if newline > 0:
            after = after[newline:].strip()
            paras = after.split('\n\n')
            for p in paras:
                p = p.strip()
                if len(p) > 100 and not p.startswith('|') and not p.startswith('#'):
                    p = re.sub(r'\[cite:\s*[\d,\s]+\]', '', p)
                    p = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', p)
                    p = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', p)
                    return p[:1500]

    return None


def extract_mandate(text):
    """Extract mandate/strategy section."""
    patterns = [
        r'#{1,3}\s*.*?[Mm]andate.*?\n',
        r'#{1,3}\s*.*?[Ss]trateg.*?\n',
        r'#{1,3}\s*.*?[Ii]nvestment\s+[Ss]trategy.*?\n',
        r'#{1,3}\s*.*?[Pp]ortfolio\s+[Bb]reakdown.*?\n',
    ]
    for p in patterns:
        result = extract_section(text, p, 3000)
        if result and len(result) > 200:
            return result
    return None


def extract_timeline(text):
    """Extract historical timeline / deployment history."""
    patterns = [
        r'#{1,3}\s*.*?[Tt]imeline.*?\n',
        r'#{1,3}\s*.*?[Hh]istor.*?\n',
        r'#{1,3}\s*.*?[Dd]eployment\s+[Pp]attern.*?\n',
        r'#{1,3}\s*.*?[Rr]ecent.*?[Dd]eal.*?\n',
        r'#{1,3}\s*.*?[Rr]ecent.*?[Aa]ctivit.*?\n',
    ]
    for p in patterns:
        result = extract_section(text, p, 3000)
        if result and len(result) > 200:
            return result
    return None


def extract_macro(text):
    """Extract macro context."""
    patterns = [
        r'#{1,3}\s*.*?[Mm]acro.*?\n',
        r'#{1,3}\s*.*?[Gg]overnment\s+[Rr]elation.*?\n',
        r'#{1,3}\s*.*?[Rr]isk\s+[Mm]anagement.*?\n',
        r'#{1,3}\s*.*?[Ee]cosystem.*?\n',
        r'#{1,3}\s*.*?[Gg]eopolitical.*?\n',
    ]
    for p in patterns:
        result = extract_section(text, p, 2000)
        if result and len(result) > 100:
            return result
    return None


def js_escape(s):
    """Escape string for JavaScript single-quoted strings."""
    if not s:
        return ''
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    s = s.replace('\n', ' ')
    s = s.replace('\r', '')
    return s


def build_profiles():
    """Build all 50 deep profiles."""
    profiles = {}

    for rank, name in FUND_MAP.items():
        path = find_profile(name)
        if not path:
            print(f"WARNING: No research file for rank {rank} ({name})")
            continue

        with open(path, 'r') as f:
            text = f.read()

        executive = extract_executive(text)
        mandate = extract_mandate(text)
        timeline = extract_timeline(text)
        macro = extract_macro(text)

        if not executive:
            print(f"WARNING: No executive summary for rank {rank} ({name})")
            executive = f"Research profile available. Full analysis pending integration."

        if not mandate:
            mandate = executive  # Fallback

        if not timeline:
            timeline = "<p>Deployment timeline data being compiled from research.</p>"

        if not macro:
            macro = "<p>Macro context analysis pending integration.</p>"

        # Determine related funds by country
        related = []
        current_country = None
        country_map = {
            "pif_saudi": "Saudi", "gosi_saudi": "Saudi", "hassana_saudi": "Saudi",
            "snb_capital_saudi": "Saudi", "al_rajhi_capital": "Saudi", "jadwa_saudi": "Saudi",
            "svc_saudi": "Saudi", "stv_saudi": "Saudi", "jada_pif": "Saudi",
            "riyad_capital": "Saudi", "sanabil_pif": "Saudi", "stc_ventures": "Saudi",
            "taqnia_saudi": "Saudi", "aramco_ventures": "Saudi",
            "adia_abudhabi": "UAE", "mubadala_abudhabi": "UAE", "adq_abudhabi": "UAE",
            "royal_group_abudhabi": "UAE", "lunate_abudhabi": "UAE", "adcg_abudhabi": "UAE",
            "shorooq_abudhabi": "UAE", "hub71_abudhabi": "UAE", "gulf_capital_abudhabi": "UAE",
            "waha_capital": "UAE", "eia_uae": "UAE", "beco_capital": "UAE",
            "global_ventures": "UAE", "nuwa_capital": "UAE", "wamda_dubai": "UAE",
            "mevp_dubai": "UAE", "icd_dubai": "UAE", "dubai_holding": "UAE",
            "landmark_group": "UAE", "majid_al_futtaim": "UAE", "al_gurg_group": "UAE",
            "al_qasimi_sharjah": "UAE",
            "kia_kuwait": "Kuwait", "nbk_wealth_kuwait": "Kuwait",
            "gulf_capital_inv_kuwait": "Kuwait", "wafra_international": "Kuwait",
            "qia_qatar": "Qatar",
            "mumtalakat_bahrain": "Bahrain", "gfh_bahrain": "Bahrain", "investcorp_bahrain": "Bahrain",
            "oia_oman": "Oman", "future_fund_oman": "Oman",
            "yba_kanoo": "Bahrain", "tvm_capital": "UAE",
            "neom_fund": "Saudi",
        }

        current_country = country_map.get(name)
        if current_country:
            for r, n in FUND_MAP.items():
                if r != rank and country_map.get(n) == current_country:
                    related.append(r)
                    if len(related) >= 4:
                        break

        profiles[rank] = {
            'executive': js_escape(executive),
            'mandateDetail': js_escape(mandate),
            'timeline': js_escape(timeline),
            'macroContext': js_escape(macro),
            'relatedFunds': related,
        }

        print(f"OK rank {rank}: {name} (exec:{len(executive or '')} mandate:{len(mandate or '')} timeline:{len(timeline or '')} macro:{len(macro or '')})")

    return profiles


def generate_js(profiles):
    """Generate JavaScript deepProfiles object."""
    lines = ["var deepProfiles = {"]

    for rank in sorted(profiles.keys()):
        p = profiles[rank]
        related_str = json.dumps(p['relatedFunds'])
        lines.append(f"  {rank}: {{")
        lines.append(f"    executive: '{p['executive']}',")
        lines.append(f"    mandateDetail: '{p['mandateDetail']}',")
        lines.append(f"    timeline: '{p['timeline']}',")
        lines.append(f"    macroContext: '{p['macroContext']}',")
        lines.append(f"    relatedFunds: {related_str}")
        lines.append(f"  }},")

    lines.append("};")
    return '\n'.join(lines)


if __name__ == '__main__':
    print("Building deep profiles from research...")
    profiles = build_profiles()
    print(f"\nGenerated {len(profiles)} profiles")

    js = generate_js(profiles)

    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deep_profiles.js")
    with open(outpath, 'w') as f:
        f.write(js)

    print(f"Written to {outpath} ({len(js)} chars)")
