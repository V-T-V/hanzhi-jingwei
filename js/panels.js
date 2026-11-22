/* ═══════════ 汉志经纬 · 卷宗面板（总览 / 部域 / 郡卡 / 域分 / 关于） ═══════════ */

const panel = document.getElementById("panel"),
      pbody = document.getElementById("pbody"),
      vname = document.getElementById("vname"),
      vseal = document.getElementById("vseal");
function showPanel(){ panel.classList.add("open"); document.body.classList.remove("nopanel"); }
function hidePanel(){ panel.classList.remove("open"); document.body.classList.add("nopanel"); }
document.getElementById("pclose").onclick = ()=>{ hidePanel(); if (selBu) selectBu(null); };
function vset(name, seal){ vname.textContent = name; vseal.textContent = seal || "漢志"; }

/* 全局统计（自解析数据实时计算） */
const ST = (()=>{
  let nJ = 0, nX = 0, nC = 0, nOk = 0, nMang = 0, nHu = 0, nKou = 0;
  HZ.bu.forEach(b=>{
    b.states.forEach(u=>{
      nJ++; nX += (u.xian || []).length;
      if (u.c) nC++;
      if (u.ok) nOk++;
      nMang += u.badges ? u.badges.mang : 0;
      nHu += u.hu || 0; nKou += u.kou || 0;
    });
  });
  return {bu: HZ.bu.length, j: nJ, x: nX, c: nC, ok: nOk, mang: nMang,
          hu: nHu, kou: nKou, yf: HZ.regions.length,
          tot: HZ.meta.totals};
})();

const fmt = n => (n || 0).toLocaleString("zh-Hans-CN");

/* ── 总览（首屏面板） ── */
function openIntro(){
  vset("漢志經緯", "總覽");
  pbody.innerHTML = `
    <div class="p-kicker">漢書·地理志 · 東漢·班固 撰 · 唐·顔師古 注 · ${HZ.meta.year}</div>
    <div class="quote" style="text-align:center;font-size:14.5px;line-height:2.3;padding:20px 10px">
      凡郡國一百三，縣邑千三百一十四<br>道三十二，侯國二百四十一……漢極盛矣</div>
    <div class="stat-strip">
      <div class="st"><b>${ST.j}</b><span>郡国</span></div>
      <div class="st"><b>${ST.x}</b><span>县邑道国入表</span></div>
      <div class="st"><b>${fmt(ST.tot.hu)}</b><span>帝国户（志总）</span></div>
      <div class="st"><b>${fmt(ST.tot.kou)}</b><span>帝国口（志总）</span></div>
    </div>
    <div class="p-cap">十四部域纲</div>
    <ul class="ful" id="bulist">
      ${HZ.bu.map(b=>`<li data-id="${b.id}">
        <span class="dot" style="width:9px;height:9px;flex:none;box-shadow:inset 0 0 0 1.5px ${b.color};background:${b.color}"></span>
        <span class="fn">${b.name}</span>
        <span class="fnow">${b.states.reduce((s,u)=>s+(u.hu||0),0) ? fmt(b.states.reduce((s,u)=>s+(u.hu||0),0)) + "户" : ""}</span>
        <span class="fct">${b.states.length}郡国</span><span class="arrow">➤</span></li>`).join("")}
    </ul>
    <div class="p-cap">卷首文献</div>
    <div class="chips" id="jschips">
      ${JUANSHOU.map((t,i)=>`<span class="chip jschip" data-i="${i}">${t}</span>`).join("")}
    </div>
    <div class="p-cap">域分风俗 · 十三区域</div>
    <div class="chips" id="yfchips">
      ${HZ.regions.map((r,i)=>`<span class="chip yfchip" data-i="${i}">${r.n}</span>`).join("")}
    </div>
    <div class="p-cap">使用</div>
    <div class="hint">左列纲目按「部域—郡国」循读（点郡名展开属县名录），点部域观其治所晕罩（非考证边界）。郡印大小随属县数，色随部域（底栏「玄墨」开关转单色）；zoom≥6 首县微点显现，zoom≥7 郡名常显。顶栏检索郡县名（回车直达），「在全书原文中检索」遍检志文全篇。深链自动写回地址栏。</div>`;
  pbody.querySelectorAll("#bulist li").forEach(li=>li.onclick=()=>{
    selectBu(li.dataset.id);
    openBu(HZ.bu.find(b=>b.id === li.dataset.id));
  });
  pbody.querySelectorAll(".jschip").forEach(c=>c.onclick=()=>openJuanshou(+c.dataset.i));
  pbody.querySelectorAll(".yfchip").forEach(c=>c.onclick=()=>openRegion(HZ.regions[+c.dataset.i].n));
  showPanel();
}

