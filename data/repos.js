window.REPO_DATA = {
  profile: "https://github.com/dddzzz123-dz",
  web: [
    {name:"cityu-msaib-course-board", title:"模拟选课网站", description:"集合选课时需要查找的课程信息、课程评价和个人体验，支持筛选课程、快速排课并导出课表。", preview:"assets/previews/cityu-course-board.png", repo:"https://github.com/dddzzz123-dz/cityu-msaib-course-board", live:"https://dddzzz123-dz.github.io/cityu-msaib-course-board/"},
    {name:"rental-maps", title:"地铁通勤租房", description:"用于筛选房源、比较租金与位置，并查看从房源到地铁站的通勤路线。", children:[
      {name:"luohu-rental-map", title:"罗湖通勤租房地图", description:"以终点为中心，沿地铁线路向外探索房源。", preview:"assets/previews/luohu-rental-map.png", live:"https://dddzzz123-dz.github.io/luohu-rental-map/"},
      {name:"beishatan-rental-map", title:"北沙滩租房地图", description:"以北沙滩站为中心，向四周发散查找房源。", preview:"assets/previews/beishatan-rental-map.png", live:"https://dddzzz123-dz.github.io/beishatan-rental-map/"}
    ]}
  ],
  skills: [
    {name:"metro-rental-research-skill", title:"地铁通勤租房研究", description:"把找房要求整理成站点、路线、小区、租金、库存、图片和优先级，再输出可以比较的研究结果。罗湖和北沙滩两个网页都是这个 Skill 的应用结果。", repo:"https://github.com/dddzzz123-dz/metro-rental-research-skill", prompt:"请从 https://github.com/dddzzz123-dz/metro-rental-research-skill 拉取这个 Skill，读取 SKILL.md，并在当前任务中按其中说明执行。"},
    {name:"codex-dsh-bridge", title:"Codex DSH Bridge", description:"连接 Codex 与 DeepSeek Harness 的本地协作工具。", repo:"https://github.com/dddzzz123-dz/codex-dsh-bridge", prompt:"请从 https://github.com/dddzzz123-dz/codex-dsh-bridge 拉取这个 Skill，读取 SKILL.md，并在当前任务中按其中说明执行。"}
  ],
  plugins: [
    {name:"pinterest-collection-console", title:"Pinterest 采集", kind:"Chrome 插件", description:"关键词采集、复核与 ZIP 导出。", download:"https://github.com/dddzzz123-dz/pinterest-collection-console/archive/refs/heads/main.zip"},
    {name:"huaban-downloader", title:"花瓣采集", kind:"Chrome 插件", description:"持久队列、去重、断点续采。", download:"https://github.com/dddzzz123-dz/huaban-downloader/archive/refs/heads/main.zip"},
    {name:"zcool-downloader", title:"站酷采集", kind:"Chrome 插件", description:"列表与详情页图片采集。", download:"https://github.com/dddzzz123-dz/zcool-downloader/archive/refs/heads/main.zip"},
    {name:"wikihow-clipper", title:"WikiHow Clipper", kind:"Chrome 插件", description:"文章转 Markdown，支持批量导出。", download:"https://github.com/dddzzz123-dz/wikihow-clipper/archive/refs/heads/main.zip"},
    {name:"dsh-plugins", title:"DeepSeek Harness", kind:"DSH 插件", description:"图片输入和语音输入，合并展示。", children:[
      {title:"图片输入", download:"https://github.com/dddzzz123-dz/dsh-read-image-plugin/archive/refs/heads/main.zip"},
      {title:"语音输入", download:"https://github.com/dddzzz123-dz/dsh-voice-input-plugin/archive/refs/heads/main.zip"}
    ]}
  ]
};
