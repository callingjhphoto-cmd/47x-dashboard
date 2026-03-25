#!/usr/bin/env python3
"""
Build script: Embed research summaries + cross-fund investment analysis into swf.html

Task A: Scan research .md files, extract summaries, inject as JS object, update openInvestment()
Task C: Detect cross-fund investments by name similarity, inject co-investor chips
"""

import os
import re
import json
from difflib import SequenceMatcher
from collections import defaultdict

RESEARCH_DIR = os.path.expanduser("~/Documents/Claude/research/swf_investments")
SWF_HTML = os.path.expanduser("~/Documents/Claude/projects/47x-dashboard/swf.html")


# --- TASK A: Extract research summaries ---

def extract_summary(filepath, max_chars=1500):
    """Extract first 1500 chars of content, skipping metadata tables."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')
    content_start = 0
    in_table = False

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('| ') and '|' in stripped[1:]:
            in_table = True
            continue
        if in_table and not stripped.startswith('|'):
            in_table = False
        if stripped == '---' and i > 5:
            content_start = i + 1
            break

    if content_start == 0:
        content_start = min(5, len(lines))

    content = '\n'.join(lines[content_start:]).strip()

    # Clean markdown for HTML display
    content = re.sub(r'\[cite:\s*[\d,\s]+\]', '', content)
    content = content.replace('**', '')
    content = re.sub(r'(?<!\n)\*(?!\*)', '', content)
    content = re.sub(r'^#{1,4}\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n{3,}', '\n\n', content)

    if len(content) > max_chars:
        truncated = content[:max_chars]
        last_period = truncated.rfind('.')
        if last_period > max_chars * 0.7:
            content = truncated[:last_period + 1]
        else:
            content = truncated.rstrip() + '...'

    return content.strip()


def scan_research_files():
    """Scan all .md files in research dir, return dict of fund/slug -> summary."""
    summaries = {}
    if not os.path.isdir(RESEARCH_DIR):
        print(f"WARNING: {RESEARCH_DIR} not found")
        return summaries

    for fund_dir in sorted(os.listdir(RESEARCH_DIR)):
        fund_path = os.path.join(RESEARCH_DIR, fund_dir)
        if not os.path.isdir(fund_path):
            continue
        for md_file in sorted(os.listdir(fund_path)):
            if not md_file.endswith('.md'):
                continue
            slug = md_file[:-3]
            filepath = os.path.join(fund_path, md_file)
            try:
                summary = extract_summary(filepath)
                if summary:
                    key = f"{fund_dir}/{slug}"
                    summaries[key] = summary
                    print(f"  Extracted: {key} ({len(summary)} chars)")
            except Exception as e:
                print(f"  ERROR reading {filepath}: {e}")

    return summaries


# --- TASK C: Cross-fund investment analysis ---

def core_name(name):
    """Extract the core entity name, stripping parentheticals and generic suffixes."""
    # Remove parenthetical details
    n = re.sub(r'\s*\([^)]*\)', '', name).strip()
    # Remove trailing generic words
    n = re.sub(r'\s+(Group|Holdings|Ltd|Limited|Inc|Corp|Co|Company|International|Technologies|LP|JV|CV)\.?$', '', n, flags=re.IGNORECASE).strip()
    return n


def extract_investments_from_html(html):
    """Extract fund rank + investment names from the funds array."""
    fund_investments = []
    # Match each fund block's rank and investments array
    fund_pattern = re.compile(r"\{rank:(\d+),.*?investments:\[(.*?)\]", re.DOTALL)
    for fm in fund_pattern.finditer(html):
        rank = int(fm.group(1))
        inv_block = fm.group(2)
        inv_names = re.findall(r"name:'((?:[^'\\]|\\.)*)'", inv_block)
        for name in inv_names:
            name = name.replace("\\'", "'")
            fund_investments.append((rank, name))
    return fund_investments


def find_cross_fund_investments(fund_investments):
    """Find investments that appear across multiple funds using strict matching."""

    # Filter out generic/portfolio-level entries
    GENERIC_PATTERNS = [
        r'portfolio', r'equities$', r'ecosystem', r'blue.?chips?', r'listed',
        r'investments?$', r'^vc fund', r'^fund of', r'^private', r'^public',
        r'saudi.?focused', r'saudi equity', r'saudi fintech', r'saudi defence',
        r'saudi growth', r'saudi education', r'saudi tadawul',
        r'^gcc ', r'^mena ', r'^us ', r'^uk ', r'^regional',
        r'^climate tech', r'^health tech', r'^ai ', r'^africa',
        r'^south asia', r'pre-seed', r'^commodity', r'sukuk$',
        r'^healthcare (facilities|portfolio)', r'^tourism', r'^technology parks',
        r'^real estate$', r'tech portfolio$', r'credit (allocation|portfolio)',
        r'vc fund commitments', r'equity funds?$',
    ]

    def is_generic(name):
        n = name.lower()
        return any(re.search(p, n) for p in GENERIC_PATTERNS)

    # Build: core_name -> [(rank, original_name), ...]
    name_groups = defaultdict(list)
    for rank, name in fund_investments:
        if is_generic(name):
            continue
        cn = core_name(name).lower()
        if len(cn) < 3:
            continue
        name_groups[cn].append((rank, name))

    cross_fund = {}

    # Pass 1: Exact core name matches
    for cn, entries in name_groups.items():
        ranks = sorted(set(r for r, n in entries))
        if len(ranks) >= 2:
            display = core_name(min((n for r, n in entries), key=len))
            cross_fund[display] = ranks

    # Pass 2: Fuzzy matches among remaining singles
    singles = {cn: entries[0] for cn, entries in name_groups.items()
               if len(set(r for r, n in entries)) == 1 and cn not in [core_name(d).lower() for d in cross_fund]}

    single_keys = list(singles.keys())
    matched = set()

    for i in range(len(single_keys)):
        if single_keys[i] in matched:
            continue
        for j in range(i + 1, len(single_keys)):
            if single_keys[j] in matched:
                continue
            a, b = single_keys[i], single_keys[j]
            # Require high similarity (0.8+) for fuzzy matches
            ratio = SequenceMatcher(None, a, b).ratio()
            if ratio >= 0.8:
                r1, n1 = singles[a]
                r2, n2 = singles[b]
                if r1 != r2:
                    display = core_name(min(n1, n2, key=len))
                    cross_fund[display] = sorted([r1, r2])
                    matched.add(a)
                    matched.add(b)

    # Pass 3: Known cross-fund mappings (manually verified entities)
    # Check for substring containment of core names across different funds
    all_entries = [(rank, name, core_name(name).lower()) for rank, name in fund_investments if not is_generic(name)]

    # For each pair of entries from different funds, check if one core name contains the other
    # But only for names with 8+ chars to avoid false positives
    seen_pairs = set()
    for i in range(len(all_entries)):
        r1, n1, c1 = all_entries[i]
        if len(c1) < 8:
            continue
        for j in range(i + 1, len(all_entries)):
            r2, n2, c2 = all_entries[j]
            if r1 == r2 or len(c2) < 8:
                continue
            pair_key = (min(r1,r2), max(r1,r2), min(c1,c2))
            if pair_key in seen_pairs:
                continue
            # Check containment
            if c1 in c2 or c2 in c1:
                display = core_name(min(n1, n2, key=len))
                if display not in cross_fund:
                    cross_fund[display] = sorted([r1, r2])
                else:
                    for r in [r1, r2]:
                        if r not in cross_fund[display]:
                            cross_fund[display].append(r)
                    cross_fund[display].sort()
                seen_pairs.add(pair_key)

    # Final filter: must have 2+ distinct funds
    cross_fund = {k: v for k, v in cross_fund.items() if len(v) >= 2}

    return cross_fund


# --- JS generation ---

def js_escape(s):
    """Escape a string for use inside JS single quotes."""
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '')
    # Escape any lone backslashes that might cause issues
    return s


def build_research_summaries_js(summaries):
    """Build the var researchSummaries = {...} JavaScript block."""
    lines = ['var researchSummaries = {']
    for key, summary in sorted(summaries.items()):
        escaped = js_escape(summary)
        lines.append(f"  '{key}': '{escaped}',")
    lines.append('};')
    return '\n'.join(lines)


def build_cross_fund_js(cross_fund):
    """Build the var crossFundInvestments = {...} JavaScript block."""
    lines = ['var crossFundInvestments = {']
    for name, ranks in sorted(cross_fund.items()):
        escaped_name = js_escape(name)
        ranks_str = ','.join(str(r) for r in ranks)
        lines.append(f"  '{escaped_name}': [{ranks_str}],")
    lines.append('};')
    return '\n'.join(lines)


def inject_into_html(html, summaries_js, cross_fund_js):
    """Inject the new JS variables and update openInvestment() function."""

    # 1. Insert new variables after researchAvailable declaration
    insert_marker = "};\n\nfunction investmentSlug"
    new_block = f"""}};

