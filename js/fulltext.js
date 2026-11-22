/* ═══════════ 汉志经纬 · 全书志文检索（懒加载分片 + Worker 扫描） ═══════════ */

const FT_KEYS = ["juanshou", "sy", "zj", "yf", "j1", "j2"];
let _ftWorker = null, _ftDocs = null;

function ftProgress(onDone){
  /* 载全部分片 → docs 列表 */
  let pending = FT_KEYS.slice();
  const step = ()=>{
    if (!pending.length){ onDone(); return; }
    const k = pending.shift();
    loadTextFile(k, ()=>step());
  };
  step();
}

function ftCollectDocs(){
  const docs = [];
  FT_KEYS.forEach(k=>{
    const bag = HZTEXT[k];
    if (!bag) return;
    const kickers = {
      juanshou: "漢書·卷首提要", sy: "漢書·地理志·志序",
      zj: "漢書·地理志·总计", yf: "漢書·地理志下·域分风俗",
      j1: "漢書·地理志卷二十八上", j2: "漢書·地理志卷二十八下",
    };
    Object.keys(bag).forEach(t=>{
      if (k === "j1" || k === "j2"){
        const bu = HZ.bu.find(b=>b.states.some(u=>u.n === t));
        const u = bu && bu.states.find(x=>x.n === t);
        docs.push({key: k, title: t, jun: t,
          kicker: "地理志卷" + (k === "j1" ? "二十八上" : "二十八下") +
                  (bu ? " · " + bu.name : ""), text: bag[t]});
      } else {
        docs.push({key: k, title: t, kicker: kickers[k] || "漢書·地理志", text: bag[t]});
      }
    });
  });
  return docs;
}

function ftRun(q){
  vset("全書檢索", "全文");
  pbody.innerHTML = `
    <div class="p-kicker">全书志文检索 · 「${escT(q)}」</div>
    <div class="hint" id="ftprog">正在加载志文分片…（首查约数秒，此后缓存）</div>
    <div id="ftresults"></div>`;
  showPanel();
  ftProgress(()=>{
    _ftDocs = ftCollectDocs();
    const prog = document.getElementById("ftprog");
    if (prog) prog.textContent = `全书 ${_ftDocs.length} 篇已就绪，Worker 扫描中…`;
    if (!_ftWorker){
      try{
        _ftWorker = new Worker("js/ftworker.js");
      }catch(e){
        _ftWorker = null;
      }
    }
    const render = results=>{
      if (prog) prog.textContent = results.length
        ? `「${escT(q)}」全书命中 ${results.length} 篇（按命中数排序）`
        : `「${escT(q)}」全书未见`;
      const box = document.getElementById("ftresults");
      if (!box) return;
      box.innerHTML = results.map((r, i)=>
        `<div class="ftrow" data-i="${i}">
          <div class="fth">${r.title} <span style="font-size:10px;color:var(--cinnabar-d)">${r.n}处</span>
            <span style="font-size:10px;color:var(--ink-faint);margin-left:6px">${r.kicker}</span></div>
          <div class="ftsnip">${r.snip}</div></div>`).join("");
      box.querySelectorAll(".ftrow").forEach(el=>{
        el.onclick = ()=>{
          const r = results[+el.dataset.i];
          if (r.key === "j1" || r.key === "j2"){
            const bu = HZ.bu.find(b=>b.states.some(u=>u.n === r.title));
            const u = bu && bu.states.find(x=>x.n === r.title);
            if (u) openJunText(bu, u, q);
          } else if (r.key === "yf"){
            openRegion(r.title);
          } else {
            renderText._q = q;
            const i2 = JUANSHOU.indexOf(r.title);
            if (i2 >= 0) openJuanshou(i2);
            else if (r.title === "志序") openJuanshou(1);
            else if (r.title === "郡國總計") openJuanshou(2);
          }
        };
      });
    };
    if (_ftWorker){
      _ftWorker.onmessage = e=>{ if (e.data.q === q) render(e.data.results); };
      _ftWorker.postMessage({q: q, docs: _ftDocs});
    } else {
      /* Worker 不可用（file:// 等）——主线程同核扫描 */
      const results = _ftDocs.map(d=>({key: d.key, title: d.title, kicker: d.kicker,
        n: countHits(d.text, q), snip: ftSnippet(d.text, q)}))
        .filter(r=>r.n > 0).sort((a, b)=>b.n - a.n).slice(0, 60);
      render(results);
    }
  });
}
