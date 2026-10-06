const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const p=await b.newPage({viewport:{width:2560,height:1440}});
await p.goto('file://'+process.cwd()+'/wallpaper.html?static=1');await p.screenshot({path:'wallpaper.png'});await b.close()})();
