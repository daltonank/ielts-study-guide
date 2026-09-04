#!/usr/bin/env python3
from pathlib import Path
import json, textwrap, re

ROOT=Path(__file__).resolve().parents[1]

FAMILY_META = {
 'multiple_choice':('Multiple Choice','Detailed understanding and main ideas','Choosing an option because it repeats passage vocabulary rather than meaning.','детальне розуміння та головна думка'),
 'tfng':('True / False / Not Given','Evidence recognition','Treating a plausible inference as information actually stated.','розрізнення підтвердженої, суперечної та відсутньої інформації'),
 'ynng':("Yes / No / Not Given","Writer's views and claims","Confusing a factual detail with the writer's position.",'позиція та твердження автора'),
 'matching_information':('Matching Information','Scanning for specific details','Matching by topic rather than the exact detail requested.','пошук конкретної інформації у параграфах'),
 'matching_headings':('Matching Headings','Main idea and paragraph purpose','Choosing a heading because of one memorable example.','визначення головної ідеї абзацу'),
 'matching_features':('Matching Features','Connecting statements to people, places or categories','Remembering the right detail but attaching it to the wrong feature.','зіставлення тверджень з людьми, місцями або категоріями'),
 'matching_sentence_endings':('Matching Sentence Endings','Meaning across clauses','Choosing a grammatically possible ending that changes the meaning.','поєднання частин речення за змістом'),
 'sentence_completion':('Sentence Completion','Locate and reproduce precise information','Ignoring grammar or word-limit constraints around the gap.','точне відтворення інформації з тексту'),
 'summary_completion':('Summary Completion','Paraphrase recognition and synthesis','Searching for identical wording instead of equivalent meaning.','розпізнавання перефразування та узагальнення'),
 'note_completion':('Note Completion','Selective detail extraction','Copying too much text instead of the required answer unit.','вибір конкретних деталей'),
 'table_completion':('Table Completion','Compare structured information','Reading rows independently and missing the table relationship.','порівняння структурованої інформації'),
 'flow_chart_completion':('Flow-chart Completion','Process sequence and paraphrase mapping','Filling a plausible stage without checking the process order stated in the passage.','відстеження послідовності процесу та перефразування'),
 'diagram_label':('Diagram Label Completion','Spatial/process mapping','Finding the right word but attaching it to the wrong stage or location.','зіставлення тексту з етапами або частинами схеми'),
 'short_answer':('Short Answer','Precise evidence retrieval','Giving background knowledge instead of the passage answer.','коротка точна відповідь на основі тексту'),
 'inference_author':('Inference & Author Position','Infer implications and attitude','Overstating what can reasonably be concluded.','висновки, підтекст і ставлення автора'),
}

MODES=[('guided','Guided Practice','6.5'),('independent','Independent Practice','7'),('timed','Timed Round','7.5'),('mastery','Mastery Check','8')]

FAMILY_GUIDANCE={
'multiple_choice':{'steps':['Read the stem and decide whether it asks for detail, purpose, inference or main idea.','Predict the answer in your own words before reading the options.','Eliminate options that are true in the passage but do not answer this exact question.'],'worked':'Passage: “The redesign reduced complaints, but opening hours were unchanged.” Question: What changed? Answer: complaints, not opening hours.','challenge':'Find one option that could be factually true yet still fail because it answers a different question.'},
'tfng':{'steps':['Turn the statement into a precise claim.','Locate the relevant evidence and compare meaning, including negatives and quantities.','Choose Not Given only when the text neither confirms nor contradicts the claim.'],'worked':'Text: “The pilot ran in two schools.” Statement: “The pilot ran in every school.” Answer: False, because two directly contradicts every.','challenge':'Explain why “probably true” must still be Not Given when the passage provides no evidence.'},
'ynng':{'steps':['Identify whether the sentence is a writer claim, not merely a factual detail.','Locate language showing stance: argues, accepts, rejects, cautions, suggests.','Use Not Given when the writer never takes a position on the claim.'],'worked':'Writer: “Repair is useful, although specialist servicing is sometimes necessary.” Claim: “Consumers should repair every component.” Answer: No.','challenge':'Separate what the writer reports from what the writer endorses.'},
'matching_information':{'steps':['Underline the unique detail in the question.','Scan paragraph labels for that specific example, reason, comparison or description.','Do not reject a paragraph just because another question has already used it unless the instructions prohibit reuse.'],'worked':'Question asks for dependence on geology. The paragraph about boreholes explicitly says performance depends on geology, so that paragraph wins.','challenge':'Match a detail whose vocabulary is paraphrased rather than repeated.'},
'matching_headings':{'steps':['Summarize the whole paragraph in one short sentence.','Separate the controlling idea from examples and consequences.','Choose the heading broad enough to cover the entire paragraph but not broader than it.'],'worked':'A paragraph lists cleaning, flattening and supports for fragile paper. The main idea is preparing fragile material, not “cleaning paper.”','challenge':'Reject a heading that perfectly describes one sentence but ignores the rest of the paragraph.'},
'matching_features':{'steps':['Create a quick mental map of the people/places/features.','Scan for distinctive actions, theories or examples attached to each one.','Check the attribution twice when several features discuss the same topic.'],'worked':'If Neri uses crushed glass while Okafor studies corrosion coatings, a statement about glass aggregate maps to Neri.','challenge':'Distinguish two features working in the same field by the method they use.'},
'matching_sentence_endings':{'steps':['Read the sentence beginning and predict the required meaning/grammar.','Check endings against the passage, not only against grammar.','Use causal and qualifying words to preserve the original relationship.'],'worked':'“Safety training is compulsory …” pairs with “since unfamiliar equipment can cause serious injury,” because the passage gives that reason.','challenge':'Find an ending that is grammatically smooth but logically unsupported.'},
'sentence_completion':{'steps':['Read words around the gap to predict part of speech.','Locate the corresponding passage area in order.','Copy only the permitted word(s), preserving passage spelling.'],'worked':'“A raised ___ reduces the step.” The passage says “A raised kerb …”, so kerb fits both grammar and evidence.','challenge':'Predict the grammatical form before locating the word.'},
'summary_completion':{'steps':['Read the entire summary first to understand its logic.','Predict the type of word required in each gap.','Match paraphrased summary meaning to one concentrated area of the passage.'],'worked':'Summary “Dense plant ___ trap particles” maps to passage “Dense plant roots trap additional particles.”','challenge':'Find an answer when the summary changes both vocabulary and sentence structure.'},
'note_completion':{'steps':['Use note headings and punctuation to predict answer type.','Search for compact factual details rather than full sentences.','Respect word limits; extra correct words can still lose the mark.'],'worked':'Note “best survey period: ___” maps to “best survey period: dawn.”','challenge':'Reduce a sentence to the smallest answer unit the note needs.'},
'table_completion':{'steps':['Read row and column meaning before searching the passage.','Compare neighbouring cells to understand what kind of information belongs in the gap.','Check that the answer belongs to the correct item, not just the correct topic.'],'worked':'For tram, the first characteristic is “high passenger capacity”; the row relationship matters.','challenge':'Use the table structure to predict an answer category before rereading.'},
'flow_chart_completion':{'steps':['Identify the process start and end.','Track sequence markers such as first, then, after, before and finally.','Do not fill a plausible process stage unless the passage places it at that exact point.'],'worked':'If shredding occurs before mixing and aeration follows mixing, “shredding” cannot label the later aeration stage.','challenge':'Reconstruct the entire sequence before filling one ambiguous gap.'},
'diagram_label':{'steps':['Orient the diagram/process description before filling labels.','Track spatial words such as upper, lower, behind, through and beneath.','Use the passage wording while checking that the label attaches to the correct part.'],'worked':'“Warm air returns … through the upper outlet” means the upper exit label is outlet.','challenge':'Distinguish two nearby components by their position and function.'},
'short_answer':{'steps':['Identify the exact factual target in the question.','Locate the answer in passage order.','Use passage words and stay within the stated word limit.'],'worked':'Question “What action moves air?” Passage “fanning their wings creates airflow.” Answer: fanning.','challenge':'Answer with the smallest passage phrase that completely satisfies the question.'},
'inference_author':{'steps':['List what is explicitly known before inferring anything.','Ask which conclusion requires the fewest unsupported assumptions.','Watch scope: some, often and may do not support all, always or must.'],'worked':'If satisfaction rose only on slow connections, the safe inference is that speed work matters most where users experience delay, not that speed never matters elsewhere.','challenge':'Choose the weakest conclusion that still captures the author’s implication.'}
}

