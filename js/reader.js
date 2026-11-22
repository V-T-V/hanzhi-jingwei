/* ═══════════ 汉志经纬 · 志文阅读器（懒加载 data/text/*.js） ═══════════
   首屏不载全文；点「阅原文」时按片注入 <script>。 */

const HZTEXT = window.HZTEXT || (window.HZTEXT = {});
const __textQueue = {};

function loadTextFile(key, cb){
  if (HZTEXT[key]) { cb(true); return; }
  if (__textQueue[key]) { __textQueue[key].push(cb); return; }
  __textQueue[key] = [cb];
  const s = document.createElement("script");
  s.src = "data/text/" + key + ".js";
  s.onload = ()=>{ const q = __textQueue[key]; delete __textQueue[key]; q.forEach(f=>f(true)); };
  s.onerror = ()=>{ const q = __textQueue[key]; delete __textQueue[key]; q.forEach(f=>f(false)); };
  document.head.appendChild(s);
}

function escT(s){ return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

/* 注文小字化：（…）与（…）内的双行夹注 */
function noteSmall(esc){
  return esc
    .replace(/（([^）]*)）/g, '<span class="zhun">（$1）</span>')
    .replace(/\(([^()]*)\)/g, '<span class="zhun">($1)</span>');
}

/* ── 阅读字号（会话级记忆） ── */
let tfs = 14.5;
/* ── 朗读（TTS）：自当前视口段落起读，逐段高亮跟随 ── */
let ttsOn = false, ttsVoice = null;
function pickVoice(){
  const vs = speechSynthesis.getVoices();
  ttsVoice = vs.find(v=>/zh[-_]CN/i.test(v.lang) && /female|Huihui|Yaoyao/i.test(v.name))
          || vs.find(v=>/^zh/i.test(v.lang)) || null;
}
if ("speechSynthesis" in window){
  pickVoice();
  speechSynthesis.onvoiceschanged = pickVoice;
}
function stopTTS(){
  if (!ttsOn) return;
  ttsOn = false;
  try{ speechSynthesis.cancel(); }catch(e){}
  pbody.querySelectorAll(".speaking").forEach(el=>el.classList.remove("speaking"));
  const b = document.getElementById("ttsb");
  if (b) b.textContent = "🔊";
}
function startTTS(txt){
  if (!("speechSynthesis" in window)) return;
  stopTTS();
  if (txt){
    ttsOn = true;
    const u0 = new SpeechSynthesisUtterance(String(txt));
    if (ttsVoice) u0.voice = ttsVoice;
    u0.lang = "zh-CN"; u0.rate = 0.95;
    u0.onend = ()=>{ ttsOn = false; };
    u0.onerror = ()=>stopTTS();
    speechSynthesis.speak(u0);
    return;
  }
  const tps = Array.from(pbody.querySelectorAll(".tp"));
  if (!tps.length) return;
  const top = pbody.getBoundingClientRect().top;
  let i0 = tps.findIndex(tp=>{
    const r = tp.getBoundingClientRect();
    return r.bottom > top + 40;
  });
  if (i0 < 0) i0 = 0;
  ttsOn = true;
  const tb = document.getElementById("ttsb");
  if (tb) tb.textContent = "⏹";
  const queue = tps.slice(i0);
  const speak = k=>{
    if (!ttsOn || k >= queue.length){ stopTTS(); return; }
    queue.forEach(tp=>tp.classList.remove("speaking"));
    queue[k].classList.add("speaking");
    queue[k].scrollIntoView({behavior: "smooth", block: "center"});
    const u = new SpeechSynthesisUtterance(queue[k].textContent);
    if (ttsVoice) u.voice = ttsVoice;
    u.lang = "zh-CN"; u.rate = 0.95;
    u.onend = ()=>speak(k + 1);
    u.onerror = ()=>stopTTS();
    speechSynthesis.speak(u);
  };
  speak(0);
}

/* 定位词：命中处常驻标记并居中 */
function jumpInText(q){
  if (!q) return;
  const eq = escT(q);
  for (const tp of pbody.querySelectorAll(".tp")){
    if (!tp.textContent.includes(q)) continue;
    const html = tp.innerHTML;
    let i = -1, from = 0;
    while ((i = html.indexOf(eq, from)) >= 0){
      const head = html.slice(0, i);
      if (head.lastIndexOf("<") <= head.lastIndexOf(">")) break;
      from = i + 1;
    }
    if (i >= 0){
      tp.innerHTML = html.slice(0, i) + "<span class='hitmark'>" + eq + "</span>" + html.slice(i + eq.length);
      tp.querySelector(".hitmark").scrollIntoView({behavior: "smooth", block: "center"});
    } else {
      tp.scrollIntoView({behavior: "smooth", block: "start"});
    }
    return;
  }
}

/* 段落形态：县名行（括号注前 ≤5 字）与裸县名行（≤6 字）为条目头 */
function paraHtml(p){
  const esc = escT(p);
  const headMatch = p.match(/^([\u4e00-\u9fff□]{1,5})（/);
  if (headMatch){
    return `<p class="tp"><span class="hd">${escT(headMatch[1])}</span>${noteSmall(esc.slice(headMatch[1].length))}</p>`;
  }
  if (p.length <= 6 && !/[，。；：]/.test(p)){
    return `<p class="tp"><span class="hd">${esc}</span></p>`;
  }
  return "<p class='tp'>" + noteSmall(esc) + "</p>";
}

function renderText(title, kicker, raw, backFn, toc){
  stopTTS();
  vset(title.length > 5 ? title.slice(0, 5) : title, "志文");
  const paras = raw.split(/\n+/).map(p=>p.trim()).filter(Boolean);
  const body = paras.map(paraHtml).join("");
  const tocHtml = (toc && toc.length)
    ? `<div class="tocrow"><span class="tocap">县目跳转</span>${toc.slice(0, 60).map(n=>
        `<span class="chip small tocz" data-n="${n}">${n}</span>`).join("")}</div>` : "";
  pbody.innerHTML = `
    <div id="readprog"><div class="bar"></div></div>
    <div class="p-kicker">${kicker}</div>
    <button class="tback" id="tback">⟨ 返回详情</button>
    <div class="tmeta">《地理志 · ${title}》全篇 · ${raw.length.toLocaleString()} 字
      <span class="tbtns"><button class="tfsb" data-d="-1" title="缩小">A−</button><button class="tfsb" data-d="1" title="放大">A+</button><button class="tfsb" id="tdl" title="存为文本">⤓ 文本</button><button class="tfsb" id="tnight" title="夜读">☾</button><button class="tfsb" id="ttsb" title="朗读">🔊</button></span>
      <span class="tlegend">朱字为县名条目头 · 小字为双行夹注（師古曰等） · Ctrl+P 存 PDF</span></div>
    ${tocHtml}
    <div class="twrap" style="font-size:${tfs}px">${body}</div>`;
  document.getElementById("tback").onclick = backFn;
  const nb = document.getElementById("tnight");
  const applyNight = on => {
    panel.classList.toggle("panel-night", on);
    nb.textContent = on ? "☀" : "☾";
    try{ localStorage.setItem("hsnight", on ? "1" : "0"); }catch(e){}
  };
  let nightOn = false;
  try{ nightOn = localStorage.getItem("hsnight") === "1"; }catch(e){}
  applyNight(nightOn);
  nb.onclick = ()=>applyNight(!panel.classList.contains("panel-night"));
  const tb = document.getElementById("ttsb");
  if (tb) tb.onclick = ()=>{ ttsOn ? stopTTS() : startTTS(); };
  document.getElementById("tdl").onclick = ()=>{
    const blob = new Blob([raw], {type: "text/plain;charset=utf-8"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "地理志-" + title + ".txt";
    a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
  };
  pbody.querySelectorAll(".tfsb[data-d]").forEach(b=>b.onclick=()=>{
    tfs = Math.min(20, Math.max(11.5, tfs + (+b.dataset.d) * 1.5));
    pbody.querySelector(".twrap").style.fontSize = tfs + "px";
  });
  pbody.querySelectorAll(".tocz").forEach(z=>z.onclick=()=>{
    const name = z.dataset.n;
    const tp = Array.from(pbody.querySelectorAll(".tp .hd"))
      .find(h=>h.textContent === name || h.textContent.includes(name));
    if (!tp) return;
    tp.scrollIntoView({behavior: "smooth", block: "start"});
    tp.parentElement.classList.add("flash");
    setTimeout(()=>tp.parentElement.classList.remove("flash"), 1600);
  });
  pbody.scrollTop = 0;
  showPanel();

  /* 阅读进度条 + 回顶 */
  const progBar = pbody.querySelector("#readprog .bar");
  const updateProg = ()=>{
    if (!progBar) return;
    const max = pbody.scrollHeight - pbody.clientHeight;
    progBar.style.width = (max > 0 ? pbody.scrollTop / max * 100 : 0).toFixed(1) + "%";
    const bt = pbody.querySelector("#backtop");
    if (bt) bt.classList.toggle("show", pbody.scrollTop > 400);
  };
  pbody.addEventListener("scroll", updateProg, {passive: true});
  const backtop = document.createElement("div");
  backtop.id = "backtop";
  backtop.textContent = "↑";
  backtop.title = "回到篇首";
  backtop.onclick = ()=>pbody.scrollTo({top: 0, behavior: "smooth"});
  pbody.querySelector(".twrap").after(backtop);
  if (renderText._q){ const q = renderText._q; renderText._q = null; setTimeout(()=>jumpInText(q), 120); }
}

function textFallback(title, backFn, note){
  vset(title.length > 5 ? title.slice(0, 5) : title, "志文");
  pbody.innerHTML = `
    <div class="p-kicker">志文全篇</div>
    <button class="tback" id="tback">⟨ 返回详情</button>
    <div class="hint" style="margin-top:10px">${note || "此篇文本未得。"}</div>`;
  document.getElementById("tback").onclick = backFn;
  showPanel();
}

/* 郡条全文 */
function openJunText(bu, u, q){
  renderText._q = q || null;
  const back = ()=>openJun(bu, u);
  loadTextFile(u.juan === "上" ? "j1" : "j2", ok=>{
    const bag = ok && HZTEXT[u.juan === "上" ? "j1" : "j2"];
    const t = bag && (bag[u.n] || null);
    if (t){
      renderText(u.n, "漢書·地理志卷" + (u.juan === "上" ? "二十八上" : "二十八下") + " · " + bu.name, t, back,
        u.xian && u.xian.length ? u.xian : null);
    } else {
      textFallback(u.n, back, "此郡条文本未得。");
    }
  });
}
/* 部域诸郡全文（连缀） */
function openBuText(bu){
  const back = ()=>openBu(bu);
  loadTextFile("j1", ()=>loadTextFile("j2", ()=>{
    const parts = bu.states.map(u=>{
      const bag = HZTEXT[u.juan === "上" ? "j1" : "j2"];
      return bag && bag[u.n];
    }).filter(Boolean);
    const raw = parts.join("\n\n");
    if (raw) renderText(bu.name + "諸郡全文", "漢書·地理志 · " + bu.name, raw, back);
    else textFallback(bu.name, back);
  }));
}
/* 卷首文献（提要/志序/总计） */
function openJuanshou(i){
  const name = JUANSHOU[i] || "卷首";
  const back = ()=>openIntro();
  const key = name === "四庫提要" ? "juanshou" : (name === "志序" ? "sy" : "zj");
  loadTextFile(key, ok=>{
    const bag = ok && HZTEXT[key];
    const t = bag && bag[name];
    if (t) renderText(name, "漢書·地理志 · 卷首", t, back);
    else textFallback(name, back);
  });
}
