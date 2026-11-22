/* ═══════════ 汉志经纬 · 地图（部域晕 / 郡印 / 首县微点） ═══════════ */

/* var（非 const）：map 挂到 window，测试页可直取 */
var map = L.map("map", {zoomControl: true, minZoom: 4, maxZoom: 12,
  attributionControl: false, maxBounds: [[15, 88], [44, 137]], maxBoundsViscosity: .6});
map.fitBounds([[28, 100], [41, 126]]);

/* 底图：Esri 地形（绢面滤镜见 css） */
var tileLayer = null, tileErrs = 0;
function setBasemap(){
  if (window.__NOTILES__) return;   /* 测试密封：断言页不拉外网瓦片 */
  tileErrs = 0;
  tileLayer = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}",
    {maxZoom: 12, maxNativeZoom: 8});
  tileLayer.addTo(map);
  tileLayer.on("tileerror", ()=>{
    tileErrs++;
    if (tileErrs === 3){
      map.removeLayer(tileLayer);
      const n = document.createElement("div");
      n.style.cssText = "position:absolute;left:50%;top:12px;transform:translateX(-50%);z-index:500;" +
        "background:rgba(245,238,218,.95);border:1px solid #8b765a;padding:4px 14px;" +
        "font:11px KaiTi,serif;letter-spacing:3px;color:#897d66;pointer-events:none";
      n.textContent = "底图离线 · 标记与数据不受影响";
      document.getElementById("map").appendChild(n);
    }
  });
}
setBasemap();

/* 图层 */
const junLayer = L.layerGroup().addTo(map);    // 郡治印（常驻）
const seatLayer = L.layerGroup();             // 首县微点（zoom≥6 挂载）
const hullLayer = L.layerGroup().addTo(map);  // 部域晕（凸包示意）
const junMarkers = {};                        // buId -> [markers]
var selBu = null;                             // 当前选中部域（var：跨脚本无 TDZ）

/* 郡印大小：随属县数缩放（6~16px） */
function sealSize(u){
  return 6 + Math.min((u.xian || []).length || 3, 37) * 0.28;
}

function fmtNum(n){
  return (n || 0).toLocaleString("zh-Hans-CN");
}

function junTip(bu, u, permanent){
  const dir = ["right", "left", "bottom", "right"][u._i % 4];
  const off = {right: [sealSize(u) / 2 + 6, 0], left: [-(sealSize(u) / 2 + 6), 0],
               bottom: [0, sealSize(u) / 2 + 4], top: [0, -(sealSize(u) / 2 + 4)]}[dir];
  if (permanent){
    return {content: u.n.replace(/郡$/, "").replace(/國$/, "國"), opts: {permanent: true, direction: dir, offset: off, className: "fulab"}};
  }
  return {content:
    `<b style="font-family:KaiTi,serif;font-size:14px;letter-spacing:2px">${u.n}</b><br>` +
    `<span style="font-size:10px;letter-spacing:1px;color:#544c3c">${bu.name} · 卷${u.juan}</span><br>` +
    `<span style="font-size:10px;letter-spacing:1px;color:#554e3d">` +
    (u.now ? "今 " + u.now : "") +
    (u.hu ? ` · 戸${fmtNum(u.hu)} 口${fmtNum(u.kou)}` : "") +
    ` · 縣${u.nx}</span>`,
    opts: {direction: "top", offset: [0, -6], opacity: .95, className: "ftip"}};
}

function buildJuns(){
  junLayer.clearLayers(); seatLayer.clearLayers(); hullLayer.clearLayers();
  for (const id in junMarkers) delete junMarkers[id];
  HZ.bu.forEach(bu => {
    junMarkers[bu.id] = [];
    bu.states.forEach((u, i) => {
      if (!u.c) return;
      u._i = i;
      const size = sealSize(u);
      const ic = L.divIcon({className: "", iconSize: [size, size],
        html: `<div class="zseal" style="--pc:${bu.color};width:${size}px;height:${size}px" title="${u.n}"></div>`});
      const m = L.marker(u.c, {icon: ic}).addTo(junLayer);
      m._bu = bu; m._u = u;
      const tip = junTip(bu, u, false);
      m.bindTooltip(tip.content, tip.opts);
      m.on("click", ()=>{ openJun(bu, u); });
      m.on("mouseover", ()=>{ const el = m.getElement() && m.getElement().querySelector(".zseal"); el && el.classList.add("hot"); });
      m.on("mouseout", ()=>{ const el = m.getElement() && m.getElement().querySelector(".zseal"); el && el.classList.remove("hot"); });
      junMarkers[bu.id].push(m);
      /* 首县微点（zoom≥6 展开；坐标=郡治，地理志体例首县例为郡治） */
      if (u.seat){
        const xi = L.divIcon({className: "", iconSize: [7, 7],
          html: `<div class="xseal fg-x" style="--pc:${bu.color}" title="${u.seat}"></div>`});
        const xm = L.marker([u.c[0] + 0.035, u.c[1] + 0.045], {icon: xi, zIndexOffset: -200}).addTo(seatLayer);
        xm._bu = bu; xm._u = u;
        xm.bindTooltip(`<b style="font-family:KaiTi,serif;font-size:13px">${u.seat}</b><br>` +
          `<span style="font-size:10px;letter-spacing:1px;color:#a8391f">首县 · 与${u.n}同治${u.seat_note ? "（有例外注）" : ""}</span>`,
          {direction: "top", offset: [0, -4], opacity: .95, className: "ftip"});
        xm.on("click", ()=>{ openJun(bu, u); });
        junMarkers[bu.id].push(xm);
      }
    });
  });
  applyZoomGates();
  applyBuDim();
}