# 56 distinct topics, grouped four per family. All texts are original training content.
TOPICS={
'multiple_choice':[
('Cooling Streets','urban design','A district replaced dark asphalt beside two schools with pale aggregate and added rows of young trees.','Surface temperatures fell most on clear afternoons, although shaded benches remained cooler than the new pavement.','The project was designed to reduce pedestrian heat exposure rather than lower the temperature of the entire city.','Engineers cautioned that reflective surfaces can create glare if orientation is ignored.'),
('Seed Library Networks','agriculture','Several farming cooperatives began exchanging locally adapted seed rather than relying on one commercial variety.','The network records which seeds tolerate late frost, short droughts and heavy soil.','Its main advantage is preserving practical genetic diversity while farmers continue normal production.','Researchers note that storage alone is insufficient because varieties must also be grown and observed.'),
('Quiet Zones in Libraries','education','A university divided one large reading hall into silent, low-conversation and collaborative zones.','Noise complaints declined after visual signs and floor materials made the boundaries obvious.','Students did not spend more total time in the library, but they reported fewer interruptions during demanding tasks.','The redesign worked best when staff consistently redirected phone calls to the collaborative area.'),
('Restoring Urban Streams','environment','A city removed concrete walls from a narrow stream and rebuilt a winding channel with gravel banks.','During moderate storms, water moved more slowly and temporary pools formed on the floodplain.','The purpose was not to eliminate flooding but to reduce the speed and concentration of runoff.','Ecologists warned that upstream pollution would still limit habitat recovery.'),
],
'tfng':[
('Night Trains and Sleep','transport','An overnight rail operator tested dimmer corridor lighting and quieter door alarms on two routes.','Passengers in the modified carriages reported fewer awakenings, but total journey time was unchanged.','The trial did not compare train sleep with hotel sleep.','The operator plans a larger test before changing its entire fleet.'),
('Museum Case Lighting','culture','A museum reduced ultraviolet exposure in textile displays by switching to filtered LED lamps.','Visitors spent approximately the same amount of time at the displays before and after the change.','Conservators selected the lamps to slow colour fading, not to make the galleries brighter.','The study did not measure visitor preference for warm versus cool light.'),
('Rooftop Pollinator Beds','ecology','Three office buildings planted shallow rooftop beds with native flowering species.','Bee visits were most frequent on roofs that offered flowers from spring through early autumn.','The roofs were not intended to replace ground-level habitat.','No data were collected on butterfly populations.'),
('Compressed Workweeks','work','A customer-service team tested four longer workdays while keeping weekly paid hours unchanged.','Absence rates fell slightly during the pilot, whereas average call resolution time remained stable.','Managers did not reduce staffing during the experiment.','The company has not reported whether employees used their extra day for childcare, study or leisure.'),
],
'ynng':[
('The Case for Smaller Parks','urban policy','The writer argues that a network of small parks can serve dense neighbourhoods better than one distant large park.','She accepts that major parks are valuable for sports and large events.','Her central claim is that daily access matters because short visits are easier to fit around work and caregiving.','She does not argue that every vacant plot should become green space.'),
('Repairable Electronics','technology','The author supports product designs that allow batteries and screens to be replaced with ordinary tools.','He argues that repairability can extend useful life even when the newest device is more energy efficient.','However, he acknowledges that safety-critical components may require specialist servicing.','He gives no opinion on whether governments should ban sealed devices.'),
('Teaching Statistical Uncertainty','education','The writer believes science courses should teach confidence intervals and uncertainty alongside headline results.','She argues that this reduces the false impression that measurements are perfectly exact.','She does not suggest removing basic arithmetic from the curriculum.','The article does not state whether students prefer uncertainty exercises.'),
('Rewilding City Edges','environment','The author favours allowing selected urban-edge grasslands to grow longer between cuts.','He argues that uniform mowing can reduce habitat complexity, while carefully placed paths preserve public access.','He accepts that sightlines must be maintained near road junctions.','He does not claim that all municipal lawns should be managed identically.'),
],
'matching_information':[
('Four Ways to Store Heat','energy',[('A','Water tanks can store heat cheaply, but their large volume makes them easier to install in new buildings than old ones.'),('B','Phase-change materials absorb energy while melting, allowing a smaller unit to hold substantial heat.'),('C','Ceramic blocks tolerate very high temperatures and are therefore useful beside industrial furnaces.'),('D','Underground boreholes store seasonal heat in surrounding rock, but performance depends strongly on geology.')]),
('Urban Tree Strategies','environment',[('A','Street trees provide immediate shade where pedestrians need it, yet underground utilities can restrict root space.'),('B','Courtyard trees are protected from traffic damage and can cool adjacent walls, although access for maintenance may be difficult.'),('C','Pocket forests use dense mixed planting on small plots and aim to create layered vegetation quickly.'),('D','Riverside planting can connect fragmented habitat while also stabilising banks during ordinary flows.')]),
('Methods of Language Learning','education',[('A','Extensive reading exposes learners to repeated vocabulary in context without interrupting every sentence for analysis.'),('B','Retrieval practice asks learners to produce an answer from memory, strengthening recall more than simple rereading.'),('C','Shadowing requires learners to repeat speech with very little delay, drawing attention to rhythm and sound linking.'),('D','Conversation exchange provides spontaneous interaction, although feedback quality depends on the partner.')]),
('Approaches to Food-Waste Reduction','sustainability',[('A','Smaller default portions reduce plate waste while still allowing customers to request more food.'),('B','Dynamic pricing lowers the price of items close to their sell-by date and can redirect stock before disposal.'),('C','Anaerobic digestion recovers energy from unavoidable food waste but does not prevent the waste from being created.'),('D','Inventory forecasting uses sales patterns and weather data to reduce over-ordering before food reaches the shelf.')]),
],
'matching_headings':[
('Why Some Maps Feel Easy','cognition',[('A','Familiar landmarks give users stable reference points, allowing them to organise otherwise complex street information.'),('B','Too many colours can compete for attention, especially when categories are not clearly different in meaning.'),('C','Route maps often simplify distance in order to clarify connections; geometric accuracy is sacrificed for navigational clarity.'),('D','People remember turns more reliably when instructions are divided into short decision points rather than one long sequence.')],['Landmarks as anchors','When colour becomes noise','Accuracy sacrificed for clarity','Breaking a journey into decisions','The economic value of maps','Why north is always best']),
('The Hidden Work of Archives','history',[('A','Before an item can be studied, staff must establish where it came from and whether ownership records are reliable.'),('B','Fragile paper may need flattening, cleaning or custom supports before it can be handled safely.'),('C','Cataloguing converts physical objects into searchable descriptions, but wording choices can influence what researchers discover.'),('D','Digitisation expands access, yet high-resolution imaging creates storage costs and does not remove the need to preserve originals.')],['Establishing provenance','Preparing fragile material','The power of catalogue language','Digital access with physical obligations','Selling duplicate collections','Replacing experts with software']),
('How Teams Share Expertise','management',[('A','Teams work faster when members know who holds particular expertise, even if no individual knows every answer.'),('B','Shared templates reduce unnecessary variation in recurring tasks, but rigid templates can suppress useful exceptions.'),('C','Short post-project reviews help teams capture decisions while memories are still fresh.'),('D','Informal conversations can reveal emerging problems before they are formal enough to appear in reports.')],['Knowing who knows what','Standardisation with limits','Learning immediately after action','Early signals in informal talk','The danger of remote work','Why larger teams are always better']),
('A Short History of Public Clocks','technology',[('A','Early civic clocks signalled hours with bells because faces were difficult to read from distant streets.'),('B','As mechanical accuracy improved, clock faces became tools for coordinating markets, transport and factory shifts.'),('C','Standard time zones later reduced disagreement between local solar times as railway networks expanded.'),('D','Today public clocks are less necessary for personal timekeeping, but many remain important landmarks and symbols of civic identity.')],['Sound before visibility','Timekeeping becomes coordination','Networks demand common time','From necessity to civic symbol','The invention of wristwatches','Why clocks caused industrial decline']),
],
'matching_features':[
('Four Researchers on Sleep','health',[('Dr Vale','studies how consistent wake times affect alertness'),('Dr Rowan','examines how late caffeine changes deep sleep'),('Dr Imani','tests whether brief naps improve procedural learning'),('Dr Chen','investigates light exposure during early morning hours')]),
('Cities Testing Water Reuse','water',[('Lydon','uses treated greywater for street-tree irrigation'),('Merrow','captures roof runoff in underground public tanks'),('Eastmere','requires new offices to separate potable and non-potable pipes'),('Vallon','offers household rebates for rain barrels')]),
('Four Materials Scientists','engineering',[('Neri','develops concrete that uses crushed glass as aggregate'),('Okafor','studies coatings that slow steel corrosion'),('Basu','tests plant-fibre insulation under humid conditions'),('Lind','designs polymers that soften at lower recycling temperatures')]),
('Approaches to School Meals','education',[('Northfield','offers vegetables before students reach the main hot dishes'),('Westbridge','lets pupils pre-order lunch in the morning to reduce unused meals'),('Greenbank','uses smaller trays to discourage taking food that will not be eaten'),('Riverside','invites families to submit culturally familiar recipes')]),
],
'matching_sentence_endings':[
('Community Weather Stations','climate',[('Small weather stations can improve local forecasts','because they reveal temperature differences hidden by distant regional sensors.'),('Their data are most useful','when sensors are maintained and placed according to consistent rules.'),('Cheap instruments can still mislead','if they are positioned beside walls or exhaust vents.'),('Volunteer networks often survive longer','when participants can see how their measurements are used.')]),
('Why Some Plants Close Leaves','biology',[('Leaf closure can reduce water loss','by lowering exposed surface area during stressful conditions.'),('In some species the movement is rapid','because specialised cells change pressure within minutes.'),('The behaviour does not always indicate damage','since it may be a normal response to darkness or touch.'),('Researchers compare repeated movements','to distinguish temporary responses from long-term stress.')]),
('Shared Workshop Spaces','economics',[('Shared workshops lower entry costs for small makers','because expensive tools can be used by many members.'),('Booking systems become important','when several users need the same machine at peak times.'),('Safety training is usually compulsory','since unfamiliar equipment can cause serious injury.'),('The strongest communities often exchange knowledge','as well as physical tools and workspace.')]),
('Restoring Old Buildings','architecture',[('Historic windows are sometimes repaired rather than replaced','because original timber can remain serviceable after targeted work.'),('Energy performance can improve','when gaps are sealed and secondary glazing is added carefully.'),('Conservation plans document alterations','so future owners can understand what was changed.'),('A modern intervention may still be appropriate','if it is visually clear and does not destroy significant fabric.')]),
],
'sentence_completion':[
('Tracking Glacier Movement','earth science',[('stakes','Researchers place stakes in the ice and measure how far they move between visits.'),('satellites','Wide regional changes can also be observed with satellites.'),('summer','Movement often accelerates during summer when meltwater reaches the glacier bed.'),('bedrock','Where the ice is frozen firmly to bedrock, sliding is much more limited.')]),
('Designing Better Bus Stops','transport',[('shelter','A basic shelter protects waiting passengers from wind and rain.'),('lighting','Good lighting improves visibility after dark and helps drivers identify waiting passengers.'),('timetable','A clear timetable reduces uncertainty when real-time displays are unavailable.'),('kerb','A raised kerb can reduce the vertical step into low-floor buses.')]),
('How Paper Is Conserved','culture',[('humidity','Conservators control humidity because repeated expansion and contraction can deform paper.'),('brush','Loose surface dirt is often removed with a soft brush.'),('acid','Some damaged papers become brittle because acid accumulates in the fibres.'),('folder','After treatment, a document may be placed in an archival folder for support.')]),
('Monitoring Urban Foxes','ecology',[('camera','A motion-sensitive camera can record animals without an observer being present.'),('tracks','Soft ground may preserve tracks that reveal regular routes.'),('den','Repeated activity near one location can indicate a den.'),('night','Surveys are often most productive at night, when foxes are more active.')]),
],
'summary_completion':[
('Microclimates in Courtyards','architecture',[('shade','Deep courtyards can provide shade for much of the day.'),('stone','Thick stone walls absorb heat slowly and release it after sunset.'),('ventilation','Openings placed on opposite sides can improve ventilation.'),('water','A shallow water feature can cool nearby air through evaporation.')]),
('Why Wetlands Filter Water','environment',[('sediment','As water slows, suspended sediment settles to the bottom.'),('roots','Dense plant roots trap additional particles.'),('microbes','Microbes in wet soils transform some dissolved nutrients.'),('overflow','During extreme storms, rapid overflow can reduce the time available for treatment.')]),
('Learning from Worked Examples','education',[('solution','A worked example shows a complete solution rather than only the final answer.'),('attention','Beginners can direct more attention to why each step is taken.'),('variation','Later examples should introduce variation so learners do not memorize one surface pattern.'),('practice','Independent practice remains necessary after guided study.')]),
('The Value of Street Markets','economics',[('rent','Temporary stalls can reduce the rent required to test a small business idea.'),('footfall','A cluster of traders may increase footfall for the surrounding area.'),('weather','Outdoor markets remain vulnerable to poor weather.'),('rules','Clear rules for waste, access and food safety can reduce conflict between users.')]),
],
'note_completion':[
('Planning a Bird Survey','ecology',[('dawn','best survey period: dawn, when many species are vocal'),('route','use the same route on each visit'),('weather','weather conditions: avoid heavy rain and strong wind'),('distance','record approximate distance from observer')]),
('Preparing an Oral History Interview','history',[('consent','obtain informed consent before recording'),('questions','prepare open questions rather than a rigid script'),('silence','allow silence so the speaker has time to remember'),('backup','create a backup immediately after the interview')]),
('Reducing Meeting Overload','management',[('agenda','circulate a clear agenda in advance'),('decision','state what decision is required'),('participants','invite only necessary participants'),('notes','record concise notes with owners and deadlines')]),
('Safe Home Fermentation','food science',[('salt','measure salt accurately to favour desirable microbes'),('jar','use a clean jar with enough space for expansion'),('submerged','keep vegetables submerged below the brine'),('smell','discard a batch if an unusual rotten smell develops')]),
],
'table_completion':[
('Comparing Urban Transport Options','transport',[('tram','high passenger capacity','high','fixed rails'),('electric bus','medium passenger capacity','medium','flexible routes'),('bicycle share','low passenger capacity per vehicle','low','short individual trips'),('walking','very low infrastructure energy','low','best for short distances')]),
('Four Methods of Cooling Food','food science',[('refrigeration','1–5°C','slows microbial growth','continuous electricity'),('freezing','below 0°C','greatly slows reactions','can alter texture'),('drying','low moisture','limits microbial activity','changes flavour and texture'),('fermentation','controlled microbial activity','produces acids or alcohol','requires process control')]),
('Habitat Survey Tools','ecology',[('quadrats','plants and slow organisms','fixed small area','good for abundance estimates'),('transects','change across a gradient','line or belt','shows spatial pattern'),('camera traps','mobile animals','unattended camera','works day and night'),('acoustic recorders','vocal species','sound file','large data volume')]),
('Ways to Preserve Digital Records','information science',[('local backup','fast restoration','same-site storage','physical disaster at same site'),('off-site backup','geographic separation','remote storage','transfer time'),('cloud replication','automatic copies','distributed storage','provider dependence'),('archive format','long-term readability','standardized file structure','may lose advanced formatting')]),
],
'flow_chart_completion':[
('Community Composting Process','sustainability',[('collection','Food scraps are first gathered at neighbourhood collection points.'),('shredding','Bulky plant material is reduced by shredding before mixing.'),('aeration','The mixture is turned regularly to improve aeration.'),('curing','Finished compost is left for a final curing period before use.')]),
('Recycling Container Glass','materials',[('sorting','Bottles are separated by colour during sorting.'),('crushing','The sorted glass is broken into cullet by crushing.'),('furnace','Cullet melts with other ingredients inside a furnace.'),('moulding','Molten glass is shaped into new containers during moulding.')]),
('Connecting a Community Solar Array','energy',[('audit','Engineers begin with a site audit of roof area and electrical demand.'),('design','The results are used to create the system design.'),('permit','Plans are submitted for a permit before construction.'),('connection','After inspection, the array receives approval for grid connection.')]),
('Processing Archaeological Finds','archaeology',[('label','Each object receives a temporary label when it arrives from the excavation.'),('cleaning','Appropriate finds then undergo careful cleaning.'),('recording','Measurements and photographs are added during recording.'),('storage','The documented object finally moves to stable storage.')]),
],
'diagram_label':[
('A Simple Rain Garden','environment',[('inlet','Runoff first enters through a shallow inlet.'),('basin','Water then spreads across a planted basin.'),('soil','A layered soil mix filters the water.'),('drain','Excess water leaves through an under-drain during prolonged rain.')]),
('Inside a Solar Air Heater','energy',[('intake','Cool room air enters through the lower intake.'),('absorber','Sunlight warms a dark absorber plate.'),('channel','Air rises through a narrow channel behind the plate.'),('outlet','Warm air returns to the room through the upper outlet.')]),
('Stages of a Seed Germination Tray','biology',[('tray','Seeds are first placed in a shallow tray.'),('medium','A moist growing medium surrounds each seed.'),('shoot','The shoot emerges upward toward light.'),('root','The root grows downward and anchors the seedling.')]),
('Basic Greywater Filter','water',[('screen','A coarse screen removes hair and large debris.'),('settling tank','Water pauses in a settling tank so heavier particles sink.'),('filter bed','A sand-and-gravel filter bed removes finer material.'),('storage tank','Treated water collects in a storage tank before irrigation.')]),
],
'short_answer':[
('How Bees Regulate Hive Temperature','biology',[('What do worker bees bring into the hive on hot days?','water','Worker bees bring water into the hive on hot days.'),('What action moves air through the hive?','fanning','Groups of bees create airflow by fanning their wings.'),('Where can water be spread to increase evaporation?','comb','Small droplets may be spread across the comb.'),('What may the colony reduce during extreme heat?','foraging','The colony may reduce foraging during extreme heat.')]),
('The Logic of Park-and-Ride','transport',[('Where do drivers leave cars?','edge of the city','Drivers leave cars at sites near the edge of the city.'),('What do they use for the rest of the journey?','public transport','They continue by public transport.'),('What problem can poor bus frequency create?','long waits','Poor frequency can create long waits.'),('What is one purpose of the system?','reduce central traffic','One purpose is to reduce central traffic.')]),
('Why Clay Pots Cool Water','physics',[('What passes through tiny pores in the pot?','water','A small amount of water passes through microscopic pores.'),('What happens to this water on the outside surface?','it evaporates','It evaporates from the outside surface.'),('What does evaporation remove?','heat','Evaporation removes heat from the remaining water.'),('In what conditions is the effect weaker?','humid conditions','The effect is weaker in humid conditions.')]),
('Community Tool Libraries','society',[('What can members borrow?','tools','Members can borrow tools for short periods.'),('What cost can the system reduce?','purchase cost','The system can reduce purchase cost by avoiding ownership of rarely used equipment.'),('What must staff inspect regularly?','safety-critical tools','Staff regularly inspect safety-critical tools.'),('What can workshops teach?','safe use','Workshops can teach safe use and basic maintenance.')]),
],
'inference_author':[
('When Faster Is Not Better','technology','A software team shortened page-loading time by removing several animations, but user satisfaction rose only on slower mobile connections. On fast office networks, ratings barely changed. The author argues that performance work should focus on delays users actually experience rather than benchmark numbers alone.','The author would most likely support measuring real-user conditions before spending heavily on further speed improvements.'),
('The Limits of Perfect Attendance','education','A college praised courses with near-perfect attendance, yet one compulsory lecture showed high attendance and weak exam performance. A smaller optional workshop had lower attendance but strong gains among participants. The writer cautions that attendance is useful evidence of engagement only when interpreted alongside learning outcomes.','The writer views attendance as informative but insufficient by itself.'),
('A Forest Is More Than Tree Count','ecology','A restoration project initially reported success because tree density doubled. Later surveys found that most new trees belonged to one fast-growing species and understorey diversity had fallen. The author argues that restoration targets should include structure and species composition, not simply the number of stems.','The author would reject tree density as a complete measure of restoration success.'),
('The Problem with One Average','data literacy','A hospital reported an average waiting time of 28 minutes. Most patients were seen within 15 minutes, but a smaller group waited more than two hours. The writer notes that the mean concealed the experience of this minority and recommends reporting the distribution as well as a single average.','The writer believes a single mean can hide important variation.'),
],
}

