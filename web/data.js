
window.APP_DATA = {
  masteryLevels:[
    {level:0,en:"Not Assessed",ua:"Не оцінено"},
    {level:1,en:"Introduced",ua:"Ознайомлення"},
    {level:2,en:"Guided",ua:"З підтримкою"},
    {level:3,en:"Independent",ua:"Самостійно"},
    {level:4,en:"Timed",ua:"У часі"},
    {level:5,en:"Mastered",ua:"Опановано"}
  ],
  secondaryNav:[
    ["start","Start Here"],["reading","Reading Lab"],["listening","Listening Lab"],
    ["task1","Writing Task 1"],["task2","Writing Task 2"],["speaking","Speaking Lab"],
    ["grammar","Grammar Clinic"],["paraphrase","Paraphrasing"],["pronunciation","Pronunciation"],
    ["errors","Error Log"],["review","Review Queue"],["search","Global Search"],
    ["settings","Settings / Backup"],["components","Component Lab"]
  ],
  modules:[
    {id:"ORI-001",skill:"Orientation",title:"IELTS Academic overview",difficulty:"foundation",minutes:8},
    {id:"READ-TFNG",skill:"Reading",title:"True / False / Not Given",difficulty:"7",minutes:18},
    {id:"READ-HEAD",skill:"Reading",title:"Matching Headings",difficulty:"7",minutes:20},
    {id:"W1-OVERVIEW",skill:"Writing Task 1",title:"Selecting overview features",difficulty:"7",minutes:18},
    {id:"W2-ARG",skill:"Writing Task 2",title:"Claim → Explanation → Example → Implication",difficulty:"7",minutes:22},
    {id:"GRAM-ART",skill:"Grammar",title:"Articles for Ukrainian speakers",difficulty:"7",minutes:14},
    {id:"SPEAK-P2",skill:"Speaking",title:"Part 2 long turn",difficulty:"7",minutes:15},
    {id:"LIST-DIST",skill:"Listening",title:"Distractors and corrections",difficulty:"7",minutes:16}
  ],
  seedReviews:[
    {id:"REV-ART",type:"Grammar",title:"Article omission review",priority:5,module:"GRAM-ART"},
    {id:"REV-W1",type:"Writing Task 1",title:"Overview feature selection",priority:4,module:"W1-OVERVIEW"}
  ],
  resources:[
    {title:"IELTS Academic sample questions",kind:"Official IELTS",url:"https://www.ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test"},
    {title:"IELTS Academic Writing format",kind:"Official IELTS",url:"https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-writing"},
    {title:"IELTS Academic Speaking format",kind:"Official IELTS",url:"https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-speaking"},
    {title:"British Council Ukraine IELTS preparation",kind:"Ukraine",url:"https://www.britishcouncil.org.ua/exam/ielts/prepare"},
    {title:"IDP IELTS Academic preparation",kind:"Official partner",url:"https://ielts.idp.com/about/academic-preparation"}
  ]
};