/* ── 部域面板 ── */
function openBu(bu){
  vset(bu.name, "部域");
  const rows = bu.states.map(u=>`
    <li data-n="${u.n}">
      <span class="fn">${u.n}</span>
      <span class="fnow">${u.now ? "今" + u.now.split("（")[0] : ""}</span>
      <span class="fct">${(u.xian || []).length ? u.xian.length + "县" : ""}</span>
      <span class="arrow">➤</span></li>`).join("");
  const nHu = bu.states.reduce((s,u)=>s+(u.hu||0), 0);
  const nKou = bu.states.reduce((s,u)=>s+(u.kou||0), 0);
  const nX = bu.states.reduce((s,u)=>s+(u.xian||[]).length, 0);
  pbody.innerHTML = `
    <div class="p-kicker">西汉末监察部域整编（示意分组） · ${bu.states[0] ? "卷" + bu.states[0].juan + "起" : ""}</div>
    <div class="p-ju">${bu.name}</div>
    <div class="stat-strip" style="margin:0 0 12px">
      <div class="st"><b>${bu.states.length}</b><span>郡国</span></div>
      <div class="st"><b>${nX}</b><span>县（名录）</span></div>
      <div class="st"><b>${fmt(nHu)}</b><span>户（分计）</span></div>
      <div class="st"><b>${fmt(nKou)}</b><span>口（分计）</span></div>
    </div>
    <div class="p-cap">郡国</div>
    <ul class="ful">${rows}</ul>
    <div class="readrow"><button class="readfull" data-buft="1">阅${bu.name}诸郡全文 ➤</button></div>`;
  pbody.querySelectorAll(".ful li[data-n]").forEach(li=>li.onclick=()=>{
    const u = bu.states.find(x=>x.n === li.dataset.n);
    if (u) openJun(bu, u);
  });
  const fb = pbody.querySelector("[data-buft]");
  if (fb) fb.onclick = ()=>openBuText(bu);
  selectBu(bu.id);
  syncHash("bu=" + bu.id);
  showPanel();
}

/* 徽标 chips */
function badgeChips(u){
  const items = [];
  BADGE_LABELS.forEach(([k, lab])=>{
    const v = u.badges && u.badges[k];
    if (v) items.push(`<span class="chip bdg" data-k="${k}">${lab}${v > 1 ? "×" + v : ""}</span>`);
  });
  return items.join("");
}