# Helper prose builders and question constructors.
def general_paragraphs(context, change, result, caution):
    return [
      f"{context}",
      f"{change}",
      f"{result}",
      f"{caution}"
    ]

def q(id_, prompt, answer, explanation, family, options=None, distractors=None, input_type='select', category=None):
    options=options or []
    dr=dict(distractors or {})
    if input_type=='select' and options:
        family_reason={
          'multiple_choice':'This option either contradicts the stated evidence, answers a different aspect of the passage, or overstates the passage’s scope.',
          'tfng':'This label misclassifies the evidence boundary: compare whether the statement is supported, contradicted, or simply absent.',
          'ynng':'This label does not match the writer’s stated position; separate what the writer endorses from what is unmentioned or rejected.',
          'matching_information':'This paragraph does not contain the specific detail requested, even if it discusses the same broad topic.',
          'matching_headings':'This heading does not capture the controlling idea of the whole paragraph; it is absent, too narrow, or focused on a supporting detail.',
          'matching_features':'This feature is associated with a different action or detail in the passage.',
          'matching_sentence_endings':'This ending may be grammatically possible, but it does not preserve the relationship stated in the passage.',
          'inference_author':'This option contradicts the evidence, overstates the conclusion, or adds an assumption the passage does not license.'
        }.get(family,'This option is not supported by the evidence required for this question.')
        for opt in options:
            if str(opt)!=str(answer) and opt not in dr:
                dr[opt]=family_reason
    return {'id':id_,'type':input_type,'skill':'Reading','questionFamily':family,'difficulty':'7','prompt':prompt,'options':options,'correctAnswer':answer,'explanation':explanation,'distractorReasoning':dr,'errorCategory':category or family,'tags':['reading',family],'estimatedMinutes':1,'originality':'original'}