// Research summaries (auto-generated by build script)
{summaries_js}

// Cross-fund investment mapping (auto-generated by build script)
{cross_fund_js}

function investmentSlug"""

    if insert_marker not in html:
        print("  ERROR: Could not find insert marker for variables")
        return html
    html = html.replace(insert_marker, new_block, 1)

    # 2. Replace the research status section in openInvestment()
    old_research_section = """  // Research status
  panel += '<div style="margin-top:12px;display:flex;align-items:center;gap:8px">';
  if(hasResearch){
    panel += '<span class="inv-detail-status available">\\u2713 Deep Research Available</span>';
    panel += '<span style="font-size:11px;color:var(--text-tertiary)">File: research/swf_investments/' + fundDir + '/' + slug + '.md</span>';
  } else {
    panel += '<span class="inv-detail-status pending">\\u25CB Research In Progress</span>';
    panel += '<span style="font-size:11px;color:var(--text-tertiary)">Full research report queued for generation</span>';
  }
  panel += '</div>';"""

    new_research_section = r"""  // Research status + summary
  panel += '<div style="margin-top:12px;display:flex;align-items:center;gap:8px">';
  var researchKey = fundDir + '/' + slug;
  if(hasResearch){
    panel += '<span class="inv-detail-status available">\u2713 Deep Research Available</span>';
    panel += '<span style="font-size:11px;color:var(--text-tertiary)">File: research/swf_investments/' + fundDir + '/' + slug + '.md</span>';
  } else {
    panel += '<span class="inv-detail-status pending">\u25CB Research In Progress</span>';
    panel += '<span style="font-size:11px;color:var(--text-tertiary)">Full research report queued for generation</span>';
  }
  panel += '</div>';

  // Show research summary if available
  if(typeof researchSummaries !== 'undefined' && researchSummaries[researchKey]){
    var summaryText = researchSummaries[researchKey];
    var paragraphs = summaryText.split('\n\n').filter(function(p){return p.trim().length > 0});
    panel += '<div class="inv-detail-research" style="margin-top:12px;max-height:400px;overflow-y:auto"><h4>\ud83d\udcca Research Summary</h4>';
    paragraphs.forEach(function(p){
      var cleaned = p.replace(/\n/g,' ').trim();
      if(cleaned.length > 0) panel += '<p style="margin-bottom:8px">' + cleaned + '</p>';
    });
    panel += '</div>';
  }

  // Cross-fund co-investors
  if(typeof crossFundInvestments !== 'undefined'){
    var invCore = inv.name.replace(/\s*\([^)]*\)/g,'').replace(/\s+(Group|Holdings|Ltd|Limited|Inc|Corp|Co|Company|International|Technologies|LP|JV|CV)\.?$/i,'').trim();
    var coInvestors = [];
    Object.keys(crossFundInvestments).forEach(function(key){
      // Match: exact match, or one contains the other (case-insensitive, min 8 chars)
      var a = invCore.toLowerCase(), b = key.toLowerCase();
      var isMatch = (a === b) || (a.length >= 8 && b.indexOf(a) !== -1) || (b.length >= 8 && a.indexOf(b) !== -1);
      if(isMatch){
        crossFundInvestments[key].forEach(function(r){
          if(r !== fundRank && coInvestors.indexOf(r) === -1) coInvestors.push(r);
        });
      }
    });
    if(coInvestors.length > 0){
      panel += '<div style="margin-top:12px"><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:var(--text-tertiary);margin-bottom:6px">\ud83e\udd1d Co-Investors (also held by)</div>';
      panel += '<div style="display:flex;flex-wrap:wrap;gap:6px">';
      coInvestors.forEach(function(r){
        var coFund = funds.find(function(x){return x.rank===r});
        if(coFund){
          panel += '<span class="co-investor-chip" onclick="closeReport();setTimeout(function(){openReport('+r+')},150)" title="'+coFund.name+'">' + coFund.short + ' <span style="font-weight:400;opacity:0.7;font-size:10px">' + coFund.country + '</span></span>';
        }
      });
      panel += '</div></div>';
    }
  }"""

    if old_research_section not in html:
        print("  ERROR: Could not find old research section in openInvestment()")
        return html
    html = html.replace(old_research_section, new_research_section, 1)

    # 3. Add CSS for co-investor chips (before .inv-detail)
    css_insert = """.co-investor-chip{display:inline-flex;align-items:center;gap:4px;padding:5px 12px;border-radius:100px;font-size:11px;font-weight:600;background:var(--purple-light);color:var(--purple);cursor:pointer;transition:all 0.2s;border:1px solid transparent}
