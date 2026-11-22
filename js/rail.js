/* ═══════════ 汉志经纬 · 左列纲目（部域—郡国—属县） ═══════════ */

const rail = document.getElementById("raillist");
const railtitle = document.getElementById("railtitle");
let railOpenJun = null;

function railYutu(){
  railtitle.innerHTML = `十四部域一百三郡国<small>循郡而读 · 县${ST.x}</small>`;
  let html = "";
  /* 开关：部域晕 / 玄墨着色 */
  html += `<div class="ri" id="hullbtn" style="border-bottom:1px solid var(--line)">
    <span class="dot" style="box-shadow:inset 0 0 0 1.5px currentColor;color:var(--xuan)"></span>
    <span><span class="nm">部域晕开关</span><span class="ju">治所凸包示意</span></span></div>`;
  html += `<div class="ri" id="monobtn">
    <span class="dot" style="box-shadow:inset 0 0 0 1.5px currentColor;color:var(--ink-faint)"></span>
    <span><span class="nm">玄墨单色</span><span class="ju">郡印着色开关</span></span></div>`;
  HZ.bu.forEach(b=>{
    html += `<div class="ri ri-bu" data-bu="${b.id}">
      <span class="dot" style="background:${b.color};box-shadow:inset 0 0 0 1.5px ${b.color}"></span>
      <span><span class="nm">${b.name}</span><span class="ju">${b.states.length}郡国 · 县${b.states.reduce((s,u)=>s+(u.xian||[]).length,0)}</span></span>
      <span class="ct">卷${b.states[0] ? b.states[0].juan : "?"}</span></div>`;
    b.states.forEach(u=>{
      const open = railOpenJun === u.n;
      html += `<div class="rsub" data-bu="${b.id}" data-jun="${u.n}">
        ${u.n.endsWith("國") ? '<span style="color:var(--cinnabar-d)">國</span> ' : ""}${u.n.replace(/郡$/, "")}
        <span style="color:var(--ink-faint)">(${u.nx})</span> ${open ? "▾" : "▸"}</div>`;
      if (open){
        (u.xian || []).forEach((x, i)=>{
          html += `<div class="rsub${i === 0 ? " kuo" : ""}" style="padding-left:48px;font-size:10.5px;color:${i === 0 ? "var(--cinnabar-d)" : "var(--ink-faint)"}">${i === 0 ? "◦ " : ""}${x}</div>`;
        });
      }
    });
  });
  rail.innerHTML = html;
  rail.querySelectorAll(".ri-bu").forEach(el=>el.onclick=()=>{
    selectBu(el.dataset.bu);
    openBu(HZ.bu.find(b=>b.id === el.dataset.bu));
  });
  rail.querySelectorAll(".rsub[data-jun]").forEach(el=>el.onclick=()=>{
    const opening = railOpenJun !== el.dataset.jun;
    railOpenJun = opening ? el.dataset.jun : null;
    railYutu();
    if (opening){
      const bu = HZ.bu.find(b=>b.id === el.dataset.bu);
      const u = bu && bu.states.find(x=>x.n === el.dataset.jun);
      if (u) syncHash("bu=" + bu.id + "&jun=" + encodeURIComponent(u.n));
    } else {
      syncHash("bu=" + el.dataset.bu);
    }
  });
  const hb = rail.querySelector("#hullbtn");
  if (hb) hb.onclick = ()=>{ hullsOn = !hullsOn; drawHulls(); setHullBtn(); };
  const mb = rail.querySelector("#monobtn");
  if (mb) mb.onclick = ()=>{
    document.body.classList.toggle("mono");
    try{ localStorage.setItem("hsvmono", document.body.classList.contains("mono") ? "1" : "0"); }catch(e){}
    setMonoBtn();
  };
  setHullBtn();
  setMonoBtn();
  highlightRail(selBu);
}

function highlightRail(buId){
  rail.querySelectorAll(".ri-bu").forEach(el=>
    el.classList.toggle("on", el.dataset.bu === buId));
}