def mcq_questions(pid, spec):
    title,domain,p1,p2,p3,p4=spec
    paras=general_paragraphs(p1,p2,p3,p4)
    qs=[]
    qs.append(q(pid+'-Q1','What was the primary purpose of the initiative?',
        {'Cooling Streets':'reduce pedestrian heat exposure','Seed Library Networks':'preserve practical genetic diversity','Quiet Zones in Libraries':'reduce interruptions during demanding study','Restoring Urban Streams':'reduce the speed and concentration of runoff'}[title],
        'The passage states the project purpose directly; choose the option that paraphrases that purpose rather than a side effect.', 'multiple_choice',
        options={
        'Cooling Streets':['lower the temperature of the entire city','reduce pedestrian heat exposure','remove all glare from streets','replace every tree with reflective paving'],
        'Seed Library Networks':['replace commercial seed completely','preserve practical genetic diversity','store seed without growing it','standardise one frost-resistant variety'],
        'Quiet Zones in Libraries':['make students remain longer','reduce interruptions during demanding study','ban collaboration from the building','increase staff numbers'],
        'Restoring Urban Streams':['eliminate all flooding','reduce the speed and concentration of runoff','remove upstream pollution','deepen the concrete channel']
        }[title], category='main_idea'))
    # Q2 factual outcome
    fact_answers={
      'Cooling Streets':('Where was the greatest cooling observed?','on clear afternoons','The second paragraph says surface temperatures fell most on clear afternoons.', ['at night','during rain','on clear afternoons','only in winter']),
      'Seed Library Networks':('What does the network record?','which seeds tolerate local stresses','It records which seeds tolerate frost, drought and heavy soil.', ['only commercial prices','which seeds tolerate local stresses','the age of each farmer','national export volumes']),
      'Quiet Zones in Libraries':('What changed after the redesign?','noise complaints declined','Noise complaints declined, although total library time did not increase.', ['library visits doubled','noise complaints declined','students stopped collaborating','staff removed signs']),
      'Restoring Urban Streams':('What happened during moderate storms?','water moved more slowly','The text says water moved more slowly and temporary pools formed.', ['water bypassed the floodplain','water moved more slowly','the stream dried completely','pollution disappeared'])}
    pr,ans,ex,opts=fact_answers[title]
    qs.append(q(pid+'-Q2',pr,ans,ex,'multiple_choice',opts,category='detail'))
    caution_answers={
      'Cooling Streets':('What implementation risk is mentioned?','glare from reflective surfaces','The final paragraph warns that reflective surfaces can create glare.', ['soil erosion','glare from reflective surfaces','higher rail noise','tree disease']),
      'Seed Library Networks':('What limitation is emphasized?','stored varieties must also be grown and observed','The passage says storage alone is insufficient.', ['all seeds must be imported','stored varieties must also be grown and observed','only one farm may hold each variety','drought data are unnecessary']),
      'Quiet Zones in Libraries':('What helped the redesign work best?','consistent staff redirection of phone calls','The final paragraph identifies consistent redirection as important.', ['longer opening hours','consistent staff redirection of phone calls','removing collaborative zones','free headphones']),
      'Restoring Urban Streams':('What still limits habitat recovery?','upstream pollution','The passage explicitly says upstream pollution remains a limitation.', ['lack of concrete walls','slow water','gravel banks','upstream pollution'])}
    pr,ans,ex,opts=caution_answers[title]
    qs.append(q(pid+'-Q3',pr,ans,ex,'multiple_choice',opts,category='detail'))
    qs.append(q(pid+'-Q4','Which statement best captures the passage?',
       {'Cooling Streets':'A targeted design change reduced local heat exposure but still required careful placement.',
        'Seed Library Networks':'Seed exchange can preserve useful diversity only if varieties remain part of active farming.',
        'Quiet Zones in Libraries':'Clear behavioural zones improved concentration without increasing total library time.',
        'Restoring Urban Streams':'A more natural channel can slow runoff, but it cannot solve upstream pollution.'}[title],
       'A strong summary includes both the main intervention and its limitation or scope.', 'multiple_choice',
       options=[
        {'Cooling Streets':'A targeted design change reduced local heat exposure but still required careful placement.','Seed Library Networks':'Seed exchange can preserve useful diversity only if varieties remain part of active farming.','Quiet Zones in Libraries':'Clear behavioural zones improved concentration without increasing total library time.','Restoring Urban Streams':'A more natural channel can slow runoff, but it cannot solve upstream pollution.'}[title],
        'The intervention solved every problem associated with the topic.','The passage argues that the project should be abandoned.','The passage is mainly a historical account rather than an evaluation.'],category='main_idea'))
    return paras,qs