/* 凸包（Andrew 单调链）：部域晕为治所凸包示意，非考证边界 */
function convexHull(points){
  const pts = [...points].sort((a, b)=>a[0]-b[0]||a[1]-b[1]);
  const cross = (o,a,b)=>(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);
  const lower = [], upper = [];
  for(const p of pts){
    while(lower.length>=2 && cross(lower[lower.length-2], lower[lower.length-1], p) <= 0) lower.pop();
    lower.push(p);
  }
  for(let i=pts.length-1; i>=0; i--){
    const p = pts[i];
    while(upper.length>=2 && cross(upper[upper.length-2], upper[upper.length-1], p) <= 0) upper.pop();
    upper.push(p);
  }
  lower.pop(); upper.pop();
  return lower.concat(upper);
}
function hullLatLngs(points, pad){
  const hull = convexHull(points);
  if (hull.length < 3) return null;
  const n = hull.length;
  const cLat = hull.reduce((s,p)=>s+p[0],0)/n, cLng = hull.reduce((s,p)=>s+p[1],0)/n;
  return hull.map(p=>[cLat+(p[0]-cLat)*pad, cLng+(p[1]-cLng)*pad]);
}

/* 部域晕开关（全部部域 / 仅选中部域） */
var hullsOn = false;
function drawHulls(){
  hullLayer.clearLayers();
  if (!hullsOn && !selBu) return;
  HZ.bu.forEach(bu => {
    if (selBu && bu.id !== selBu) return;
    const pts = bu.states.filter(u=>u.c).map(u=>u.c);
    if (pts.length < 3) return;
    const hull = hullLatLngs(pts, 1.16);
    if (!hull) return;
    L.polygon(hull, {color: bu.color, weight: 2.2, dashArray: "7 6", opacity: .8,
      fillColor: bu.color, fillOpacity: .10, lineCap: "round", interactive: false}).addTo(hullLayer);
    /* 部域名标签：晕重心 */
    const lat = hull.reduce((s,p)=>s+p[0],0)/hull.length;
    const lng = hull.reduce((s,p)=>s+p[1],0)/hull.length;
    L.marker([lat, lng], {icon: L.divIcon({className: "", iconSize: [90, 20],
      html: `<div class="dao-lab">${bu.name}</div>`}), interactive: false,
      zIndexOffset: -600}).addTo(hullLayer);
  });
}

/* 缩放分级：首县微点 zoom≥6；郡名常显 zoom≥7 */
function applyZoomGates(){
  const z = map.getZoom();
  if (z >= 6) map.addLayer(seatLayer); else map.removeLayer(seatLayer);
  Object.values(junMarkers).flat().forEach(m => {
    if (!m._u || !m._bu) return;
    m.unbindTooltip();
    const tip = junTip(m._bu, m._u, z >= 7);
    m.bindTooltip(tip.content, tip.opts);
  });
  applyBuDim();
}
map.on("zoomend", applyZoomGates);

/* 部域选淡出：非选中部域的印/点加 .dim */
function applyBuDim(){
  for (const id in junMarkers){
    junMarkers[id].forEach(m => {
      const el = m.getElement && m.getElement();
      if (!el) return;
      const f = el.querySelector(".zseal");
      if (f) f.classList.toggle("dim", !!selBu && id !== selBu);
      const x = el.querySelector(".xseal");
      if (x) x.classList.toggle("dim", !!selBu && id !== selBu);
    });
  }
}

/* 容器未完成布局（尺寸 0）时飞行动画会 NaN——就绪前延迟重试 */
function safeFly(bounds, opts){
  if (map.getSize().x > 40){
    try{ map.flyToBounds(bounds, opts); }
    catch(e){ map.fitBounds(bounds); }
  } else {
    setTimeout(()=>safeFly(bounds, opts), 250);
  }
}
function safeFlyTo(center, zoom, opts){
  if (map.getSize().x > 40){
    try{ map.flyTo(center, zoom, opts); }
    catch(e){ map.setView(center, zoom); }
  } else {
    setTimeout(()=>safeFlyTo(center, zoom, opts), 250);
  }
}

/* 部域选择 */
function selectBu(id){
  selBu = id;
  document.body.classList.toggle("selbu", !!id);
  applyBuDim();
  drawHulls();
  setHullBtn();
  if (typeof highlightRail === "function") highlightRail(id);
  if (id){
    const bu = HZ.bu.find(b=>b.id === id);
    if (bu){
      const pts = bu.states.filter(u=>u.c).map(u=>u.c);
      if (pts.length){
        safeFly(L.latLngBounds(pts).pad(.22), {duration: 1.1});
      }
      syncHash("bu=" + id);
    }
  } else {
    syncHash(null);
  }
}

/* 部域晕按钮 / 着色开关 */
function setHullBtn(){
  const b = document.getElementById("hullbtn");
  if (b) b.classList.toggle("on", hullsOn);
}
function setMonoBtn(){
  const b = document.getElementById("monobtn");
  if (b) b.classList.toggle("on", document.body.classList.contains("mono"));
}

/* 舆图：点空白取消部域选 */
map.on("click", ()=>{ if (selBu) selectBu(null); });

/* 检索定位郡：飞至 + 脉冲环 */
function revealJun(buId, name){
  const bu = HZ.bu.find(b=>b.id === buId);
  if (!bu) return false;
  const u = bu.states.find(x=>x.n === name || x.raw === name);
  if (!u || !u.c) return false;
  selectBu(buId);
  openJun(bu, u);
  setTimeout(()=>{
    safeFlyTo(u.c, 7, {duration: 1});
    const ring = L.circleMarker(u.c, {radius: 14, weight: 2.2, color: "#a8391f",
      opacity: .9, fill: false, className: "evring"}).addTo(map);
    setTimeout(()=>map.removeLayer(ring), 3200);
  }, 420);
  return true;
}
