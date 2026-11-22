// Choinka ASCII 3D - skrypt zewnętrzny. Życzenia edytujesz w tablicy LINES poniżej.
// ---- ustawienia ----
const LINES=["Wesolych Swiat!","Duzo zdrowia i szczescia","Spelnienia marzen","I wszystkiego najlepszego ode mnie"], NG=9, NL=170, NF=300, SPIN=.55, T0=1, GAP=.9, HOLD=9, FALL=.9;
// ---- stałe ----
const TAU=Math.PI*2, TILT=.2, CT=Math.cos(TILT), ST=Math.sin(TILT), M=Math;
const CD=".:'`,", CM="vxo%&", CB="WXS#@", KD=[22,22,28,23,22], KM=[28,34,34,40,28], KB=[40,46,82,118,46];
const LC=[196,226,39,201,231,208,46,214];
const BASE16=["#000","#cd0000","#00cd00","#cdcd00","#0000ee","#cd00cd","#00cdcd","#e5e5e5","#7f7f7f","#f00","#0f0","#ff0","#5c5cff","#f0f","#0ff","#fff"];
const PAL=Array.from({length:256},(_,n)=>{
  if(n<16)return BASE16[n];
  if(n<232){n-=16;const f=v=>v?55+40*v:0;return `rgb(${f(n/36|0)},${f((n/6|0)%6)},${f(n%6)})`}
  const v=8+10*(n-232);return `rgb(${v},${v},${v})`});
const rng=a=>()=>{a|=0;a=a+0x6D2B79F5|0;let t=M.imul(a^a>>>15,1|a);t=t+M.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296};

const TI=[...Array(6)].map((_,k)=>[2.95-k*.43,.8+k*.95,1.6]);
const SZ=.8+5*.95+1.6+.25;
const radiusAt=z=>{let b=0;for(const[R,z0,h]of TI)if(z>=z0&&z<=z0+h)b=M.max(b,R*(1-(z-z0)/h));return b};
const inPoly=(px,py,p)=>{let o=false;for(let i=0,j=p.length-1;i<p.length;j=i++){const[xi,yi]=p[i],[xj,yj]=p[j];if((yi>py)!=(yj>py)&&px<(xj-xi)*(py-yi)/(yj-yi+1e-12)+xi)o=!o}return o};
const bounce=p=>{const n=7.5625,d=2.75;if(p<1/d)return n*p*p;if(p<2/d){p-=1.5/d;return n*p*p+.75}if(p<2.5/d){p-=2.25/d;return n*p*p+.9375}p-=2.625/d;return n*p*p+.984375};