def tfng_questions(pid,spec):
    title,domain,a,b,c,d=spec
    paras=[a,b,c,d]
    configs={
    'Night Trains and Sleep':[
      ('The modified carriages were quieter and dimmer.','True','The first sentence says corridor lighting was dimmed and door alarms were quieter.'),
      ('The modified route was shorter than the original route.','False','The passage says total journey time was unchanged.'),
      ('The study proved sleeping on a train is better than sleeping in a hotel.','Not Given','The passage explicitly says hotel sleep was not compared.'),
      ('The operator intends to test the changes on a larger scale.','True','The final sentence states that a larger test is planned.')],
    'Museum Case Lighting':[
      ('Filtered LED lamps were introduced to reduce ultraviolet exposure.','True','The first sentence states this directly.'),
      ('Visitors spent substantially longer at the displays after the lighting change.','False','Visitor time was approximately unchanged.'),
      ('Visitors preferred warm-coloured LEDs.','Not Given','The study did not measure preference for warm versus cool light.'),
      ('Slowing colour fading was a conservation goal.','True','The passage says conservators selected the lamps to slow fading.')],
    'Rooftop Pollinator Beds':[
      ('The rooftop beds used native flowering species.','True','This is stated in the opening sentence.'),
      ('Bee visits were highest where flowers were available for only a short summer period.','False','Visits were highest where flowering extended from spring through early autumn.'),
      ('Butterfly numbers increased on all three roofs.','Not Given','No butterfly data were collected.'),
      ('The project was not presented as a substitute for ground-level habitat.','True','The third sentence states this explicitly.')],
    'Compressed Workweeks':[
      ('Weekly paid hours were kept the same during the pilot.','True','The first sentence says weekly paid hours were unchanged.'),
      ('Average call resolution became slower.','False','Resolution time remained stable.'),
      ('Most employees used the extra day for childcare.','Not Given','The company has not reported how the day was used.'),
      ('Staffing levels were not reduced during the experiment.','True','Managers did not reduce staffing.')]
    }
    qs=[q(f'{pid}-Q{i+1}',s,ans,ex,'tfng',['True','False','Not Given'],category='evidence_boundary') for i,(s,ans,ex) in enumerate(configs[title])]
    return paras,qs

