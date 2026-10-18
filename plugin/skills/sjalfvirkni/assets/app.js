const { $, fmt, tabs } = BF;
const CH = {};
const DAYS = ['sunnudagur', 'mánudagur', 'þriðjudagur', 'miðvikudagur', 'fimmtudagur', 'föstudagur', 'laugardagur'];
const DS = ['sun', 'mán', 'þri', 'mið', 'fim', 'fös', 'lau'];
const MFULL = ['janúar', 'febrúar', 'mars', 'apríl', 'maí', 'júní', 'júlí', 'ágúst', 'september', 'október', 'nóvember', 'desember'];
const MODE = { notify: 'Tilkynning', propose: 'Tillaga', draft: 'Drög í BC' };
const SEV = { h: ['h', 'Bregðast við'], m: ['m', 'Athuga'], l: ['l', 'Í lagi'], i: ['i', 'Ekki keyrt'] };
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const pad = n => String(n).padStart(2, '0');
const dstr = d => `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()}`;

/* Vörulisti: fastur í kóða. Stillingar og saga eru í STATE. */
const CAT = [
  // Vöktun
  { id: 'manadarlok', k: 'agent', flow: 'Mánaðarlok', n: 'Mánaðarlok', d: 'Gátlisti um lokun mánaðar: laun, vörunotkun, afskriftir og VSK bókuð, jöfnuður innan mánaðar, tímabili lokað.', w: 0 },
  { id: 'afstemmingar', k: 'agent', flow: 'Banki og fjármagn', n: 'Afstemmingar', d: 'Banki á móti bankabók og fjárhag, kort, undirbækur á móti fjárhag, VSK og innbyrðis staða. Tillögur að pörun.', w: 0 },
  { id: 'faersluvakt', k: 'agent', flow: 'Innra eftirlit', n: 'Færsluvakt', d: 'Handfærðar tekjur, sléttar fjárhæðir, helgarfærslur, tvíreikningsfærsla, breyttir bankareikningar birgja.', w: 0 },
  { id: 'innheimta', k: 'agent', flow: 'Sala til innheimtu', n: 'Innheimta', d: 'Aldursgreining, drög að innheimtupóstum og viðvörun þegar nýr reikningur fer á viðskiptavin í vanskilum.', w: 0 },
  { id: 'samthykkt', k: 'agent', flow: 'Innkaup til greiðslu', n: 'Samþykkt reikninga', d: 'Áminning til samþykkjanda fyrir gjalddaga og staðgreiðsluafslátt. Leitar að tvíteknum reikningum.', w: 0 },
  { id: 'reikningsfaersla', k: 'agent', flow: 'Sala til innheimtu', n: 'Reikningsfærsla (tekjuleki)', d: 'Óreikningsfærð vinna á verkum, notkun á 0 kr. og vinna eftir samningslok. Drög að reikningum.', w: 1 },
  { id: 'sjodstada', k: 'agent', flow: 'Banki og fjármagn', n: 'Sjóðstaða', d: 'Uppfærir 13 vikna spá og varar við ef lægsta staða fer undir lágmark.', w: 0 },
  { id: 'stjornarpakki', k: 'agent', flow: 'Mánaðarlok', n: 'Stjórnarpakki', d: 'Uppfærir mælaborðin, raun á móti spá, og skrifar drög að stöðupósti til stjórnar.', w: 0 },
  { id: 'arsuppgjor', k: 'agent', flow: 'Laun og opinber skil', n: 'Ársuppgjör', d: 'Undirbúningslisti fyrir endurskoðanda, lokun fyrra árs, skilafrestir og stærðarflokkur skv. lögum nr. 3/2006.', w: 0 },
  // Handverk
  { id: 'innlestur', k: 'hand', flow: 'Innkaup til greiðslu', n: 'Innlestur innkaupareikninga', d: 'Les rafræna reikninga og PDF, stofnar innkomið skjal og gerir bókunartillögu (lykill, VSK, deild, verk) eftir sögu birgis.', w: 1 },
  { id: 'parun_innkaupa', k: 'hand', flow: 'Innkaup til greiðslu', n: 'Pörun pöntunar, móttöku og reiknings', d: 'Þríhliða pörun og merking verð- og magnfrávika.', w: 0 },
  { id: 'kort', k: 'hand', flow: 'Innkaup til greiðslu', n: 'Kortafærslur og kvittanir', d: 'Parar kvittanir, flokkar kostnað, merkir risnu og ófrádráttarbæran VSK, eltir kvittanir sem vantar.', w: 1 },
  { id: 'greidslubunkar', k: 'hand', flow: 'Innkaup til greiðslu', n: 'Greiðslutillögur', d: 'Greiðslubunki eftir gjalddögum, afslætti og sjóðstöðu. Bókari samþykkir, bankinn framkvæmir.', w: 1 },
  { id: 'fyrirspurnir', k: 'hand', flow: 'Innkaup til greiðslu', n: 'Fyrirspurnir birgja', d: 'Svar um stöðu reiknings og samþykktarferli.', w: 0 },
  { id: 'timar', k: 'hand', flow: 'Sala til innheimtu', n: 'Reikningar úr tímum og verkum', d: 'Drög að sölureikningum úr tímaskráningu og verkáföngum.', w: 1 },
  { id: 'endurteknir', k: 'hand', flow: 'Sala til innheimtu', n: 'Endurteknir reikningar', d: 'Áskriftir og leiga, verðuppfærsla eftir vísitölu þar sem samningur kveður á um.', w: 1 },
  { id: 'innborganir', k: 'hand', flow: 'Sala til innheimtu', n: 'Pörun innborgana', d: 'Parar innborganir við kröfur eftir tilvísun, kennitölu eða fjárhæð.', w: 1 },
  { id: 'yfirlit', k: 'hand', flow: 'Sala til innheimtu', n: 'Viðskiptayfirlit og stöðustaðfestingar', d: 'Sendir yfirlit, sérstaklega við áramót.', w: 0 },
  { id: 'bankafaerslur', k: 'hand', flow: 'Banki og fjármagn', n: 'Bókun bankahreyfinga', d: 'Reglur fyrir bankagjöld, vexti, millifærslur milli eigin reikninga og fastar greiðslur.', w: 1 },
  { id: 'verdbaetur', k: 'hand', flow: 'Banki og fjármagn', n: 'Verðbætur verðtryggðra lána', d: 'Mánaðarleg færsla verðbóta og vaxta eftir vísitölu og afborganatöflu.', w: 1 },
  { id: 'gengi', k: 'hand', flow: 'Banki og fjármagn', n: 'Gengismunur', d: 'Endurmat erlendra krafna, skulda og banka á gengi Seðlabankans.', w: 1 },
  { id: 'timabundnar', k: 'hand', flow: 'Mánaðarlok', n: 'Áfallinn og fyrirframgreiddur kostnaður', d: 'Mánaðarleg dreifing og sjálfvirk bakfærsla.', w: 1 },
  { id: 'afskriftir', k: 'hand', flow: 'Mánaðarlok', n: 'Afskriftir og nýjar eignir', d: 'Keyrir afskriftir og stingur upp á eignfærslu innkaupa yfir mörkum.', w: 1 },
  { id: 'innbyrdis', k: 'hand', flow: 'Mánaðarlok', n: 'Innbyrðis viðskipti', d: 'Umsýslugjöld milli félaga, millifélagareikningar og jöfnun samstæðu.', w: 1 },
  { id: 'landad', k: 'hand', flow: 'Mánaðarlok', n: 'Landað kostnaðarverð', d: 'Dreifir tolli, flutningi og aðflutningsgjöldum á vörur.', w: 1 },
  { id: 'laun', k: 'hand', flow: 'Laun og opinber skil', n: 'Bókun launa', d: 'Les launaskrá og bókar laun, staðgreiðslu, lífeyri, stéttarfélög og tryggingagjald.', w: 1 },
  { id: 'stadgreidsla', k: 'hand', flow: 'Laun og opinber skil', n: 'Afstemming staðgreiðslu og lífeyris', d: 'Skil 15. hvers mánaðar á móti fjárhag.', w: 0 },
  { id: 'vsk', k: 'hand', flow: 'Laun og opinber skil', n: 'VSK-skil', d: 'Undirbýr skýrslu tímabilsins, afstemmir uppgjörsreikning, finnur ranga VSK-kóða.', w: 0 },
  { id: 'midar', k: 'hand', flow: 'Laun og opinber skil', n: 'Launamiðar, verktakamiðar og hlunnindi', d: 'Undirbúningur í janúar úr gögnum ársins.', w: 0 },
  { id: 'nyir', k: 'hand', flow: 'Grunnskrár', n: 'Nýir birgjar og viðskiptamenn', d: 'Flettir upp kennitölu og VSK-númeri, varar við tvískráningu.', w: 1 },
  { id: 'bankabirgja', k: 'hand', flow: 'Grunnskrár', n: 'Breytingar á bankaupplýsingum birgja', d: 'Krefst staðfestingar annars aðila (svikavörn).', w: 0 },
  { id: 'aaetlun', k: 'hand', flow: 'Grunnskrár', n: 'Fjárhagsáætlun inn í BC', d: 'Hleður áætlun inn svo raun á móti áætlun virki.', w: 1 },
];
const FLOWS = ['Innkaup til greiðslu', 'Sala til innheimtu', 'Banki og fjármagn', 'Mánaðarlok', 'Laun og opinber skil', 'Grunnskrár', 'Innra eftirlit'];