// ---- scena ----
const cache={};
function build(sc){
  const key=M.round(sc*2)/2; if(cache[key])return cache[key];
  const r=rng(11), dens=4*key*key, tree=[], trunk=[], lights=[], garland=[], star=[], loc=[], flakes=[];
  const areas=TI.map(([R,,h])=>M.PI*R*M.hypot(R,h));
  TI.forEach(([R,z0,h],k)=>{const n=areas[k]*dens|0;for(let i=0;i<n;i++){
    const f=1-M.sqrt(r()),rr=R*(1-f),a=r()*TAU;let b=r()*.55;if(f>.8)b+=.25;if(f<.12)b-=.25;
    tree.push([rr*M.cos(a),rr*M.sin(a),z0+f*h,a,b,r()*5|0])}});
  for(let i=0;i<260*key;i++){const a=r()*TAU;trunk.push([.32*M.cos(a),.32*M.sin(a),r()*.85,"#H8"[r()*3|0],[94,130,95][r()*3|0]])}
  const tot=areas.reduce((a,b)=>a+b);
  for(let i=0;i<NL;i++){let q=r()*tot,k=0;while(q>areas[k]&&k<5)q-=areas[k++];
    const[R,z0,h]=TI[k],f=.04+r()*.76,rr=R*(1-f)*1.06+.03,a=r()*TAU;
    lights.push([rr*M.cos(a),rr*M.sin(a),z0+f*h,r()*TAU,LC[r()*8|0],"O@0o"[r()*4|0]])}
  const gn=150*key|0;
  for(let s=0;s<gn;s++){const f=s/gn,z=.95+f*5.7,rr=radiusAt(z)+.1;if(rr<.15)continue;const a=f*TAU*8;
    garland.push([rr*M.cos(a),rr*M.sin(a),z,s%3?'=':'~',s%2?220:178])}
  const vs=[...Array(10)].map((_,i)=>{const rd=i%2?.26:.62,a=M.PI/2+i*TAU/10;return[rd*M.cos(a),rd*M.sin(a)]});
  for(let gx=-.65;gx<=.65;gx+=.045)for(let gy=-.65;gy<=.65;gy+=.045)if(inPoly(gx,gy,vs)){star.push([gx,0,SZ+gy],[0,gx,SZ+gy])}
  const N=M.max(7,key*1.7|0);
  for(let a=0;a<=N;a++)for(let b=0;b<=N;b++){const u=a/N-.5,v=b/N-.5,p=(a+b)%2,w=v+.5,s=M.abs(u)<.11;
    loc.push([u,v,1,s||M.abs(v)<.11,p],[u,-.5,w,s,p],[u,.5,w,s,p],[-.5,u,w,s,p],[.5,u,w,s,p])}
  for(const s of[-1,1])loc.push([.2*s,0,1.12,1,0],[.12*s,0,1.22,1,1],[0,.2*s,1.12,1,0],[0,.12*s,1.22,1,1]);
  loc.push([0,0,1.15,1,1],[0,0,1.3,1,0]);
  const GB=[27,196,34,129,208,39,160,205,178], GR=[231,220,220,231,231,220,231,220,196], ord=[0,5,2,7,4,1,8,3,6];
  const gifts=ord.slice(0,NG).map((slot,i)=>{const a=TAU*slot/NG+(r()*.24-.12),rd=3.7+r()*1.1;
    return{cx:rd*M.cos(a),cy:rd*M.sin(a),s:.55+r()*.35,yaw:r()*TAU,w:(i%2?1:-1)*(.5+r()*.7),b:GB[i%9],rb:GR[i%9],t0:T0+i*GAP}});
  for(let i=0;i<NF;i++)flakes.push([r(),r(),.35+r()*.95,r()*TAU,r()*3|0]);
  return cache[key]={tree,trunk,lights,garland,star,loc,gifts,flakes};
}