def ynng_questions(pid,spec):
    title,domain,*paras=spec
    configs={
    'The Case for Smaller Parks':[
      ('A network of small parks can be especially useful in dense neighbourhoods.','Yes','This is the writer’s central position.'),
      ('Large parks have no value for cities.','No','The writer explicitly accepts their value for sports and events.'),
      ('Residents prefer small parks because they are safer at night.','Not Given','Safety preference is not discussed.'),
      ('Ease of fitting short visits into daily life matters.','Yes','The writer uses this as a reason for daily access.')],
    'Repairable Electronics':[
      ('Devices should allow common components to be replaced with ordinary tools.','Yes','The author supports repairable design.'),
      ('Every component should be serviced by consumers at home.','No','The author says safety-critical parts may require specialists.'),
      ('Governments should ban sealed devices.','Not Given','The article gives no opinion on a ban.'),
      ('Repairability can matter even when newer devices use energy more efficiently.','Yes','The author explicitly makes this argument.')],
    'Teaching Statistical Uncertainty':[
      ('Science education should teach uncertainty alongside results.','Yes','This is the writer’s stated position.'),
      ('Basic arithmetic should be removed to make room for uncertainty.','No','The writer specifically does not propose this.'),
      ('Students enjoy uncertainty exercises more than conventional exercises.','Not Given','Student preference is not stated.'),
      ('Teaching uncertainty can reduce false impressions of perfect precision.','Yes','This is the writer’s reasoning.')],
    'Rewilding City Edges':[
      ('Selected grasslands should sometimes be cut less frequently.','Yes','The author favours longer growth intervals in selected areas.'),
      ('All municipal lawns should follow exactly the same management plan.','No','The writer rejects a one-size-fits-all approach.'),
      ('Longer grass is cheaper to maintain in every city.','Not Given','Cost is not discussed.'),
      ('Road-junction sightlines still need active management.','Yes','The author accepts this constraint.')]
    }
    qs=[q(f'{pid}-Q{i+1}',s,ans,ex,'ynng',['Yes','No','Not Given'],category='writer_position') for i,(s,ans,ex) in enumerate(configs[title])]
    return paras,qs

def matching_info_questions(pid,spec):
    title,domain,parts=spec
    paras=[f'{label}. {text}' for label,text in parts]
    prompts=[]
    for i,(label,text) in enumerate(parts):
        if title=='Four Ways to Store Heat': asks=['Which paragraph mentions dependence on geology?','Which paragraph describes melting as part of heat storage?','Which paragraph refers to extremely high operating temperatures?','Which paragraph says large volume can complicate installation in older buildings?']; answers=['D','B','C','A']
        elif title=='Urban Tree Strategies': asks=['Which paragraph mentions underground services limiting roots?','Which paragraph describes dense mixed planting on a small site?','Which paragraph connects habitat while stabilising banks?','Which paragraph mentions maintenance access difficulties?']; answers=['A','C','D','B']
        elif title=='Methods of Language Learning': asks=['Which paragraph emphasizes producing an answer from memory?','Which paragraph focuses on repeated vocabulary exposure through reading?','Which paragraph involves repeating speech with minimal delay?','Which paragraph notes that feedback quality varies with the partner?']; answers=['B','A','C','D']
        else: asks=['Which paragraph describes changing prices near a sell-by date?','Which paragraph concerns preventing over-ordering before stock reaches shelves?','Which paragraph reduces waste by changing the default serving size?','Which paragraph recovers energy from waste that already exists?']; answers=['B','D','A','C']
        break
    options=['A','B','C','D']
    qs=[q(f'{pid}-Q{i+1}',asks[i],answers[i],f'Paragraph {answers[i]} contains the exact requested detail; match the specific information, not merely the broad topic.','matching_information',options,category='scan_specific_detail') for i in range(4)]
    return paras,qs

def headings_questions(pid,spec):
    title,domain,parts,heads=spec
    paras=[f'{label}. {text}' for label,text in parts]
    correct=heads[:4]
    qs=[q(f'{pid}-Q{i+1}',f'Choose the best heading for paragraph {parts[i][0]}.',correct[i],f'Paragraph {parts[i][0]} is mainly about {correct[i].lower()}; examples in the paragraph support that central purpose.','matching_headings',heads,category='main_idea') for i in range(4)]
    return paras,qs

def features_questions(pid,spec):
    title,domain,features=spec
    paras=[f'{name}: {detail}.' for name,detail in features]
    # Ask by detail, answer feature name.
    qs=[]
    for i,(name,detail) in enumerate(features):
        phrase=detail[0].upper()+detail[1:]
        qs.append(q(f'{pid}-Q{i+1}',phrase+' — who or which place is associated with this?',name,f'The passage assigns this feature specifically to {name}.','matching_features',[x[0] for x in features],category='feature_attribution'))
    return paras,qs

def endings_questions(pid,spec):
    title,domain,pairs=spec
    paras=[f'{start} {ending}' for start,ending in pairs]
    endings=[e for _,e in pairs]
    # Scramble deterministic order.
    options=[endings[2],endings[0],endings[3],endings[1]]
    qs=[q(f'{pid}-Q{i+1}',start+' …',ending,'The selected ending preserves both the grammar and the causal/qualifying meaning stated in the passage.','matching_sentence_endings',options,category='clause_meaning') for i,(start,ending) in enumerate(pairs)]
    return paras,qs

