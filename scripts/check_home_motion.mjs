import {writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {browser} from './home_browser.mjs';

const chrome = await browser(9235);
const pause = ms => new Promise(r => setTimeout(r, ms));
try {
  await chrome.call('Emulation.setDeviceMetricsOverride', {width:1440,height:1500,deviceScaleFactor:1,mobile:false});
  await chrome.call('Page.navigate', {url:'http://localhost:8501'});
  for(let i=0;i<80;i++) {
    if(await chrome.evaluate(`[...document.querySelectorAll('*')].some(e=>e.shadowRoot?.querySelector('.scene img')?.naturalWidth===1600)`)) break;
    await pause(500);
  }
  await pause(3000);
  const metrics = await chrome.evaluate(`(() => {
    const scene = document.querySelector('.st-key-home_scene');
    const title = document.querySelector('.st-key-home_hero h1');
    const root = [...document.querySelectorAll('*')].find(e=>e.shadowRoot?.querySelector('.scene'))?.shadowRoot;
    return {title:title?.innerHTML, titleSize:title && getComputedStyle(title).fontSize,
      scene:scene?.getBoundingClientRect().toJSON(), background:!!document.querySelector('.home-backdrop'),
      backdropRect:document.querySelector('.home-backdrop')?.getBoundingClientRect().toJSON(),
      sceneLoaded:root?.querySelector('img').naturalWidth, points:root?.querySelectorAll('button').length,
      overflow:document.documentElement.scrollWidth>innerWidth};
  })()`);
  console.log(JSON.stringify(metrics));
  assert.equal(metrics.sceneLoaded, 1600);
  assert.equal(metrics.points, 4);
  assert.equal(metrics.overflow, false);
  await writeFile('docs/screenshots/homepage-lovable-motion-desktop.png', Buffer.from((await chrome.call('Page.captureScreenshot',{format:'png'})).data,'base64'));
  for(const topic of ['earth','habitats','detection','flame']) {
    await chrome.evaluate(`(() => {const root=[...document.querySelectorAll('*')].find(e=>e.shadowRoot?.querySelector('.scene')).shadowRoot;root.querySelector('[data-topic="${topic}"]').click()})()`);
    await pause(1000);
    assert.equal(await chrome.evaluate(`(() => {const root=[...document.querySelectorAll('*')].find(e=>e.shadowRoot?.querySelector('.scene')).shadowRoot;return root.querySelector('[aria-pressed="true"]').dataset.topic})()`), topic);
    console.log('selected',topic);
  }
  await chrome.evaluate(`document.querySelector('.st-key-home_motion input').click()`);
  await pause(1000);
  const paused = await chrome.evaluate(`(() => {
    const root=[...document.querySelectorAll('*')].find(e=>e.shadowRoot?.querySelector('.scene')).shadowRoot;
    return {backdrop:getComputedStyle(document.querySelector('.home-backdrop img')).animationPlayState,
      scene:getComputedStyle(root.querySelector('.scene-world')).animationPlayState};
  })()`);
  assert.deepEqual(paused,{backdrop:'paused',scene:'paused'});
  console.log('paused',paused);
  await chrome.evaluate(`document.querySelector('.st-key-home_motion input').click()`);
  await pause(1000);
  await chrome.call('Emulation.setDeviceMetricsOverride', {width:390,height:900,deviceScaleFactor:1,mobile:true});
  await pause(1000);
  await chrome.evaluate('window.scrollTo(0,0)');
  await writeFile('docs/screenshots/homepage-lovable-motion-mobile.png', Buffer.from((await chrome.call('Page.captureScreenshot',{format:'png'})).data,'base64'));
  console.log('mobile', await chrome.evaluate(`({width:innerWidth,scroll:document.documentElement.scrollWidth})`));
  assert.equal(await chrome.evaluate('document.documentElement.scrollWidth'),390);
  await chrome.call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
  console.log('reduced motion', await chrome.evaluate(`getComputedStyle(document.querySelector('.home-backdrop img')).animationName`));
  assert.equal(await chrome.evaluate(`getComputedStyle(document.querySelector('.home-backdrop img')).animationName`),'none');
} finally {await chrome.close()}
