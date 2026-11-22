/* ═══════════ 汉志经纬 · 统计 / 启动 / 快捷键 / 书签 ═══════════ */

/* 状态写回 URL（刷新/分享保持视图） */
function syncHash(rest){
  const h = rest ? "#" + rest : location.pathname + location.search;
  try{
    history.replaceState(null, "", rest ? (location.pathname + location.search + h) : h);
  }catch(e){}
}

/* 初始图层与纲目 */
buildJuns();
railYutu();

/* 着色开关记忆 */
try{
  if (localStorage.getItem("hsvmono") === "1") document.body.classList.add("mono");
}catch(e){}
setMonoBtn();

/* 底栏统计 */
document.getElementById("bookstat").textContent =
  `${ST.bu}部域 · ${ST.j}郡国 · 县${ST.x} · 戸${(ST.hu / 10000).toFixed(1)}万（分计）`;

/* 序幕 */
function dismissBoot(cb){
  const b = document.getElementById("boot");
  if (!b){ cb && cb(); return; }
  b.classList.add("gone");
  setTimeout(()=>{ b.remove(); cb && cb(); }, 900);
}
var _bt = document.getElementById("boot");
if (_bt) _bt.onclick = ()=>dismissBoot(()=>openIntro());

/* ── 书签（localStorage，至多 30） ── */
const BM = {
  load(){
    try{ return JSON.parse(localStorage.getItem("hsbm") || "[]"); }catch(e){ return []; }
  },
  save(list){
    try{ localStorage.setItem("hsbm", JSON.stringify(list.slice(0, 30))); }catch(e){}
  },
  has(buId, n){ return this.load().some(b=>b.bu === buId && b.n === n); },
  toggle(bu, u){
    const list = this.load();
    const i = list.findIndex(b=>b.bu === bu.id && b.n === u.n);
    if (i >= 0) list.splice(i, 1);
    else list.push({bu: bu.id, n: u.n, now: u.now ? u.now.split("（")[0] : ""});
    this.save(list);
    return i < 0;
  },
};
function openBookmarks(){
  vset("書籤", "藏");
  const list = BM.load();
  pbody.innerHTML = `
    <div class="p-kicker">我的书签 · ${list.length} 处郡国</div>
    ${list.length ? `<ul class="ful">${list.map((b, i)=>`
      <li data-i="${i}"><span class="fn">${b.n}</span>
        <span class="fnow">${b.now ? "今" + b.now : ""}</span>
        <span class="fct" data-del="${i}" style="color:var(--cinnabar);cursor:pointer">✕</span>
        <span class="arrow">➤</span></li>`).join("")}</ul>`
      : `<div class="hint">尚无书签——郡详情页点 ☆ 收藏。</div>`}`;
  pbody.querySelectorAll(".ful li").forEach(li=>li.onclick=e=>{
    if (e.target.dataset.del !== undefined){
      const list2 = BM.load();
      list2.splice(+e.target.dataset.del, 1);
      BM.save(list2);
      openBookmarks();
      return;
    }
    const b = list[+li.dataset.i];
    const bu = HZ.bu.find(x=>x.id === b.bu);
    const u = bu && bu.states.find(x=>x.n === b.n);
    if (u) openJun(bu, u);
  });
  showPanel();
}

/* ── 漫游：随机入郡 ── */
function wander(){
  const pool = [];
  HZ.bu.forEach(b=>b.states.forEach(u=>{ if (u.c && u.hu) pool.push([b, u]); }));
  const [bu, u] = pool[Math.floor(Math.random() * pool.length)];
  selectBu(bu.id);
  setTimeout(()=>openJun(bu, u), 400);
}

/* 快捷键：Esc 收面板 / ? 关于 / / 聚焦检索 */
document.addEventListener("keydown", e=>{
  if (e.key === "Escape"){
    hidePanel();
    if (selBu) selectBu(null);
    return;
  }
  if (e.key === "?" && e.target.tagName !== "INPUT"){ openAbout(); return; }
  if (e.key === "/" && e.target.tagName !== "INPUT"){
    e.preventDefault();
    sinput.focus(); sinput.select();
  }
});

var _al = document.getElementById("aboutlink");
if (_al) _al.onclick = openAbout;
var _wl = document.getElementById("wanderlink");
if (_wl) _wl.onclick = wander;
var _bl = document.getElementById("bmlink");
if (_bl) _bl.onclick = openBookmarks;
var _yl = document.getElementById("yflink");
if (_yl) _yl.onclick = ()=>openRegion(HZ.regions[0].n);
var _td = document.getElementById("tdlink");
if (_td) _td.onclick = function(){
  location.href = "3d.html" + (__curJun
    ? "#bu=" + __curJun.bu + "&jun=" + encodeURIComponent(__curJun.n) : "");
};
var _nl = document.getElementById("nightlink");
if (_nl) _nl.onclick = ()=>{
  panel.classList.toggle("panel-night");
  try{ localStorage.setItem("hsnight", panel.classList.contains("panel-night") ? "1" : "0"); }catch(e){}
};
var _xl = document.getElementById("xreflink");
if (_xl) _xl.onclick = openXref;

/* PWA 离线徽标 */
(function(){
  const el = document.getElementById("swstate");
  if (!el || !("serviceWorker" in navigator) || !/^https?:$/.test(location.protocol)) return;
  navigator.serviceWorker.ready.then(()=>{
    el.style.display = "";
    const upd = ()=>{ el.textContent = navigator.onLine ? "◼ 离线可用" : "◼ 离线中 · 全志可读"; };
    upd();
    addEventListener("online", upd);
    addEventListener("offline", upd);
  }).catch(()=>{});
})();