const S = JSON.parse(JSON.stringify(STATE));
/* Niðurstöður síðustu keyrslu: STATE.find = { id: ['h'|'m'|'l', 'texti'] } */
CAT.forEach(a => { if (S.find && S.find[a.id]) a.r = S.find[a.id]; else if (a.k === 'agent') a.r = ['i', 'Ekki keyrt.']; });
const cfg = id => S.sched[id] || { on: false, freq: 'manual', time: '07:00', mode: 'notify', sc: S.company || '', rc: 'Fjármálastjóri' };

/* Næsta keyrsla */
function nthWorkday(y, m, n) { let c = 0; for (let d = 1; d <= 31; d++) { const x = new Date(y, m, d); if (x.getMonth() !== m) break; const w = x.getDay(); if (w > 0 && w < 6 && ++c === n) return x; } return null; }
function nextRun(c, from = new Date()) {
  if (!c.on || c.freq === 'manual' || c.freq === 'event') return null;
  const [hh, mm] = (c.time || '07:00').split(':').map(Number);
  const at = d => { const x = new Date(d); x.setHours(hh, mm, 0, 0); return x; };
  for (let i = 0; i < 800; i++) {
    const d = at(new Date(from.getFullYear(), from.getMonth(), from.getDate() + i));
    if (d <= from) continue;
    const w = d.getDay(), dom = d.getDate(), mo = d.getMonth();
    const last = new Date(d.getFullYear(), mo + 1, 0).getDate();
    const md = c.md === 'last' ? last : +c.md || 1;
    if (c.freq === 'daily' && w > 0 && w < 6) return d;
    if (c.freq === 'weekly' && w === (+c.wd || 1)) return d;
    if (c.freq === 'monthly' && dom === Math.min(md, last)) return d;
    if (c.freq === 'workday') { const t = nthWorkday(d.getFullYear(), mo, +c.md || 1); if (t && t.getDate() === dom) return d; }
    if (c.freq === 'bimonthly' && mo % 2 === 1 && dom === Math.min(md, last)) return d; // feb, apr, jún… (VSK-gjalddagi 5. annars mánaðar)
    if (c.freq === 'quarterly' && mo % 3 === 0 && dom === Math.min(md, last)) return d;
    if (c.freq === 'yearly' && mo === (+c.mo || 0) && dom === Math.min(md, last)) return d;
  }
  return null;
}
function schedText(c) {
  if (!c.on) return 'Óvirkt';
  const t = c.time || '07:00', md = c.md === 'last' ? 'síðasta dag' : `${c.md || 1}.`;
  return ({ daily: `Virka daga kl. ${t}`, weekly: `Hvern ${DAYS[+c.wd || 1]} kl. ${t}`, monthly: `Mánaðarlega, ${md} dag kl. ${t}`, workday: `${c.md || 1}. virka dag mánaðar kl. ${t}`,
    bimonthly: `Á 2 mán. fresti, ${md} dag kl. ${t}`, quarterly: `Ársfjórðungslega, ${md} dag kl. ${t}`, yearly: `Árlega ${md} ${MFULL[+c.mo || 0]} kl. ${t}`,
    event: `Við atburð: ${(c.ev || 'bókun í fjárhag').toLowerCase()}`, manual: 'Aðeins handvirkt' })[c.freq];
}
const fmtNext = d => d ? `${DS[d.getDay()]} ${dstr(d)} kl. ${pad(d.getHours())}:${pad(d.getMinutes())}` : '–';