/* ── 郡卡（详情） ── */
var __curJun = null;
function openJun(bu, u){
  __curJun = { bu: bu.id, n: u.n };
  vset(u.n.replace(/郡$/, "").slice(0, 5), u.n.endsWith("國") ? "國" : "郡");
  const xchips = (u.xian || []).map((x, i)=>
    `<span class="chip${i === 0 ? " fg" : ""}" title="${i === 0 ? "首县 · 例为郡治" : "属县（名录存真，治所未定位）"}">${x}${i === 0 ? " · 首县" : ""}</span>`).join("");
  const bd = badgeChips(u);
  pbody.innerHTML = `
    <div class="p-kicker">${bu.name} · 卷${u.juan}${u.ok ? "" : " · 名录对账未全（如实标注）"}</div>
    ${u.now ? `<div class="p-now">治今 ${u.now}${u.conf === 2 ? "（推）" : ""}</div>` : ""}
    ${u.seat_note ? `<div class="lostnote">${u.seat_note}</div>` : ""}
    <div class="readrow" style="margin:0 0 4px">
      <button class="readfull" data-ft="1">阅郡条原文 ➤</button>
      <button class="star" data-st="1">☆ 书签</button>
    </div>
    <div class="p-cap">元始二年户口（原书句）</div>
    <div class="hukou">「${u.hukou_v || "（户口文未详）"}」<br>
      <b>戸 ${fmt(u.hu)} · 口 ${fmt(u.kou)} · 縣 ${u.nx}</b></div>
    <div class="p-cap">辖县${(u.xian || []).length ? " · 管" + u.xian.length + "县（入表" + u.xian.length + " / 原文载" + u.nx + "）" : ""}</div>
    <div class="chips">${xchips || '<span class="chip small">县名录未详</span>'}</div>
    ${bd ? `<div class="p-cap">名物注记（注中实证）</div><div class="chips">${bd}</div>` : ""}
    <div class="readrow" style="margin-top:8px">
      <button class="readfull" id="shareJun" title="复制此景链接">🔗 分享此景</button>
    </div>
    <div class="p-cap">出处 · 定位</div>
    <div class="hint">《漢書·地理志》卷${u.juan} · ${u.n}条。治所坐标为依汉代政区地理整编之今地（src:derived${u.conf === 2 ? " · 置信度：推" : " · 置信度：确"}），郡治从首县例（例外者已注）；属县但存名录，未作定位。户口为元始二年（公元2年）之籍。</div>`;
  const fb = pbody.querySelector("[data-ft]");
  if (fb) fb.onclick = ()=>openJunText(bu, u);
  const sb = pbody.querySelector("[data-st]");
  if (sb) sb.onclick = ()=>{
    const added = BM.toggle(bu, u);
    sb.classList.toggle("on", added);
    sb.textContent = (added ? "★" : "☆") + " 书签";
  };
  const sh = pbody.querySelector("#shareJun");
  if (sh) sh.onclick = ()=>{
    const url = location.origin + location.pathname +
      "#bu=" + bu.id + "&jun=" + encodeURIComponent(u.n);
    const ok = ()=>{ sh.textContent = "✓ 已复制"; setTimeout(()=>sh.textContent = "🔗 分享此景", 1600); };
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(ok, ok);
    else {
      const ta = document.createElement("textarea");
      ta.value = url; document.body.appendChild(ta);
      ta.select(); document.execCommand("copy"); ta.remove(); ok();
    }
  };
  pbody.querySelectorAll(".chip.bdg").forEach(c=>c.onclick=()=>jumpInJunText(bu, u, BADGE_LABELS.find(b=>b[0] === c.dataset.k)[1]));
  if (u.c) safeFlyTo(u.c, 7, {duration: 1.1});
  syncHash("bu=" + bu.id + "&jun=" + encodeURIComponent(u.n));
  showPanel();
}

/* 徽标 → 郡条原文中定位（如「铁官」） */
function jumpInJunText(bu, u, kw){
  openJunText(bu, u, kw);
}

/* ── 域分风俗（十三区域） ── */
function regionJuns(rn){
  /* 区域文中实及的郡国（语料字符串匹配，展示用） */
  return HZ.bu.flatMap(b=>b.states).filter(u =>
    window.HZTEXT && HZTEXT.yf && (HZTEXT.yf[rn] || "").includes(u.n.replace(/郡$/, "").replace(/國$/, "")) ||
    (HZTEXT.yf[rn] || "").includes(u.n));
}
function openRegion(rn){
  vset(rn, "域分");
  loadTextFile("yf", ok=>{
    const t = ok && HZTEXT.yf ? HZTEXT.yf[rn] : null;
    const meta = HZ.regions.find(r=>r.n === rn) || {};
    const body = t
      ? t.split("\n").map(p=>{
          if (p.length > 6 && /^[\u4e00-\u9fff]{2}地，/.test(p))
            return `<p class="tp"><span class="hd">${escT(p.slice(0, 2))}地</span>${escT(p.slice(2))}</p>`;
          return "<p class='tp'>" + escT(p) + "</p>";
        }).join("")
      : `<div class="hint">区域文本未得。</div>`;
    pbody.innerHTML = `
      <div class="p-kicker">地理志下 · 域分风俗 · 分野：${meta.fy || ""}</div>
      <div class="p-ju">${rn}</div>
      <div class="stat-strip" style="margin:0 0 10px">
        <div class="st"><b>${meta.chars || 0}</b><span>字数</span></div>
        <div class="st"><b>${HZ.regions.length}</b><span>区域</span></div>
      </div>
      <div class="twrap" style="font-size:13.5px">${body}</div>
      <div class="p-cap">他域</div>
      <div class="chips">${HZ.regions.map(r=>`<span class="chip${r.n === rn ? " fg" : ""}" data-r="${r.n}">${r.n}</span>`).join("")}</div>`;
    pbody.querySelectorAll(".chip[data-r]").forEach(c=>c.onclick=()=>openRegion(c.dataset.r));
    showPanel();
    syncHash("yf=" + encodeURIComponent(rn));
  });
}