def completion_questions(pid,spec,family,style):
    title,domain,pairs=spec
    paras=[sentence for answer,sentence in pairs]
    qs=[]
    for i,(answer,sentence) in enumerate(pairs):
        # Replace first exact answer occurrence with blank in a paraphrased instruction where possible.
        if family=='sentence_completion':
            prompt={
              'Tracking Glacier Movement':['Researchers place ______ in ice to measure movement.','Regional glacier changes can be observed with ______.','Glacier movement often becomes faster during ______.','Sliding is limited where ice is fixed to ______.'],
              'Designing Better Bus Stops':['A ______ protects passengers from rain and wind.','Good ______ makes waiting passengers easier to see after dark.','A clear ______ reduces uncertainty without a live display.','A raised ______ reduces the step into a low-floor bus.'],
              'How Paper Is Conserved':['Controlling ______ reduces repeated expansion and contraction.','Loose dirt may be removed with a soft ______.','Accumulated ______ can make some paper brittle.','A treated document may be stored in an archival ______.'],
              'Monitoring Urban Foxes':['A motion-sensitive ______ records animals without an observer.','Soft ground can preserve ______ that show regular routes.','Repeated use of one location may indicate a ______.','Surveys are often most productive at ______.']
            }[title][i]
        elif family=='summary_completion':
            prompt=f'Summary gap {i+1}: {sentence.replace(answer,"______",1)}'
        elif family=='note_completion':
            prompt=f'Complete the note: {sentence.replace(answer,"______",1)}'
        elif family=='diagram_label':
            prompt=f'Label stage {i+1}: {sentence.replace(answer,"______",1)}'
        elif family=='flow_chart_completion':
            prompt=f'Flow step {i+1}: {sentence.replace(answer,"______",1)}'
        else:
            prompt=f'Complete: {sentence.replace(answer,"______",1)}'
        qs.append(q(f'{pid}-Q{i+1}',prompt,answer,f'The exact answer “{answer}” appears in the passage and fits the grammar and meaning of the gap.','%s'%family,[],input_type='text',category='completion_precision'))
    return paras,qs

def table_questions(pid,spec):
    title,domain,rowspec=spec
    paras=[f'{name}: {a}; {b}; {c}.' for name,a,b,c in rowspec]
    # Four questions pull one cell each.
    qs=[]
    for i,(name,a,b,c) in enumerate(rowspec):
        attrs=[a,b,c]
        answer=attrs[i%3]
        labels=['first characteristic','second characteristic','third characteristic']
        qs.append(q(f'{pid}-Q{i+1}',f'For {name}, what is the {labels[i%3]}?',answer,f'The {name} row states “{answer}” as that characteristic.','table_completion',[],input_type='text',category='table_relationship'))
    return paras,qs

def short_questions(pid,spec):
    title,domain,items=spec
    paras=[sentence for prompt,answer,sentence in items]
    qs=[q(f'{pid}-Q{i+1}',prompt,answer,f'The passage states: {sentence}','short_answer',[],input_type='text',category='precise_retrieval') for i,(prompt,answer,sentence) in enumerate(items)]
    return paras,qs

def inference_questions(pid,spec):
    title,domain,text,claim=spec
    # Divide supplied text into 3 paragraphs/sentences.
    paras=[s.strip()+'.' for s in re.split(r'(?<=\.)\s+',text) if s.strip()]
    if title=='When Faster Is Not Better':
        items=[
        ('What does the comparison between mobile and office networks imply?','Performance improvements matter most where users actually experience delay',['All users value animation equally.','Performance improvements matter most where users actually experience delay.','Office networks should be deliberately slowed.','Benchmark scores always predict satisfaction.']),
        ('What is the author’s attitude toward benchmark numbers?','They are useful only when connected to real experience',['They should replace user research.','They are useful only when connected to real experience.','They are always misleading.','They matter more than network conditions.']),
        ('Which action would the author most likely support?','measuring real-user conditions before further optimization',['removing every animation immediately','measuring real-user conditions before further optimization','ignoring slow mobile users','optimizing only for office networks']),
        ('What broader principle is suggested?','prioritize problems by experienced impact rather than abstract metrics',['prioritize problems by experienced impact rather than abstract metrics','always maximize one technical metric','user satisfaction cannot be measured','visual design never affects performance'])]
    elif title=='The Limits of Perfect Attendance':
        items=[
        ('What can be inferred from the compulsory lecture?','Attendance alone did not guarantee strong learning',['High attendance always produces high scores.','Attendance alone did not guarantee strong learning.','Optional workshops are ineffective.','Compulsory courses should be removed.']),
        ('How does the writer treat attendance data?','as one indicator that needs outcome data',['as a complete measure of learning','as one indicator that needs outcome data','as irrelevant in all cases','as a substitute for exams']),
        ('Why mention the smaller workshop?','to show that lower attendance can coexist with strong gains',['to prove workshops should be compulsory','to show that lower attendance can coexist with strong gains','to criticize small classes','to claim attendance cannot be recorded']),
        ('Which statement best reflects the writer’s position?','Engagement metrics require context',['Engagement metrics require context','Attendance should never be measured','Exam scores are the only useful evidence','Optional classes always outperform lectures'])]
    elif title=='A Forest Is More Than Tree Count':
        items=[
        ('Why did the initial success claim become questionable?','tree numbers increased while diversity and structure worsened',['the project planted no trees','tree numbers increased while diversity and structure worsened','all species increased equally','surveys stopped too early']),
        ('What does the author imply about restoration metrics?','they should measure ecological quality as well as quantity',['they should count stems only','they should measure ecological quality as well as quantity','they should ignore species composition','they should focus only on cost']),
        ('What role does the fast-growing species play in the argument?','it shows that a numerical gain can hide reduced diversity',['it proves fast-growing species are always harmful','it shows that a numerical gain can hide reduced diversity','it demonstrates understorey recovery','it explains why tree density fell']),
        ('Which target would the author most likely prefer?','a mix of density, structure and species-composition measures',['one tree-count target','a mix of density, structure and species-composition measures','only canopy height','only planting speed'])]
    else:
        items=[
        ('Why was the reported average potentially misleading?','a minority experienced much longer waits',['most patients waited exactly 28 minutes','a minority experienced much longer waits','the hospital recorded no waiting times','the mean was calculated incorrectly']),
        ('What does the author recommend?','reporting the distribution alongside the mean',['removing all averages','reporting the distribution alongside the mean','reporting only the longest wait','using the median without any other information']),
        ('What is implied about summary statistics?','they can conceal important subgroups',['they always provide complete information','they can conceal important subgroups','they are useless in medicine','they should never be compared']),
        ('Which statement best matches the author’s attitude?','single-number summaries need context',['single-number summaries need context','averages are mathematically invalid','waiting times cannot be compared','long waits are inevitable'])]
    qs=[q(f'{pid}-Q{i+1}',pr,ans,ex if (ex:='The answer follows from the evidence and the author’s stated caution without extending beyond what the passage supports.') else '', 'inference_author',opts,category='inference_boundary') for i,(pr,ans,opts) in enumerate(items)]
    return paras,qs