// ---- klatka: siatka znaków ----
function frame(t,W,H,aspect,fps){
  const top=LINES.length+3,bottom=H-6,area=bottom-top,sc=M.max(1.2,M.min(area/9.4,W/(10.5*aspect))),S=build(sc);
  const sxs=aspect*sc,base=bottom-sc,mid=W/2,ang=t*SPIN,ca=M.cos(ang),sa=M.sin(ang),n=W*H,lim=H-5;
  const C=new Array(n).fill(null),K=new Int16Array(n).fill(-1),zb=new Float32Array(n).fill(-1e9),tw=new Array(n).fill(null);
  const set=(i,ch,k)=>{C[i]=ch;K[i]=k};
  // śnieżne pole
  const hz=top+.6*area|0;
  for(let r=hz;r<M.min(H,bottom+5);r++){const d=(r-hz)/M.max(1,bottom+5-hz),m=9-(d*5|0);
    for(let c=0;c<W;c++){const h=(c*7+r*13)%m,i=r*W+c;
      if(h==0)set(i,':',d<.5?60:67);else if(h==3&&d>.25)set(i,'.',103);else if((c*5+r*11+(t*2|0))%97==0)set(i,'+',153)}}
  const plot=(x,y,z,ch,col,bias=0)=>{
    const yr=x*sa+y*ca,sx=(mid+(x*ca-y*sa)*sxs)|0,sy=(base-(z*CT-yr*ST)*sc)|0;
    if(sx>=0&&sx<W&&sy>=1&&sy<lim){const i=sy*W+sx,d=yr*CT+z*ST+bias;if(d>zb[i]){zb[i]=d;set(i,ch,col);tw[i]=null;return i}}
    return -1};
  for(const p of S.tree){const yr=p[0]*sa+p[1]*ca,sx=(mid+(p[0]*ca-p[1]*sa)*sxs)|0,sy=(base-(p[2]*CT-yr*ST)*sc)|0;
    if(sx>=0&&sx<W&&sy>=1&&sy<lim){const i=sy*W+sx,d=yr*CT+p[2]*ST;if(d>zb[i]){zb[i]=d;tw[i]=p}}}
  for(const[x,y,z,ch,k]of S.trunk)plot(x,y,z,ch,k);
  for(const[x,y,z,ch,k]of S.garland)plot(x,y,z,ch,k,.05);
  const lc=[];
  for(const[x,y,z,ph,col,ch]of S.lights){const s=M.sin(t*4+ph);let i,g=0,c2=col,c3=ch;
    if(s>.75){c2=231;g=1;i=plot(x,y,z,ch,231,.1)}else if(s>-.25){g=.6;i=plot(x,y,z,ch,col,.1)}else{i=plot(x,y,z,'o',238,.05)}
    if(i>=0&&g)lc.push([i,col,g,C[i],K[i]])}
  const sk=M.sin(t*5)>-.3?226:229;
  for(const[x,y,z]of S.star)plot(x,y,z,'#',sk,.3);
  // prezenty
  const tt=t;
  for(const g of S.gifts){if(tt<g.t0)continue;
    const p=M.min(1,(tt-g.t0)/FALL),zo=7*(1-bounce(p)),s=g.s*M.min(1,.35+p*3),yw=g.yaw+t*g.w,c=M.cos(yw),sn=M.sin(yw);
    for(const[lx,ly,lz,rb,par]of S.loc){const x=(lx*c-ly*sn)*s+g.cx,y=(lx*sn+ly*c)*s+g.cy,z=lz*s+zo;
      if(rb)plot(x,y,z,par?'=':'+',g.rb,.02);else plot(x,y,z,par?'X':'#',g.b,0)}}
  // cieniowanie choinki
  const fk=t*10|0;
  for(let i=0;i<n;i++){const p=tw[i];if(!p)continue;const k=p[5],L=p[4]*.65+.35*(.5+.5*M.sin(p[3]+ang+.9));
    if((i*7+fk*13)%83==0)set(i,'*',231);else if(L<.28)set(i,CD[k],KD[k]);else if(L<.58)set(i,CM[k],KM[k]);else set(i,CB[k],KB[k])}
  // promienie gwiazdy
  const scx=mid|0,scy=(base-SZ*CT*sc)|0,reach=1.7*sc*aspect|0;
  for(let dx=2;dx<reach;dx++){const col=dx<reach*.4?136:dx<reach*.75?94:58;
    for(const sg of[-1,1]){const c=scx+sg*dx;if(c>=0&&c<W&&scy>=1&&scy<H&&zb[scy*W+c]<-1e8)set(scy*W+c,'-',col)}}
  for(let dy=1;dy<1.9*sc;dy++){const r=scy-dy;if(r>=1&&r<H&&zb[r*W+scx]<-1e8)set(r*W+scx,'|',dy<sc*.7?136:94)}
  for(let dd=2;dd<sc*1.1;dd++)for(const[a,b,ch]of[[1,-1,'/'],[-1,-1,'\\']]){const c=scx+a*dd*2,r=scy+b*dd;
    if(c>=0&&c<W&&r>=1&&r<H&&zb[r*W+c]<-1e8)set(r*W+c,ch,94)}
  // śnieg
  for(const[nx,ny,sp,ph,ly]of S.flakes){const c=(((nx*W+2*M.sin(t*1.3+ph))|0)%W+W)%W,r=((ny*H+t*sp*H*.1)|0)%H,i=r*W+c;
    if(zb[i]<-1e8&&r<H-5)ly==0?set(i,'.',244):ly==1?set(i,'+',250):set(i,sp>.9?'*':'+',255)}
  let letters=0;for(let i=0;i<n;i++)if(K[i]>=0)letters++;
  const txt=(row,col,s,k)=>{for(let j=0;j<s.length;j++){const c=col+j;if(c>=0&&c<W){if(s[j]==' ')K[row*W+c]=-1;else set(row*W+c,s[j],k)}}};
  // napis i HUD
  const cp=[196,40,226,231,39];
  const mobile = W < 80;
  const textStart = mobile
    ? M.max(1, star[1] - LINES.length + 2)
    : 1;

  LINES.forEach((ln,r)=>{
    const c0=(W-ln.length)/2|0;
    const row=textStart+r;

    for(let j=0;j<ln.length;j++){
      const x=c0+j;
      if(x<0||x>=W)continue;
      const i=row*W+x;

      if(ln[j]==' ')K[i]=-1;
      else set(i,ln[j],cp[(j+(t*2|0))%5]);
    }
});

return{C,K,glows:lc.filter(([i,,,ch,k])=>C[i]===ch&&K[i]===k),star:[scx,scy]};
}