/* ---------- Teikning ---------- */
function render() {
  const all = CAT, on = all.filter(a => cfg(a.id).on), ag = all.filter(a => a.k === 'agent'), hand = all.filter(a => a.k === 'hand');
  const finds = ag.filter(a => a.r && a.r[0] !== 'i' && a.r[0] !== 'l');
  const ups = on.map(a => ({ a, t: nextRun(cfg(a.id)) })).filter(x => x.t).sort((x, y) => x.t - y.t);
  $('h-big').innerHTML = `${on.length}<small>af ${all.length} á áætlun</small>`;
  $('h-txt').textContent = ups.length ? `Næsta keyrsla: ${ups[0].a.n}, ${fmtNext(ups[0].t)}. ${finds.filter(a => a.r[0] === 'h').length} ábendingar kalla á viðbrögð.` : 'Engin keyrsla á áætlun. Veldu erindreka eða handverk og stilltu hvenær það keyrir.';
  $('h-row').innerHTML = [['Vöktunarerindrekar', `${ag.filter(a => cfg(a.id).on).length}/${ag.length}`], ['Handverk', `${hand.filter(a => cfg(a.id).on).length}/${hand.length}`], ['Í biðröð', S.queue.length], ['Við atburð', on.filter(a => cfg(a.id).freq === 'event').length]]
    .map(([l, v]) => `<div><b>${v}</b><span>${l}</span></div>`).join('');
  $('kpis').innerHTML = [
    ['Opnar ábendingar', finds.length, `${finds.filter(a => a.r[0] === 'h').length} kalla á viðbrögð`],
    ['Keyrslur næstu 7 daga', ups.filter(x => x.t - new Date() < 7 * 864e5).length, 'skv. áætlun'],
    ['Virkjað með ráðgjafa', 0, 'keyrsla óvirk þar til virkjað'],
    ['Síðast vistað', S.updated ? dstr(new Date(S.updated)) : '–', S.updated ? `kl. ${new Date(S.updated).toTimeString().slice(0, 5)}` : 'ekkert vistað enn'],
  ].map(([l, v, d]) => `<div class="card kpi"><span class="l">${l}</span><span class="v">${v}</span><span class="d">${d}</span></div>`).join('');
  $('next').innerHTML = ups.filter(x => x.t - new Date() < 7 * 864e5).slice(0, 6).map(({ a, t }) =>
    `<div class="d-item"><span class="d-ico l">${DS[t.getDay()]}</span><div><b>${esc(a.n)}</b><p>${fmtNext(t)} · ${MODE[cfg(a.id).mode]} · ${esc(cfg(a.id).rc)}</p></div><span></span></div>`).join('') || '<p class="sub">Engar keyrslur næstu 7 daga.</p>';
  $('finds').innerHTML = finds.sort((x, y) => (x.r[0] === 'h' ? 0 : 1) - (y.r[0] === 'h' ? 0 : 1)).slice(0, 6).map(a =>
    `<div class="d-item"><span class="d-ico ${a.r[0]}">!</span><div><b>${esc(a.n)}</b><p>${esc(a.r[1])}</p></div><button class="btn sm" type="button" disabled title="Virkja þarf aðgerð með ráðgjafa">🔒 Keyra aftur</button></div>`).join('');
  $('byflow').innerHTML = FLOWS.map(f => { const L = all.filter(a => a.flow === f), n = L.filter(a => cfg(a.id).on).length, p = L.length ? 100 * n / L.length : 0;
    return `<div class="r"><span>${f}</span><div class="t"><span style="left:0;width:${p}%;background:var(--s2)"></span></div><span class="n">${n}/${L.length}</span></div>`; }).join('');
  renderAgents(); renderHand(); renderCal(); renderSaga(); bindRows();
}
function card(a) {
  const c = cfg(a.id), nx = nextRun(c), q = S.queue.some(x => x.id === a.id), sv = a.r ? SEV[a.r[0]] : null;
  return `<article class="card ac ${c.on ? 'on' : ''}">
    <div class="ch"><h2>${esc(a.n)}</h2><label class="sw" title="Setja á áætlun eða taka af"><input type="checkbox" data-tog="${a.id}" ${c.on ? 'checked' : ''} aria-label="Setja ${esc(a.n)} á áætlun"><span></span></label></div>
    <p class="sub">${esc(a.d)}</p>
    ${a.r ? `<div class="res"><span class="pill ${sv[0]}">${sv[1]}</span><span>${esc(a.r[1])}</span></div>` : ''}
    <div class="meta"><span>🕑 ${schedText(c)}</span>${nx ? `<span>Næst: ${fmtNext(nx)}</span>` : ''}<span>${MODE[c.mode]}</span><span class="pill i">Bíður virkjunar</span></div>
    <div class="acts"><button class="btn" type="button" disabled title="Virkja þarf aðgerð með ráðgjafa">🔒 Keyra núna</button><button class="btn ghost" data-cfg="${a.id}" type="button">Stilla tíma</button></div>
  </article>`;
}
function renderAgents() { $('agents').innerHTML = CAT.filter(a => a.k === 'agent').map(card).join(''); }
let flowF = 'all';
function renderHand() {
  const fl = FLOWS.filter(f => CAT.some(a => a.k === 'hand' && a.flow === f));
  $('flowf').innerHTML = [['all', 'Öll ferli'], ...fl.map(f => [f, f])].map(([v, l]) => `<button type="button" data-flow="${esc(v)}" aria-pressed="${flowF === v}">${l}</button>`).join('');
  $('hand').innerHTML = fl.filter(f => flowF === 'all' || flowF === f).map(f => `<section class="card"><div class="ch"><h2>${f}</h2><span class="sub">${CAT.filter(a => a.k === 'hand' && a.flow === f && cfg(a.id).on).length} virk</span></div>
    <div class="scroll"><table class="ht"><thead><tr><th>Á áætlun</th><th>Verk</th><th>Hvað erindrekinn gerir</th><th>Keyrsla</th><th></th></tr></thead><tbody>${CAT.filter(a => a.k === 'hand' && a.flow === f).map(a => { const c = cfg(a.id), q = S.queue.some(x => x.id === a.id);
      return `<tr><td><label class="sw"><input type="checkbox" data-tog="${a.id}" ${c.on ? 'checked' : ''} aria-label="Setja ${esc(a.n)} á áætlun"><span></span></label></td><td><b>${esc(a.n)}</b>${a.w ? '<br><span class="pill i">getur stofnað drög</span>' : ''}</td><td class="sub">${esc(a.d)}</td><td><span class="sched">${schedText(c)}</span><br><span class="sub">${MODE[c.mode]}</span></td>
      <td class="acts"><button class="btn sm" type="button" disabled title="Virkja þarf aðgerð með ráðgjafa">🔒 Keyra</button><button class="btn sm ghost" data-cfg="${a.id}" type="button">Stilla</button></td></tr>`; }).join('')}</tbody></table></div></section>`).join('');
  document.querySelectorAll('#flowf button').forEach(b => b.onclick = () => { flowF = b.dataset.flow; renderHand(); bindRows(); });
}
function renderCal() {
  const now = new Date(), days = [...Array(14)].map((_, i) => new Date(now.getFullYear(), now.getMonth(), now.getDate() + i));
  const runs = CAT.filter(a => cfg(a.id).on).flatMap(a => { const out = []; let t = new Date(now); for (let k = 0; k < 14; k++) { t = nextRun(cfg(a.id), t); if (!t || t - now > 14 * 864e5) break; out.push({ a, t }); } return out; });
  $('cal-sub').textContent = `${dstr(days[0])}–${dstr(days[13])} · ${runs.length} keyrslur`;
  $('cal').innerHTML = days.map(d => { const R = runs.filter(x => x.t.toDateString() === d.toDateString()).sort((x, y) => x.t - y.t), we = d.getDay() === 0 || d.getDay() === 6;
    return `<div class="cd ${we ? 'we' : ''} ${d.toDateString() === now.toDateString() ? 'today' : ''}"><div class="cdh"><b>${DS[d.getDay()]}</b> ${d.getDate()}.${d.getMonth() + 1}.</div>${R.map(x => `<div class="ev ${x.a.k}">${pad(x.t.getHours())}:${pad(x.t.getMinutes())} ${esc(x.a.n)}</div>`).join('')}</div>`; }).join('');
  const ev = CAT.filter(a => cfg(a.id).on && cfg(a.id).freq === 'event');
  $('events').innerHTML = ev.map(a => `<div class="d-item"><span class="d-ico m">⚡</span><div><b>${esc(a.n)}</b><p>${schedText(cfg(a.id))} · ${MODE[cfg(a.id).mode]}</p></div><span></span></div>`).join('') || '<p class="sub">Enginn erindreki keyrir við atburð.</p>';
}
function renderSaga() {
  $('queue').innerHTML = S.queue.map(q => { const a = CAT.find(x => x.id === q.id); return `<div class="d-item"><span class="d-ico m">⏳</span><div><b>${esc(a ? a.n : q.id)}</b><p>Sett í biðröð ${dstr(new Date(q.at))} kl. ${new Date(q.at).toTimeString().slice(0, 5)}</p></div><button class="btn sm ghost" data-unq="${q.id}" type="button">Fjarlægja</button></div>`; }).join('') || '<p class="sub">Biðröðin er tóm.</p>';
  $('log').innerHTML = `<thead><tr><th>Tími</th><th>Erindreki</th><th>Niðurstaða</th><th>Staða</th></tr></thead><tbody>` + S.log.slice().reverse().map(l => { const a = CAT.find(x => x.id === l.id), sv = SEV[l.s] || SEV.i;
    return `<tr><td class="mono">${dstr(new Date(l.at))} ${new Date(l.at).toTimeString().slice(0, 5)}</td><td>${esc(a ? a.n : l.id)}</td><td class="sub">${esc(l.txt)}</td><td><span class="pill ${sv[0]}">${sv[1]}</span></td></tr>`; }).join('') + '</tbody>';
}
function bindRows() {
  document.querySelectorAll('[data-tog]').forEach(x => x.onchange = () => { const id = x.dataset.tog, c = { ...cfg(id), on: x.checked }; if (x.checked && c.freq === 'manual') return openCfg(id); S.sched[id] = c; save(); });
  document.querySelectorAll('[data-run]').forEach(x => x.onclick = () => { const id = x.dataset.run; if (!S.queue.some(q => q.id === id)) S.queue.push({ id, at: new Date().toISOString() }); save(); });
  document.querySelectorAll('[data-cfg]').forEach(x => x.onclick = () => openCfg(x.dataset.cfg));
  document.querySelectorAll('[data-unq]').forEach(x => x.onclick = () => { S.queue = S.queue.filter(q => q.id !== x.dataset.unq); save(); });
}
$('q-clear').onclick = () => { S.queue = []; save(); };