/* ── 关于 · 版本与体例（如实标注） ── */
function openAbout(){
  vset("關於", "校記");
  pbody.innerHTML = `
    <div class="p-kicker">汉志经纬 · 数据与体例</div>
    <div class="stat-strip" style="margin-top:2px">
      <div class="st"><b>${ST.bu}</b><span>部域（整编）</span></div>
      <div class="st"><b>${ST.j}</b><span>郡国</span></div>
      <div class="st"><b>${ST.x}</b><span>县入表</span></div>
      <div class="st"><b>${ST.c}</b><span>郡治坐标</span></div>
      <div class="st"><b>${ST.ok}</b><span>名录对账全合</span></div>
      <div class="st"><b>${ST.mang}</b><span>莽改县注</span></div>
      <div class="st"><b>${ST.yf}</b><span>域分区域</span></div>
      <div class="st"><b>${fmt(ST.hu)}</b><span>户（郡分计）</span></div>
    </div>
    <div class="p-cap">源流</div>
    <div class="hint">文本取自 kanripo《前漢書》（KR2a0007，文淵閣四庫本）卷二十八上/下，即《漢書·地理志》全志；抓取解析管线 tools/fetch_text.py → build_data.py → build_text.py。郡国 103 条县名录与原书「縣N」逐一对账全合，入表县 ${ST.x}；域分风俗十三区域、名物注记（铁官/盐官/工官/橘官/木官/祠/莽曰）皆出自脚本。凡数字出自 data/stats.json。</div>
    <div class="p-cap">版本与体例</div>
    <div class="hint">${MISSING_NOTE}</div>
    <div class="p-cap">户口对账（如实并陈）</div>
    <div class="hint">郡分计：戸 ${fmt(ST.hu)} · 口 ${fmt(ST.kou)}；志末总计：戸 ${fmt(ST.tot.hu)} · 口 ${fmt(ST.tot.kou)}。分计与总計有差（户差 ${fmt(ST.hu - ST.tot.hu)}、口差 ${fmt(ST.kou - ST.tot.kou)}）——传世志文户 口 分计与总计数不合，旧籍实情，两存之。縣分计 ${ST.x}，志总 1587（縣邑1314+道32+侯国241），差 9 同此。</div>
    <div class="p-cap">已知之阙</div>
    <div class="hint">郡治坐标为今地整编（非考古定位），置信分确/推；部域分组为西汉末监察部域整编示意（淮陽/梁/魯从豫、桂陽从荆等从通说），非考证边界。县治未定位（志无道里可推），仅首县与郡同治。静态本地站，无追踪，首访后可离线（Service Worker）。</div>`;
  showPanel();
}

