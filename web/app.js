
(() => {
const VERSION="1.1.0-phase3";
const STORE="ieltsC1UAEN.state.v1";
const MODES={en:"EN",uaen:"UA + EN",uahelp:"UA Help"};
const defaultState=()=>({
 schemaVersion:"1.0.0",
 settings:{languageMode:"uaen",targetBand:7.5,targetDate:null,preferredMinutes:30},
 diagnostic:{completed:false,familiarity:{},baseline:{},weakAreas:[]},
 mastery:{}, vocabulary:{}, errors:[], reviews:[], savedResponses:[], practiceResults:[], mockResults:[], studyHistory:[],
 recommendationState:{lastActivity:null,lastRecommendation:null},reading:{activeFamily:null,activePassageId:null,answers:{},results:[],timer:null},
 writing1:{activeFamily:null,activeExerciseId:null,activePromptId:null,activeBandId:null,activeBandLevel:null,bandsOpened:{},answers:{},results:[],drafts:{},checklists:{},submissions:[],timer:null,exerciseTimer:null},backups:[]
});
let state=loadState();
let route=location.hash.replace("#/","")||"today";
let timerHandle=null, timerSeconds=60;
let readingTimerHandle=null;
let w1TimerHandle=null, w1ExTimerHandle=null;

function loadState(){try{const x=JSON.parse(localStorage.getItem(STORE));const d=defaultState();return {...d,...x,settings:{...d.settings,...(x?.settings||{})},reading:{...d.reading,...(x?.reading||{}),answers:{...(x?.reading?.answers||{})},results:[...(x?.reading?.results||[])]},writing1:{...d.writing1,...(x?.writing1||{}),answers:{...(x?.writing1?.answers||{})},drafts:{...(x?.writing1?.drafts||{})},checklists:{...(x?.writing1?.checklists||{})},bandsOpened:{...(x?.writing1?.bandsOpened||{})},results:[...(x?.writing1?.results||[])],submissions:[...(x?.writing1?.submissions||[])]}}}catch(e){return defaultState()}}
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
function allModules(){return [...APP_DATA.modules,...((window.READING_DATA?.modules)||[]),...((window.WRITING1_DATA?.modules)||[])]}
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
 const route={"Reading":"reading","Writing Task 1":"task1"}[skill];
 const open=route?`<button class="btn" data-route="${route}" style="margin-bottom:10px">Open ${escapeHTML(skill)}</button>`:"";
 const shown=mods.slice(0,6);
 return card(skill,`${open}<div class="module-list">${mods.length?shown.map(m=>`<div class="module-item"><div class="mastery-dot">${state.mastery[m.id]??0}</div><div><strong>${escapeHTML(m.title)}</strong><div class="small muted">${escapeHTML(m.difficulty)}${m.minutes?` • ${m.minutes} min`:""}</div></div>${masteryBadge(m.id)}</div>`).join(""):`<p class="muted">Curriculum content is assigned to a later gated phase.</p>`}</div>${mods.length>shown.length?`<p class="small muted">+ ${mods.length-shown.length} more inside the academy.</p>`:""}`,"half")
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
/* ---------------- Phase 4 • Writing Task 1 ---------------- */
const W1_SERIES=["#2754c5","#b45309","#009e8e","#a21caf"];
const W1_RAMP=["#173a8c","#2754c5","#4a72d8","#7b98e4","#a9bcef","#d5e0f8"];
const W1_STATUS={added:{c:"#207357",label:"Added"},removed:{c:"#a33838",label:"Removed"},replaced:{c:"#875d00",label:"Replaced"},unchanged:{c:"#66738b",label:"Unchanged"}};
function w1(){return window.WRITING1_DATA}
function w1Meta(f){return w1()?.familyMeta?.[f]}
function w1Module(f){return (w1()?.modules||[]).find(m=>m.subskill===f)}
function w1Visual(id){return (w1()?.visuals||[]).find(v=>v.id===id)}
function w1Exercise(id){return (w1()?.exercises||[]).find(e=>e.id===id)}
function w1Prompt(id){return (w1()?.prompts||[]).find(p=>p.id===id)}
function w1FamilyExercises(f){return (w1()?.exercises||[]).filter(e=>e.questionFamily===f)}
function w1FamilyPrompts(f){return (w1()?.prompts||[]).filter(p=>p.questionFamily===f)}
function w1LatestResult(id){return [...(state.writing1.results||[])].reverse().find(r=>r.exerciseId===id)}
function w1LatestSubmission(id){return [...(state.writing1.submissions||[])].reverse().find(s=>s.promptId===id)}
function w1Words(t){return String(t||"").trim().split(/\s+/).filter(Boolean).length}
function w1Colour(i){return W1_SERIES[i%W1_SERIES.length]}
function w1Num(v){return Number.isInteger(v)?String(v):String(v)}
function w1NiceMax(v){
 if(!(v>0))return 1;
 const mag=Math.pow(10,Math.floor(Math.log10(v)));const n=v/mag;
 let step;if(n<=1)step=1;else if(n<=1.5)step=1.5;else if(n<=2)step=2;else if(n<=2.5)step=2.5;else if(n<=5)step=5;else step=10;
 return step*mag;
}

/* --- visual renderers: every family draws from its own data --- */
function w1LineSvg(cats,series,axisLabel){
 const X0=36,X1=272,Y0=28,Y1=170,max=w1NiceMax(Math.max(...series.flatMap(s=>s.values))*1.08);
 const x=i=>cats.length<2?X0:X0+i*(X1-X0)/(cats.length-1), y=v=>Y1-(v/max)*(Y1-Y0);
 const ticks=[0,.25,.5,.75,1].map(t=>t*max);
 const grid=ticks.map(t=>`<line x1="${X0}" y1="${y(t).toFixed(1)}" x2="${X1}" y2="${y(t).toFixed(1)}"/>`).join("");
 const yLab=ticks.map(t=>`<text x="${X0-6}" y="${(y(t)+3.5).toFixed(1)}">${w1Num(Math.round(t*10)/10)}</text>`).join("");
 const step=Math.ceil(cats.length/5);
 const xLab=cats.map((c,i)=>i%step===0||i===cats.length-1?`<text x="${x(i).toFixed(1)}" y="${Y1+18}">${escapeHTML(c)}</text>`:"").join("");
 const lines=series.map((s,si)=>`<polyline points="${s.values.map((v,i)=>`${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ")}" fill="none" stroke="${w1Colour(si)}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`).join("");
 const dots=series.map((s,si)=>s.values.map((v,i)=>`<circle cx="${x(i).toFixed(1)}" cy="${y(v).toFixed(1)}" r="4" fill="${w1Colour(si)}"/>`).join("")).join("");
 const ends=series.map((s,si)=>({si,v:s.values.at(-1)})).sort((a,b)=>a.v-b.v)
   .map((e,idx,arr)=>{let ly=y(e.v);const prev=arr[idx-1];if(prev&&Math.abs(ly-prev._ly)<13)ly=prev._ly-13;e._ly=ly;
     return `<text x="${X1+8}" y="${(ly+4).toFixed(1)}" fill="${w1Colour(e.si)}" font-size="12" font-weight="700">${w1Num(e.v)}</text>`}).join("");
 return `<svg viewBox="0 0 320 196" width="100%" role="img" aria-label="${escapeHTML(axisLabel||"Line graph")}">
 <g stroke="var(--line)" stroke-width="1">${grid}</g>
 <g fill="var(--muted)" font-size="11" text-anchor="end">${yLab}</g>
 <g fill="var(--muted)" font-size="11" text-anchor="middle">${xLab}</g>
 <text x="2" y="12" fill="var(--muted)" font-size="11">${escapeHTML(axisLabel||"")}</text>
 ${lines}<g stroke="#fff" stroke-width="2">${dots}</g>${ends}</svg>`;
}
function w1BarSvg(cats,series,axisLabel){
 const X0=38,X1=304,Y0=28,Y1=170,max=w1NiceMax(Math.max(...series.flatMap(s=>s.values))*1.08);
 const y=v=>Y1-(v/max)*(Y1-Y0), gw=(X1-X0)/cats.length, bw=Math.max(6,Math.min(22,(gw-10)/series.length-2));
 const ticks=[0,.25,.5,.75,1].map(t=>t*max);
 const grid=ticks.map(t=>`<line x1="${X0}" y1="${y(t).toFixed(1)}" x2="${X1}" y2="${y(t).toFixed(1)}"/>`).join("");
 const yLab=ticks.map(t=>`<text x="${X0-6}" y="${(y(t)+3.5).toFixed(1)}">${w1Num(Math.round(t*10)/10)}</text>`).join("");
 let bars="";
 cats.forEach((c,ci)=>{const inner=series.length*bw+(series.length-1)*2, sx=X0+ci*gw+(gw-inner)/2;
  series.forEach((s,si)=>{const v=s.values[ci],bx=sx+si*(bw+2),by=y(v),r=Math.min(4,bw/2);
   bars+=`<path d="M${bx.toFixed(1)} ${Y1} L${bx.toFixed(1)} ${(by+r).toFixed(1)} Q${bx.toFixed(1)} ${by.toFixed(1)} ${(bx+r).toFixed(1)} ${by.toFixed(1)} L${(bx+bw-r).toFixed(1)} ${by.toFixed(1)} Q${(bx+bw).toFixed(1)} ${by.toFixed(1)} ${(bx+bw).toFixed(1)} ${(by+r).toFixed(1)} L${(bx+bw).toFixed(1)} ${Y1} Z" fill="${w1Colour(si)}"/>`})});
 const xLab=cats.map((c,ci)=>`<text x="${(X0+ci*gw+gw/2).toFixed(1)}" y="${Y1+18}">${escapeHTML(c)}</text>`).join("");
 return `<svg viewBox="0 0 320 196" width="100%" role="img" aria-label="${escapeHTML(axisLabel||"Bar chart")}">
 <g stroke="var(--line)" stroke-width="1">${grid}</g>
 <g fill="var(--muted)" font-size="11" text-anchor="end">${yLab}</g>
 <text x="2" y="12" fill="var(--muted)" font-size="11">${escapeHTML(axisLabel||"")}</text>
 ${bars}<g fill="var(--muted)" font-size="11" text-anchor="middle">${xLab}</g></svg>`;
}
function w1PieSvg(snapshots){
 const r=38,sw=24,C=2*Math.PI*r,two=snapshots.length>1,w=two?320:180;
 const donut=(snap,cx)=>{let off=0;
  const arcs=snap.slices.map((sl,i)=>{const len=sl.value/100*C,seg=`<circle cx="${cx}" cy="72" r="${r}" fill="none" stroke="${W1_RAMP[i%W1_RAMP.length]}" stroke-width="${sw}" stroke-dasharray="${Math.max(0,len-2).toFixed(2)} ${C.toFixed(2)}" stroke-dashoffset="${(-off).toFixed(2)}"/>`;off+=len;return seg}).join("");
  return `<g transform="rotate(-90 ${cx} 72)">${arcs}</g><text x="${cx}" y="76" text-anchor="middle" font-size="14" font-weight="850" fill="var(--ink)">${escapeHTML(snap.label)}</text>`};
 const cxs=two?[82,238]:[90];
 return `<svg viewBox="0 0 ${w} 148" width="100%" role="img" aria-label="Proportional breakdown">${snapshots.map((s,i)=>donut(s,cxs[i])).join("")}</svg>`;
}
function w1PieTable(snapshots){
 const labels=snapshots[0].slices.map(s=>s.label);
 const val=(snap,l)=>{const s=snap.slices.find(x=>x.label===l);return s?s.value+"%":"—"};
 const delta=l=>{if(snapshots.length<2)return"";const a=snapshots[0].slices.find(x=>x.label===l),b=snapshots[1].slices.find(x=>x.label===l);
  if(!a||!b)return"<td>—</td>";const d=Math.round((b.value-a.value)*10)/10;
  return `<td style="color:${d>0?"var(--good)":d<0?"var(--danger)":"var(--muted)"}">${d>0?"+":""}${d} pts</td>`};
 return `<div class="table-wrap w1-narrow-table"><table><thead><tr><th>Category</th>${snapshots.map(s=>`<th>${escapeHTML(s.label)}</th>`).join("")}${snapshots.length>1?"<th>Change</th>":""}</tr></thead><tbody>
 ${labels.map((l,i)=>`<tr><td><span class="w1-sw" style="background:${W1_RAMP[i%W1_RAMP.length]}"></span>${escapeHTML(l)}</td>${snapshots.map(s=>`<td>${val(s,l)}</td>`).join("")}${snapshots.length>1?delta(l):""}</tr>`).join("")}
 </tbody></table></div>`;
}
function w1TableHtml(v){
 return `<div class="table-wrap"><table><thead><tr><th>${escapeHTML(v.rowHeader||"")}</th>${v.columns.map(c=>`<th>${escapeHTML(c)}</th>`).join("")}</tr></thead><tbody>
 ${v.rows.map(r=>`<tr><td><strong>${escapeHTML(r.label)}</strong></td>${r.cells.map(c=>`<td>${w1Num(c)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}
function w1ProcessHtml(v){
 return `<div class="w1-flowhead"><span class="badge${v.cyclical?" warn":""}">${v.cyclical?"Closed loop":"Linear"}</span><span>${v.stages.length} stages · in: ${escapeHTML(v.input)} · out: ${escapeHTML(v.output)}</span></div>
 <ol class="w1-stages">${v.stages.map(s=>`<li class="w1-stage"><span class="w1-stage-n" aria-hidden="true">${s.n}</span><div><strong>${escapeHTML(s.label)}</strong><div class="small muted">${escapeHTML(s.detail)}</div></div></li>`).join("")}</ol>
 ${v.cyclical?`<p class="w1-loop">Stage ${v.stages.length} returns to stage 1 — the loop closes.</p>`:""}`;
}
function w1MapHtml(v){
 const order=["added","removed","replaced","unchanged"];
 return `<p class="small muted">${escapeHTML(v.periods.join(" → "))}</p>
 <div class="w1-legend">${order.map(k=>`<span class="w1-lg"><span class="w1-sw" style="background:${W1_STATUS[k].c}"></span>${W1_STATUS[k].label}</span>`).join("")}</div>
 <div class="w1-features">${v.features.map(f=>`<div class="w1-feature" style="border-left-color:${W1_STATUS[f.status].c}">
  <div class="row"><strong>${escapeHTML(f.label)}</strong><span class="badge" style="background:#fff;border:1px solid ${W1_STATUS[f.status].c};color:${W1_STATUS[f.status].c}">${W1_STATUS[f.status].label}</span></div>
  <div class="small muted">${escapeHTML(f.area)} — ${escapeHTML(f.note)}</div></div>`).join("")}</div>`;
}
function w1Legend(series){
 return `<div class="w1-legend">${series.map((s,i)=>`<span class="w1-lg"><span class="w1-sw" style="background:${w1Colour(i)}"></span>${escapeHTML(s.name)}</span>`).join("")}</div>`;
}
function w1SeriesTable(cats,series){
 return `<div class="table-wrap w1-narrow-table"><table><thead><tr><th></th>${cats.map(c=>`<th>${escapeHTML(c)}</th>`).join("")}</tr></thead><tbody>
 ${series.map((s,i)=>`<tr><td><span class="w1-sw" style="background:${w1Colour(i)}"></span>${escapeHTML(s.name)}</td>${s.values.map(v=>`<td>${w1Num(v)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}
function w1RenderComponent(c){
 if(c.kind==="line")return `<div class="w1-chart">${w1LineSvg(c.categories,c.series,c.axisLabel||c.unit)}</div>`+w1Legend(c.series)+w1SeriesTable(c.categories,c.series);
 if(c.kind==="bar")return `<div class="w1-chart">${w1BarSvg(c.categories,c.series,c.axisLabel||c.unit)}</div>`+w1Legend(c.series)+w1SeriesTable(c.categories,c.series);
 if(c.kind==="pie")return `<div class="w1-chart">${w1PieSvg(c.snapshots)}</div>`+w1PieTable(c.snapshots);
 if(c.kind==="table")return w1TableHtml(c);
 if(c.kind==="process")return w1ProcessHtml(c);
 if(c.kind==="map")return w1MapHtml(c);
 return "";
}
function w1VisualPanel(v,opts={}){
 const body=v.kind==="mixed"
  ?v.components.map((c,i)=>`<div class="w1-subvisual"><div class="w1-subtitle">Chart ${i+1} · ${escapeHTML(c.title||"")}</div>${w1RenderComponent(c)}</div>`).join("")
  :w1RenderComponent(v);
 return `<section class="w1-visual" aria-label="Task visual">
 ${opts.hideRubric?"":`<p class="w1-rubric">${escapeHTML(v.taskStatement)}</p>`}
 ${body}
 <details class="w1-alt"><summary>Describe this visual in words</summary><p>${escapeHTML(v.altText)}</p></details>
 <p class="w1-src">${escapeHTML(v.sourceNote)} · ${escapeHTML(v.unit)}</p></section>`;
}

/* --- mastery, per DECISIONS.md D-015 --- */
function w1UpdateMastery(family){
 const mod=w1Module(family);if(!mod)return;
 const exs=w1FamilyExercises(family),latest={};
 (state.writing1.results||[]).filter(r=>r.family===family).forEach(r=>latest[r.exerciseId]=r);
 const vals=Object.values(latest);
 const rate=mode=>{const set=vals.filter(r=>r.mode===mode);return set.length?set.filter(r=>r.correct).length/set.length:null};
 const subs=(state.writing1.submissions||[]).filter(s=>s.family===family);
 const fullLength=s=>s.meetsLength??(s.words>=(w1Prompt(s.promptId)?.wordMinimum??150));
 const timedSub=subs.some(s=>s.withinLimit&&s.checklistDone>=s.checklistTotal&&fullLength(s));
 let level=state.mastery[mod.id]??0;
 const guided=rate("guided");if(guided!==null&&guided>=.5&&vals.filter(r=>r.mode==="guided").length>=exs.filter(e=>e.mode==="guided").length)level=Math.max(level,2);
 const indep=rate("independent");if(indep!==null&&indep>=.75&&vals.filter(r=>r.mode==="independent").length>=exs.filter(e=>e.mode==="independent").length)level=Math.max(level,3);
 const timed=rate("timed");if(timed!==null&&timed>=.75&&timedSub)level=Math.max(level,4);
 const dates=new Set(vals.map(r=>r.date)),masteryEx=vals.find(r=>r.mode==="mastery"&&r.correct);
 const overall=vals.length?vals.filter(r=>r.correct).length/vals.length:0;
 if(vals.length>=3&&dates.size>=2&&masteryEx&&overall>=.85&&subs.some(s=>s.withinLimit&&fullLength(s)))level=5;
 state.mastery[mod.id]=level;
}
function w1FamilyProgress(family){
 const exs=w1FamilyExercises(family),done=exs.filter(e=>w1LatestResult(e.id)).length;
 const correct=exs.filter(e=>w1LatestResult(e.id)?.correct).length;
 const prompts=w1FamilyPrompts(family),subs=prompts.filter(p=>w1LatestSubmission(p.id)).length;
 return {total:exs.length,done,correct,prompts:prompts.length,subs};
}

/* --- answer checking --- */
function w1Check(ex,given){
 if(ex.type==="select")return given===ex.correctAnswer;
 if(ex.type==="cloze")return (ex.acceptableAnswers||[]).some(a=>normalizeAnswer(a)===normalizeAnswer(given));
 if(ex.type==="order")return Array.isArray(given)&&given.length===ex.correctAnswer.length&&given.every((x,i)=>x===ex.correctAnswer[i]);
 return false;
}
function w1SetAnswer(id,val){state.writing1.answers=state.writing1.answers||{};state.writing1.answers[id]=val;saveState()}
function w1Order(ex){
 const saved=state.writing1.answers?.[ex.id];
 if(Array.isArray(saved)&&saved.length===ex.items.length)return saved;
 return ex.items.map(i=>i.id);
}
function w1MoveOrder(id,idx,dir){
 const ex=w1Exercise(id),cur=w1Order(ex).slice(),to=idx+dir;
 if(to<0||to>=cur.length)return;
 [cur[idx],cur[to]]=[cur[to],cur[idx]];w1SetAnswer(id,cur);render();
}
function w1SubmitExercise(id){
 const ex=w1Exercise(id);if(!ex)return;
 const given=ex.type==="order"?w1Order(ex):(state.writing1.answers?.[id]??"");
 if(ex.type!=="order"&&!String(given).trim())return toast("Choose or type an answer first");
 const correct=w1Check(ex,given);
 const t=state.writing1.exerciseTimer,timed=["timed","mastery"].includes(ex.mode);
 const elapsed=timed&&t?.exerciseId===id?Math.floor((Date.now()-t.startAt)/1000):null;
 const withinLimit=timed?(elapsed!==null&&elapsed<=ex.estimatedMinutes*60):true;
 const result={id:uid("W1RES"),date:new Date().toISOString().slice(0,10),createdAt:new Date().toISOString(),
  exerciseId:id,moduleId:w1Module(ex.questionFamily)?.id||"",family:ex.questionFamily,microType:ex.microType,
  mode:ex.mode,correct,timed,elapsedSeconds:elapsed,withinLimit,answer:given};
 state.writing1.results.push(result);
 state.practiceResults.push({id:result.id,date:result.date,skill:"Writing Task 1",module:result.moduleId,
  score:correct?1:0,total:1,accuracy:correct?1:0,timed,withinLimit});
 if(!correct){
  const cat=(w1()?.errorTaxonomy||[]).find(c=>c.id===ex.errorCategory);
  const prior=state.errors.some(e=>e.skill==="Writing Task 1"&&e.category===(cat?.en||ex.errorCategory)&&!e.resolved);
  state.errors.unshift({id:uid("ERR"),date:result.date,skill:"Writing Task 1",module:result.moduleId,questionId:id,
   learnerAnswer:Array.isArray(given)?given.join(" → "):String(given),
   correctAnswer:Array.isArray(ex.correctAnswer)?ex.correctAnswer.join(" → "):String(ex.correctAnswer),
   category:cat?.en||ex.errorCategory,explanation:ex.explanation,correction:cat?.correction||"",
   repeated:prior,reviewDate:new Date(Date.now()+3*86400000).toISOString().slice(0,10),resolved:false});
  if(!state.reviews.some(r=>r.questionId===id))state.reviews.push({id:uid("REV"),type:"Writing Task 1",
   title:`Review: ${w1Meta(ex.questionFamily)?.title||ex.questionFamily} — ${ex.microTypeLabel}`,
   priority:prior?5:4,module:result.moduleId,questionId:id,
   dueDate:new Date(Date.now()+3*86400000).toISOString().slice(0,10)});
 }
 w1UpdateMastery(ex.questionFamily);
 state.studyHistory.unshift({date:result.date,minutes:ex.estimatedMinutes,skill:"Writing Task 1",module:result.moduleId,accuracy:correct?1:0});
 state.writing1.exerciseTimer=null;saveState();render();toast(correct?"Correct":"Review the feedback below");
}

/* --- writing drafts and timing --- */
function w1Draft(pid){return (state.writing1.drafts||{})[pid]||{plan:"",text:"",updatedAt:null}}
function w1SaveDraft(pid,patch){
 state.writing1.drafts=state.writing1.drafts||{};
 state.writing1.drafts[pid]={...w1Draft(pid),...patch,updatedAt:new Date().toISOString()};saveState();
}
function w1StartPromptTimer(pid){
 const p=w1Prompt(pid);if(!p)return;
 state.writing1.timer={promptId:pid,startAt:Date.now(),limitSeconds:p.estimatedMinutes*60};saveState();
 clearInterval(w1TimerHandle);w1TimerHandle=setInterval(()=>w1DrawTimer(pid),250);w1DrawTimer(pid);toast("Timed draft started")
}
function w1DrawTimer(pid){
 const el=document.querySelector("#w1Timer");if(!el)return;
 const p=w1Prompt(pid),t=state.writing1.timer;
 if(!t||t.promptId!==pid){el.textContent=String(p.estimatedMinutes).padStart(2,"0")+":00";return}
 const elapsed=Math.floor((Date.now()-t.startAt)/1000),remain=Math.max(0,t.limitSeconds-elapsed);
 el.textContent=String(Math.floor(remain/60)).padStart(2,"0")+":"+String(remain%60).padStart(2,"0");
 el.classList.toggle("over",remain===0);
 const bar=document.querySelector("#w1TimerBar");if(bar)bar.style.width=Math.min(100,elapsed/t.limitSeconds*100)+"%";
 if(remain===0)clearInterval(w1TimerHandle);
}
function w1DrawExerciseTimer(id){
 const el=document.querySelector("#w1ExTimer");if(!el)return;
 const ex=w1Exercise(id),t=state.writing1.exerciseTimer;
 if(!t||t.exerciseId!==id){el.textContent=String(ex.estimatedMinutes).padStart(2,"0")+":00";return}
 const elapsed=Math.floor((Date.now()-t.startAt)/1000),remain=Math.max(0,ex.estimatedMinutes*60-elapsed);
 el.textContent=String(Math.floor(remain/60)).padStart(2,"0")+":"+String(remain%60).padStart(2,"0");
}
function w1ToggleCheck(pid,cid){
 state.writing1.checklists=state.writing1.checklists||{};
 const cur=state.writing1.checklists[pid]||{};cur[cid]=!cur[cid];
 state.writing1.checklists[pid]=cur;saveState();render();
}
function w1SubmitPrompt(pid){
 const p=w1Prompt(pid),d=w1Draft(pid),words=w1Words(d.text);
 if(words<20)return toast("Write a response before submitting");
 const t=state.writing1.timer,elapsed=t?.promptId===pid?Math.floor((Date.now()-t.startAt)/1000):null;
 const ticks=state.writing1.checklists?.[pid]||{},done=p.checklist.filter(c=>ticks[c.id]).length;
 const sub={id:uid("W1SUB"),date:new Date().toISOString().slice(0,10),createdAt:new Date().toISOString(),
  promptId:pid,moduleId:w1Module(p.questionFamily)?.id||"",family:p.questionFamily,mode:p.mode,
  words,wordMinimum:p.wordMinimum,meetsLength:words>=p.wordMinimum,
  elapsedSeconds:elapsed,withinLimit:elapsed!==null&&elapsed<=p.estimatedMinutes*60,
  checklistDone:done,checklistTotal:p.checklist.length,timed:elapsed!==null};
 state.writing1.submissions.push(sub);
 state.savedResponses.push({id:"W1-"+pid+"-"+sub.id,type:"writing",promptId:pid,text:d.text,plan:d.plan,updatedAt:sub.createdAt});
 p.checklist.filter(c=>!ticks[c.id]).slice(0,3).forEach(c=>{
  if(!state.reviews.some(r=>r.questionId===pid+":"+c.id))state.reviews.push({id:uid("REV"),type:"Writing Task 1",
   title:`Self-review gap: ${c.text}`,priority:3,module:sub.moduleId,questionId:pid+":"+c.id,
   dueDate:new Date(Date.now()+2*86400000).toISOString().slice(0,10)})});
 if(!sub.meetsLength){
  const uc=(w1()?.errorTaxonomy||[]).find(c=>c.id==="underlength_response");
  state.errors.unshift({id:uid("ERR"),date:sub.date,skill:"Writing Task 1",module:sub.moduleId,questionId:pid,
   learnerAnswer:`${words} words`,correctAnswer:`at least ${p.wordMinimum} words`,
   category:uc?.en||"Underlength response",explanation:uc?.description||"",correction:uc?.correction||"",
   repeated:false,reviewDate:new Date(Date.now()+2*86400000).toISOString().slice(0,10),resolved:false});
 }
 if(elapsed!==null&&elapsed>p.estimatedMinutes*60){
  const cat=(w1()?.errorTaxonomy||[]).find(c=>c.id==="timing_failure");
  state.errors.unshift({id:uid("ERR"),date:sub.date,skill:"Writing Task 1",module:sub.moduleId,questionId:pid,
   learnerAnswer:`${Math.round(elapsed/60)} minutes`,correctAnswer:`${p.estimatedMinutes} minutes`,
   category:cat?.en||"Timing failure",explanation:cat?.description||"",correction:cat?.correction||"",
   repeated:false,reviewDate:new Date(Date.now()+3*86400000).toISOString().slice(0,10),resolved:false});
 }
 w1UpdateMastery(p.questionFamily);
 state.studyHistory.unshift({date:sub.date,minutes:p.estimatedMinutes,skill:"Writing Task 1",module:sub.moduleId});
 state.writing1.timer=null;saveState();render();
 toast(sub.meetsLength?`Response recorded — ${words} words`
  :`Recorded, but ${words} words is under the ${p.wordMinimum}-word minimum — an underlength answer cannot count towards L4 or L5`);
}

/* --- views --- */
function renderWriting1(){
 const d=w1();
 if(!d)return genericLab("Writing Task 1","Writing Task 1 curriculum data failed to load.","Дані Writing Task 1 не завантажилися.");
 if(state.writing1.activeBandId)return renderW1Band(state.writing1.activeBandId);
 if(state.writing1.activePromptId)return renderW1Prompt(state.writing1.activePromptId);
 if(state.writing1.activeExerciseId)return renderW1Exercise(state.writing1.activeExerciseId);
 if(state.writing1.activeFamily)return renderW1Family(state.writing1.activeFamily);
 const doneEx=(d.exercises||[]).filter(e=>w1LatestResult(e.id)).length;
 const doneP=(d.prompts||[]).filter(p=>w1LatestSubmission(p.id)).length;
 return pageHero("WRITING TASK 1","Report the data, not every number","Seven visual families, each trained from key-feature selection through to a full timed response.","Task 1 — це звіт, а не есе. Двадцять хвилин, щонайменше 150 слів, жодних причин, оцінок і порад.")+
 `<div class="grid">
 ${card("G4 curriculum inventory",`<div class="kpi-grid">
  <div class="kpi"><span class="muted">Visual families</span><strong>${d.meta.familyCount}</strong></div>
  <div class="kpi"><span class="muted">Micro-exercises</span><strong>${d.meta.microExerciseCount}</strong></div>
  <div class="kpi"><span class="muted">Full prompts</span><strong>${d.meta.promptCount}</strong></div>
  <div class="kpi"><span class="muted">Exercises done</span><strong>${doneEx} / ${d.meta.microExerciseCount}</strong></div>
  <div class="kpi"><span class="muted">Prompts answered</span><strong>${doneP} / ${d.meta.promptCount}</strong></div></div>
  <p class="small muted">${escapeHTML(d.meta.scoringNote)}</p>`)}
 ${card("Foundation",`<div class="module-list">${d.modules.filter(m=>m.kind==="foundation").map(m=>`<div class="module-item"><div class="mastery-dot">${state.mastery[m.id]??0}</div><div><strong>${escapeHTML(m.title)}</strong><div class="small muted">${escapeHTML(m.objectives[0])}</div><details><summary>Learn the strategy</summary><ol>${m.lesson.map(x=>`<li>${escapeHTML(x)}</li>`).join("")}</ol>${m.workedExamples?.[0]?`<div class="strategy-block"><span class="badge">Worked example</span><p><strong>${escapeHTML(m.workedExamples[0].title)}</strong></p><p>${escapeHTML(m.workedExamples[0].analysis)}</p></div>`:""}${ua("",escapeHTML(m.uaSupport))}</details></div><button class="btn secondary" data-w1-foundation="${m.id}">Mark introduced</button></div>`).join("")}</div>`)}
 ${card("Visual families",`<div class="family-grid">${d.familyOrder.map(f=>{const meta=d.familyMeta[f],mod=w1Module(f),pg=w1FamilyProgress(f);
  return `<button class="family-card" data-w1-family="${f}"><span class="badge">L${state.mastery[mod.id]??0}</span><strong>${escapeHTML(meta.title)}</strong><span>${escapeHTML(meta.skill)}</span><div class="progress" aria-label="${escapeHTML(meta.title)} progress"><span style="width:${Math.round(pg.done/pg.total*100)}%"></span></div><small>${pg.done}/${pg.total} exercises • ${pg.subs}/${pg.prompts} prompts</small></button>`}).join("")}</div>`)}
 ${card("Mastery rule",`<p>${d.masteryRules.levels.map(l=>`<strong>L${l.level} ${l.name}:</strong> ${escapeHTML(l.rule)}`).join(" ")}</p><p class="small muted">${escapeHTML(d.masteryRules.note)}</p>`)}
 </div>`;
}
function w1Band(id){return (w1()?.bandComparisons||[]).find(b=>b.id===id)}
function w1FamilyBands(f){return (w1()?.bandComparisons||[]).filter(b=>b.questionFamily===f)}
function w1BandOpened(id){return !!(state.writing1.bandsOpened||{})[id]}
function renderW1Band(id){
 const b=w1Band(id),v=w1Visual(b.visualId),meta=w1Meta(b.questionFamily);
 const active=state.writing1.activeBandLevel||"Band 8";
 const shown=b.responses.find(r=>r.level===active)||b.responses[0];
 return pageHero("BAND COMPARISON LAB",meta.title,b.focus,b.uaSupport)+`<div class="grid w1-workspace">
 ${card("The task",`<div class="row"><button class="btn ghost" data-w1-back-family="${b.questionFamily}">← Module</button></div>${w1VisualPanel(v)}`,"half")}
 ${card("Three responses to the same task",`
  <div class="notice">${escapeHTML(b.scoringNote)}</div>
  <div class="segmented" style="margin-top:12px">${b.responses.map(r=>`<button class="btn ${r.level===active?"":"secondary"}" data-w1-band-level="${escapeHTML(r.level)}">${escapeHTML(r.level)}</button>`).join("")}</div>
  <div class="w1-bandcard" style="margin-top:12px">
   <div class="row"><span class="badge warn">${escapeHTML(shown.styleLabel||shown.level+"-style sample")}</span><strong>${escapeHTML(shown.label)}</strong><span class="small muted">${shown.wordCount} words (Task 1 minimum ${shown.wordMinimum??150})</span></div>
   <div class="w1-model" style="margin-top:10px">${shown.text.map(p=>`<p>${escapeHTML(p)}</p>`).join("")}</div>
   <div class="grid" style="margin-top:10px">
    <div class="strategy-block half"><span class="badge good">What it does</span><ul>${shown.does.length?shown.does.map(x=>`<li>${escapeHTML(x)}</li>`).join(""):"<li>—</li>"}</ul></div>
    <div class="strategy-block half"><span class="badge ${shown.missing.length?"warn":"good"}">${shown.missing.length?"What holds it back":"Nothing holding it back"}</span><ul>${shown.missing.length?shown.missing.map(x=>`<li>${escapeHTML(x)}</li>`).join(""):"<li>This response models the target.</li>"}</ul></div>
   </div>
   ${ua("",escapeHTML((w1().bandLevels.find(l=>l.level===shown.level)||{}).ua||""))}
  </div>`,"half")}
 ${card("What actually separates them",`<div class="table-wrap"><table><thead><tr><th>Aspect</th><th>IELTS criterion</th>${b.responses.map(r=>`<th>${escapeHTML(r.level)}</th>`).join("")}</tr></thead><tbody>
  ${b.comparison.map(row=>`<tr><td><strong>${escapeHTML(row.aspect)}</strong></td><td class="small muted">${escapeHTML((b.aspectCriteria||{})[row.aspect]||"—")}</td><td>${escapeHTML(row.b6)}</td><td>${escapeHTML(row.b7)}</td><td>${escapeHTML(row.b8)}</td></tr>`).join("")}
  </tbody></table></div>
  ${b.descriptorReference?`<p class="small muted" style="margin-top:8px">${escapeHTML(b.descriptorReference)}</p>`:""}
  <div class="notice" style="margin-top:12px"><strong>Takeaway.</strong> ${escapeHTML(b.takeaway)}</div>
  ${ua("",escapeHTML(b.uaSupport))}
  <div class="row" style="margin-top:12px"><button class="btn" data-w1-band-read="${b.id}">${w1BandOpened(b.id)?"Reviewed":"Mark as reviewed"}</button><button class="btn ghost" data-w1-back-family="${b.questionFamily}">Back to module</button></div>`)}
 </div>`;
}

function renderW1Family(f){
 const meta=w1Meta(f),mod=w1Module(f),exs=w1FamilyExercises(f),prompts=w1FamilyPrompts(f);
 const modeGroup=m=>exs.filter(e=>e.mode===m);
 const exRow=e=>{const r=w1LatestResult(e.id);
  return `<div class="session-item"><div><span class="badge${e.mode==="mastery"?" warn":""}">${escapeHTML(e.microTypeLabel)}</span><strong>${escapeHTML(e.skillFocus)}</strong><div class="small muted">${e.estimatedMinutes} min · ${escapeHTML(e.modeLabel)}</div>${r?`<div class="small"><span class="badge ${r.correct?"good":"warn"}">${r.correct?"Correct":"Review"}</span></div>`:""}</div><button class="btn${r?" secondary":""}" data-w1-exercise="${e.id}">${r?"Retry":"Start"}</button></div>`};
 return pageHero("WRITING TASK 1 MODULE",meta.title,meta.skill,meta.uaTransferNote)+`<div class="grid">
 ${card("Learn → See → Think → Challenge",`<div class="stack">
  <div class="lesson-objective"><strong>What this family tests</strong><p>${escapeHTML(meta.whatItTests)}</p></div>
  <div class="strategy-block"><span class="badge">How IELTS builds it</span><p>${escapeHTML(meta.howIeltsConstructs)}</p></div>
  <div class="strategy-block"><span class="badge">Learn</span><ol>${mod.strategySteps.map(s=>`<li>${escapeHTML(s)}</li>`).join("")}</ol></div>
  <div class="strategy-block"><span class="badge">See · worked example</span><p class="small muted">${escapeHTML(mod.workedExamples[0].taskStatement)}</p><p><em>${escapeHTML(mod.workedExamples[0].modelSentence)}</em></p><p class="small">${escapeHTML(mod.workedExamples[0].analysis)}</p></div>
  <div class="trap"><strong>Common trap</strong><p>${escapeHTML(meta.trap)}</p></div>
  <div class="strategy-block"><span class="badge">Tense</span><p>${escapeHTML(meta.tenseRule)}</p></div>
  ${ua("",escapeHTML(mod.uaSupport))}
  <div class="row"><button class="btn ghost" data-w1-home>← All families</button><button class="btn secondary" data-w1-foundation="${mod.id}">Mark lesson introduced</button></div></div>`,"half")}
 ${card("What goes wrong here",`<div class="stack">${meta.commonErrors.map(c=>{const cat=(w1().errorTaxonomy||[]).find(x=>x.id===c.errorId);
  return `<div class="session-item" style="display:block"><span class="badge warn">${escapeHTML(cat?.en||c.errorId)}</span><p class="small"><strong>Symptom:</strong> ${escapeHTML(c.symptom)}</p><p class="small muted"><strong>Repair:</strong> ${escapeHTML(c.repair)}</p></div>`}).join("")}</div>`,"half")}
 ${card("Language bank",`<div class="stack">${Object.entries(mod.languageBank).map(([k,v])=>`<div class="strategy-block"><div class="w1-subtitle">${escapeHTML(k)}</div><div class="row" style="margin-top:8px">${v.map(x=>`<span class="badge">${escapeHTML(x)}</span>`).join("")}</div></div>`).join("")}${ua("",escapeHTML(meta.uaTransferNote))}</div>`,"half")}
 ${card("Practice progression",`<div class="stack">
  ${["guided","independent","timed","mastery"].map(m=>modeGroup(m).length?`<div class="w1-subtitle">${escapeHTML(w1().modeLabels[m])} · ${modeGroup(m).length}</div>`+modeGroup(m).map(exRow).join(""):"").join("")}
  ${w1FamilyBands(f).map(b=>`<div class="session-item" style="border-color:var(--ua)"><div><span class="badge">Band comparison lab</span><strong>Three responses to the same task, compared</strong><div class="small muted">${b.responses.length} sample responses · ${b.estimatedMinutes} min${w1BandOpened(b.id)?" · reviewed":""}</div></div><button class="btn secondary" data-w1-band="${b.id}">Open</button></div>`).join("")}
  <div class="w1-subtitle">Full timed prompts · ${prompts.length}</div>
  ${prompts.map(p=>{const s=w1LatestSubmission(p.id);
   return `<div class="session-item" style="border-color:var(--yellow)"><div><span class="badge warn">${escapeHTML(p.modeLabel)}</span><strong>${escapeHTML(w1Visual(p.visualId).title)}</strong><div class="small muted">${p.estimatedMinutes} min · ≥${p.wordMinimum} words</div>${s?`<div class="small"><strong>${s.words} words</strong> (min ${p.wordMinimum})${s.words>=p.wordMinimum?"":" — underlength"} · ${s.withinLimit?"within time":"over time"} · checklist ${s.checklistDone}/${s.checklistTotal}</div>`:""}</div><button class="btn" data-w1-prompt="${p.id}">${s?"Reopen":"Open"}</button></div>`}).join("")}
  </div>`,"half")}
 ${card("Mastery",`<div class="row"><span class="badge">L${state.mastery[mod.id]??0} · ${escapeHTML(APP_DATA.masteryLevels[state.mastery[mod.id]??0].en)}</span><div class="progress" style="flex:1" aria-label="Mastery"><span style="width:${(state.mastery[mod.id]??0)/5*100}%"></span></div></div>
  <p style="margin-top:10px">${w1().masteryRules.levels.map(l=>`<strong>L${l.level} ${l.name}:</strong> ${escapeHTML(l.rule)}`).join(" ")}</p>
  <p class="small muted">${escapeHTML(w1().masteryRules.note)}</p>`)}
 </div>`;
}
function renderW1Exercise(id){
 const ex=w1Exercise(id),v=w1Visual(ex.visualId),r=w1LatestResult(id),meta=w1Meta(ex.questionFamily);
 const timed=["timed","mastery"].includes(ex.mode);
 const given=ex.type==="order"?w1Order(ex):(state.writing1.answers?.[id]??"");
 let input="";
 if(ex.type==="select"){
  input=`<fieldset class="w1-options"><legend class="sr-only">${escapeHTML(ex.prompt)}</legend>${ex.options.map((o,i)=>{
   const chosen=given===o,isRight=o===ex.correctAnswer,cls=r?(isRight?" correct":(chosen?" wrong":" faded")):"";
   return `<label class="w1-opt${cls}"><input type="radio" name="w1opt-${id}" value="${escapeHTML(o)}" ${chosen?"checked":""} data-w1-answer="${id}"><span>${escapeHTML(o)}</span></label>`}).join("")}</fieldset>`;
 }else if(ex.type==="cloze"){
  const parts=ex.sentence.split("____");
  input=`<p class="w1-cloze">${escapeHTML(parts[0])}<input type="text" data-w1-answer="${id}" value="${escapeHTML(given)}" aria-label="Missing word" autocomplete="off" spellcheck="false">${escapeHTML(parts[1]||"")}</p>`;
 }else{
  input=`<ol class="w1-order">${given.map((iid,i)=>{const it=ex.items.find(x=>x.id===iid);
   return `<li class="w1-order-item${r?(ex.correctAnswer[i]===iid?" correct":" wrong"):""}"><div class="w1-order-ctl"><button class="btn ghost" data-w1-up="${id}:${i}" ${i===0?"disabled":""} aria-label="Move up">▲</button><button class="btn ghost" data-w1-down="${id}:${i}" ${i===given.length-1?"disabled":""} aria-label="Move down">▼</button></div><p>${escapeHTML(it.text)}</p></li>`}).join("")}</ol>`;
 }
 const feedback=r?`<div class="answer-feedback"><span class="badge ${r.correct?"good":"warn"}">${r.correct?"Correct":"Review"}</span>
  ${ex.type!=="order"?`<p><strong>Correct answer:</strong> ${escapeHTML(Array.isArray(ex.correctAnswer)?ex.correctAnswer.join(" → "):ex.correctAnswer)}</p>`:""}
  <p>${escapeHTML(ex.explanation)}</p>
  ${!r.correct&&ex.type==="select"?`<p class="small"><strong>Why your choice fails:</strong> ${escapeHTML(ex.distractorReasoning?.[given]||"This answer is not supported by the visual.")}</p>`:""}
  ${!r.correct?`<p class="small"><strong>Error category:</strong> ${escapeHTML((w1().errorTaxonomy.find(c=>c.id===ex.errorCategory)||{}).en||ex.errorCategory)}</p>`:""}
  ${ua("",escapeHTML(ex.uaSupport))}</div>`:ua("",escapeHTML(ex.uaSupport));
 return pageHero(ex.modeLabel,ex.microTypeLabel,`${meta.title} · ${escapeHTML(ex.skillFocus)}`,ex.uaSupport)+`<div class="grid w1-workspace">
 ${card("Task visual",`<div class="row"><button class="btn ghost" data-w1-back-family="${ex.questionFamily}">← Module</button><span class="badge">Original training data</span></div>${w1VisualPanel(v)}`,"half")}
 ${card("Exercise",`<form id="w1Form" class="stack">
  ${timed?`<div class="reading-timer-panel"><div id="w1ExTimer" class="timer">${String(ex.estimatedMinutes).padStart(2,"0")}:00</div><button type="button" class="btn secondary" data-w1-ex-timer="${id}">Start timed attempt</button></div>`:""}
  <div class="question-card ${r?(r.correct?"q-correct":"q-wrong"):""}"><p><strong>${escapeHTML(ex.prompt)}</strong></p>${input}${feedback}</div>
  <button type="button" class="btn" data-w1-submit="${id}">${r?"Try again":"Check answer"}</button>
  <div class="row"><button type="button" class="btn ghost" data-w1-back-family="${ex.questionFamily}">Back to module</button>${w1NextExercise(id)?`<button type="button" class="btn secondary" data-w1-exercise="${w1NextExercise(id)}">Next exercise →</button>`:""}</div>
  </form>`,"half")}
 </div>`;
}
function w1NextExercise(id){
 const ex=w1Exercise(id),list=w1FamilyExercises(ex.questionFamily),i=list.findIndex(e=>e.id===id);
 return i>=0&&i<list.length-1?list[i+1].id:null;
}
function renderW1Prompt(pid){
 const p=w1Prompt(pid),v=w1Visual(p.visualId),d=w1Draft(pid),s=w1LatestSubmission(pid);
 const ticks=state.writing1.checklists?.[pid]||{},done=p.checklist.filter(c=>ticks[c.id]).length;
 const words=w1Words(d.text),running=state.writing1.timer?.promptId===pid;
 const stage=s?"review":(running||words>0?"draft":"plan");
 const step=(n,label,active)=>`<div class="w1-step${active?" on":""}"><span class="w1-dot">${n}</span><span>${label}</span></div>`;
 return pageHero("FULL PROMPT · "+p.modeLabel,v.title,`${p.estimatedMinutes} minutes · at least ${p.wordMinimum} words`,p.uaSupport)+`<div class="grid w1-workspace">
 ${card("Task",`<div class="row"><button class="btn ghost" data-w1-back-family="${p.questionFamily}">← Module</button></div>
  <p class="w1-rubric" style="margin-top:12px">${escapeHTML(p.prompt)}</p>${w1VisualPanel(v,{hideRubric:true})}`,"half")}
 ${card("Your response",`<div class="w1-stepper">${step(1,"Plan",stage==="plan")}${step(2,"Draft",stage==="draft")}${step(3,"Review",stage==="review")}</div>
  <div class="stack" style="margin-top:12px">
  <details class="strategy-block" ${stage==="plan"?"open":""}><summary><strong>1 · Plan</strong> — ${p.planning.minutes} min</summary>
   <ol>${p.planning.steps.map(x=>`<li>${escapeHTML(x)}</li>`).join("")}</ol>
   <label class="field">Your plan<textarea id="w1Plan" data-w1-plan="${pid}" placeholder="${escapeHTML(p.planning.placeholder)}">${escapeHTML(d.plan)}</textarea></label></details>
  <div class="reading-timer-panel"><div id="w1Timer" class="timer">${String(p.estimatedMinutes).padStart(2,"0")}:00</div>
   <div class="row"><button class="btn secondary" data-w1-start-timer="${pid}">${running?"Restart timer":"Start timed draft"}</button></div></div>
  <div class="progress" aria-label="Time used"><span id="w1TimerBar" style="width:0%"></span></div>
  <label class="field">Your response<textarea id="w1Draft" class="w1-draft" data-w1-draft="${pid}" placeholder="Write your report here…">${escapeHTML(d.text)}</textarea></label>
  <div class="row" style="justify-content:space-between"><span class="small ${words>=p.wordMinimum?"":"muted"}"><span id="w1Words">${words}</span> / ${p.wordMinimum} words</span><span class="small muted" id="w1SaveState">${d.updatedAt?"Saved locally":"Autosaves as you type"}</span></div>
  <div class="notice">Your draft is kept locally even if you close the page. Timing evidence is only recorded when you submit.</div>
  <button class="btn" data-w1-submit-prompt="${pid}">Submit response</button>
  </div>`,"half")}
 ${card("Self-review checklist",`<p class="small muted">${escapeHTML(p.scoringNote)}</p>
  <div class="stack" style="margin-top:10px">${p.checklist.map(c=>`<label class="w1-chk"><input type="checkbox" ${ticks[c.id]?"checked":""} data-w1-check="${pid}:${c.id}"><span>${escapeHTML(c.text)} <span class="muted">· ${escapeHTML(c.criterion)}</span></span></label>`).join("")}</div>
  <p class="small" style="margin-top:10px"><strong>${done}/${p.checklist.length}</strong> ticked</p>`,"half")}
 ${card("Model response",`<details class="strategy-block"><summary><strong>Compare with the annotated model</strong></summary>
  <div class="w1-model">${p.modelResponse.map((par,i)=>`<p class="${i===1?"w1-overview":""}">${escapeHTML(par)}</p>`).join("")}</div>
  <div class="stack" style="margin-top:10px">${p.modelNotes.map((n,i)=>`<div class="row"><span class="badge">${i+1}</span><span class="small">${escapeHTML(n)}</span></div>`).join("")}</div>
  <div class="strategy-block" style="margin-top:10px"><span class="badge">Target features</span><ul>${p.targetFeatures.map(t=>`<li>${escapeHTML(t)}</li>`).join("")}</ul></div>
  ${ua("",escapeHTML(p.uaSupport))}</details>`,"half")}
 ${s?card("Recorded",`<div class="kpi-grid">
  <div class="kpi"><span class="muted">Time used</span><strong>${s.elapsedSeconds!==null?String(Math.floor(s.elapsedSeconds/60)).padStart(2,"0")+":"+String(s.elapsedSeconds%60).padStart(2,"0"):"untimed"}</strong></div>
  <div class="kpi"><span class="muted">Words</span><strong>${s.words}</strong></div>
  <div class="kpi"><span class="muted">Checklist</span><strong>${s.checklistDone}/${s.checklistTotal}</strong></div>
  <div class="kpi"><span class="muted">Mastery</span><strong>${masteryBadge(w1Module(p.questionFamily).id)}</strong></div></div>
  <div class="notice" style="margin-top:10px">${s.withinLimit?"<strong>Within the "+p.estimatedMinutes+"-minute limit.</strong> Timed evidence recorded.":"<strong>Over the "+p.estimatedMinutes+"-minute limit.</strong> Logged as a timing error."} ${s.checklistDone<s.checklistTotal?"Unticked checklist items were queued for review.":""}</div>`):""}
 </div>`;
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
 (window.WRITING1_DATA?.visuals||[]).forEach(v=>{if(`${v.title} ${v.family} ${v.taskStatement}`.toLowerCase().includes(q))hits.push({type:"Writing Task 1",title:v.title,detail:window.WRITING1_DATA.familyMeta[v.family].title})});
 (window.WRITING1_DATA?.exercises||[]).forEach(e=>{if(`${e.prompt} ${e.microTypeLabel} ${e.skillFocus}`.toLowerCase().includes(q))hits.push({type:"Writing Task 1",title:e.microTypeLabel,detail:e.skillFocus})});
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
 task1:renderWriting1,
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
 document.querySelectorAll('[data-w1-family]').forEach(b=>b.onclick=()=>{state.writing1.activeFamily=b.dataset.w1Family;state.writing1.activeExerciseId=null;state.writing1.activePromptId=null;state.writing1.activeBandId=null;saveState();render()});
 document.querySelectorAll('[data-w1-home]').forEach(b=>b.onclick=()=>{state.writing1.activeFamily=null;state.writing1.activeExerciseId=null;state.writing1.activePromptId=null;state.writing1.activeBandId=null;saveState();render()});
 document.querySelectorAll('[data-w1-back-family]').forEach(b=>b.onclick=()=>{state.writing1.activeFamily=b.dataset.w1BackFamily;state.writing1.activeExerciseId=null;state.writing1.activePromptId=null;state.writing1.activeBandId=null;saveState();render()});
 document.querySelectorAll('[data-w1-exercise]').forEach(b=>b.onclick=()=>{const id=b.dataset.w1Exercise;state.writing1.activeExerciseId=id;state.writing1.activePromptId=null;state.writing1.activeBandId=null;state.writing1.activeFamily=w1Exercise(id).questionFamily;state.writing1.exerciseTimer=null;saveState();render()});
 document.querySelectorAll('[data-w1-prompt]').forEach(b=>b.onclick=()=>{const id=b.dataset.w1Prompt;state.writing1.activePromptId=id;state.writing1.activeExerciseId=null;state.writing1.activeBandId=null;state.writing1.activeFamily=w1Prompt(id).questionFamily;saveState();render()});
 document.querySelectorAll('[data-w1-foundation]').forEach(b=>b.onclick=()=>{const id=b.dataset.w1Foundation;state.mastery[id]=Math.max(state.mastery[id]??0,1);saveState();toast('Introduced — mastery now requires performance evidence');render()});
 document.querySelectorAll('[data-w1-answer]').forEach(el=>el.addEventListener(el.type==='radio'?'change':'input',e=>w1SetAnswer(e.target.dataset.w1Answer,e.target.value)));
 document.querySelectorAll('[data-w1-up]').forEach(b=>b.onclick=()=>{const[id,i]=b.dataset.w1Up.split(':');w1MoveOrder(id,Number(i),-1)});
 document.querySelectorAll('[data-w1-down]').forEach(b=>b.onclick=()=>{const[id,i]=b.dataset.w1Down.split(':');w1MoveOrder(id,Number(i),1)});
 document.querySelectorAll('[data-w1-submit]').forEach(b=>b.onclick=()=>w1SubmitExercise(b.dataset.w1Submit));
 document.querySelectorAll('[data-w1-ex-timer]').forEach(b=>b.onclick=()=>{const id=b.dataset.w1ExTimer;state.writing1.exerciseTimer={exerciseId:id,startAt:Date.now()};saveState();clearInterval(w1ExTimerHandle);w1ExTimerHandle=setInterval(()=>w1DrawExerciseTimer(id),250);w1DrawExerciseTimer(id);toast('Timed attempt started')});
 document.querySelectorAll('[data-w1-plan]').forEach(t=>t.addEventListener('input',e=>{w1SaveDraft(e.target.dataset.w1Plan,{plan:e.target.value});const s=document.querySelector('#w1SaveState');if(s)s.textContent='Saved locally'}));
 document.querySelectorAll('[data-w1-draft]').forEach(t=>t.addEventListener('input',e=>{w1SaveDraft(e.target.dataset.w1Draft,{text:e.target.value});const w=document.querySelector('#w1Words');if(w)w.textContent=w1Words(e.target.value);const s=document.querySelector('#w1SaveState');if(s)s.textContent='Saved locally'}));
 document.querySelectorAll('[data-w1-start-timer]').forEach(b=>b.onclick=()=>w1StartPromptTimer(b.dataset.w1StartTimer));
 document.querySelectorAll('[data-w1-check]').forEach(c=>c.onchange=()=>{const[pid,cid]=c.dataset.w1Check.split(':');w1ToggleCheck(pid,cid)});
 document.querySelectorAll('[data-w1-submit-prompt]').forEach(b=>b.onclick=()=>w1SubmitPrompt(b.dataset.w1SubmitPrompt));
 document.querySelectorAll('[data-w1-band]').forEach(b=>b.onclick=()=>{const id=b.dataset.w1Band;state.writing1.activeBandId=id;state.writing1.activeExerciseId=null;state.writing1.activePromptId=null;state.writing1.activeFamily=w1Band(id).questionFamily;state.writing1.activeBandLevel=state.writing1.activeBandLevel||'Band 8';saveState();render()});
 document.querySelectorAll('[data-w1-band-level]').forEach(b=>b.onclick=()=>{state.writing1.activeBandLevel=b.dataset.w1BandLevel;saveState();render()});
 document.querySelectorAll('[data-w1-band-read]').forEach(b=>b.onclick=()=>{state.writing1.bandsOpened=state.writing1.bandsOpened||{};state.writing1.bandsOpened[b.dataset.w1BandRead]=true;saveState();toast('Marked as reviewed');render()});
 if(state.writing1.activePromptId){w1DrawTimer(state.writing1.activePromptId);if(state.writing1.timer?.promptId===state.writing1.activePromptId){clearInterval(w1TimerHandle);w1TimerHandle=setInterval(()=>w1DrawTimer(state.writing1.activePromptId),250)}}
 if(state.writing1.activeExerciseId){w1DrawExerciseTimer(state.writing1.activeExerciseId);if(state.writing1.exerciseTimer?.exerciseId===state.writing1.activeExerciseId){clearInterval(w1ExTimerHandle);w1ExTimerHandle=setInterval(()=>w1DrawExerciseTimer(state.writing1.activeExerciseId),250)}}
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