/* ---------- Stillingargluggi ---------- */
let editing = null;
(() => { $('f-md').innerHTML = [...Array(28)].map((_, i) => `<option value="${i + 1}">${i + 1}.</option>`).join('') + '<option value="last">síðasti dagur</option>';
  $('f-mo').innerHTML = MFULL.map((m, i) => `<option value="${i}">${m}</option>`).join(''); })();
function formCfg() { return { on: true, freq: $('f-freq').value, wd: $('f-wd').value, md: $('f-md').value, mo: $('f-mo').value, ev: $('f-ev').value, time: $('f-tm').value || '07:00',
  mode: (document.querySelector('input[name=f-mode]:checked') || {}).value || 'notify', sc: $('f-sc').value, rc: $('f-rc').value }; }
function syncForm() {
  const f = $('f-freq').value, show = (id, v) => { $(id).hidden = !v; };
  show('w-wd', f === 'weekly'); show('w-md', ['monthly', 'workday', 'bimonthly', 'quarterly', 'yearly'].includes(f)); show('w-mo', f === 'yearly'); show('w-ev', f === 'event'); show('w-tm', !['event', 'manual'].includes(f));
  $('w-md').querySelector('span').textContent = f === 'workday' ? 'Virkur dagur nr.' : 'Dagur mánaðar';
  const nx = nextRun(formCfg());
  $('dlg-next').textContent = f === 'event' ? 'Keyrir um leið og atburðurinn verður í BC (Bifröst-áskrift að viðskiptaatburði).' : f === 'manual' ? 'Keyrir aðeins þegar ýtt er á „Keyra núna“.' : nx ? `Næsta keyrsla: ${fmtNext(nx)}.` : '';
}
function openCfg(id) {
  editing = id; const a = CAT.find(x => x.id === id), c = cfg(id);
  $('dlg-t').textContent = a.n; $('dlg-d').textContent = a.d;
  $('f-freq').value = c.freq === 'manual' && !c.on ? (a.k === 'agent' ? 'weekly' : 'monthly') : c.freq; $('f-wd').value = c.wd || 1; $('f-md').value = c.md || 1; $('f-mo').value = c.mo || 0; $('f-ev').value = c.ev || 'Bókun í fjárhag';
  $('f-tm').value = c.time || '07:00'; $('f-sc').value = c.sc; $('f-rc').value = c.rc;
  $('r-draft').hidden = !a.w; const m = !a.w && c.mode === 'draft' ? 'propose' : c.mode;
  document.querySelectorAll('input[name=f-mode]').forEach(r => r.checked = r.value === m);
  syncForm(); $('dlg').showModal();
}
['f-freq', 'f-wd', 'f-md', 'f-mo', 'f-tm'].forEach(id => $(id).addEventListener('input', syncForm));
$('dlg').addEventListener('close', () => { if ($('dlg').returnValue === 'save' && editing) { S.sched[editing] = formCfg(); save(); } else render(); editing = null; });

