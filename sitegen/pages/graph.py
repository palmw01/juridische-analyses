import json
from pathlib import Path

from sitegen.config import JAS_KLEUREN
from sitegen.html import schrijf_html


def gen_graph(out: Path, begrippen: list, regels: list, annotaties: list):
    nodes: list[dict] = []
    node_ids: set[str] = set()
    links: list[dict] = []

    def add_node(nid: str, label: str, groep: str, node_type: str = "begrip", page: str | None = None):
        if nid not in node_ids:
            nd: dict = {"id": nid, "label": label, "groep": groep, "type": node_type}
            if page:
                nd["page"] = page
            nodes.append(nd)
            node_ids.add(nid)

    for b in begrippen:
        add_node(b["id"], b["naam"], b["jas_klasse"], "begrip", f'begrippen/{b["slug"]}.html')
    for b in begrippen:
        for rt in ("is-een", "heeft", "leidt-tot"):
            for target in b["relaties"][rt]:
                if target not in node_ids:
                    add_node(target, target.rsplit("/", 1)[-1], "onbekend", "begrip", None)
                links.append({"source": b["id"], "target": target, "relatie": rt})
    for r in regels:
        add_node(r["id"], r["naam"], "afleidingsregel", "regel", f'regels/{r["id"]}.html')
        for inv in r.get("invoer") or []:
            if inv not in node_ids:
                add_node(inv, inv.rsplit("/", 1)[-1], "onbekend", "begrip", None)
            links.append({"source": r["id"], "target": inv, "relatie": "invoer"})
        for uitv in r.get("uitvoer") or []:
            if uitv not in node_ids:
                add_node(uitv, uitv.rsplit("/", 1)[-1], "onbekend", "begrip", None)
            links.append({"source": r["id"], "target": uitv, "relatie": "uitvoer"})

    # graph.json schrijven
    data_dir = out / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    graph_data = {"nodes": nodes, "links": links, "colorMap": JAS_KLEUREN}
    (data_dir / "graph.json").write_text(json.dumps(graph_data, ensure_ascii=False))

    aanwezige_klassen = sorted({n["groep"] for n in nodes if n["groep"] != "onbekend"})
    klasse_opties = "".join(f'<option value="{k}">{k}</option>' for k in aanwezige_klassen)

    body = f"""<h1>Kennisgraaf</h1>
<p class="subtitle">Interactieve graaf van begrippen (cirkels) en afleidingsregels (ruiten). Sleep nodes om te herschikken.</p>
<div class="graph-toolbar">
  <label for="klasseFilter">JAS-klasse:</label>
  <select id="klasseFilter" aria-label="Filter op JAS-klasse">
    <option value="all">Alle klassen</option>
    {klasse_opties}
  </select>
  <span class="graph-count" id="nodeCount"></span>
  <button class="btn-secondary" id="resetBtn" type="button">Reset weergave</button>
  <button class="btn-secondary" id="fullscreenBtn" type="button" aria-label="Volledig scherm" title="Volledig scherm">&#x26F6; Volledig scherm</button>
</div>
<div class="graph-container" id="graphContainer">
  <button class="graph-close-btn" id="graphCloseBtn" type="button" aria-label="Volledig scherm sluiten" title="Sluiten">&#x2715;</button>
  <div class="graph-legend" id="graphLegend"></div>
</div>
<script src="https://d3js.org/d3.v7.min.js" integrity="sha384-CjloA8y00+1SDAUkjs099PVfnY2KmDC2BZnws9kh8D/lX1s46w6EPhpXdqMfjK6i" crossorigin="anonymous"></script>
<script>
fetch('data/graph.json').then(function(r){{return r.json()}}).then(function(graphData){{
var data = graphData;
var colorMap = graphData.colorMap;
var width = document.getElementById('graphContainer').clientWidth;
var height = Math.max(400, Math.min(window.innerHeight * 0.6, 700));
var svg = d3.select("#graphContainer").append("svg").attr("width", width).attr("height", height);
var g = svg.append("g");
var zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", function(e){{ g.attr("transform", e.transform); }});
svg.call(zoom).on("dblclick.zoom", null);
g.append("rect").attr("x",-width*5).attr("y",-height*5).attr("width",width*10).attr("height",height*10).attr("fill","none").attr("pointer-events","all");
svg.append("defs").append("marker").attr("id","arrow").attr("viewBox","0 -5 10 10").attr("refX",20).attr("refY",0).attr("markerWidth",6).attr("markerHeight",6).attr("orient","auto")
  .append("path").attr("d","M0,-5L10,0L0,5").attr("fill","#94a3b8");
var link = g.append("g").selectAll("line").data(data.links).join("line")
  .attr("stroke","#94a3b8").attr("stroke-width",1).attr("stroke-opacity",0.5).attr("marker-end","url(#arrow)");
var node = g.append("g").selectAll("g").data(data.nodes).join("g").call(
  d3.drag().on("start",function(e,d){{if(!e.active)simulation.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y}})
  .on("drag",function(e,d){{d.fx=e.x;d.fy=e.y}})
  .on("end",function(e,d){{if(!e.active)simulation.alphaTarget(0);d.fx=null;d.fy=null}}));
node.append("title").text(function(d){{return d.label}});
node.append("path")
  .attr("d",function(d){{return d.type==='regel'?d3.symbol().type(d3.symbolDiamond).size(220)():null}})
  .attr("fill",function(d){{return colorMap[d.groep]||'#94a3b8'}}).attr("stroke","#fff").attr("stroke-width",1.5)
  .attr("opacity",function(d){{return d.type==='regel'?1:0}});
node.append("circle").attr("r",7)
  .attr("fill",function(d){{return colorMap[d.groep]||'#94a3b8'}}).attr("stroke","#fff").attr("stroke-width",1.5)
  .attr("opacity",function(d){{return d.type==='begrip'?1:0}});
var nodeText = node.append("text").attr("dx",12).attr("dy",4).attr("font-size","11px")
  .text(function(d){{return d.label.length>28?d.label.slice(0,25)+'…':d.label}});
function updateTextColor(){{
  nodeText.attr("fill",document.documentElement.getAttribute('data-theme')==='dark'?'#dce8f0':'#2d3f52');
}}
updateTextColor();
new MutationObserver(updateTextColor).observe(document.documentElement,{{attributes:true,attributeFilter:['data-theme']}});
node.on("click",function(e,d){{if(d.page)window.location.href=d.page;}});
node.style("cursor",function(d){{return d.page?'pointer':'default'}});
var simulation = d3.forceSimulation(data.nodes)
  .force("link",d3.forceLink(data.links).id(function(d){{return d.id}}).distance(100))
  .force("charge",d3.forceManyBody().strength(-180))
  .force("center",d3.forceCenter(width/2,height/2))
  .force("collision",d3.forceCollide(18));
simulation.on("tick",function(){{
  link.attr("x1",function(d){{return d.source.x}}).attr("y1",function(d){{return d.source.y}})
      .attr("x2",function(d){{return d.target.x}}).attr("y2",function(d){{return d.target.y}});
  node.attr("transform",function(d){{return"translate("+d.x+","+d.y+")"}});
}});
var defaultTransform = d3.zoomIdentity.translate(width/2,height/2).scale(0.85).translate(-width/2,-height/2);
simulation.on("end",function(){{
  svg.transition().duration(600).call(zoom.transform, defaultTransform);
}});
function resetView(){{
  document.getElementById('klasseFilter').value='all';
  applyFilter('all');
  svg.transition().duration(500).call(zoom.transform, defaultTransform);
}}
document.getElementById('resetBtn').addEventListener('click', resetView);

var aanwezigeKlassen = Array.from(new Set(data.nodes.map(function(d){{return d.groep}}))).filter(function(k){{return k!=='onbekend'&&colorMap[k]}});
var legendEl = document.getElementById('graphLegend');
var legend = d3.select(legendEl);
var hdr = legend.append("div").attr("class","graph-legend-header").attr("role","button").attr("tabindex","0").attr("aria-expanded","true").attr("aria-label","Legenda in-/uitklappen");
hdr.append("div").attr("class","graph-legend-title").text("Legenda");
hdr.append("span").attr("class","graph-legend-chevron").text("▾");
var body = legend.append("div").attr("class","graph-legend-body");
var bRow = body.append("div").attr("class","graph-legend-item");
bRow.append("div").attr("class","graph-legend-dot").style("background","#94a3b8");
bRow.append("span").text("begrip");
var rRow = body.append("div").attr("class","graph-legend-item");
rRow.append("div").attr("class","graph-legend-diamond").style("background","#94a3b8");
rRow.append("span").text("regel (ruit)");
body.append("div").style("border-top","1px solid var(--border)").style("margin","0.4rem 0");
aanwezigeKlassen.sort().forEach(function(k){{
  var row = body.append("div").attr("class","graph-legend-item");
  row.append("div").attr("class","graph-legend-dot").style("background",colorMap[k]);
  row.append("span").text(k);
}});
var hdrEl=hdr.node();
function toggleLegend(){{
  var collapsed=legendEl.classList.toggle('collapsed');
  hdrEl.setAttribute('aria-expanded',String(!collapsed));
}}
hdrEl.addEventListener('click',toggleLegend);
hdrEl.addEventListener('keydown',function(e){{if(e.key==='Enter'||e.key===' '){{e.preventDefault();toggleLegend();}}}});
if(window.innerWidth < 768) legendEl.classList.add('collapsed');

function updateCount(matchedIds){{
  var el = document.getElementById('nodeCount');
  if(!el) return;
  el.textContent = matchedIds ? matchedIds.size + ' nodes' : '';
}}
function applyFilter(v){{
  if(v==='all'){{
    node.attr("opacity",1);
    link.attr("stroke-opacity",0.5);
    updateCount(null);
    return;
  }}
  var matchedIds = new Set(data.nodes.filter(function(d){{return d.groep===v}}).map(function(d){{return d.id}}));
  var neighborIds = new Set();
  data.links.forEach(function(l){{
    var sid=l.source.id||l.source, tid=l.target.id||l.target;
    if(matchedIds.has(sid)) neighborIds.add(tid);
    if(matchedIds.has(tid)) neighborIds.add(sid);
  }});
  node.attr("opacity",function(d){{
    return matchedIds.has(d.id)?1:neighborIds.has(d.id)?0.35:0.06;
  }});
  link.attr("stroke-opacity",function(d){{
    var sid=d.source.id||d.source, tid=d.target.id||d.target;
    if(matchedIds.has(sid)&&matchedIds.has(tid)) return 0.7;
    if(matchedIds.has(sid)||matchedIds.has(tid)) return 0.3;
    return 0.04;
  }});
  updateCount(matchedIds);
}}
document.getElementById('klasseFilter').addEventListener('change',function(){{applyFilter(this.value)}});

var cssFsActive=false;

function resizeGraph(){{
  var container=document.getElementById('graphContainer');
  var newW=container.clientWidth;
  var nativeFsOn=document.fullscreenElement===container||document.webkitFullscreenElement===container;
  var fsOn=nativeFsOn||cssFsActive;
  var newH=fsOn?window.innerHeight:Math.max(400,Math.min(window.innerHeight*0.6,700));
  if(fsOn)container.style.height=newH+'px';
  else container.style.height='';
  svg.attr('width',newW).attr('height',newH);
  simulation.force('center',d3.forceCenter(newW/2,newH/2)).alpha(0.3).restart();
  defaultTransform=d3.zoomIdentity.translate(newW/2,newH/2).scale(0.85).translate(-newW/2,-newH/2);
}}
var _rt;window.addEventListener('resize',function(){{clearTimeout(_rt);_rt=setTimeout(resizeGraph,150);}});

var fsBtn=document.getElementById('fullscreenBtn');
var closeBtn=document.getElementById('graphCloseBtn');
var container=document.getElementById('graphContainer');
var nativeFs=!!(container.requestFullscreen||container.webkitRequestFullscreen);

function setFsUi(fs){{
  container.classList.toggle('graph-fullscreen',fs);
  closeBtn.style.display=fs?'flex':'none';
  fsBtn.innerHTML=fs?'&#x2B1C; Normaal':'&#x26F6; Volledig scherm';
  fsBtn.title=fs?'Volledig scherm afsluiten':'Volledig scherm';
  setTimeout(resizeGraph,50);
}}
function enterCssFallback(){{
  cssFsActive=true;
  document.body.style.overflow='hidden';
  setFsUi(true);
}}
function exitCssFallback(){{
  cssFsActive=false;
  document.body.style.overflow='';
  setFsUi(false);
}}
function enterFullscreen(){{
  if(nativeFs){{
    if(container.requestFullscreen)container.requestFullscreen();
    else if(container.webkitRequestFullscreen)container.webkitRequestFullscreen();
  }} else {{
    enterCssFallback();
  }}
}}
function exitFullscreen(){{
  if(nativeFs){{
    if(document.exitFullscreen)document.exitFullscreen();
    else if(document.webkitExitFullscreen)document.webkitExitFullscreen();
  }} else {{
    exitCssFallback();
  }}
}}
function onNativeFsChange(){{
  var fs=document.fullscreenElement===container||document.webkitFullscreenElement===container;
  setFsUi(fs);
}}
document.addEventListener('fullscreenchange',onNativeFsChange);
document.addEventListener('webkitfullscreenchange',onNativeFsChange);
if(fsBtn)fsBtn.addEventListener('click',function(){{
  var fs=nativeFs?(document.fullscreenElement===container||document.webkitFullscreenElement===container):cssFsActive;
  fs?exitFullscreen():enterFullscreen();
}});
if(closeBtn)closeBtn.addEventListener('click',exitFullscreen);
document.addEventListener('keydown',function(e){{
  if(e.key==='Escape'){{
    if(nativeFs&&(document.fullscreenElement===container||document.webkitFullscreenElement===container))exitFullscreen();
    else if(!nativeFs&&cssFsActive)exitCssFallback();
  }}
}});
}});
</script>"""
    schrijf_html(out, "graph.html", "Kennisgraaf | Belastingdienst", body, active="graaf")