/* ═══════════ 汉唐对照 · 元和互查桥（data/xref_yh.js，build_xref_yh.py 生成） ═══════════ */
function xrefLink(m){
  return "../YHJZ/#dao=" + m.id + "&zhou=" + encodeURIComponent(m.n);
}
function openXref(){
  vset("漢唐對照", "橋");
  const M = HZXREF.meta;
  const badges = m => {
    let b = "";
    if (m.kind === "承名同地") b += `<span class="xb xb-r">改名</span>`;
    if (m.tongcheng) b += `<span class="xb xb-s">同城</span>`;
    if (m.qianyi) b += `<span class="xb xb-y">迁治</span>`;
    return b;
  };
  const groups = HZXREF.byBu.map(g=>{
    const rows = HZXREF.rows.filter(r=>r.bu === g.bu).map(r=>{
      if (r.m){
        return `<li data-bu="${g.id}" data-jun="${r.n}">
          <span class="fn">${r.n}</span>
          <span class="fnow">${r.why || ""}</span>
          <span class="fct">${r.m.n}${badges(r.m)}</span>
          <a class="xgo" href="${xrefLink(r.m)}" target="_blank" rel="noopener" title="于元和经纬开此条">↗</a></li>`;
      }
      return `<li class="lostrow">
          <span class="fn" style="color:var(--ink-faint)">${r.n}</span>
          <span class="fnow">${r.why}</span></li>`;
    }).join("");
    return `<div class="p-cap" style="margin-top:10px">${g.bu} <span style="color:var(--ink-faint)">·得唐对应 ${g.matched} / ${g.total}${g.qianyi ? " ·迁治 " + g.qianyi : ""}</span></div><ul class="ful">${rows}</ul>`;
  }).join("");
  const samples = (HZXREF.samples || []).map(s=>`
    <div class="xsamp">
      <div class="xs-head"><b>漢 · ${s.hn}</b>${s.kind === "承名同地" ? '<span class="xb xb-r">改名</span>' : ""}${s.tongcheng ? '<span class="xb xb-s">同城</span>' : ""}${s.qianyi ? '<span class="xb xb-y">迁治</span>' : ""}</div>
      <div class="xs-q">「${s.hq}」<span class="xs-src">——漢書地理志</span></div>
      <div class="xs-head" style="margin-top:6px"><b>唐 · ${s.tn}</b>
        <a class="xgo" href="../YHJZ/#dao=${s.tid}&zhou=${encodeURIComponent(s.tn)}" target="_blank" rel="noopener">↗元和</a></div>
      <div class="xs-q">「${s.tq}」<span class="xs-src">——元和郡县图志</span></div>
    </div>`).join("");
  pbody.innerHTML = `
    <div class="p-kicker">汉（元始二年·公元2年）× 唐（元和八年·813）郡治↔州治对照 · 凡计数出自 tools/build_xref_yh.py</div>
    <div class="stat-strip" style="margin:2px 0 10px">
      <div class="st"><b>${M.han_juns}</b><span>汉郡国</span></div>
      <div class="st"><b>${M.matched}</b><span>得唐对应</span></div>
      <div class="st"><b>${M.same_name}</b><span>同名</span></div>
      <div class="st"><b>${M.renamed}</b><span>承名同地</span></div>
      <div class="st"><b>${M.tongcheng}</b><span>同城双治</span></div>
      <div class="st"><b>${M.unmatched}</b><span>无对应</span></div>
    </div>
    <div class="p-cap">样例 · 汉志原文 × 元和原文</div>
    ${samples}
    <div class="hint">同名=汉郡名去郡/國尾与唐州府名相合且治所今地相合（≤60 km）；承名同地=治所近而名承（汉郡→唐州承名如河东郡→河中府同城异名者计「同城」）；无对应如实分档（唐废/改置/边外）。同名异地者不入档。</div>
    <div class="p-cap">全表 · 按汉部域分组</div>
    ${groups}
    <div class="hint">↗ 于姊妹站「元和经纬」打开对应条目（相对路径 ../YHJZ/——需父目录同根服务，见 README）。唐侧另有 ${M.tang_new} 州无汉郡对应（新置），不计入汉侧。</div>`;
  pbody.querySelectorAll(".ful li[data-jun]").forEach(li=>li.onclick=()=>{
    const bu = HZ.bu.find(b=>b.id === li.dataset.bu);
    const u = bu && bu.states.find(x=>x.n === li.dataset.jun);
    if (u) openJun(bu, u);
  });
  pbody.querySelectorAll("a.xgo").forEach(a=>a.onclick=e=>e.stopPropagation());
  showPanel();
}