/* ---------- Vistun: síðan er skráin (artifact.publish) ---------- */
let ART = null, canSave = false, timer = null;
function setState(t) { $('save-state').innerHTML = t; }
function save() {
  S.updated = new Date().toISOString(); render();
  if (!canSave) { setState('Breytingar vistast ekki'); return; }
  setState('Vista…'); clearTimeout(timer); timer = setTimeout(doPublish, 700);
}
function docFor(state) {
  const tokS = '%%' + 'STATE' + '%%', tokT = '%%' + 'TEMPLATE' + '%%', tokP = '%%' + 'PREFIX' + '%%';
  const js = v => JSON.stringify(v).replace(/</g, '\\u003c');
  const body = TEMPLATE.replace(tokP, () => js(PREFIX)).replace(tokS, () => js(state)).replace(tokT, () => js(TEMPLATE));
  return PREFIX + body + '\n</body></html>';
}
async function doPublish() {
  try { await ART.publish(docFor(S)); setState('Vistað'); }
  catch (e) { const c = e && e.code; setState(c === 'conflict' ? 'Annar vistaði á undan' : c === 'not_writer' || c === 'not_granted' ? 'Aðeins lesaðgangur' : 'Vistun mistókst'); }
}
(async () => {
  if (!PREFIX || !window.claude || !claude.use) { setState('Forskoðun · vistast ekki'); return; }
  try { ART = await claude.use('artifact'); } catch (e) { ART = null; }
  canSave = !!ART; setState(canSave ? 'Tengt · vistast sjálfkrafa' : 'Aðeins lesaðgangur');
})();

BF.themeToggle($('mode'), render);
tabs(document.querySelector('.tabs'));
render();