# Build Reading modules: 8 foundations + the current official family set plus dedicated inference/author-position training.
foundations=[
 ('READ-F01','IELTS Reading Structure','Understand 60-minute test logic, evidence discipline and question sequencing.','Структура тесту та дисципліна роботи з доказами.'),
 ('READ-F02','Skimming for Structure','Identify topic, purpose and paragraph function before chasing details.','Швидко визначати структуру та функцію абзаців.'),
 ('READ-F03','Scanning for Evidence','Locate names, dates, technical terms and paraphrased anchors efficiently.','Шукати конкретні докази, а не перечитувати весь текст.'),
 ('READ-F04','Paraphrase Recognition','Recognize meaning changes across synonyms and grammatical reformulation.','Розпізнавати перефразування, а не лише однакові слова.'),
 ('READ-F05','Reference Words','Track pronouns, demonstratives and lexical references across sentences.','Відстежувати, до чого належать it, they, this, these та інші посилання.'),
 ('READ-F06','Vocabulary from Context','Infer approximate meaning without stopping the reading process.','Виводити значення слова з контексту.'),
 ('READ-F07','Evidence Location','Separate the exact evidence sentence from surrounding background.','Відокремлювати доказ від фонової інформації.'),
 ('READ-F08','Inference Boundaries','Infer what follows while refusing assumptions not licensed by the text.','Робити обережні висновки без додавання власних знань.')
]
modules=[]
foundation_lessons={
 'READ-F01':['Academic Reading allows 60 minutes for 3 sections and 40 questions; official full-test texts total roughly 2,150–2,750 words.','Each correct answer earns one raw mark. Practice therefore needs both accuracy and time control.','Treat every answer as an evidence claim: the passage, not outside knowledge, decides the answer.'],
 'READ-F02':['Read the title and first/last lines to predict structure before reading sentence by sentence.','Give each paragraph a five-to-eight-word mental label; this makes later evidence searches faster.','Skimming is not careless reading. It is reading selectively for organisation and purpose.'],
 'READ-F03':['Scan for stable anchors such as names, dates, unusual nouns, units and technical terms.','Expect the question to paraphrase the passage, so scan for semantic neighbours rather than one exact keyword.','Once you locate the likely area, slow down and read enough context to verify the answer.'],
 'READ-F04':['IELTS frequently changes word class: decide → decision, consume → consumption, stable → stability.','It also changes grammatical shape: because prices fell → due to lower prices.','Ask whether two phrases preserve the same relationship, not merely whether they share vocabulary.'],
 'READ-F05':['A reference word such as this, these, they or former compresses earlier information.','Trace the reference backward until the sentence becomes unambiguous.','If two possible nouns fit grammatically, use meaning and number agreement to choose the correct referent.'],
 'READ-F06':['Infer only the amount of meaning needed for the question. You rarely need a perfect dictionary definition.','Use nearby contrast, examples, cause/effect and word parts as clues.','Keep moving if the unknown word is not carrying the question’s key meaning.'],
 'READ-F07':['Separate evidence from commentary around it. One sentence may state a result while the next limits its scope.','For difficult questions, identify the smallest passage span that proves or disproves the claim.','A highlighted keyword is not evidence until the surrounding proposition matches the question.'],
 'READ-F08':['Inference is a controlled step beyond explicit wording, not permission to invent a likely story.','Prefer the weakest conclusion fully supported by the text over a stronger but speculative claim.','Author-position questions often turn on qualification words such as may, generally, only, however and although.']}
for id_,title,obj,ua in foundations:
    modules.append({'id':id_,'title':title,'skill':'Reading','subskill':'Foundation','difficulty':'foundation','objectives':[obj],'lesson':foundation_lessons[id_],'workedExamples':[],'exercises':[],'masteryCheck':[],'relatedModules':[],'prerequisites':[],'errorCategories':['reading_strategy'],'vocabularyTags':[],'uaSupport':ua,'kind':'foundation'})
for fam,(title,skill,trap,ua_skill) in FAMILY_META.items():
    mid='READ-'+fam.upper().replace('_','-')
    modules.append({'id':mid,'title':title,'skill':'Reading','subskill':fam,'difficulty':'7','objectives':[f'Use {title} strategy accurately under IELTS-style conditions.',f'Explain why the correct answer is supported and why common distractors fail.'],'lesson':[f'This family primarily tests {skill.lower()}.',f'Core strategy: identify the evidence target before comparing answer choices.',f'Common trap: {trap}'],'workedExamples':[{'prompt':'Evidence first','analysis':'Locate or summarize the relevant passage idea before committing to an option.'}],'exercises':[],'masteryCheck':[],'relatedModules':['READ-F03','READ-F04','READ-F07','READ-F08'],'prerequisites':['READ-F01'],'errorCategories':[fam],'vocabularyTags':['reading'],'uaSupport':f'Цей тип завдань перевіряє {ua_skill}. Не обирайте відповідь лише через знайоме слово.','strategySteps':FAMILY_GUIDANCE[fam]['steps'],'workedExample':FAMILY_GUIDANCE[fam]['worked'],'challenge':FAMILY_GUIDANCE[fam]['challenge'],'kind':'question_family'})

passages=[]
family_counter={k:0 for k in FAMILY_META}
for fam,specs in TOPICS.items():
    for idx,spec in enumerate(specs):
        mode,label,diff=MODES[idx]
        family_counter[fam]+=1
        pid=f'READ-{fam.upper().replace("_","-")}-P{idx+1:02d}'
        if fam=='multiple_choice': paras,qs=mcq_questions(pid,spec)
        elif fam=='tfng': paras,qs=tfng_questions(pid,spec)
        elif fam=='ynng': paras,qs=ynng_questions(pid,spec)
        elif fam=='matching_information': paras,qs=matching_info_questions(pid,spec)
        elif fam=='matching_headings': paras,qs=headings_questions(pid,spec)
        elif fam=='matching_features': paras,qs=features_questions(pid,spec)
        elif fam=='matching_sentence_endings': paras,qs=endings_questions(pid,spec)
        elif fam in {'sentence_completion','summary_completion','note_completion','flow_chart_completion','diagram_label'}: paras,qs=completion_questions(pid,spec,fam,label)
        elif fam=='table_completion': paras,qs=table_questions(pid,spec)
        elif fam=='short_answer': paras,qs=short_questions(pid,spec)
        elif fam=='inference_author': paras,qs=inference_questions(pid,spec)
        else: raise ValueError(fam)
        title=spec[0]; domain=spec[1]
        for qx in qs:
            qx['difficulty']=diff
            qx['estimatedMinutes']=1.2 if mode in {'timed','mastery'} else 1.5
        passage={'id':pid,'title':title,'domain':domain,'family':fam,'moduleId':'READ-'+fam.upper().replace('_','-'),'mode':mode,'modeLabel':label,'difficulty':diff,'paragraphs':paras,'questions':qs,'estimatedMinutes':8 if mode in {'timed','mastery'} else 10,'originality':'original','sourceNote':'Original synthetic IELTS-style training text created for this application.'}
        passages.append(passage)
        # Wire passage/exercise ids into module.
        mod=next(m for m in modules if m['id']==passage['moduleId'])
        mod['exercises'].append(pid)
        if mode=='mastery': mod['masteryCheck'].extend([q['id'] for q in qs])

# Inventory.
questions=[q for p in passages for q in p['questions']]
meta={'passageCount':len(passages),'questionCount':len(questions),'familyCount':len(FAMILY_META),'moduleCount':len(modules),'foundationModuleCount':len(foundations),'questionFamilyModuleCount':len(FAMILY_META),'families':{f:sum(1 for p in passages if p['family']==f) for f in FAMILY_META},'questionsByFamily':{f:sum(len(p['questions']) for p in passages if p['family']==f) for f in FAMILY_META},'originality':'All passages and scored questions are original training content.'}

payload={'meta':meta,'familyMeta':{k:{'title':v[0],'skill':v[1],'trap':v[2],'ua':v[3]} for k,v in FAMILY_META.items()},'modules':modules,'passages':passages}
out=ROOT/'web'/'reading_data.js'
out.write_text('window.READING_DATA='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
(ROOT/'docs'/'reading_inventory.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,indent=2))