/* ═══════════ 郡国导出（与 tools/export_data.py 同口径：CSV BOM / KML / GeoJSON） ═══════════ */
function exportRows(){
  /* 郡国表：部域/郡国/卷/戸/口/縣数/入表县数/首县/治所今地/纬/经/src/置信/坐标注记 */
  const jun = [];
  HZ.bu.forEach(b=>b.states.forEach(u=>{
    const note = "整编今地坐标（非考古定位）" + (u.seat_note ? "；" + u.seat_note : "");
    jun.push([b.name, u.n, u.juan || "", u.hu || "", u.kou || "", u.nx || "",
              (u.xian || []).length, u.seat || "", u.now || "",
              (u.c ? u.c[0] : ""), (u.c ? u.c[1] : ""),
              u.src || "derived", u.conf === 2 ? "推" : "确", note]);
  }));
  /* 县表：部域/郡国/县/首县|属县/附注 */
  const xian = [];
  HZ.bu.forEach(b=>b.states.forEach(u=>(u.xian || []).forEach((x, i)=>{
    xian.push([b.name, u.n, x, i === 0 ? "首县" : "属县",
      i === 0 ? "与郡治同治（" + (u.now || "").split("（")[0] + "）" : "名录存真，治所未定位"]);
  })));
  return {jun, xian};
}
function dlBlob(content, mime, fname){
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], {type: mime}));
  a.download = fname;
  a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href), 3000);
}
function csvOf(rows){
  const NL = String.fromCharCode(10), BOM = String.fromCharCode(0xFEFF);
  return BOM + rows.map(r=>r.join(",")).join(NL);
}
function openExport(){
  vset("導出", "集");
  const E = exportRows();
  const M = window.HZXREF ? HZXREF.meta : null;
  pbody.innerHTML = `
    <div class="p-kicker">古今对照导出 · 与 tools/export_data.py 同口径（${E.jun.length} 郡国 / ${E.xian.length} 县）</div>
    <div class="readrow" style="flex-direction:column;align-items:stretch;gap:8px">
      <button class="readfull" id="ex-jcsv">⤓ 郡国对照 CSV（${E.jun.length} 行 · 带 BOM）</button>
      <button class="readfull" id="ex-xcsv">⤓ 县名录 CSV（${E.xian.length} 行 · 带 BOM）</button>
      <button class="readfull" id="ex-kml">⤓ 郡治点位 KML（Google Earth）</button>
      <button class="readfull" id="ex-geo">⤓ 郡治点位 GeoJSON</button>
    </div>
    <div class="p-cap">字段口径</div>
    <div class="hint">郡国表：部域、郡国、卷（上/下）、戸与口（元始二年）、縣数（原文载）与入表县数、首县、治所今地（即今名依据）、纬度、经度、src、置信（确/推）、坐标注记。县表：部域、郡国、县、首县/属县、附注。坐标为依汉代政区地理整编之今地（src:derived，非考古定位），首县例与郡同治（例外注明），余县但存名录不做定位臆测——导出中如实注明。汉唐对照另见「漢唐」页签${M ? "（匹配 " + M.matched + " 郡）" : ""}。</div>`;
  pbody.querySelector("#ex-jcsv").onclick = ()=>{
    const {jun} = exportRows();
    jun.unshift(["部域","郡国","卷","戸（元始二年）","口","縣数（原文载）","入表县数","首县","治所今地（依据）","纬度","经度","src","置信","坐标注记"]);
    dlBlob(csvOf(jun), "text/csv;charset=utf-8", "汉志经纬-郡国对照.csv");
  };
  pbody.querySelector("#ex-xcsv").onclick = ()=>{
    const {xian} = exportRows();
    xian.unshift(["部域","郡国","县","首县/属县","附注"]);
    dlBlob(csvOf(xian), "text/csv;charset=utf-8", "汉志经纬-县名录.csv");
  };
  pbody.querySelector("#ex-kml").onclick = ()=>{
    let pins = "";
    HZ.bu.forEach(b=>b.states.forEach(u=>{
      if (!u.c) return;
      pins += `<Placemark><name>${u.n}</name><description>${b.name} · 卷${u.juan || ""} · 戸${u.hu || ""} 口${u.kou || ""} 縣${u.nx || ""} 今${u.now || ""}（src:derived 置信${u.conf === 2 ? "推" : "确"}）</description><Point><coordinates>${u.c[1]},${u.c[0]},0</coordinates></Point></Placemark>`;
    }));
    const kml = `<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>汉志经纬·郡治点位（整编今地坐标）</name>${pins}</Document></kml>`;
    dlBlob(kml, "application/vnd.google-earth.kml+xml", "汉志经纬-郡治点位.kml");
  };
  pbody.querySelector("#ex-geo").onclick = ()=>{
    const feats = [];
    HZ.bu.forEach(b=>b.states.forEach(u=>{
      if (!u.c) return;
      feats.push({type: "Feature", geometry: {type: "Point", coordinates: [u.c[1], u.c[0]]},
        properties: {名: u.n, 部域: b.name, 卷: u.juan || "", 戸: u.hu || 0, 口: u.kou || 0,
          縣: u.nx || 0, 首县: u.seat || "", 今地: u.now || "",
          src: u.src || "derived", 置信: u.conf === 2 ? "推" : "确",
          坐标注记: "整编今地坐标（非考古定位）"}});
    }));
    dlBlob(JSON.stringify({type: "FeatureCollection", features: feats}), "application/geo+json", "汉志经纬-郡治点位.geojson");
  };
  showPanel();
}