// ---- rysowanie na canvasie ----
const cv=document.getElementById('c'),ctx=cv.getContext('2d');
let cw,chh,W,H,ox,oy,fs,mul=1,vw,vh,dpr,bg;
const glowC={};
function glow(col,r){const k=col+'|'+r;if(glowC[k])return glowC[k];
  const o=document.createElement('canvas');o.width=o.height=r*2;const g=o.getContext('2d'),q=g.createRadialGradient(r,r,0,r,r,r);
  q.addColorStop(0,PAL[col]);q.addColorStop(1,'rgba(0,0,0,0)');g.globalAlpha=.8;g.fillStyle=q;g.fillRect(0,0,r*2,r*2);return glowC[k]=o}
function setup(){
  dpr=devicePixelRatio||1;vw=innerWidth;vh=innerHeight;cv.width=vw*dpr;cv.height=vh*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);
  fs=M.max(8,M.min(60,M.round(15*mul*M.sqrt(vw*vh/900000))));
  ctx.font=`${fs}px Consolas,"Cascadia Mono","Courier New",monospace`;ctx.textBaseline='top';
  cw=ctx.measureText('M').width;chh=M.round(fs*1.17);W=M.max(40,vw/cw|0);H=M.max(24,vh/chh|0);
  ox=(vw-W*cw)/2;oy=(vh-H*chh)/2;
  bg=ctx.createLinearGradient(0,0,0,vh);bg.addColorStop(0,'#0b142e');bg.addColorStop(1,'#04060c');
}
addEventListener('resize',setup);setup();
let t=0,last=performance.now(),fps=60;
const sky=Array.from({length:80},()=>[Math.random(),Math.random()*.6,Math.random()*TAU]);
function loop(now){
  const dt=(now-last)/1000;last=now;if(dt>0)fps=fps*.95+(1/dt)*.05;t+=M.min(dt,.1);
  const{C,K,glows,star}=frame(t,W,H,chh/cw,fps);
  ctx.globalCompositeOperation='source-over';ctx.fillStyle=bg;ctx.fillRect(0,0,vw,vh);
  for(const[x,y,p]of sky){const v=70+70*M.sin(t*2+p)|0;ctx.fillStyle=`rgb(${v},${v},${v+20})`;ctx.fillRect(x*vw,y*vh,1.5,1.5)}
  ctx.globalCompositeOperation='lighter';
  const rs=cw*9*(.85+.15*M.sin(t*5))|0,gs=glow(226,rs);ctx.drawImage(gs,ox+star[0]*cw+cw/2-rs,oy+star[1]*chh-rs);
  const rl=cw*3|0;for(const[i,col,g]of glows){const x=ox+(i%W)*cw+cw/2-rl,y=oy+(i/W|0)*chh+chh/2-rl,im=glow(col,rl);
    ctx.drawImage(im,x,y);if(g>=1)ctx.drawImage(im,x,y)}
  ctx.globalCompositeOperation='source-over';
  const by=new Map();
  for(let i=0;i<K.length;i++){const k=K[i];if(k>=0){let a=by.get(k);if(!a)by.set(k,a=[]);a.push(i)}}
  for(const[k,a]of by){ctx.fillStyle=PAL[k];for(const i of a)ctx.fillText(C[i],ox+(i%W)*cw,oy+(i/W|0)*chh)}
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