.co-investor-chip:hover{background:var(--purple);color:#fff;border-color:var(--purple)}
"""
    html = html.replace('\n.inv-detail{', '\n' + css_insert + '.inv-detail{', 1)

    return html


def main():
    print("=" * 60)
    print("SWF Enhancement Build Script")
    print("=" * 60)

    print("\n[1] Reading swf.html...")
    with open(SWF_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    original_len = len(html)
    print(f"  Read {original_len} bytes ({html.count(chr(10))} lines)")

    # Task A
    print("\n[2] Scanning research files...")
    summaries = scan_research_files()
    print(f"  Found {len(summaries)} research summaries")
    summaries_js = build_research_summaries_js(summaries)

    # Task C
    print("\n[3] Analyzing cross-fund investments...")
    fund_investments = extract_investments_from_html(html)
    print(f"  Found {len(fund_investments)} total investments across all funds")
    cross_fund = find_cross_fund_investments(fund_investments)
    print(f"  Found {len(cross_fund)} cross-fund investments:")
    for name, ranks in sorted(cross_fund.items()):
        print(f"    {name}: funds {ranks}")
    cross_fund_js = build_cross_fund_js(cross_fund)

    # Inject
    print("\n[4] Injecting into swf.html...")
    new_html = inject_into_html(html, summaries_js, cross_fund_js)

    if len(new_html) == original_len:
        print("  ERROR: No changes made!")
        return False

    with open(SWF_HTML, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"  Written {len(new_html)} bytes ({new_html.count(chr(10))} lines)")
    print(f"  Delta: +{len(new_html) - original_len} bytes")

    print("\n[5] Done!")
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
