/* ═══════════ 汉志经纬 · 深链（#bu=sili&jun=弘農郡 / #yf=秦地 / #search=… / #xref=1） ═══════════
   加载链最末：app.js 已完成 buildJuns/railYutu 初始化。 */

(function deeplink(){
  const q = new URLSearchParams(location.hash.replace(/^#/, ""));
  if (![...q.keys()].length) return;
  dismissBoot();
  if (q.get("search")){
    setTimeout(()=>{
      const si = document.getElementById("search");
      si.value = q.get("search");
      si.dispatchEvent(new Event("input"));
      si.focus();
    }, 700);
    return;
  }
  if (q.get("xref")){
    setTimeout(()=>openXref(), 400);
    return;
  }
  if (q.get("yf")){
    setTimeout(()=>openRegion(q.get("yf")), 400);
    return;
  }
  if (q.get("bu")){
    const bu = HZ.bu.find(x=>x.id === q.get("bu"));
    if (!bu) return;
    selectBu(bu.id);
    if (q.get("jun")){
      const u = bu.states.find(x=>x.n === q.get("jun") || x.raw === q.get("jun"));
      if (u){
        railOpenJun = u.n;
        railYutu();
        setTimeout(()=>openJun(bu, u), 600);
        return;
      }
    }
    openBu(bu);
  }
})();
