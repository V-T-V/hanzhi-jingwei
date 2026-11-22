/* ═══════════ 汉志经纬 · 检索（部域·郡国·县·域分） ═══════════ */

const IDX = (()=>{
  const a = [];
  HZ.bu.forEach(b=>{
    a.push({t: b.name, k: "部", ctx: b.states.length + "郡国", bu: b.id});
    b.states.forEach(u=>{
      a.push({t: u.n, k: "郡", ctx: b.name + (u.now ? " · 今" + u.now.split("（")[0] : ""), bu: b.id, jun: u.n});
      (u.xian || []).forEach(x=>{
        a.push({t: x, k: "县", ctx: b.name + " · " + u.n, bu: b.id, jun: u.n});
      });
    });
  });
  HZ.regions.forEach(r=>{
    a.push({t: r.n, k: "域", ctx: r.fy || "域分风俗", yf: r.n});
  });
  return a;
})();

const sinput = document.getElementById("search"), sres = document.getElementById("sresults");

function searchHits(q){
  return IDX.filter(x=>x.t.includes(q))
    .sort((a, b)=>(a.t === q ? -1 : 0) - (b.t === q ? -1 : 0) ||
                   a.t.indexOf(q) - b.t.indexOf(q) || a.t.length - b.t.length)
    .slice(0, 14);
}
function renderHits(hits, q){
  const escQ = q.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const ftRow = `<div class="sr ftall" id="ftall">📖 在全书志文中检索「${escQ}」…</div>`;
  if (!hits.length){
    sres.innerHTML = `<div class="none">名录未见「${escQ}」</div>` + ftRow;
  } else {
    sres.innerHTML = hits.map((h, i)=>
      `<div class="sr" data-i="${i}"><span class="tag t${h.k}">${h.k}</span>` +
      `<span>${h.t}</span><span class="ctx">${h.ctx}</span></div>`).join("") + ftRow;
    sres.querySelectorAll(".sr[data-i]").forEach(el=>
      el.onclick = ()=>goHit(hits[+el.dataset.i]));
  }
  sres.classList.add("open");
  const fa = sres.querySelector("#ftall");
  if (fa) fa.onclick = ()=>ftRun(q);
}
function goHit(h){
  sinput.value = h.t;
  sres.classList.remove("open");
  if (h.k === "部"){
    selectBu(h.bu);
    openBu(HZ.bu.find(b=>b.id === h.bu));
  } else if (h.k === "郡" || (h.k === "县" && h.jun && revealJun(h.bu, h.jun))){
    if (h.k === "郡") revealJun(h.bu, h.jun);
  } else if (h.k === "域"){
    openRegion(h.yf);
  } else {
    const bu = HZ.bu.find(b=>b.id === h.bu);
    if (bu) openBu(bu);
  }
}

/* 输入防抖：IME 组合期不逐键重建 */
let _sT = null;
sinput.addEventListener("input", ()=>{
  const q = sinput.value.trim();
  if (!q){ clearTimeout(_sT); sres.classList.remove("open"); return; }
  clearTimeout(_sT);
  _sT = setTimeout(()=>renderHits(searchHits(q), q), 110);
});
/* 回车直达第一条 */
sinput.addEventListener("keydown", e=>{
  if (e.key !== "Enter") return;
  const q = sinput.value.trim();
  if (!q) return;
  const hits = searchHits(q);
  if (hits.length) goHit(hits[0]);
});
document.addEventListener("click", e=>{
  if (!e.target.closest("#searchwrap")) sres.classList.remove("open");
});
