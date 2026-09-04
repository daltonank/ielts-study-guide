
(() => {
const VERSION="1.1.0-phase3";
const STORE="ieltsC1UAEN.state.v1";
const MODES={en:"EN",uaen:"UA + EN",uahelp:"UA Help"};
const defaultState=()=>({
 schemaVersion:"1.0.0",
 settings:{languageMode:"uaen",targetBand:7.5,targetDate:null,preferredMinutes:30},
 diagnostic:{completed:false,familiarity:{},baseline:{},weakAreas:[]},
 mastery:{}, vocabulary:{}, errors:[], reviews:[], savedResponses:[], practiceResults:[], mockResults:[], studyHistory:[],
 recommendationState:{lastActivity:null,lastRecommendation:null},reading:{activeFamily:null,activePassageId:null,answers:{},results:[],timer:null},backups:[]
});
let state=loadState();
let route=location.hash.replace("#/","")||"today";
let timerHandle=null, timerSeconds=60;
let readingTimerHandle=null;

function loadState(){try{const x=JSON.parse(localStorage.getItem(STORE));const d=defaultState();return {...d,...x,settings:{...d.settings,...(x?.settings||{})},reading:{...d.reading,...(x?.reading||{}),answers:{...(x?.reading?.answers||{})},results:[...(x?.reading?.results||[])]}}}catch(e){return defaultState()}}
function saveState(){localStorage.setItem(STORE,JSON.stringify(state))}
function escapeHTML(s){return String(s??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
function uid(p="ID"){return p+"-"+Date.now().toString(36)+"-"+Math.random().toString(36).slice(2,7)}
function toast(msg){const el=document.querySelector("#toast");el.textContent=msg;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),1800)}
function ua(en,uaText){
 const m=state.settings.languageMode;
 if(m==="en") return "";
 if(m==="uaen") return `<div class="ua-note"><strong>UA:</strong> ${uaText}</div>`;
 return `<div class="ua-note"><strong>Пояснення українською:</strong> ${uaText}</div>`;
}
function pageHero(kicker,title,desc,uaDesc=""){
 return `<section class="hero"><div class="eyebrow">${kicker}</div><h1>${title}</h1><p>${desc}</p>${uaDesc?ua("",uaDesc):""}</section>`;
}
function card(title,body,cls=""){return `<section class="card ${cls}"><h2>${title}</h2>${body}</section>`}
function masteryBadge(id){const l=state.mastery[id]??0;const x=APP_DATA.masteryLevels[l];return `<span class="badge">L${l} • ${x.en}</span>`}
function progressPct(){const vals=Object.values(state.mastery);return vals.length?Math.round(vals.reduce((a,b)=>a+b,0)/(vals.length*5)*100):0}
function allModules(){return [...APP_DATA.modules,...((window.READING_DATA?.modules)||[])]}
function readingModuleId(family){return "READ-"+family.toUpperCase().replaceAll("_","-")}
function readingPassage(id){return (window.READING_DATA?.passages||[]).find(p=>p.id===id)}
function readingFamilyPassages(family){return (window.READING_DATA?.passages||[]).filter(p=>p.family===family)}
function readingLatestResult(pid){return [...(state.reading.results||[])].reverse().find(r=>r.passageId===pid)}

function recommendation(){
 const noDiag=!state.diagnostic.completed;
 if(noDiag) return {top:"Complete the baseline diagnostic",reason:"There is not enough performance evidence to prioritize a weak IELTS skill yet.",module:"start",secondary:"Orientation"};
 const recentErrors=state.errors.filter(e=>!e.resolved);
 const counts={}; recentErrors.forEach(e=>counts[e.category]=(counts[e.category]||0)+1);
 const ranked=Object.entries(counts).sort((a,b)=>b[1]-a[1]);
 const baseline=state.diagnostic.baseline||{};
 const nums=Object.entries(baseline).filter(([,v])=>Number(v)>0).sort((a,b)=>Number(a[1])-Number(b[1]));
 if(ranked[0] && ranked[0][1]>=2) return {top:`Review ${ranked[0][0]}`,reason:`This category appears ${ranked[0][1]} times in unresolved errors, so recurrence currently outweighs broad practice.`,module:"errors",secondary:"Error-driven repair"};
 if(nums[0]) return {top:`Practice ${nums[0][0]}`,reason:`Your saved baseline places ${nums[0][0]} at ${nums[0][1]}, currently the lowest recorded skill estimate.`,module:"skills",secondary:"Lowest baseline skill"};
 return {top:"Build an evidence baseline",reason:"You completed orientation, but the system still lacks enough scored work to personalize confidently.",module:"practice",secondary:"Collect practice evidence"};
}
function session(minutes=state.settings.preferredMinutes||30){
 const rec=recommendation();
 const reviews=(state.reviews.length?state.reviews:APP_DATA.seedReviews).slice().sort((a,b)=>(b.priority||0)-(a.priority||0));
 let items=[];
 let remaining=minutes;
 if(reviews.length && remaining>=10){items.push({minutes:Math.min(10,remaining),title:reviews[0].title,type:"Review"});remaining-=Math.min(10,remaining)}
 if(remaining>=10){items.push({minutes:Math.min(Math.max(10,Math.round(remaining*.6)),remaining),title:rec.top,type:"Priority"});remaining-=items.at(-1).minutes}
 if(remaining>0){items.push({minutes:remaining,title:"Vocabulary active-use review",type:"Language"})}
 return {minutes,items,reason:rec.reason};
}
function renderToday(){
 const rec=recommendation(), s=session();
 return pageHero("TODAY","Know what matters next","The home screen uses diagnostic evidence, mastery, errors and review debt to choose a practical next move.","Відкрийте застосунок і одразу побачте, що варто вчити далі та чому.")+
 `<div class="grid">
 ${card("Top priority",`<div class="priority session-item"><div><span class="badge warn">Recommended</span><h3>${escapeHTML(rec.top)}</h3><p>${escapeHTML(rec.reason)}</p></div><button class="btn" data-route="${rec.module}">Start</button></div>`,"twoThird")}
 ${card("Target",`<div class="big">Band ${state.settings.targetBand}</div><p class="muted">Practice indicators are non-official. Only qualified IELTS examiners award official Writing/Speaking bands.</p><div class="progress" aria-label="Overall mastery ${progressPct()}%"><span style="width:${progressPct()}%"></span></div>`,"third")}
 ${card("Study time",`<div class="segmented">${[10,20,30,45,60,90].map(m=>`<button class="btn ${m===s.minutes?"":"secondary"}" data-minutes="${m}">${m} min</button>`).join("")}</div><div class="stack" style="margin-top:12px">${s.items.map(x=>`<div class="session-item"><div><span class="badge">${x.type}</span><strong>${escapeHTML(x.title)}</strong></div><span>${x.minutes} min</span></div>`).join("")}</div><p class="small muted">${escapeHTML(s.reason)}</p>`,"half")}
 ${card("Resume / due review",renderReviewItems(3),"half")}
 </div>`;
}
function renderReviewItems(limit=99){
 const items=(state.reviews.length?state.reviews:APP_DATA.seedReviews).slice(0,limit);
 return `<div class="stack">${items.map(r=>`<div class="review-item"><span class="badge">${escapeHTML(r.type)}</span><strong>${escapeHTML(r.title)}</strong><div class="small muted">Priority ${r.priority||1}</div></div>`).join("")}</div>`;
}
function renderStart(){
 const b=state.diagnostic.baseline||{};
 return pageHero("START HERE","Diagnostic before prescription","Capture familiarity and a baseline, then let the system prioritize evidence rather than treating every skill equally.","Спочатку збираємо базові дані. Рекомендації мають спиратися на докази, а не на припущення.")+
 `<div class="grid">
 ${card("Stage 1 • Familiarity",`<div class="stack">
 <label class="field">Prior IELTS experience<select id="priorIelts"><option value="">Choose</option><option ${state.diagnostic.familiarity.prior==="none"?"selected":""} value="none">None</option><option ${state.diagnostic.familiarity.prior==="practice"?"selected":""} value="practice">Practice only</option><option ${state.diagnostic.familiarity.prior==="official"?"selected":""} value="official">Taken official IELTS</option></select></label>
 <label class="field">Perceived weakest area<select id="perceivedWeak"><option value="">Choose</option>${["Reading","Listening","Writing Task 1","Writing Task 2","Speaking","Grammar"].map(x=>`<option ${state.diagnostic.familiarity.weak===x?"selected":""}>${x}</option>`).join("")}</select></label>
 <button class="btn" id="saveFamiliarity">Save familiarity</button></div>`,"half")}
 ${card("Baseline scorecard",`<p class="muted">Use actual or practice estimates where known. Leave unknown fields blank.</p>
 <div class="grid">${["Reading","Listening","Writing","Speaking"].map(k=>`<label class="field half">${k}<input id="base${k}" type="number" min="0" max="9" step=".5" value="${escapeHTML(b[k]??"")}"></label>`).join("")}</div>
 <button class="btn" id="saveBaseline">Save baseline</button>`,"half")}
 ${card("Diagnostic status",`<p><strong>${state.diagnostic.completed?"Baseline saved":"Not yet complete"}</strong></p><p>${escapeHTML(recommendation().reason)}</p><button class="btn secondary" data-route="skills">View skill map</button>`)}
 </div>`;
}
function renderSkills(){
 return pageHero("CORE SKILLS","The IELTS training map","Phase 1 establishes the module/mastery shell. Later gated phases populate the complete Reading, Writing, Speaking and Listening banks.","Кожен модуль має рівень опанування 0–5. Відкриття сторінки саме по собі не підвищує mastery.")+
 `<div class="grid">${["Reading","Listening","Writing Task 1","Writing Task 2","Speaking","Grammar"].map(skill=>{
 const mods=allModules().filter(m=>m.skill===skill);
 return card(skill,`<div class="module-list">${mods.length?mods.map(m=>`<div class="module-item"><div class="mastery-dot">${state.mastery[m.id]??0}</div><div><strong>${m.title}</strong><div class="small muted">${m.difficulty} • ${m.minutes} min</div></div>${masteryBadge(m.id)}</div>`).join(""):`<p class="muted">Curriculum content is assigned to a later gated phase.</p>`}</div>`,"half")
 }).join("")}</div>`;
}
function renderPractice(){
 return pageHero("PRACTICE","Practice, capture error, explain, review","The practice shell already records errors and saved work; phase content fills it only after preceding gates pass.","Помилка має стати навчальним сигналом: що сталося, чому, і що повторити далі.")+
 `<div class="grid">
 ${card("Review Today",renderReviewItems(),"half")}
 ${card("Quick error capture",`<div class="stack">
 <label class="field">Skill<select id="errSkill">${["Reading","Listening","Writing Task 1","Writing Task 2","Speaking","Grammar","Vocabulary"].map(x=>`<option>${x}</option>`).join("")}</select></label>
 <label class="field">Category<input id="errCategory" placeholder="e.g. article omission"></label>
 <label class="field">Explanation<textarea id="errExplanation" placeholder="What happened, and what should happen next time?"></textarea></label>
 <button class="btn" id="saveError">Save error</button></div>`,"half")}
 ${card("Writing autosave",`<p class="muted">Foundation validation field. Saved locally while you type.</p><label class="field">Practice response<textarea id="autosaveWriting" placeholder="Type here…">${escapeHTML(state.savedResponses.find(x=>x.id==="AUTOSAVE-WRITING")?.text||"")}</textarea></label><span id="autosaveStatus" class="small muted">Local draft</span>`,"half")}
 ${card("Timer",`<div id="timer" class="timer">01:00</div><div class="row"><button class="btn" data-timer="60">1:00 prep</button><button class="btn secondary" data-timer="120">2:00 speak</button><button class="btn ghost" data-timer="0">Reset</button></div>`,"half")}
 </div>`;
}
function vocabState(id){return state.vocabulary[id]||{stage:"New",confidence:0,lastReviewed:null,nextReview:null,collocation:"",example:""}}
function renderWords(){
 const meta=window.VOCABULARY_META||{};
 const data=window.VOCABULARY||[];
 const priorities=[...new Set(data.map(v=>v.priority).filter(Boolean))].sort();
 const sources=[...new Set(data.map(v=>v.source).filter(Boolean))].sort();
 const topics=[...new Set(data.map(v=>v.topic).filter(Boolean))].sort();
 return pageHero("WORDS","Vocabulary, but for production","The legacy bank remains integrated, but words become useful only when they move from recognition to controlled IELTS use.","Лексика лишається серцевиною сайту, але слово вважається по-справжньому засвоєним лише тоді, коли його можна впізнати, відтворити й природно використати у відповіді IELTS.")+
 `<div class="grid">
 ${card("Migration gate",`<div class="notice"><strong>${meta.complete?"G2 PASS":"G2 BLOCKED"}</strong><br>${meta.complete?`${window.VOCABULARY.length} / ${meta.expectedCount} records loaded from ${escapeHTML(meta.sourceWorkbook||'legacy workbook')}.`:`${meta.seedCount} audited preview records loaded. Expected full bank: ${meta.expectedCount}.`}</div><p class="small muted">Mastery remains strict: a word is not auto-promoted to Mastered merely because its Ukrainian meaning was recognized once.</p>`)}
 ${card("Search and filter",`<div class="stack"><input id="vocabSearch" class="search" type="search" placeholder="Search English or Ukrainian…" aria-label="Search vocabulary">
 <div class="grid">
 <label class="field half">Source<select id="vocabFilterSource"><option value="">All</option>${sources.map(x=>`<option>${escapeHTML(x)}</option>`).join('')}</select></label>
 <label class="field half">Priority<select id="vocabFilterPriority"><option value="">All</option>${priorities.map(x=>`<option>${escapeHTML(x)}</option>`).join('')}</select></label>
 <label class="field half">Topic<select id="vocabFilterTopic"><option value="">All</option>${topics.map(x=>`<option>${escapeHTML(x)}</option>`).join('')}</select></label>
 <label class="field half">Mastery<select id="vocabFilterStage"><option value="">All</option>${["New","Recognized","Recall","Active","Mastered"].map(x=>`<option>${x}</option>`).join('')}</select></label>
 </div><div id="vocabResultsMeta" class="small muted"></div><div id="vocabResults" class="stack"></div></div>`)}
 </div>`;
}
function renderVocabResults(){
 const target=document.querySelector("#vocabResults"); if(!target)return;
 const metaBox=document.querySelector('#vocabResultsMeta');
 const q=(document.querySelector('#vocabSearch')?.value||'').trim().toLowerCase();
 const fs=document.querySelector('#vocabFilterSource')?.value||'';
 const fp=document.querySelector('#vocabFilterPriority')?.value||'';
 const ft=document.querySelector('#vocabFilterTopic')?.value||'';
 const fstage=document.querySelector('#vocabFilterStage')?.value||'';
 let rows=(window.VOCABULARY||[]).filter(v=>{
   const s=vocabState(v.id);
   const hay=`${v.word} ${v.ua} ${v.definitionUa||''} ${v.topic||''} ${v.source||''}`.toLowerCase();
   return (!q || hay.includes(q)) && (!fs || v.source===fs) && (!fp || v.priority===fp) && (!ft || v.topic===ft) && (!fstage || s.stage===fstage);
 });
 const total=rows.length;
 rows=rows.slice(0,80);
 if(metaBox) metaBox.textContent=`${rows.length}${total>rows.length?` of ${total}`:''} result${total===1?'':'s'} shown.`;
 target.innerHTML=rows.map(v=>{const s=vocabState(v.id);return `<div class="vocab-card">
 <div class="row"><strong>${escapeHTML(v.word)}</strong><span class="badge">${escapeHTML(v.pos||'')}</span><span class="badge">${escapeHTML(v.source)}</span>${v.starter100?'<span class="badge good">Starter 100</span>':''}</div>
 <div class="ua-note"><strong>UA:</strong> ${escapeHTML(v.ua)}${v.definitionUa?`<br><span class="small">${escapeHTML(v.definitionUa)}</span>`:''}</div>
 <div class="row small muted" style="margin-top:6px">${v.topic?`<span>Topic: ${escapeHTML(v.topic)}</span>`:''}${v.priority?`<span>Priority: ${escapeHTML(v.priority)}</span>`:''}${v.sourceRefs?.awlSublist?`<span>AWL Sublist: ${escapeHTML(v.sourceRefs.awlSublist)}</span>`:''}</div>
 ${v.collocations?.length?`<div class="small"><strong>Collocations:</strong> ${escapeHTML(v.collocations.join('; '))}</div>`:''}
 ${v.example?`<div class="small"><strong>Example:</strong> ${escapeHTML(v.example)}</div>`:''}
 <div class="row" style="margin-top:9px"><label class="field">Mastery<select data-vocab-stage="${v.id}">${["New","Recognized","Recall","Active","Mastered"].map(x=>`<option ${s.stage===x?"selected":""}>${x}</option>`).join("")}</select></label>
 <label class="field">Confidence<select data-vocab-confidence="${v.id}">${[0,1,2,3,4,5].map(x=>`<option ${Number(s.confidence)===x?"selected":""}>${x}</option>`).join("")}</select></label></div>
 </div>`}).join("")||`<p class="muted">No matches.</p>`;
}
function renderProgress(){
 const errCounts={};state.errors.forEach(e=>{if(!e.resolved)errCounts[e.category]=(errCounts[e.category]||0)+1});
 const top=Object.entries(errCounts).sort((a,b)=>b[1]-a[1]).slice(0,5);
 return pageHero("PROGRESS","Evidence, not decoration","The dashboard emphasizes mastery, recurring errors, review debt and meaningful changes rather than streak pressure.","Прогрес показує навчальні сигнали, а не карає за пропущений день.")+
 `<div class="grid">
 ${card("Current profile",`<div class="kpi-grid">
 <div class="kpi"><span class="muted">Mastery</span><strong>${progressPct()}%</strong></div>
 <div class="kpi"><span class="muted">Errors open</span><strong>${state.errors.filter(e=>!e.resolved).length}</strong></div>
 <div class="kpi"><span class="muted">Saved writing</span><strong>${state.savedResponses.length}</strong></div>
 <div class="kpi"><span class="muted">Reviews due</span><strong>${(state.reviews.length||APP_DATA.seedReviews.length)}</strong></div>
 </div>`)}
 ${card("Weak areas",top.length?`<div class="stack">${top.map(([k,v])=>`<div class="review-item"><strong>${escapeHTML(k)}</strong><span>${v} unresolved</span></div>`).join("")}</div>`:`<p class="muted">No recurring error pattern yet.</p>`,"half")}
 ${card("Recommendation",`<h3>${escapeHTML(recommendation().top)}</h3><p>${escapeHTML(recommendation().reason)}</p>`,"half")}
 ${card("Study history",state.studyHistory.length?state.studyHistory.map(x=>`<div class="review-item">${escapeHTML(x.date)} • ${x.minutes} min • ${escapeHTML(x.skill||"Mixed")}</div>`).join(""):`<p class="muted">History will populate as scored curriculum phases come online.</p>`)}
 </div>`;
}

function readingFamilyModule(family){return (window.READING_DATA?.modules||[]).find(m=>m.subskill===family)}
function readingQuestionInput(passage,qx){
 const saved=state.reading.answers?.[passage.id]?.[qx.id]??"";
 if(qx.type==="text") return `<input class="reading-answer" data-reading-q="${qx.id}" type="text" value="${escapeHTML(saved)}" autocomplete="off">`;
 return `<select class="reading-answer" data-reading-q="${qx.id}"><option value="">Choose…</option>${qx.options.map(o=>`<option value="${escapeHTML(o)}" ${saved===o?"selected":""}>${escapeHTML(o)}</option>`).join("")}</select>`;
}
function normalizeAnswer(x){return String(x??"").trim().toLowerCase().replace(/[.,;:!?]+$/g,"").replace(/\s+/g," ")}
function readingAnswerCorrect(given,expected){return normalizeAnswer(given)===normalizeAnswer(expected)}
function renderReading(){
 const rd=window.READING_DATA;
 if(!rd) return genericLab("Reading Lab","Reading curriculum data failed to load.","Дані Reading Academy не завантажилися.");
 const activePassage=state.reading.activePassageId?readingPassage(state.reading.activePassageId):null;
 const activeFamily=state.reading.activeFamily;
 if(activePassage) return renderReadingPassage(activePassage);
 if(activeFamily) return renderReadingFamily(activeFamily);
 const completed=new Set((state.reading.results||[]).map(r=>r.passageId)).size;
 return pageHero("READING ACADEMY","Read for evidence, not familiarity","The full G3 bank trains IELTS question mechanics through original texts, explicit reasoning and error diagnosis.","Читайте не за відчуттям знайомості, а за доказами. Кожна помилка пояснюється і повертається в систему повторення.")+
 `<div class="grid">
 ${card("G3 curriculum inventory",`<div class="kpi-grid"><div class="kpi"><span class="muted">Original texts</span><strong>${rd.meta.passageCount}</strong></div><div class="kpi"><span class="muted">Scored questions</span><strong>${rd.meta.questionCount}</strong></div><div class="kpi"><span class="muted">Question families</span><strong>${rd.meta.familyCount}</strong></div><div class="kpi"><span class="muted">Sets completed</span><strong>${completed}</strong></div></div><p class="small muted">Academic Reading is 60 minutes. This training bank isolates mechanics before later mock phases combine them into full simulations.</p>`)}
 ${card("Foundation modules",`<div class="module-list">${rd.modules.filter(m=>m.kind==="foundation").map(m=>`<div class="module-item foundation-item"><div class="mastery-dot">${state.mastery[m.id]??0}</div><div><strong>${escapeHTML(m.title)}</strong><div class="small muted">${escapeHTML(m.objectives[0])}</div><details><summary>Learn the strategy</summary><ol>${m.lesson.map(x=>`<li>${escapeHTML(x)}</li>`).join("")}</ol>${ua("",escapeHTML(m.uaSupport))}</details></div><button class="btn secondary" data-reading-foundation="${m.id}">Mark introduced</button></div>`).join("")}</div>`)}
 ${card("Question families",`<div class="reading-family-grid">${Object.entries(rd.familyMeta).map(([fam,meta])=>{const mod=readingFamilyModule(fam);const sets=readingFamilyPassages(fam);const done=sets.filter(p=>readingLatestResult(p.id)).length;return `<button class="reading-family-card" data-reading-family="${fam}"><span class="badge">L${state.mastery[mod.id]??0}</span><strong>${escapeHTML(meta.title)}</strong><span>${escapeHTML(meta.skill)}</span><small>${done}/4 sets completed</small></button>`}).join("")}</div>`)}
 </div>`;
}
function renderReadingFamily(family){
 const meta=window.READING_DATA.familyMeta[family],mod=readingFamilyModule(family),sets=readingFamilyPassages(family);
 return pageHero("READING MODULE",meta.title,meta.skill,meta.ua)+`<div class="grid">
 ${card("Learn → See → Think → Challenge",`<div class="stack"><div class="lesson-objective"><strong>Objective</strong><p>${escapeHTML(mod.objectives[0])}</p></div><div class="strategy-block"><span class="badge">Learn</span><ol>${(mod.strategySteps||[]).map(x=>`<li>${escapeHTML(x)}</li>`).join("")}</ol></div><div class="strategy-block"><span class="badge">See</span><p><strong>Worked example:</strong> ${escapeHTML(mod.workedExample||mod.workedExamples?.[0]?.analysis||"")}</p></div><div class="strategy-block"><span class="badge">Think</span><p>${escapeHTML(mod.lesson?.[0]||"")}</p></div><div class="trap"><strong>Common trap</strong><p>${escapeHTML(window.READING_DATA.familyMeta[family].trap)}</p></div><div class="strategy-block"><span class="badge warn">Challenge</span><p>${escapeHTML(mod.challenge||"")}</p></div>${ua("",escapeHTML(mod.uaSupport))}<div class="row"><button class="btn ghost" data-reading-home>← All Reading modules</button><button class="btn secondary" data-reading-foundation="${mod.id}">Mark lesson introduced</button></div></div>`,'half')}
 ${card("Practice progression",`<div class="stack">${sets.map(p=>{const r=readingLatestResult(p.id);return `<div class="session-item"><div><span class="badge ${p.mode==='mastery'?'warn':''}">${escapeHTML(p.modeLabel)}</span><strong>${escapeHTML(p.title)}</strong><div class="small muted">${escapeHTML(p.domain)} • Band ${p.difficulty} training • ${p.estimatedMinutes} min</div>${r?`<div class="small"><strong>${r.score}/${r.total}</strong> • ${Math.round(r.accuracy*100)}% ${r.timed?`• ${r.withinLimit?"within time":"over time"}`:""}</div>`:""}</div><button class="btn" data-reading-passage="${p.id}">${r?"Retry":"Start"}</button></div>`}).join("")}</div>`,'half')}
 ${card("Mastery rule",`<p><strong>L2 Guided:</strong> ≥50% on the guided set. <strong>L3 Independent:</strong> ≥75% on the unseen independent set. <strong>L4 Timed:</strong> timed + mastery sets average ≥75% and both finish within their limits. <strong>L5 Mastered:</strong> ≥85% across at least three different sets on two different dates, including the mastery set.</p><p class="small muted">Opening or scrolling a lesson does not advance mastery.</p>`)}
 </div>`;
}
function renderReadingPassage(p){
 const result=readingLatestResult(p.id);const isTimed=['timed','mastery'].includes(p.mode);const answers=state.reading.answers?.[p.id]||{};
 return pageHero(p.modeLabel,p.title,`${p.domain} • ${window.READING_DATA.familyMeta[p.family].title} • Band ${p.difficulty} training`,"Оберіть відповідь лише після того, як можете вказати, де текст її підтверджує.")+`<div class="grid reading-workspace">
 ${card("Passage",`<div class="row"><button class="btn ghost" data-reading-back>← Module</button><span class="badge">Original training text</span>${isTimed?`<span class="badge warn">${p.estimatedMinutes}:00 target</span>`:""}</div>${isTimed?`<div class="reading-timer-panel"><div id="readingTimer" class="timer">${String(p.estimatedMinutes).padStart(2,"0")}:00</div><button class="btn secondary" data-reading-start-timer="${p.id}">Start timed set</button></div>`:""}<article class="reading-passage">${p.paragraphs.map((para,i)=>`<p><span class="paragraph-label">${String.fromCharCode(65+i)}</span>${escapeHTML(para.replace(/^[A-D]\.\s*/,''))}</p>`).join("")}</article><p class="small muted">${escapeHTML(p.sourceNote)}</p>`,'half')}
 ${card("Questions",`<form id="readingForm" class="stack">${p.questions.map((qx,i)=>{const correct=result?readingAnswerCorrect(result.answers[qx.id],qx.correctAnswer):null;return `<div class="question-card ${result?(correct?"q-correct":"q-wrong"):""}"><label><strong>${i+1}. ${escapeHTML(qx.prompt)}</strong>${readingQuestionInput(p,qx)}</label>${result?`<div class="answer-feedback"><span class="badge ${correct?"good":"warn"}">${correct?"Correct":"Review"}</span><p><strong>Correct answer:</strong> ${escapeHTML(qx.correctAnswer)}</p><p>${escapeHTML(qx.explanation)}</p>${!correct?`<p class="small"><strong>Why your choice fails:</strong> ${escapeHTML(qx.distractorReasoning?.[result.answers[qx.id]]||"This answer is not supported by the required evidence.")}</p><p class="small"><strong>Error category:</strong> ${escapeHTML(qx.errorCategory)}</p>`:""}</div>`:""}</div>`}).join("")}<button type="button" class="btn" data-reading-submit="${p.id}">${result?"Submit another attempt":"Check answers"}</button></form>`,'half')}
 ${result?card("Result",`<div class="score-summary"><div class="big">${result.score}/${result.total}</div><p>${Math.round(result.accuracy*100)}% accuracy${result.timed?` • ${result.withinLimit?"within target time":"over target time"}`:""}</p><p>Module mastery: ${masteryBadge(p.moduleId)}</p><button class="btn secondary" data-reading-back>Continue module</button></div>`):""}
 </div>`;
}
function readingSetAnswer(pid,qid,value){state.reading.answers=state.reading.answers||{};state.reading.answers[pid]=state.reading.answers[pid]||{};state.reading.answers[pid][qid]=value;saveState()}
function readingStartTimer(pid){
 const p=readingPassage(pid);if(!p)return;
 state.reading.timer={passageId:pid,startAt:Date.now(),limitSeconds:p.estimatedMinutes*60};saveState();
 clearInterval(readingTimerHandle);readingTimerHandle=setInterval(()=>readingDrawTimer(pid),250);readingDrawTimer(pid);toast("Timed set started")
}
function readingDrawTimer(pid){
 const el=document.querySelector('#readingTimer');if(!el)return;const t=state.reading.timer;if(!t||t.passageId!==pid){el.textContent=`${String(readingPassage(pid).estimatedMinutes).padStart(2,'0')}:00`;return}
 const elapsed=Math.floor((Date.now()-t.startAt)/1000),remain=Math.max(0,t.limitSeconds-elapsed);el.textContent=String(Math.floor(remain/60)).padStart(2,'0')+':'+String(remain%60).padStart(2,'0');if(remain===0)clearInterval(readingTimerHandle)
}
function updateReadingMastery(moduleId){
 const modulePassages=(window.READING_DATA.passages||[]).filter(p=>p.moduleId===moduleId);const results=(state.reading.results||[]).filter(r=>r.moduleId===moduleId);let level=state.mastery[moduleId]??0;
 const latestByPass={};results.forEach(r=>latestByPass[r.passageId]=r);const vals=Object.values(latestByPass);
 const guided=vals.find(r=>r.mode==='guided');if(guided&&guided.accuracy>=.5)level=Math.max(level,2);
 const independent=vals.find(r=>r.mode==='independent');if(independent&&independent.accuracy>=.75)level=Math.max(level,3);
 const timed=vals.filter(r=>['timed','mastery'].includes(r.mode)&&r.withinLimit);if(timed.length>=2&&timed.reduce((a,b)=>a+b.accuracy,0)/timed.length>=.75)level=Math.max(level,4);
 const dates=new Set(vals.map(r=>r.date));const mastery=vals.find(r=>r.mode==='mastery');if(vals.length>=3&&dates.size>=2&&mastery&&vals.reduce((a,b)=>a+b.accuracy,0)/vals.length>=.85)level=5;
 state.mastery[moduleId]=level;
}
function submitReading(pid){
 const p=readingPassage(pid);if(!p)return;const answers=state.reading.answers?.[pid]||{};let score=0;const wrong=[];
 p.questions.forEach(qx=>{const given=answers[qx.id]??"";if(readingAnswerCorrect(given,qx.correctAnswer))score++;else wrong.push({qx,given})});
 const timer=state.reading.timer;const timed=['timed','mastery'].includes(p.mode);const elapsed=timed&&timer?.passageId===pid?Math.floor((Date.now()-timer.startAt)/1000):null;const withinLimit=timed?elapsed!==null&&elapsed<=p.estimatedMinutes*60:true;
 const result={id:uid('READRES'),date:new Date().toISOString().slice(0,10),createdAt:new Date().toISOString(),passageId:pid,moduleId:p.moduleId,family:p.family,mode:p.mode,score,total:p.questions.length,accuracy:score/p.questions.length,timed,elapsedSeconds:elapsed,withinLimit,answers:{...answers}};
 state.reading.results.push(result);state.practiceResults.push({id:result.id,date:result.date,skill:'Reading',module:p.moduleId,score,total:p.questions.length,accuracy:result.accuracy,timed,withinLimit});
 wrong.forEach(({qx,given})=>{const prior=state.errors.some(e=>e.skill==='Reading'&&e.category===qx.errorCategory&&!e.resolved);state.errors.unshift({id:uid('ERR'),date:result.date,skill:'Reading',module:p.moduleId,questionId:qx.id,learnerAnswer:String(given),correctAnswer:String(qx.correctAnswer),category:qx.errorCategory,explanation:qx.explanation,correction:`Review ${window.READING_DATA.familyMeta[p.family].title} evidence strategy.`,repeated:prior,reviewDate:new Date(Date.now()+3*86400000).toISOString().slice(0,10),resolved:false});if(!state.reviews.some(r=>r.questionId===qx.id))state.reviews.push({id:uid('REV'),type:'Reading',title:`Review: ${window.READING_DATA.familyMeta[p.family].title}`,priority:prior?5:4,module:p.moduleId,questionId:qx.id,dueDate:new Date(Date.now()+3*86400000).toISOString().slice(0,10)})});
 updateReadingMastery(p.moduleId);state.studyHistory.unshift({date:result.date,minutes:p.estimatedMinutes,skill:'Reading',module:p.moduleId,accuracy:result.accuracy});state.reading.timer=null;saveState();render();toast(`${score}/${p.questions.length} correct`)
}
function genericLab(name,desc,uaText){
 return pageHero("CURRICULUM SHELL",name,desc,uaText)+`<div class="grid">${card("Gate status",`<div class="notice"><strong>Not gate-complete.</strong><br>This route exists in the stable platform shell, but its benchmark content is intentionally not marked complete before prerequisite gates pass.</div>`)}${card("Module mastery contract",`<p>Opening content does not increase mastery. Level 2 requires guided evidence; Level 3 unseen independent performance; Level 4 repeated timed performance; Level 5 spaced consistency.</p>`)}</div>`;
}
function renderErrors(){
 return pageHero("ERROR LOG","Turn mistakes into a dataset","Filterable records feed later adaptive recommendations.","Помилки зберігаються локально і можуть бути позначені як resolved після повторної успішної практики.")+
 `<div class="grid">${card("Open errors",state.errors.length?`<div class="stack">${state.errors.map(e=>`<div class="error-card"><div class="row"><span class="badge">${escapeHTML(e.skill)}</span><strong>${escapeHTML(e.category)}</strong><span class="small muted">${escapeHTML(e.date)}</span></div><p>${escapeHTML(e.explanation)}</p><button class="btn secondary" data-resolve="${e.id}">${e.resolved?"Reopen":"Mark resolved"}</button></div>`).join("")}</div>`:`<p class="muted">No logged errors yet.</p>`)}</div>`;
}
function renderSearch(){
 return pageHero("SEARCH","One search across the study system","Search modules, vocabulary and saved errors in one place.","Пошук групує результати за типом, щоб швидко перейти від терміну до вправи або власної помилки.")+
 `<div class="grid">${card("Global search",`<input id="globalSearch" class="search" type="search" placeholder="Try: articles" aria-label="Global search"><div id="globalResults" class="stack" style="margin-top:12px"></div>`)}</div>`;
}
function renderGlobal(q=""){
 const el=document.querySelector("#globalResults");if(!el)return;q=q.trim().toLowerCase();
 if(!q){el.innerHTML="<p class='muted'>Enter a search term.</p>";return}
 let hits=[];
 allModules().forEach(m=>{if(`${m.title} ${m.skill} ${m.subskill||""}`.toLowerCase().includes(q))hits.push({type:"Module",title:m.title,detail:m.skill})});
 (window.READING_DATA?.passages||[]).forEach(p=>{if(`${p.title} ${p.domain} ${p.family}`.toLowerCase().includes(q))hits.push({type:"Reading",title:p.title,detail:`${p.domain} • ${p.modeLabel}`})});
 (window.VOCABULARY||[]).forEach(v=>{if(`${v.word} ${v.ua}`.toLowerCase().includes(q))hits.push({type:"Vocabulary",title:v.word,detail:v.ua})});
 state.errors.forEach(e=>{if(`${e.category} ${e.explanation}`.toLowerCase().includes(q))hits.push({type:"Error",title:e.category,detail:e.explanation})});
 el.innerHTML=hits.slice(0,50).map(h=>`<div class="search-item"><span class="badge">${h.type}</span><strong>${escapeHTML(h.title)}</strong><div class="small muted">${escapeHTML(h.detail)}</div></div>`).join("")||"<p class='muted'>No results.</p>";
}
function renderSettings(){
 return pageHero("SETTINGS","Language, target and backup","Settings persist locally. Import validates the expected learner-state structure before replacement.","Перед імпортом застосунок зберігає резервну копію поточного стану.")+
 `<div class="grid">
 ${card("Study settings",`<div class="stack"><label class="field">Target band<input id="targetBand" type="number" min="0" max="9" step=".5" value="${state.settings.targetBand}"></label><label class="field">Preferred session<select id="preferredMinutes">${[10,20,30,45,60,90].map(x=>`<option ${x===state.settings.preferredMinutes?"selected":""}>${x}</option>`).join("")}</select></label><button id="saveSettings" class="btn">Save settings</button></div>`,"half")}
 ${card("Backup / restore",`<div class="stack"><button id="exportBtn" class="btn">Export Progress JSON</button><button id="importBtn" class="btn secondary">Import Progress JSON</button><p class="small muted">Import does not silently overwrite malformed data. A snapshot of the current state is retained before a valid replacement.</p></div>`,"half")}
 ${card("Build identity",`<div class="dev-note">Version ${VERSION}\nVocabulary gate: ${(window.VOCABULARY_META||{}).gate}\nStorage key: ${STORE}</div>`)}
 </div>`;
}
function renderComponents(){
 const names=["Section header","Module header","Lesson objective","Ukrainian explanation","Example","Worked example","Examiner note","Common trap","Strategy block","Practice item","Multiple choice","T/F/NG","Matching activity","Text response","Answer reveal","Explanation panel","Timer","Progress bar","Mastery badge","Vocabulary card","Collocation card","Graph exercise","Writing response","Speaking cue card","Error record","Review item","Score summary","Weak-area recommendation","Study session card","Diagnostic result","Resource card"];
 return pageHero("DESIGN SYSTEM","Reusable component inventory","A Phase 1 verification surface for shared spacing, states, focus behavior and responsive rules.","Це внутрішня QA-сторінка: вона підтверджує, що компоненти використовують одну систему, а не випадкові стилі.")+
 `<div class="grid">${names.map((n,i)=>`<div class="card third"><span class="badge">C-${String(i+1).padStart(2,"0")}</span><h3>${n}</h3><p class="muted">Shared token/component primitive ready for curriculum binding.</p></div>`).join("")}</div>`;
}
function renderReview(){return pageHero("REVIEW TODAY","Due work before new work","Review debt, recurring errors and mastery weakness determine what returns.","Черга повторення зменшує забування та не дозволяє слабким місцям загубитися.")+`<div class="grid">${card("Queue",renderReviewItems())}</div>`}

function routeView(){
 const map={
 today:renderToday,start:renderStart,skills:renderSkills,practice:renderPractice,words:renderWords,progress:renderProgress,
 reading:renderReading,
 listening:()=>genericLab("Listening Lab","Strategy and error-taxonomy content is assigned to Phase 8.","Listening використовує лише оригінальні, дозволені або офіційно пов'язані матеріали."),
 task1:()=>genericLab("Writing Task 1","Original visual-analysis curriculum is assigned to Phase 4.","Візуали будуть оригінальними, а автоматичні оцінки не називатимуться офіційними IELTS bands."),
 task2:()=>genericLab("Writing Task 2","Argument and essay curriculum is assigned to Phase 5.","Task 2 має вищу вагу в Writing, тому пізніша адаптивна система врахує це."),
 speaking:()=>genericLab("Speaking Lab","Parts 1–3 curriculum and Together Mode are assigned to Phase 7.","Мета pronunciation: зрозумілість, а не стирання акценту."),
 grammar:()=>genericLab("Grammar Clinic","Ukrainian→English transfer curriculum is assigned to Phase 6.","Українські пояснення використовуються там, де контраст справді допомагає."),
 paraphrase:()=>genericLab("Paraphrasing Academy","Cross-skill transformation practice is assigned to Phase 6.","Перефразування пов'язується з Reading, Listening, Writing і Speaking."),
 pronunciation:()=>genericLab("Pronunciation Lab","Intelligibility-focused curriculum is assigned to Phase 6.","Не 'прибираємо акцент'; тренуємо stress, sounds, thought groups та fluency repair."),
 errors:renderErrors,review:renderReview,search:renderSearch,settings:renderSettings,components:renderComponents
 };
 return (map[route]||renderToday)();
}
function navigate(r){
 const y=window.scrollY; route=r; history.replaceState(null,"","#/"+r); render(); window.scrollTo({top:0,behavior:"instant"});
 closeDrawer();
}
function render(){
 const main=document.querySelector("#main");main.innerHTML=routeView();
 document.documentElement.lang=state.settings.languageMode==="uahelp"?"uk":"en";
 document.querySelector("#languageMode").value=state.settings.languageMode;
 document.querySelectorAll(".mobile-nav button").forEach(b=>b.classList.toggle("active",b.dataset.route===route));
 bindPage();
}
function bindPage(){
 document.querySelectorAll("[data-route]").forEach(b=>b.addEventListener("click",()=>navigate(b.dataset.route)));
 document.querySelectorAll("[data-minutes]").forEach(b=>b.addEventListener("click",()=>{state.settings.preferredMinutes=Number(b.dataset.minutes);saveState();render()}));
 if(document.querySelector("#saveFamiliarity"))document.querySelector("#saveFamiliarity").onclick=()=>{state.diagnostic.familiarity={prior:priorIelts.value,weak:perceivedWeak.value};saveState();toast("Familiarity saved")};
 if(document.querySelector("#saveBaseline"))document.querySelector("#saveBaseline").onclick=()=>{state.diagnostic.baseline={Reading:baseReading.value,Listening:baseListening.value,Writing:baseWriting.value,Speaking:baseSpeaking.value};state.diagnostic.completed=Object.values(state.diagnostic.baseline).some(Boolean);saveState();toast("Baseline saved");render()};
 if(document.querySelector("#saveError"))document.querySelector("#saveError").onclick=()=>{if(!errCategory.value.trim())return toast("Add an error category");state.errors.unshift({id:uid("ERR"),date:new Date().toISOString().slice(0,10),skill:errSkill.value,module:"",questionId:"",learnerAnswer:"",correctAnswer:"",category:errCategory.value.trim(),explanation:errExplanation.value.trim(),correction:"",repeated:false,reviewDate:null,resolved:false});saveState();toast("Error saved");render()};
 if(document.querySelector("#autosaveWriting"))document.querySelector("#autosaveWriting").addEventListener("input",e=>{let x=state.savedResponses.find(x=>x.id==="AUTOSAVE-WRITING");if(!x){x={id:"AUTOSAVE-WRITING",type:"writing",text:"",updatedAt:""};state.savedResponses.push(x)}x.text=e.target.value;x.updatedAt=new Date().toISOString();saveState();document.querySelector("#autosaveStatus").textContent="Saved locally"});
 document.querySelectorAll("[data-timer]").forEach(b=>b.onclick=()=>startTimer(Number(b.dataset.timer)));
 if(document.querySelector('#vocabSearch')){['#vocabSearch','#vocabFilterSource','#vocabFilterPriority','#vocabFilterTopic','#vocabFilterStage'].forEach(sel=>document.querySelector(sel)?.addEventListener('input',renderVocabResults));['#vocabFilterSource','#vocabFilterPriority','#vocabFilterTopic','#vocabFilterStage'].forEach(sel=>document.querySelector(sel)?.addEventListener('change',renderVocabResults));renderVocabResults();}
 document.querySelectorAll("[data-vocab-stage]").forEach(s=>s.onchange=()=>{const id=s.dataset.vocabStage;state.vocabulary[id]={...vocabState(id),stage:s.value,lastReviewed:new Date().toISOString().slice(0,10)};saveState();toast("Vocabulary state saved")});
 document.querySelectorAll("[data-vocab-confidence]").forEach(s=>s.onchange=()=>{const id=s.dataset.vocabConfidence;state.vocabulary[id]={...vocabState(id),confidence:Number(s.value)};saveState();toast("Confidence saved")});
 document.querySelectorAll("[data-resolve]").forEach(b=>b.onclick=()=>{const e=state.errors.find(x=>x.id===b.dataset.resolve);if(e){e.resolved=!e.resolved;saveState();render()}});
 document.querySelectorAll('[data-reading-family]').forEach(b=>b.onclick=()=>{state.reading.activeFamily=b.dataset.readingFamily;state.reading.activePassageId=null;saveState();render()});
 document.querySelectorAll('[data-reading-passage]').forEach(b=>b.onclick=()=>{state.reading.activePassageId=b.dataset.readingPassage;saveState();render()});
 document.querySelectorAll('[data-reading-home]').forEach(b=>b.onclick=()=>{state.reading.activeFamily=null;state.reading.activePassageId=null;saveState();render()});
 document.querySelectorAll('[data-reading-back]').forEach(b=>b.onclick=()=>{state.reading.activePassageId=null;saveState();render()});
 document.querySelectorAll('[data-reading-foundation]').forEach(b=>b.onclick=()=>{state.mastery[b.dataset.readingFoundation]=Math.max(state.mastery[b.dataset.readingFoundation]??0,1);saveState();toast('Introduced — mastery now requires performance evidence');render()});
 document.querySelectorAll('[data-reading-q]').forEach(el=>el.addEventListener('input',e=>readingSetAnswer(state.reading.activePassageId,e.target.dataset.readingQ,e.target.value)));
 document.querySelectorAll('[data-reading-submit]').forEach(b=>b.onclick=()=>submitReading(b.dataset.readingSubmit));
 document.querySelectorAll('[data-reading-start-timer]').forEach(b=>b.onclick=()=>readingStartTimer(b.dataset.readingStartTimer));
 if(state.reading.activePassageId)readingDrawTimer(state.reading.activePassageId);
 if(document.querySelector("#globalSearch"))document.querySelector("#globalSearch").addEventListener("input",e=>renderGlobal(e.target.value));
 if(document.querySelector("#saveSettings"))document.querySelector("#saveSettings").onclick=()=>{state.settings.targetBand=Number(targetBand.value);state.settings.preferredMinutes=Number(preferredMinutes.value);saveState();toast("Settings saved");render()};
 if(document.querySelector("#exportBtn"))document.querySelector("#exportBtn").onclick=exportData;
 if(document.querySelector("#importBtn"))document.querySelector("#importBtn").onclick=()=>document.querySelector("#importFile").click();
}
function startTimer(sec){clearInterval(timerHandle);timerSeconds=sec||60;drawTimer();if(!sec)return;timerHandle=setInterval(()=>{timerSeconds--;drawTimer();if(timerSeconds<=0){clearInterval(timerHandle);toast("Timer complete")}},1000)}
function drawTimer(){const el=document.querySelector("#timer");if(!el)return;el.textContent=String(Math.floor(timerSeconds/60)).padStart(2,"0")+":"+String(timerSeconds%60).padStart(2,"0")}
function exportData(){const blob=new Blob([JSON.stringify(state,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=`ielts-c1-progress-${new Date().toISOString().slice(0,10)}.json`;a.click();URL.revokeObjectURL(a.href)}
function validImport(x){return x&&typeof x==="object"&&typeof x.schemaVersion==="string"&&x.settings&&["en","uaen","uahelp"].includes(x.settings.languageMode)&&Array.isArray(x.errors)&&Array.isArray(x.savedResponses)&&Array.isArray(x.studyHistory)}
function importData(file){const r=new FileReader();r.onload=()=>{try{const x=JSON.parse(r.result);if(!validImport(x))throw new Error("Schema check failed");const backup=JSON.parse(JSON.stringify(state));x.backups=Array.isArray(x.backups)?x.backups:[];x.backups.unshift({createdAt:new Date().toISOString(),state:backup});state=x;saveState();toast("Import successful");render()}catch(e){toast("Import rejected: "+e.message)}};r.readAsText(file)}
function openDrawer(){drawer.hidden=false;scrim.hidden=false;menuBtn.setAttribute("aria-expanded","true")}
function closeDrawer(){drawer.hidden=true;scrim.hidden=true;menuBtn.setAttribute("aria-expanded","false")}
function init(){
 secondaryNav.innerHTML=APP_DATA.secondaryNav.map(([r,t])=>`<button data-route="${r}">${t}</button>`).join("");
 menuBtn.onclick=()=>drawer.hidden?openDrawer():closeDrawer();scrim.onclick=closeDrawer;
 languageMode.onchange=()=>{const y=window.scrollY;state.settings.languageMode=languageMode.value;saveState();render();requestAnimationFrame(()=>window.scrollTo(0,y));toast("Language support: "+MODES[state.settings.languageMode])};
 importFile.onchange=e=>{if(e.target.files[0])importData(e.target.files[0]);e.target.value=""};
 window.addEventListener("hashchange",()=>{route=location.hash.replace("#/","")||"today";render()});
 render();
}
init();
})();
