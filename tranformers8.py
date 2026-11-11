#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tranformer8.py - AK Electrical: หน้าหม้อแปลงไฟฟ้า 3 เฟส (ไฟล์เดียวจบ)

ไฟล์นี้เป็นทั้งเว็บเซิร์ฟเวอร์และตัวหน้าเว็บ ไม่ต้องมีไฟล์ .html แยก

วิธีใช้:
  python tranformer8.py                 เปิดเซิร์ฟเวอร์ที่ http://localhost:8000 แล้วเปิดเบราว์เซอร์ให้
  python tranformer8.py --port 9000     เปลี่ยนพอร์ต
  python tranformer8.py --host 0.0.0.0  ให้เครื่องอื่นในเครือข่ายเดียวกันเปิดดูได้
  python tranformer8.py --no-open       ไม่เปิดเบราว์เซอร์อัตโนมัติ
  python tranformer8.py --export        เขียนเป็นไฟล์ transformers.html (ถ้าต้องการไฟล์ HTML)

หยุดเซิร์ฟเวอร์ด้วย Ctrl+C
"""
import os
import pathlib
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ลิงก์ "← กลับเว็บหลัก" ชี้ไปที่ไหน (แก้ตรงนี้ได้ เช่น "https://www.ตัวอย่าง.com/")
MAIN_SITE_URL = "index.html"

HTML = r'''<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>AK Electrical – หม้อแปลงไฟฟ้า 3 เฟส</title>
<style>
:root{color-scheme:dark;--navy:#090909;--main:#141414;--hi:#FF3131;--mute:#b9c8dc;--line:rgba(255,49,49,.28);box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
html{scroll-padding-top:env(safe-area-inset-top,0px);scroll-behavior:smooth}
*{box-sizing:border-box}
body{margin:0;color:#fff;font-family:"Prompt","Noto Sans Thai",system-ui,sans-serif;line-height:1.7;min-height:100vh;background:radial-gradient(ellipse 70% 50% at 10% 0%,rgba(255,49,49,.22),transparent 70%),linear-gradient(135deg,#000,var(--navy) 50%,var(--main)) fixed}
body::before{content:"";position:fixed;z-index:0;inset:0;pointer-events:none;opacity:.28;background-image:linear-gradient(rgba(255,49,49,.14) 1px,transparent 1px),linear-gradient(90deg,rgba(255,49,49,.14) 1px,transparent 1px);background-size:48px 48px}
.embers{position:fixed;z-index:1;inset:0;overflow:hidden;pointer-events:none;opacity:0;transition:opacity 1s ease}
.is-home .embers{opacity:.9}
.embers span{position:absolute;bottom:-12vh;left:var(--x);width:var(--size);height:calc(var(--size)*1.5);border-radius:50% 50% 45% 0;
  background:linear-gradient(160deg,#fff1ad 0%,#ff9b35 42%,#ff3131 100%);box-shadow:0 0 7px 2px rgba(255,107,36,.55),0 0 18px 4px rgba(255,49,49,.2);
  opacity:0;transform:rotate(45deg);animation:ember-rise var(--duration) linear var(--delay) infinite}
@keyframes ember-rise{0%{opacity:0;transform:translate3d(0,0,0) rotate(45deg) scale(.55)}
  12%{opacity:.9}72%{opacity:.72}100%{opacity:0;transform:translate3d(var(--drift),-115vh,0) rotate(45deg) scale(.15)}}
body::after{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);background:#000;z-index:11}
.top{flex-wrap:wrap;position:sticky;top:env(safe-area-inset-top,0px);z-index:10;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 22px;background:rgba(0,0,0,.65);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.logo{font-weight:700;letter-spacing:.5px;text-decoration:none;color:#fff}.logo span,.hi{color:var(--hi)}
.top nav{display:flex;gap:8px;flex-wrap:wrap}
.site{color:var(--mute);font-size:14px;text-decoration:none;white-space:nowrap}.site:hover{color:#fff}
.top nav a{color:var(--mute);text-decoration:none;font-size:14px;padding:4px 12px;border-radius:99px;border:1px solid transparent}
.top nav a:hover,.top nav a.on{color:#fff;border-color:var(--hi);background:rgba(255,49,49,.15)}
.wrap{position:relative;z-index:2;max-width:1040px;margin:0 auto;padding:0 20px 80px}
.hero{position:relative;overflow:hidden;margin:22px 0 10px;padding:44px 34px;border-radius:22px;border:1px solid var(--line);background:linear-gradient(135deg,rgba(20,20,20,.94),rgba(0,0,0,.88))}
.hero.home{box-shadow:0 0 20px rgba(255,49,49,.06),inset 0 0 15px rgba(255,49,49,.025)}
.hero::after{content:"";position:absolute;left:0;right:0;height:2px;top:0;background:linear-gradient(90deg,transparent,var(--hi),transparent);animation:scan 4s linear infinite;opacity:.7}
@keyframes scan{to{top:100%}}
.orb{position:absolute;right:-80px;top:-80px;width:340px;height:340px;border-radius:50%;background:radial-gradient(circle,rgba(255,49,49,.45),transparent 65%);animation:pulse 4s ease-in-out infinite}
@keyframes pulse{50%{transform:scale(1.15);opacity:.7}}
.hero svg{position:absolute;left:0;top:0;height:100%;width:42%;opacity:.9;-webkit-mask-image:linear-gradient(90deg,#000 55%,transparent);mask-image:linear-gradient(90deg,#000 55%,transparent)}
.hero .in{position:relative}.hero.home .in{margin-left:44%}
.eyebrow{color:var(--hi);font-size:13px;letter-spacing:2px;text-transform:uppercase}
.cyber-title{color:#FF6B24;font-size:13px;font-weight:900;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px}
h1{font-size:clamp(28px,4.4vw,48px);margin:6px 0 8px;line-height:1.2}
.big{font-size:clamp(64px,13vw,128px);font-weight:800;line-height:1;background:linear-gradient(180deg,#fff,var(--hi));-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 24px rgba(255,49,49,.45))}
.big span{font-size:.3em;-webkit-text-fill-color:var(--hi)}
p{color:var(--mute)}
.cyber-description{font-size:15px;line-height:1.8}
.cyber-line{height:2px;margin:18px 0;background:linear-gradient(90deg,#FF3131,#FF6B24,transparent)}
.system-status{color:#3ddc84;font-size:12px;font-weight:800;letter-spacing:2px}
.system-status span{display:inline-block;margin-right:6px;animation:statusPulse 1.8s ease-in-out infinite}
@keyframes statusPulse{50%{opacity:.45}}
.cyber-pulse{animation:cyberPulse 3s ease-in-out infinite}
@keyframes cyberPulse{0%,100%{box-shadow:0 0 8px rgba(255,49,49,.08)}50%{box-shadow:0 0 22px rgba(255,49,49,.2)}}
.chips{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}
.chip{padding:8px 16px;border-radius:99px;border:1px solid var(--line);background:rgba(255,49,49,.1);font-size:14px}.chip b{color:var(--hi)}
section{margin-top:38px}
h2{display:flex;align-items:center;gap:12px;font-size:21px;margin:0 0 16px}
h2 i{font-style:normal;display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:var(--hi);color:#000;font-weight:700;box-shadow:0 0 18px rgba(255,49,49,.6)}
h2::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
.boxes,.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px}
.cards{grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;margin-top:22px}
.box,.card{display:block;text-decoration:none;color:inherit;padding:18px 20px;border-radius:14px;border:1.5px solid var(--line);background:linear-gradient(160deg,rgba(20,20,20,.92),rgba(0,0,0,.8));transition:transform .2s,border-color .2s,box-shadow .2s;cursor:pointer}
.box:hover,.box:active,.card:hover{transform:translateY(-8px);border-color:var(--hi);box-shadow:0 14px 30px rgba(255,49,49,.28)}
.box small,.card small{display:block;color:var(--mute);font-size:14px}
.box b{font-size:21px;font-weight:600}
.card .kva{font-size:44px;font-weight:800;color:var(--hi)}
.card .go{display:inline-block;margin-top:10px;color:var(--hi);font-weight:600}
.bar{margin:6px 0 2px;height:8px;border-radius:9px;background:rgba(255,255,255,.08);overflow:hidden}.bar i{display:block;height:100%;border-radius:9px;background:linear-gradient(90deg,#b31524,var(--hi))}
.meter{margin-top:14px;padding:18px 20px;border-radius:14px;border:1px solid var(--line);background:rgba(0,0,0,.5)}
.meter div.row{display:flex;justify-content:space-between;font-size:15px}.meter .bar{height:12px;margin:6px 0 14px}
.steps{list-style:none;margin:0;padding:0;counter-reset:s}
.steps li{counter-increment:s;position:relative;padding:12px 16px 12px 58px;margin-bottom:10px;border-radius:12px;border:1px solid var(--line);background:rgba(0,0,0,.45);color:var(--mute)}
.steps li::before{content:counter(s);position:absolute;left:14px;top:50%;transform:translateY(-50%);width:30px;height:30px;border-radius:50%;display:grid;place-items:center;background:rgba(255,49,49,.2);border:1px solid var(--hi);color:#fff;font-weight:700}
.steps li{transition:transform .25s cubic-bezier(.34,1.56,.64,1),border-color .25s,box-shadow .25s,background .25s,color .25s;cursor:pointer}
.steps li::before{transition:transform .25s cubic-bezier(.34,1.56,.64,1),background .25s,box-shadow .25s,color .25s}
.steps li:hover,.steps li:active{transform:translateY(-8px);border-color:var(--hi);background:rgba(255,49,49,.14);box-shadow:0 14px 28px rgba(255,49,49,.3);color:#fff}
.steps li:hover::before,.steps li:active::before{background:var(--hi);color:#000;box-shadow:0 0 16px var(--hi);transform:translateY(-50%) scale(1.15)}
.rv.show .steps li{animation:pop .65s cubic-bezier(.34,1.56,.64,1) backwards}
.rv.show .steps li:nth-child(1){animation-delay:.1s}.rv.show .steps li:nth-child(2){animation-delay:.25s}.rv.show .steps li:nth-child(3){animation-delay:.4s}.rv.show .steps li:nth-child(4){animation-delay:.55s}
@keyframes pop{0%{opacity:0;transform:translateY(34px) scale(.9)}60%{opacity:1;transform:translateY(-8px) scale(1.03)}100%{opacity:1;transform:none}}
.note{margin-top:20px;padding:14px 18px;border-left:3px solid var(--hi);background:rgba(255,49,49,.08);border-radius:0 10px 10px 0;color:var(--mute);font-size:15px}
a{color:var(--hi)}
.scroll{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;min-width:480px;background:rgba(0,0,0,.45)}
th,td{padding:12px 16px;text-align:left;border-bottom:1px solid rgba(255,49,49,.15)}
th{background:rgba(255,49,49,.14)}tr:last-child td{border-bottom:0}
ul{color:var(--mute);padding-left:22px}.ver li::marker{color:#3ddc84}.chk li::marker{color:#ffb020}
.nav{display:flex;justify-content:space-between;gap:12px;margin-top:36px;flex-wrap:wrap}
.btn{padding:10px 18px;border:1px solid var(--line);border-radius:10px;text-decoration:none;background:rgba(20,20,20,.82)}.btn:hover{border-color:var(--hi);box-shadow:0 0 18px rgba(255,49,49,.3)}
.docs{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin-bottom:16px}
.docs .box b{display:block;margin:2px 0 4px}
.refgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px}
.rc{padding:20px;border-radius:16px;border:1.5px solid;transition:transform .2s,box-shadow .2s}
.rc:hover{transform:translateY(-6px)}
.rc.ok{border-color:rgba(61,220,132,.55);background:linear-gradient(160deg,rgba(61,220,132,.1),rgba(0,0,0,.75))}.rc.ok:hover{box-shadow:0 14px 30px rgba(61,220,132,.22)}
.rc.wn{border-color:rgba(255,176,32,.55);background:linear-gradient(160deg,rgba(255,176,32,.1),rgba(0,0,0,.75))}.rc.wn:hover{box-shadow:0 14px 30px rgba(255,176,32,.22)}
.rc h3{display:flex;align-items:center;gap:10px;margin:0 0 8px;font-size:17px}
.rc h3 span{display:grid;place-items:center;width:28px;height:28px;border-radius:50%;color:#000;font-weight:800}
.ok h3 span{background:#3ddc84}.wn h3 span{background:#ffb020}
.it{display:flex;gap:12px;padding:11px 0;border-bottom:1px dashed rgba(255,255,255,.12)}.it:last-child{border-bottom:0}
.it i{flex:none;width:8px;height:8px;border-radius:50%;margin-top:11px}.ok .it i{background:#3ddc84;box-shadow:0 0 8px #3ddc84}.wn .it i{background:#ffb020;box-shadow:0 0 8px #ffb020}
.it b{display:block;font-weight:600}.it small{display:block;color:var(--mute);font-size:14px;line-height:1.5}
.it em{font-style:normal;font-size:12px;padding:1px 8px;border-radius:99px;background:rgba(255,49,49,.2);border:1px solid var(--hi);margin-left:6px;vertical-align:middle}
.foot{font-size:13px;margin-top:14px}
.rv{opacity:0;transform:translateY(18px);transition:opacity .6s,transform .6s}.rv.show{opacity:1;transform:none}.card.rv{transition:opacity .6s,transform .2s,border-color .2s,box-shadow .2s}.rv.show.card:hover{transform:translateY(-8px)}
@media(max-width:700px){.hero.home .in{margin-left:0;padding-top:150px}.hero svg{width:100%;height:170px}.hero{padding:30px 20px}.embers span:nth-child(n+13){display:none}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.rv{opacity:1;transform:none}.embers span{display:none}.is-home .embers{opacity:.65;background:radial-gradient(ellipse at 12% 100%,rgba(255,49,49,.18),transparent 42%),radial-gradient(ellipse at 88% 100%,rgba(255,107,36,.12),transparent 38%)}}
</style>
</head>
<body>
<div class="embers" aria-hidden="true"><span style="--x:4%;--size:3px;--duration:17s;--delay:-8s;--drift:28px"></span><span style="--x:10%;--size:5px;--duration:23s;--delay:-15s;--drift:-34px"></span><span style="--x:16%;--size:2px;--duration:19s;--delay:-4s;--drift:42px"></span><span style="--x:23%;--size:4px;--duration:25s;--delay:-19s;--drift:-25px"></span><span style="--x:29%;--size:3px;--duration:18s;--delay:-11s;--drift:36px"></span><span style="--x:35%;--size:5px;--duration:22s;--delay:-6s;--drift:-42px"></span><span style="--x:41%;--size:2px;--duration:20s;--delay:-16s;--drift:24px"></span><span style="--x:47%;--size:4px;--duration:24s;--delay:-9s;--drift:-30px"></span><span style="--x:53%;--size:3px;--duration:16s;--delay:-13s;--drift:40px"></span><span style="--x:59%;--size:5px;--duration:26s;--delay:-21s;--drift:-22px"></span><span style="--x:65%;--size:2px;--duration:19s;--delay:-7s;--drift:32px"></span><span style="--x:71%;--size:4px;--duration:23s;--delay:-17s;--drift:-38px"></span><span style="--x:77%;--size:3px;--duration:18s;--delay:-10s;--drift:26px"></span><span style="--x:83%;--size:5px;--duration:25s;--delay:-14s;--drift:-32px"></span><span style="--x:89%;--size:2px;--duration:21s;--delay:-5s;--drift:44px"></span><span style="--x:96%;--size:4px;--duration:17s;--delay:-18s;--drift:-28px"></span></div>
<header class="top"><a class="logo" href="#home">⚡ AK <span>Electrical</span></a><nav id="nav"></nav><a class="site" href="index.html">← กลับเว็บหลัก</a></header>
<div class="wrap" id="app"></div>
<script>
var PEA="https://www.pea.co.th/sites/default/files/documents/PEA-product-acceptance/6.Criteria%20for%20product%20evaluation%20of%20distribution%20transformers%20Ed.1.pdf";
var SPEC="https://bidding.pea.co.th/sites/default/files/tor/2023-06/9d078bfc-eff0-4aa2-88fb-7a4f3392c77b/4.pdf";
var T={
 t100:{kva:100,kw:80,a416:138.8,a400:144.3,a80:111,nl:250,ll:1550,z:4,pos:"ขนาดนี้ติดตั้งแบบแขวนเสาหรือนั่งร้านก็ได้ ขึ้นกับแบบก่อสร้างและข้อกำหนดของ PEA เขตนั้น"},
 t160:{kva:160,kw:128,a416:222.1,a400:230.9,a80:178,nl:360,ll:2100,z:4,pos:"พบเอกสาร กปภ. ที่ระบุหม้อแปลง 160 kVA แบบมีนั่งร้านตามมาตรฐาน กฟภ. จึงควรยืนยันรูปแบบติดตั้งกับ PEA เขตก่อน"},
 t250:{kva:250,kw:200,a416:347.0,a400:360.8,a80:278,nl:500,ll:2950,z:4,pos:"เป็นขนาดสูงสุดในช่วงหม้อแปลงจ่ายไฟทั่วไปของ PEA โดยทั่วไปนิยมติดตั้งแบบนั่งร้าน ควรยืนยันกับ PEA เขต"}
};
var ORDER=["t100","t160","t250"];
var NOTE='<div class="note rv"><b>หมายเหตุ:</b> ตัวเลขทั้งหมดเป็นค่าโดยประมาณจากการคำนวณและเอกสารอ้างอิง ไม่ใช่ข้อมูลสำหรับออกแบบจริง กรุณาตรวจสอบกับ <a href="'+PEA+'" target="_blank" rel="noopener">เอกสาร PEA-TRAN-001</a> และสเปคฉบับล่าสุดของ PEA ก่อนใช้งาน</div>';
function it(t,d,tag){return '<div class="it"><i></i><div><b>'+t+(tag?' <em>'+tag+'</em>':'')+'</b><small>'+d+'</small></div></div>'}
var REFS='<section class="rv"><h2><i>R</i>แหล่งอ้างอิงและสถานะข้อมูล</h2>'
+'<div class="docs"><a class="box" href="'+SPEC+'" target="_blank" rel="noopener"><small>เอกสารหลัก · เปิดไฟล์ PDF ↗</small><b>PEA สเปค RTRN-035/2561</b><small>หม้อแปลง 3 เฟส 22/33 kV ทนการลัดวงจร · Rev. 5 อนุมัติ 30/05/2562</small></a>'
+'<a class="box" href="'+PEA+'" target="_blank" rel="noopener"><small>เอกสารประกอบ · เปิดไฟล์ PDF ↗</small><b>PEA-TRAN-001 Ed.1</b><small>หลักเกณฑ์ตรวจประเมินผลิตภัณฑ์ ใช้เรื่องขึ้นทะเบียนและตรวจรับรอง ไม่ใช่ที่มาของตัวเลขทางเทคนิค</small></a></div>'
+'<div class="refgrid"><div class="rc ok"><h3><span>✓</span>ยืนยันแล้วจากเอกสาร PEA</h3>'
+it("ขนาด 100, 160 และ 250 kVA","มีหม้อแปลง 3 เฟส ขนาดเหล่านี้ในสเปค RTRN-035/2561")
+it("กลุ่มต่อขดลวด Dyn11","ระบุในสเปค RTRN-035/2561")
+it("แรงดัน 22-0.416/0.24 kV","ระบุในรายการจัดซื้อของ PEA สำหรับขนาดเหล่านี้")
+it("กระแสและกำลังที่ PF 0.8","คำนวณเองด้วยสูตรมาตรฐาน ไม่ได้อ่านจากเอกสารโดยตรง","คำนวณเอง")
+'</div><div class="rc wn"><h3><span>!</span>ยังต้องตรวจกับ PEA</h3>'
+it("แรงดันด้านแรงต่ำ","เอกสารจัดซื้อระบุ 416/240 V แต่สำเนาสเปคบางฉบับระบุ 400/230 V ขึ้นกับฉบับแก้ไข")
+it("ค่าสูญเสียและอิมพีแดนซ์","อ่านจากสำเนาสเปคบน Scribd ซึ่งไม่ใช่ไฟล์ต้นทางของ PEA")
+it("อุณหภูมิขึ้นสูงสุด 60 K / 65 K","มาจากสำเนาเดียวกัน และสเปค PEA ของหม้อแปลงชนิดอื่นใช้ค่าต่างกัน")
+it("รูปแบบติดตั้ง (แขวนเสา/นั่งร้าน)","ยังไม่พบเอกสาร PEA ที่กำหนดเกณฑ์ตามขนาด")
+it("ค่าแนะนำ 80% และ PF 0.8","เป็นหลักปฏิบัติ/ค่าสมมติ ไม่ใช่ข้อกำหนดมาตรฐาน")
+'</div></div><p class="foot">ไม่ได้ใช้ข้อมูลจาก วสท. หรือมาตรฐาน มอก. เพราะยังไม่ได้ตรวจสอบแหล่งที่มา</p></section>';
var CABLE='<svg viewBox="0 0 700 420" preserveAspectRatio="xMinYMid meet" aria-hidden="true"><defs><linearGradient id="j" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b3441"/><stop offset=".3" stop-color="#10151c"/><stop offset="1" stop-color="#05070a"/></linearGradient><linearGradient id="cu" x1="0" x2="1"><stop offset="0" stop-color="#8a4a22"/><stop offset=".5" stop-color="#e29a5c"/><stop offset="1" stop-color="#b8672f"/></linearGradient></defs><g fill="none" stroke-linecap="round"><path d="M240,168 C340,168 380,70 520,70 L550,70" stroke="#c9252d" stroke-width="24"/><path d="M240,190 C340,190 390,140 540,140 L570,140" stroke="#1f9d55" stroke-width="24"/><path d="M240,210 C340,210 400,210 560,210 L590,210" stroke="#7a4a2a" stroke-width="24"/><path d="M240,232 C340,232 390,280 540,280 L570,280" stroke="#e9edf2" stroke-width="24"/><path d="M240,254 C340,254 380,350 520,350 L550,350" stroke="#0a0a0c" stroke-width="24"/><path d="M240,254 C340,254 380,350 520,350 L550,350" stroke="#3a4a63" stroke-width="1.5"/><path d="M550,70 L590,70M570,140 L610,140M590,210 L630,210M570,280 L610,280M550,350 L590,350" stroke="url(#cu)" stroke-width="12"/></g><path d="M-10,150 L225,150 Q245,150 245,170 L245,250 Q245,270 225,270 L-10,270 Z" fill="url(#j)"/><ellipse cx="236" cy="210" rx="10" ry="60" fill="#000" opacity=".5"/></svg>';
function f(n,d){return n.toLocaleString("en-US",{minimumFractionDigits:d||0,maximumFractionDigits:d||0})}
function bx(l,v){return '<div class="box"><small>'+l+'</small><b>'+v+'</b></div>'}
function sec(n,t,b){return '<section class="rv"><h2><i>'+n+'</i>'+t+'</h2>'+b+'</section>'}
function home(){
 var cards=ORDER.map(function(k){var t=T[k];return '<a class="card rv" href="#'+k+'"><small>หม้อแปลง 3 เฟส</small><div class="kva">'+t.kva+' kVA</div><small>22 kV / 416-240 V · Dyn11</small><div class="bar"><i style="width:'+Math.round(t.a416/347*100)+'%"></i></div><small>กระแสด้านแรงต่ำ ≈ '+f(t.a416,0)+' A</small><span class="go">ดูรายละเอียด →</span></a>'}).join("");
 var rows=ORDER.map(function(k){var t=T[k];return '<tr><td><a href="#'+k+'">'+t.kva+' kVA</a></td><td>'+t.kw+' kW</td><td>≈ '+f(t.a416,0)+' A</td><td>≈ '+f(t.a400,0)+' A</td></tr>'}).join("");
 return '<div class="hero home cyber-pulse">'+CABLE+'<div class="orb"></div><div class="in"><div class="cyber-title">AK ELECTRICAL · INTELLIGENCE · SUPPLY</div><h1>ศูนย์ควบคุม<br>พลังงานไฟฟ้า <span class="hi">3 เฟส</span></h1><p class="cyber-description">เครื่องมือคำนวณและวิเคราะห์ระบบไฟฟ้าสำหรับงานวิศวกรรมยุคใหม่ เลือกขนาดเพื่อดูข้อมูลจำเพาะ กระแส ค่าสูญเสีย และข้อควรตรวจสอบ</p><div class="cyber-line"></div><div class="system-status"><span>●</span> SYSTEM STATUS : ONLINE</div><div class="chips"><span class="chip">22 kV <b>→</b> 416/240 V</span><span class="chip">Dyn11</span><span class="chip">PEA RTRN-035/2561</span></div></div></div>'
 +'<div class="cards">'+cards+'</div>'+sec("≡","ตารางเปรียบเทียบ",'<div class="scroll"><table><tr><th>ขนาด</th><th>กำลังที่ PF 0.8</th><th>กระแสที่ 416 V</th><th>กระแสที่ 400 V</th></tr>'+rows+'</table></div>')+NOTE+REFS;
}
function detail(k){
 var t=T[k],i=ORDER.indexOf(k),p=ORDER[i-1],n=ORDER[i+1];
 return '<div class="hero"><div class="orb"></div><div class="in"><div class="eyebrow">หม้อแปลงจำหน่าย 3 เฟส · PEA RTRN-035/2561</div><div class="big">'+t.kva+'<span> kVA</span></div><div class="chips"><span class="chip">กำลัง <b>≈ '+t.kw+' kW</b></span><span class="chip">กระแส 416 V <b>≈ '+f(t.a416,0)+' A</b></span><span class="chip">อิมพีแดนซ์ <b>'+t.z+' %</b></span></div></div></div>'
 +sec(1,"ข้อมูลทั่วไป",'<div class="boxes">'+bx("ขนาดพิกัด",t.kva+" kVA")+bx("ระบบ","3 เฟส")+bx("แรงดันตามสเปคจัดซื้อ PEA","22 – 0.416/0.24 kV")+bx("กลุ่มต่อขดลวด","Dyn11")+bx("กำลังไฟฟ้าที่ PF 0.8","≈ "+t.kw+" kW")+'</div>')
 +sec(2,"กระแสด้านแรงต่ำ",'<div class="boxes">'+bx("ที่ 416 V (ตามสเปค PEA)","≈ "+f(t.a416,1)+" A")+bx("ที่ 400 V (อ้างอิง)","≈ "+f(t.a400,1)+" A")+bx("ค่าแนะนำที่ 80% (416 V)","≈ "+t.a80+" A")+'</div><div class="meter"><div class="row"><span>กระแสพิกัด 100%</span><b>≈ '+f(t.a416,0)+' A</b></div><div class="bar"><i style="width:100%"></i></div><div class="row"><span>ค่าแนะนำใช้งาน 80%</span><b>≈ '+t.a80+' A</b></div><div class="bar"><i style="width:80%"></i></div><small style="color:var(--mute)">สูตร I = kVA / (√3 × kV) · 80% เป็นหลักปฏิบัติของผู้ออกแบบบางราย ไม่ใช่ข้อกำหนดของ PEA</small></div>')
 +sec(3,"ค่าสูญเสียและอิมพีแดนซ์ (22 kV, 75 °C)",'<div class="boxes">'+bx("No-load loss",f(t.nl)+" W")+bx("Load loss",f(t.ll)+" W")+bx("Short-circuit impedance",t.z+" %")+bx("อุณหภูมิขึ้นสูงสุด (น้ำมัน / ขดลวด)","60 K / 65 K")+'</div><p style="font-size:14px">ค่านี้มาจากสำเนาสเปคหม้อแปลงจำหน่ายที่ยังไม่ยืนยันว่าเป็นไฟล์ทางการของ PEA</p>')
 +sec(4,"การติดตั้ง",'<div class="box" style="cursor:default"><small>ข้อควรทราบ</small><b style="font-size:17px;font-weight:500;line-height:1.6">'+t.pos+'</b></div>')
 +sec(5,"ลำดับการตรวจสอบก่อนเลือกใช้",'<ol class="steps"><li>คำนวณโหลดรวมและ PF จริงของสถานที่</li><li>เลือกขนาดโดยเผื่อโหลดอนาคต</li><li>ยืนยันรูปแบบติดตั้งและข้อกำหนดกับ PEA เขต</li><li>ตรวจใบรับรองผลิตภัณฑ์ตามเอกสาร PEA-TRAN-001</li></ol>')
 +NOTE+REFS
 +'<div class="nav">'+(p?'<a class="btn" href="#'+p+'">← '+T[p].kva+' kVA</a>':'<span></span>')+(n?'<a class="btn" href="#'+n+'">'+T[n].kva+' kVA →</a>':'<span></span>')+'</div>';
}
function route(){
 var h=(location.hash||"").replace("#","");
 var isDetail=Object.prototype.hasOwnProperty.call(T,h);
 document.body.classList.toggle("is-home",!isDetail);
 document.getElementById("app").innerHTML=isDetail?detail(h):home();
 document.getElementById("nav").innerHTML=ORDER.map(function(k){return '<a href="#'+k+'"'+(k===h?' class="on"':'')+'>'+T[k].kva+' kVA</a>'}).join("");
 window.scrollTo(0,0);
 var els=document.querySelectorAll(".rv");
 if("IntersectionObserver" in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("show");io.unobserve(e.target)}})},{threshold:.08});els.forEach(function(e){io.observe(e)})}
 if(!("IntersectionObserver" in window)){els.forEach(function(e){e.classList.add("show")})}
}
window.addEventListener("hashchange",route);route();
</script>
</body>
</html>
'''.replace('href="index.html"', 'href="%s"' % MAIN_SITE_URL)

PAGE_PATHS = {"/", "/transformers.html", "/tranformer8", "/tranformer8.py"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8", head_only=False):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    def _route(self, head_only=False):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        if path in PAGE_PATHS:
            self._send(200, HTML, head_only=head_only)
        elif path == "/healthz":
            self._send(200, "ok", "text/plain; charset=utf-8", head_only)
        else:
            self._send(404, "ไม่พบหน้านี้ (Not found)", "text/plain; charset=utf-8", head_only)

    def do_GET(self):
        self._route()

    def do_HEAD(self):
        self._route(head_only=True)

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


def arg_value(name, default):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def main():
    if "--export" in sys.argv:
        out = pathlib.Path(__file__).resolve().parent / "transformers.html"
        out.write_text(HTML, encoding="utf-8")
        print("เขียนไฟล์แล้ว:", out)
        return

    # โฮสต์ที่กำหนดตัวแปร PORT ให้ (เช่น Render, Railway) จะใช้ค่านั้นและเปิดรับจากภายนอก
    env_port = os.environ.get("PORT")
    host = arg_value("--host", "0.0.0.0" if env_port else "127.0.0.1")
    try:
        port = int(arg_value("--port", env_port or 8000))
    except ValueError:
        sys.exit("พอร์ตต้องเป็นตัวเลข")

    try:
        server = ThreadingHTTPServer((host, port), Handler)
    except OSError as e:
        sys.exit("เปิดพอร์ต %d ไม่ได้ (%s) ลองเปลี่ยนด้วย --port 9000" % (port, e))

    url = "http://localhost:%d/" % port
    print("เปิดเว็บแล้วที่", url, "(กด Ctrl+C เพื่อหยุด)")
    if "--no-open" not in sys.argv and not env_port:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nหยุดเซิร์ฟเวอร์แล้ว")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()