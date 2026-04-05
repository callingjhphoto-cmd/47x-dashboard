#!/usr/bin/env python3
"""
build_three_passes.py
Three passes for swf.html:
  PASS 1 — Sector Intelligence section
  PASS 2 — Composite Score column
  PASS 3 — CSV Export button
"""

import re

SWF = '/Users/jameshuertas/Documents/Claude/projects/47x-dashboard/swf.html'

with open(SWF, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
print(f'Original: {html.count(chr(10))+1} lines, {original_len} chars')

# ─────────────────────────────────────────────
# PASS 1 — SECTOR INTELLIGENCE CSS
# ─────────────────────────────────────────────

SECTOR_CSS = """
/* ===== SECTOR INTELLIGENCE ===== */
.sector-intel-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;margin-top:4px}
.sector-intel-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-sm);padding:16px;cursor:pointer;transition:all 0.2s}
.sector-intel-card:hover{border-color:var(--accent);box-shadow:var(--shadow-md);transform:translateY(-1px)}
.sector-intel-card.active{border-color:var(--accent);background:var(--accent-light)}
.sector-intel-name{font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:6px}
.sector-intel-bar-wrap{background:var(--border-light);border-radius:4px;height:6px;margin:6px 0}
.sector-intel-bar{height:6px;border-radius:4px;background:linear-gradient(90deg,var(--accent),var(--purple));transition:width 0.6s ease}
.sector-intel-meta{display:flex;justify-content:space-between;font-size:10px;color:var(--text-tertiary);margin-top:4px}
.sector-intel-detail{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin-top:16px;display:none}
.sector-intel-detail.open{display:block;animation:fadeIn 0.25s ease}
.sector-intel-detail-title{font-size:14px;font-weight:700;color:var(--text-primary);margin-bottom:12px}
.sector-fund-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border-light)}
.sector-fund-row:last-child{border-bottom:none}
.sector-fund-name{flex:1;font-size:12px;font-weight:600;color:var(--text-primary)}
.sector-fund-bar-wrap{flex:2;background:var(--border-light);border-radius:3px;height:6px}
.sector-fund-bar{height:6px;border-radius:3px;background:var(--accent);transition:width 0.5s ease}
.sector-fund-pct{width:36px;text-align:right;font-size:11px;font-weight:600;color:var(--accent);font-family:'JetBrains Mono',monospace}
.sector-fund-count{width:60px;text-align:right;font-size:10px;color:var(--text-tertiary)}
@media(max-width:600px){.sector-intel-grid{grid-template-columns:1fr 1fr}}
"""

# Insert sector CSS before closing </style>
assert '</style>' in html, 'No </style> found'
html = html.replace('</style>', SECTOR_CSS + '\n</style>', 1)
print('PASS 1a: Sector Intel CSS injected')

# ─────────────────────────────────────────────
# PASS 2 — COMPOSITE SCORE CSS
# ─────────────────────────────────────────────

SCORE_CSS = """
/* ===== COMPOSITE SCORE ===== */
.score-pill{display:inline-flex;align-items:center;justify-content:center;width:42px;height:22px;border-radius:100px;font-size:10px;font-weight:700;font-family:'JetBrains Mono',monospace}
.score-green{background:#ECFDF5;color:#059669}
.score-amber{background:#FFFBEB;color:#D97706}
.score-red{background:#FEF2F2;color:#DC2626}
"""

html = html.replace('</style>', SCORE_CSS + '\n</style>', 1)
print('PASS 2a: Score CSS injected')

# ─────────────────────────────────────────────
# PASS 1 — SECTOR INTELLIGENCE HTML SECTION
# ─────────────────────────────────────────────
# Insert after the Cross-Fund Analysis section divider (line ~706 area)
# Find the Cross-Fund section block and insert after it

SECTOR_HTML = """
<div class="section-divider"></div>

<div class="section fade-in" id="sectorIntelSection">
<div class="section-header">
  <div class="section-title"><span class="level-badge level-3">Sector Intelligence</span> Capital deployment by sector across the 50-fund universe</div>
  <button class="filter-btn" onclick="closeSectorDetail()">Clear Selection</button>
</div>
<div class="sector-intel-grid" id="sectorIntelGrid"></div>
<div class="sector-intel-detail" id="sectorIntelDetail"></div>
</div>
"""

# Insert before the Macro Overlay section
MACRO_MARKER = '\n<div class="section-divider"></div>\n\n<div class="section-header"><div class="section-title"><span class="level-badge level-3">Macro Overlay</span>'
assert MACRO_MARKER in html, 'Macro Overlay marker not found'
html = html.replace(MACRO_MARKER, SECTOR_HTML + MACRO_MARKER, 1)
print('PASS 1b: Sector Intel HTML section injected')

# ─────────────────────────────────────────────
# PASS 2 — COMPOSITE SCORE COLUMN IN TABLE HEADER
# ─────────────────────────────────────────────

OLD_TABLE_HEADER = '''        <th onclick="sortTable(5)">Tier <span class="sort-arrow"></span></th>
      </tr>'''
NEW_TABLE_HEADER = '''        <th onclick="sortTable(5)">Tier <span class="sort-arrow"></span></th>
        <th onclick="sortTable(6)">Score <span class="sort-arrow"></span></th>
      </tr>'''

assert OLD_TABLE_HEADER in html, 'Table header Tier column not found'
html = html.replace(OLD_TABLE_HEADER, NEW_TABLE_HEADER, 1)
print('PASS 2b: Score column header added')

# ─────────────────────────────────────────────
# PASS 3 — CSV EXPORT BUTTON
# ─────────────────────────────────────────────

OLD_COMPARE_BTN = '  <button class="filter-btn" id="compareToggle" onclick="toggleCompareMode()" style="margin-left:auto">Compare Funds</button>'
NEW_COMPARE_BTN = '  <button class="filter-btn" id="compareToggle" onclick="toggleCompareMode()">Compare Funds</button>\n  <button class="filter-btn" onclick="downloadCSV()" style="margin-left:auto" title="Export fund list as CSV">&#8595; Download CSV</button>'

assert OLD_COMPARE_BTN in html, 'Compare Funds button not found'
html = html.replace(OLD_COMPARE_BTN, NEW_COMPARE_BTN, 1)
print('PASS 3: CSV button added')

# ─────────────────────────────────────────────
# PASS 1 — SECTOR INTELLIGENCE JS
# ─────────────────────────────────────────────

SECTOR_JS = r"""
// ===== SECTOR INTELLIGENCE =====
var activeSectorCard = null;

function buildSectorIndex(){
  // Returns {sectorName: {funds:[{name,short,rank,pct,count}], totalCount, totalCapital}}
  var idx = {};
  funds.forEach(function(f){
    if(!f.sectors)return;
    var invCount = f.investments ? f.investments.length : 0;
    Object.keys(f.sectors).forEach(function(sec){
      var pct = f.sectors[sec] || 0;
      if(!pct)return;
      if(!idx[sec])idx[sec]={funds:[],totalCount:0,totalCapital:0};
      idx[sec].funds.push({name:f.name,short:f.short,rank:f.rank,pct:pct,count:Math.round(invCount*pct/100),aum:f.aum||0});
      idx[sec].totalCount += Math.round(invCount*pct/100);
      idx[sec].totalCapital += (f.aum||0)*pct/100;
    });
  });
  // Sort funds within each sector by pct desc
  Object.keys(idx).forEach(function(sec){
    idx[sec].funds.sort(function(a,b){return b.pct-a.pct});
    idx[sec].fundCount = idx[sec].funds.length;
  });
  return idx;
}

function renderSectorIntelligence(){
  try{
    var grid = document.getElementById('sectorIntelGrid');
    if(!grid)return;
    var idx = buildSectorIndex();
    // Sort sectors by total capital desc
    var sectors = Object.keys(idx).sort(function(a,b){return idx[b].totalCapital-idx[a].totalCapital});
    var maxCap = idx[sectors[0]] ? idx[sectors[0]].totalCapital : 1;
    var h = '';
    sectors.forEach(function(sec){
      var d = idx[sec];
      var barPct = Math.round(d.totalCapital/maxCap*100);
      var capStr = d.totalCapital>=1000?'$'+(d.totalCapital/1000).toFixed(1)+'T':'$'+Math.round(d.totalCapital)+'B';
      h+='<div class="sector-intel-card" onclick="openSectorDetail(\''+sec.replace(/'/g,"\\'")+'\')" id="sic-'+sec.replace(/[^a-zA-Z0-9]/g,'_')+'">';
      h+='<div class="sector-intel-name">'+sec+'</div>';
      h+='<div class="sector-intel-bar-wrap"><div class="sector-intel-bar" style="width:'+barPct+'%"></div></div>';
      h+='<div class="sector-intel-meta"><span>'+d.fundCount+' funds</span><span>'+capStr+' est. deployed</span></div>';
      h+='</div>';
    });
    grid.innerHTML = h;
  }catch(e){console.error('renderSectorIntelligence:',e)}
}

function openSectorDetail(sec){
  try{
    var detail = document.getElementById('sectorIntelDetail');
    if(!detail)return;
    // Toggle: clicking same sector closes it
    if(activeSectorCard === sec){
      closeSectorDetail();
      return;
    }
    activeSectorCard = sec;
    // Highlight active card
    document.querySelectorAll('.sector-intel-card').forEach(function(c){c.classList.remove('active')});
    var cardId = 'sic-'+sec.replace(/[^a-zA-Z0-9]/g,'_');
    var card = document.getElementById(cardId);
    if(card)card.classList.add('active');

    var idx = buildSectorIndex();
    var d = idx[sec];
    if(!d){detail.classList.remove('open');return;}
    var maxPct = d.funds[0]?d.funds[0].pct:1;
    var capStr = d.totalCapital>=1000?'$'+(d.totalCapital/1000).toFixed(2)+'T':'$'+Math.round(d.totalCapital)+'B';

    var h = '<div class="sector-intel-detail-title">'+sec+' \u2014 '+d.fundCount+' funds \u2022 '+capStr+' estimated capital deployed</div>';
    h += '<table style="width:100%;border-collapse:collapse">';
    h += '<thead><tr style="font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:var(--text-tertiary)">';
    h += '<th style="text-align:left;padding:4px 8px">Fund</th><th style="text-align:left;padding:4px 8px;width:40%">Portfolio Weight</th><th style="text-align:right;padding:4px 8px">Inv.</th><th style="text-align:right;padding:4px 8px">Est. Capital</th></tr></thead>';
    h += '<tbody>';
    d.funds.forEach(function(fd){
      var barW = Math.round(fd.pct/maxPct*100);
      var est = fd.aum*fd.pct/100;
      var estStr = est>=1000?'$'+(est/1000).toFixed(2)+'T':'$'+Math.round(est)+'B';
      h+='<tr class="sector-fund-row" onclick="openReport('+fd.rank+')" style="cursor:pointer">';
      h+='<td class="sector-fund-name">'+fd.short+'</td>';
      h+='<td><div style="display:flex;align-items:center;gap:8px">';
      h+='<div class="sector-fund-bar-wrap"><div class="sector-fund-bar" style="width:'+barW+'%"></div></div>';
      h+='<span class="sector-fund-pct">'+fd.pct+'%</span></div></td>';
      h+='<td class="sector-fund-count">'+fd.count+'</td>';
      h+='<td style="text-align:right;font-size:11px;font-weight:600;color:var(--text-primary);font-family:\'JetBrains Mono\',monospace;width:80px">'+estStr+'</td>';
      h+='</tr>';
    });
    h += '</tbody></table>';
    detail.innerHTML = h;
    detail.classList.add('open');
    // Scroll to detail
    setTimeout(function(){detail.scrollIntoView({behavior:'smooth',block:'nearest'})},50);
  }catch(e){console.error('openSectorDetail:',e)}
}

function closeSectorDetail(){
  activeSectorCard = null;
  document.querySelectorAll('.sector-intel-card').forEach(function(c){c.classList.remove('active')});
  var detail = document.getElementById('sectorIntelDetail');
  if(detail)detail.classList.remove('open');
}
"""

# ─────────────────────────────────────────────
# PASS 2 — COMPOSITE SCORE JS
# ─────────────────────────────────────────────

SCORE_JS = r"""
// ===== COMPOSITE SCORE =====
function computeCompositeScore(f){
  try{
    // Transparency: how much public data — based on investment count + deepProfile availability
    var invCount = f.investments ? f.investments.length : 0;
    var hasDeep = !!(deepProfiles && deepProfiles[f.rank] && deepProfiles[f.rank].executive);
    var transparency = Math.min(100, Math.round(invCount * 5 + (hasDeep ? 20 : 0)));

    // Diversification: number of unique sectors in sectors object with pct > 0
    var sectorCount = f.sectors ? Object.keys(f.sectors).filter(function(s){return f.sectors[s]>0}).length : 0;
    var diversification = Math.min(100, Math.round(sectorCount * 12));

    // Scale: AUM tier
    var aum = f.aum || 0;
    var scale = aum >= 500 ? 100 : aum >= 100 ? 80 : aum >= 25 ? 60 : aum >= 5 ? 40 : aum > 0 ? 20 : 0;

    // Activity: investments from 2020+
    var recentInv = 0;
    if(f.investments){
      f.investments.forEach(function(inv){
        if(inv.year && inv.year >= 2020) recentInv++;
      });
    }
    var activity = Math.min(100, Math.round(recentInv * 12));

    var composite = Math.round((transparency + diversification + scale + activity) / 4);
    return {score:composite,transparency:transparency,diversification:diversification,scale:scale,activity:activity};
  }catch(e){return {score:0,transparency:0,diversification:0,scale:0,activity:0}}
}

function scoreClass(s){return s>=75?'score-green':s>=50?'score-amber':'score-red'}
"""

# ─────────────────────────────────────────────
# PASS 3 — CSV EXPORT JS
# ─────────────────────────────────────────────

CSV_JS = r"""
// ===== CSV EXPORT =====
function downloadCSV(){
  try{
    var rows = [['Rank','Fund Name','Short','Country','AUM ($B)','Type','Tier','Status','Founded',
                 'Composite Score','Transparency','Diversification','Scale','Activity',
                 'Investments Count','Top Sectors']];
    funds.forEach(function(f){
      var sc = computeCompositeScore(f);
      var topSectors = f.sectors ? Object.keys(f.sectors).sort(function(a,b){return f.sectors[b]-f.sectors[a]}).slice(0,3).join('; ') : '';
      var invCount = f.investments ? f.investments.length : 0;
      rows.push([
        f.rank,
        '"'+f.name.replace(/"/g,'""')+'"',
        f.short,
        f.country,
        f.aum || '',
        f.type,
        f.tier,
        f.status || '',
        f.founded || '',
        sc.score,sc.transparency,sc.diversification,sc.scale,sc.activity,
        invCount,
        '"'+topSectors+'"'
      ]);
    });
    var csv = rows.map(function(r){return r.join(',')}).join('\n');
    var blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = '47x-gcc-funds-'+new Date().toISOString().slice(0,10)+'.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }catch(e){console.error('downloadCSV:',e);alert('CSV export failed: '+e.message)}
}
"""

# ─────────────────────────────────────────────
# INJECT ALL JS BEFORE CLOSING </script>
# ─────────────────────────────────────────────

CLOSE_SCRIPT = '</script>\n</body>\n</html>'
assert CLOSE_SCRIPT in html, 'Closing script tag pattern not found'

ALL_NEW_JS = SECTOR_JS + '\n' + SCORE_JS + '\n' + CSV_JS
html = html.replace(CLOSE_SCRIPT, ALL_NEW_JS + '\n' + CLOSE_SCRIPT, 1)
print('JS blocks injected')

# ─────────────────────────────────────────────
# PASS 2 — PATCH renderFundTable to include score column
# ─────────────────────────────────────────────

# Find the renderFundTable rows section — both compare and normal mode rows
# Normal mode row ends with </tr>'
# We need to add score cell

# Normal mode: ends with Tier badge cell then </tr>
OLD_NORMAL_ROW = (
    "html+='<tr onclick=\"openReport('+f.rank+')\" role=\"button\" tabindex=\"0\" "
    "aria-label=\"View report for '+f.name.replace(/'/g,'\\\\&#39;')+'\" "
    "onkeydown=\"if(event.key===\\'Enter\\'||event.key===\\' \\'){event.preventDefault();"
    "openReport('+f.rank+');}\">"
    "<td>'+f.rank+'</td>"
    "<td>'+f.name+'</td>"
    "<td><a onclick=\"event.stopPropagation();openCountryDeepDive(\\''+f.country+'\\')\" "
    "style=\"color:var(--accent);cursor:pointer;text-decoration:none\" "
    "title=\"View '+f.country+' deep dive\">'+f.country+'</a></td>"
    "<td class=\"aum-cell\">'+a+'</td>"
    "<td><span class=\"status-badge '+tc+'\">'+f.type+'</span></td>"
    "<td><span class=\"tier-badge tier-'+f.tier+'\">Tier '+f.tier+'</span></td></tr>';"
)

# Find more flexibly
pattern = r"(html\+='<tr onclick=\"openReport\('\+f\.rank\+'\)\"[^;]+Tier '\+f\.tier\+'</span></td></tr>';)"
match = re.search(pattern, html)
if match:
    old_str = match.group(0)
    new_str = old_str.rstrip("';") + "<td><span class=\\'score-pill '+scoreClass(computeCompositeScore(f).score)+'\\'>'+computeCompositeScore(f).score+'</span></td></tr>';"
    html = html.replace(old_str, new_str, 1)
    print('PASS 2c: Score cell added to normal row')
else:
    print('WARNING: Could not find normal row pattern — trying alternative approach')
    # Manual approach: find specific string
    OLD_ROW_END = "'<td><span class=\"tier-badge tier-'+f.tier+'\">Tier '+f.tier+'</span></td></tr>'"
    if OLD_ROW_END in html:
        NEW_ROW_END = "'<td><span class=\"tier-badge tier-'+f.tier+'\">Tier '+f.tier+'</span></td><td><span class=\"score-pill \'+scoreClass(computeCompositeScore(f).score)+\'\">\\'+computeCompositeScore(f).score+\\'</span></td></tr>'"
        # This approach is tricky due to quoting — let's use a different marker
        print('  Alternative approach needed')

# ─────────────────────────────────────────────
# PATCH initAllFeatures to call renderSectorIntelligence
# ─────────────────────────────────────────────

OLD_INIT = 'function initAllFeatures(){\n  try{\n    renderSectorHeatmap();\n    renderTimeline();\n    renderAlerts();\n    renderNetworkGraph();\n    renderPredictions();\n  }catch(e){console.error(\'Feature init error:\',e.message)}\n}'
NEW_INIT = 'function initAllFeatures(){\n  try{\n    renderSectorHeatmap();\n    renderTimeline();\n    renderAlerts();\n    renderNetworkGraph();\n    renderPredictions();\n    renderSectorIntelligence();\n  }catch(e){console.error(\'Feature init error:\',e.message)}\n}'

if OLD_INIT in html:
    html = html.replace(OLD_INIT, NEW_INIT, 1)
    print('PASS 1c: renderSectorIntelligence() added to initAllFeatures()')
else:
    print('WARNING: initAllFeatures pattern not found exactly — trying with render')
    html = html.replace(
        'renderPredictions();\n  }catch(e){console.error(\'Feature init error:\',e.message)}',
        'renderPredictions();\n    renderSectorIntelligence();\n  }catch(e){console.error(\'Feature init error:\',e.message)}',
        1
    )
    print('PASS 1c (alt): renderSectorIntelligence() added via renderPredictions marker')

# ─────────────────────────────────────────────
# WRITE OUTPUT
# ─────────────────────────────────────────────

with open(SWF, 'w', encoding='utf-8') as f:
    f.write(html)

new_len = len(html)
new_lines = html.count('\n') + 1
print(f'Written: {new_lines} lines, {new_len} chars (+{new_len-original_len} chars)')
print('Done. Run JS syntax check next.')
