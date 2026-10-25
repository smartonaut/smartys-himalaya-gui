let konto=null, ordner='INBOX', mail=null, signaturCache=null;
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function hole(u){const r=await fetch(u);return r.json()}
async function ladeKonten(){
  const d=await hole('/api/accounts');
  const el=document.getElementById('kontenliste');
  // "No configuration found" ist kein Defekt, sondern der Normalfall beim
  // ersten Start: dann gehoert der Einrichtungsassistent hin, nicht der
  // rohe Fehlertext von himalaya.
  const keineKonfig = d.error && /no configuration|config.*not found/i.test(d.error);
  if(d.error && !keineKonfig){el.textContent='Fehler: '+d.error;return}
  el.innerHTML='';
  if(keineKonfig || !(d.accounts||[]).length){kontoAssistent();return}
  (d.accounts||[]).forEach(a=>{
    const div=document.createElement('div');
    div.className='konto';div.dataset.name=a.name;
    div.innerHTML='<span class="kontoname">'+esc(a.name)+'</span>'+
      (a.default?'<span class="standard" title="Standardkonto">★</span>':'');
    div.onclick=()=>waehleKonto(a.name,div);
    el.appendChild(div);
  });
}

/* ---------------------------------------------------------------- Konten */
async function kontoAssistent(){
  const box=document.getElementById('lesen');
  box.innerHTML='<h2>Konto einrichten</h2>'+
    '<div class="hinweis" style="padding:0 0 14px">Trag deine E-Mail-Adresse und das Passwort ein — '+
    'die Servereinstellungen erkennt die App meist selbst. Nichts hiervon verlässt deinen Rechner.</div>'+
    '<div class="verfassen" style="border-top:0;padding-top:0">'+
      '<input id="kEmail" placeholder="E-Mail-Adresse" autocomplete="username">'+
      '<input id="kPass" type="password" placeholder="Passwort" autocomplete="current-password">'+
      '<input id="kName" placeholder="Anzeigename (optional)">'+
      '<div id="kHinweis" class="hinweis" style="padding:8px 0;display:none"></div>'+
      '<details style="margin:6px 0 10px"><summary style="cursor:pointer;color:#8fa0b8;font-size:12.5px">'+
        'Server selbst eintragen</summary>'+
        '<input id="kImap" placeholder="IMAP-Server (z.B. imap.gmx.net)" style="margin-top:8px">'+
        '<input id="kImapPort" placeholder="IMAP-Port (993)" value="993">'+
        '<input id="kSmtp" placeholder="SMTP-Server (z.B. mail.gmx.net)">'+
        '<input id="kSmtpPort" placeholder="SMTP-Port (465)" value="465">'+
      '</details>'+
      '<div class="senden-zeile"><button id="kSpeichern" onclick="kontoSpeichern()">Konto hinzufügen</button>'+
        '<span class="status" id="kStatus"></span></div>'+
    '</div>';
  const mail=document.getElementById('kEmail');
  mail.addEventListener('blur',async()=>{
    const adresse=mail.value.trim();
    if(!adresse.includes('@'))return;
    const r=await fetch('/api/konto/pruefen',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({email:adresse})});
    const d=await r.json();
    const hin=document.getElementById('kHinweis');
    if(d.imap_host){
      document.getElementById('kImap').value=d.imap_host;
      document.getElementById('kImapPort').value=d.imap_port;
      document.getElementById('kSmtp').value=d.smtp_host;
      document.getElementById('kSmtpPort').value=d.smtp_port;
    }
    if(d.hinweis){
      hin.style.display='block';
      hin.innerHTML='<b>Hinweis:</b> '+esc(d.hinweis);
    }else{hin.style.display='none'}
  });
  mail.focus();
}
async function kontoSpeichern(){
  const st=document.getElementById('kStatus'),bt=document.getElementById('kSpeichern');
  const daten={
    email:document.getElementById('kEmail').value.trim(),
    passwort:document.getElementById('kPass').value,
    anzeigename:document.getElementById('kName').value.trim(),
    imap_host:document.getElementById('kImap').value.trim(),
    imap_port:document.getElementById('kImapPort').value.trim()||993,
    smtp_host:document.getElementById('kSmtp').value.trim(),
    smtp_port:document.getElementById('kSmtpPort').value.trim()||465
  };
  if(!daten.email||!daten.passwort){
    st.className='status fehler';st.textContent='E-Mail und Passwort sind nötig.';return;
  }
  bt.disabled=true;st.className='status';st.textContent='prüfe Zugangsdaten…';
  const r=await fetch('/api/konto/anlegen',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(daten)});
  const d=await r.json();
  bt.disabled=false;
  if(d.error){st.className='status fehler';st.textContent=d.error;return}
  st.className='status ok';st.textContent='Konto „'+d.name+'" eingerichtet. Lade neu…';
  setTimeout(()=>{document.getElementById('kontenliste').innerHTML='lade…';ladeKonten()},1200);
}
async function waehleKonto(name,el){
  konto=name;mail=null;ordner='INBOX';
  document.querySelectorAll('.konto').forEach(k=>k.classList.remove('aktiv'));
  if(el)el.classList.add('aktiv');
  document.querySelectorAll('.ordnerblock').forEach(b=>b.remove());
  const block=document.createElement('div');block.className='ordnerblock';
  el.after(block);
  const m=await hole('/api/mailboxes?account='+encodeURIComponent(name));
  const boxen=(m.mailboxes||[]);
  // Der Eingangsordner heisst je Provider anders ("Inbox", "INBOX", "Posteingang").
  const eingang=boxen.find(b=>(b.name||'').toLowerCase()==='inbox');
  if(eingang) ordner=eingang.name;
  if(!boxen.length){
    const o=document.createElement('div');o.className='ordner aktiv';o.textContent=ordner;
    o.onclick=()=>{ordner=o.textContent;ladeListe()};block.appendChild(o);
  }
  boxen.forEach(b=>{
    const o=document.createElement('div');
    o.className='ordner'+(b.name===ordner?' aktiv':'');
    o.textContent=ordnerName(b.name);
    o.onclick=()=>{document.querySelectorAll('.ordner').forEach(x=>x.classList.remove('aktiv'));
                   o.classList.add('aktiv');ordner=b.name;ladeListe();};
    block.appendChild(o);
  });
  ladeListe();
}
async function ladeListe(){
  document.getElementById('listenkopf').textContent=konto+' · '+ordner;
  const box=document.getElementById('liste');
  box.querySelectorAll('.mail,.ladehinweis').forEach(m=>m.remove());
  const d=await hole('/api/list?account='+encodeURIComponent(konto)+
                     '&mailbox='+encodeURIComponent(ordner));
  if(d.error){box.insertAdjacentHTML('beforeend',
    '<div class="hinweis ladehinweis">Fehler: '+esc(d.error)+'</div>');return}
  (d.envelopes||[]).forEach(e=>box.appendChild(mailZeile(e)));
  if(!(d.envelopes||[]).length)
    box.insertAdjacentHTML('beforeend','<div class="hinweis ladehinweis">Keine Nachrichten</div>');
}
const ORDNER_DE={'inbox':'Posteingang','sent':'Gesendet','sent items':'Gesendet',
 'sent messages':'Gesendet','drafts':'Entwürfe','trash':'Papierkorb',
 'deleted items':'Papierkorb','junk':'Spam','junk mail':'Spam','spam':'Spam',
 'archive':'Archiv','archives':'Archiv','outbox':'Postausgang'};
function ordnerName(name){return ORDNER_DE[(name||'').toLowerCase()]||name}
function zeitKurz(iso){
  const d=new Date(iso);
  if(isNaN(d))return (iso||'').slice(11,16);
  const jetzt=new Date();
  const gleichTag=d.toDateString()===jetzt.toDateString();
  const gestern=new Date(jetzt); gestern.setDate(jetzt.getDate()-1);
  if(gleichTag)return d.toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'});
  if(d.toDateString()===gestern.toDateString())return 'gestern';
  if(jetzt-d<6*86400000)return d.toLocaleDateString('de-DE',{weekday:'short'})+'.';
  return d.toLocaleDateString('de-DE',{day:'2-digit',month:'2-digit',year:'2-digit'});
}
function absenderKopf(von){
  // "Anna Berger <a@b.de>" -> Name fett, Adresse in Monospace, per Klick kopierbar.
  // Wer eine Mail prueft, will oft genau diese Adresse weiterverwenden.
  const m=(von||'').match(/^\s*(.*?)\s*<([^>]+)>\s*$/);
  const name=m?m[1].trim():'';
  const adresse=m?m[2].trim():(von||'').trim();
  if(!adresse)return '<span class="kopf-name">'+esc(von||'')+'</span>';
  return (name?'<span class="kopf-name">'+esc(name)+'</span> ':'')+
    '<span class="kopf-adresse" title="Adresse kopieren" '+
    'onclick="adresseKopieren(this)">'+esc(adresse)+'</span>';
}
function adresseKopieren(el){
  const text=el.textContent;
  const fertig=()=>{const alt=el.textContent;el.textContent='kopiert';el.classList.add('kopiert');
    setTimeout(()=>{el.textContent=alt;el.classList.remove('kopiert')},1100)};
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(fertig).catch(()=>{});
  }else{
    const t=document.createElement('textarea');t.value=text;document.body.appendChild(t);
    t.select();try{document.execCommand('copy');fertig()}catch(e){}
    document.body.removeChild(t);
  }
}
function zeitLang(iso){
  const d=new Date(iso);
  if(isNaN(d))return iso||'';
  return d.toLocaleDateString('de-DE',{day:'2-digit',month:'2-digit',year:'numeric'})+
         ', '+d.toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'})+' Uhr';
}
function initialen(name){
  const sauber=(name||'?').replace(/["'<>,]/g,'').trim();
  const teile=sauber.split(/[\s.@_-]+/).filter(Boolean);
  if(!teile.length)return '?';
  if(teile.length===1)return teile[0].slice(0,1).toUpperCase();
  return (teile[0][0]+teile[1][0]).toUpperCase();
}
function mailZeile(e){
  const abs=(e.from&&e.from[0])||{};
  const name=(abs.name||'').trim();
  const adresse=(abs.email||'').trim();
  // Zur Spam-Erkennung gehoert die echte Adresse, nicht nur der Anzeigename:
  // jeder kann sich "Sparkasse" nennen. Steht ein Name da, wird die Adresse
  // darunter gezeigt; ohne Namen ist sie selbst die erste Zeile.
  const oben=name||adresse||'(unbekannt)';
  const div=document.createElement('div');
  div.className='mail'+((e.flags||[]).length?'':' ungelesen');
  div.innerHTML='<div class="von"><span title="'+esc(oben)+'">'+esc(oben)+'</span>'+
      '<span>'+esc(zeitKurz(e.date))+'</span></div>'+
    (name&&adresse?'<div class="adresse" title="'+esc(adresse)+'">'+esc(adresse)+'</div>':'')+
    '<div class="betreff">'+esc(e.subject||'(ohne Betreff)')+'</div>';
  div.onclick=()=>lese(e.id,div,e);
  return div;
}
async function lese(id,el,env){
  mail=id;
  document.querySelectorAll('.mail').forEach(m=>m.classList.remove('aktiv'));
  if(el)el.classList.add('aktiv');
  const box=document.getElementById('lesen');
  box.innerHTML='<div class="hinweis">lade…</div>';
  const d=await hole('/api/read?account='+encodeURIComponent(konto)+'&id='+encodeURIComponent(id)+
                     '&mailbox='+encodeURIComponent(ordner));
  if(d.error){box.innerHTML='<div class="hinweis">Fehler: '+esc(d.error)+'</div>';return}
  // Betreff/Absender aus der Liste als Rueckfall: die Lese-API liefert sie
  // gelegentlich nicht (anderer Ordnername, exotische Mail).
  const envBetreff=(env&&env.subject)||'';
  const envVon=(env&&env.from&&env.from[0])?(env.from[0].name?env.from[0].name+(env.from[0].email?' <'+env.from[0].email+'>':''):(env.from[0].email||'')):'';
  const betreff=d.subject||envBetreff||'';
  const von=d.from||envVon||'';
  let anhangHtml='';
  if((d.anhaenge||[]).length){
    anhangHtml='<div class="anhaenge"><b>Anhänge</b><br>'+
      d.anhaenge.map((a,i)=>'<a href="/api/attachment?account='+encodeURIComponent(konto)+
        '&id='+encodeURIComponent(id)+'&index='+i+'&mailbox='+encodeURIComponent(ordner)+'">'+
        esc(a.name||('Anhang '+(i+1)))+'</a>').join('')+'</div>';
  }
  box.innerHTML='<h2>'+esc(betreff||'(ohne Betreff)')+'</h2>'+
    '<div class="meta">'+absenderKopf(von)+'  ·  '+esc(zeitLang(d.date))+'</div>'+
    anhangHtml+
    '<div class="knopfleiste">'+
      '<button onclick="antworten()" title="Antworten (A)">\u21a9 Antworten</button>'+
      '<button onclick="weiterleiten()" title="Weiterleiten (W)">\u21aa Weiterleiten</button>'+
      '<button onclick="alsGelesen()" title="Als gelesen oder ungelesen markieren">\u25cf Gelesen</button>'+
      '<button onclick="loeschen()" title="In den Papierkorb (Entf)">\u2715 Löschen</button>'+
    '</div>'+
    '<pre class="body">'+esc(d.body||'')+'</pre>'+
    '<div id="editorbereich"></div>';
  window._letzte={subject:betreff, from:von, date:d.date||'', body:d.body||''};
  // Gelesene Nachricht nicht weiter als ungelesen anzeigen
  if(el&&el.classList.contains('ungelesen')){
    el.classList.remove('ungelesen');
    fetch('/api/flag',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({account:konto,id:id,mailbox:ordner,gelesen:true})}).catch(()=>{});
  }
}
function editorHtml(){
  return '<div class="verfassen">'+
    '<input id="fAn" placeholder="An (mehrere mit Komma trennen)">'+
    '<input id="fCc" placeholder="Cc (optional)">'+
    '<input id="fBetreff" placeholder="Betreff">'+
    '<div class="toolbar">'+
      '<button onmousedown="event.preventDefault();fmt(\'bold\')" title="Fett"><b>B</b></button>'+
      '<button onmousedown="event.preventDefault();fmt(\'italic\')" title="Kursiv"><i>I</i></button>'+
      '<button onmousedown="event.preventDefault();fmt(\'underline\')" title="Unterstrichen"><u>U</u></button>'+
      '<button onmousedown="event.preventDefault();fmt(\'strikeThrough\')" title="Durchgestrichen"><s>S</s></button>'+
      '<select onchange="fmtWert(\'fontSize\',this.value)"><option value="">Größe</option>'+
        '<option value="1">klein</option><option value="3">normal</option>'+
        '<option value="5">groß</option><option value="6">sehr groß</option></select>'+
      '<select onchange="fmtWert(\'fontName\',this.value)"><option value="">Schrift</option>'+
        '<option value="Arial">Arial</option><option value="Georgia">Georgia</option>'+
        '<option value="Courier New">Courier</option><option value="Verdana">Verdana</option></select>'+
      '<input type="color" value="#111111" onchange="fmtWert(\'foreColor\',this.value)" title="Schriftfarbe">'+
      '<input type="color" value="#ffff00" onchange="fmtWert(\'hiliteColor\',this.value)" title="Textmarker">'+
      '<button onmousedown="event.preventDefault();fmt(\'insertUnorderedList\')" title="Aufzählung">•</button>'+
      '<button onmousedown="event.preventDefault();fmt(\'insertOrderedList\')" title="Nummerierung">1.</button>'+
      '<button onmousedown="event.preventDefault();linkEinfuegen()" title="Link">Link</button>'+
      '<button onmousedown="event.preventDefault();fmt(\'removeFormat\')" title="Formatierung entfernen">×</button>'+
    '</div>'+
    '<div id="editor" contenteditable="true"></div>'+
    '<div class="senden-zeile"><button id="sendenbtn" onclick="senden()">Senden</button>'+
      '<span class="status" id="sendestatus"></span></div></div>';
}
function fmt(b){document.getElementById('editor').focus();document.execCommand(b,false,null)}
function fmtWert(b,w){document.getElementById('editor').focus();document.execCommand(b,false,w)}
function linkEinfuegen(){
  const u=prompt('Adresse (https://…):');if(!u)return;
  document.getElementById('editor').focus();document.execCommand('createLink',false,u);
}
async function sigFuer(){
  if(signaturCache===null){
    const d=await hole('/api/signaturen');
    signaturCache=(d.gruppen||{});
  }
  const gruppe=(konto||'').includes('-')?(konto||'').split('-')[0]:(konto||'');
  const eintrag=signaturCache[gruppe];
  return (eintrag&&eintrag.html)||'';
}
async function oeffneEditor(v){
  const bereich=document.getElementById('editorbereich');
  if(!bereich)return;
  bereich.innerHTML=editorHtml();
  document.getElementById('fAn').value=v.an||'';
  document.getElementById('fCc').value=v.cc||'';
  document.getElementById('fBetreff').value=v.betreff||'';
  const ed=document.getElementById('editor');
  const sig=await sigFuer();
  ed.innerHTML=(v.text||'')+(sig?('<div><br></div>'+sig):'');
  ed.focus();
  bereich.scrollIntoView({behavior:'smooth',block:'start'});
}
function zitat(){
  const m=window._letzte||{};
  return '<p><br></p><p style="color:#888">----- Ursprüngliche Nachricht -----<br>'+
    esc((m.from||'')+' · '+(m.date||'')).replace(/\n/g,'<br>')+'</p>'+
    '<blockquote style="border-left:3px solid #ccc;margin-left:0;padding-left:10px;color:#555">'+
    esc((m.body||'').slice(0,4000)).replace(/\n/g,'<br>')+'</blockquote>';
}
function antworten(){
  const m=window._letzte||{};
  const treffer=(m.from||'').match(/[\w.\-+]+@[\w.\-]+\.\w+/);
  const s=m.subject||'';
  oeffneEditor({an:treffer?treffer[0]:'',
    betreff:s.toLowerCase().startsWith('re:')?s:'Re: '+s, text:zitat()});
}
function weiterleiten(){
  const m=window._letzte||{};
  oeffneEditor({an:'',betreff:'Fwd: '+(m.subject||''),text:zitat()});
}
function neueMail(){
  if(!konto){alert('Erst ein Konto wählen');return}
  mail=null;
  document.getElementById('lesen').innerHTML='<h2>Neue Nachricht</h2><div id="editorbereich"></div>';
  oeffneEditor({});
}
async function signaturBearbeiten(){
  const box=document.getElementById('lesen');
  box.innerHTML='<div class="hinweis">lade…</div>';
  const d=await hole('/api/signaturen');
  const gruppen=Object.entries(d.gruppen||{}).sort((a,b)=>b[1].konten.length-a[1].konten.length);
  let html='<h2>Signaturen</h2>'+
    '<div class="hinweis" style="padding:0 0 12px">Eine Signatur gilt für alle Konten einer Gruppe — '+
    'die Gruppen ergeben sich aus dem Namensanfang (dekohuwelen-*, smartystech-* …).</div>';
  if(!gruppen.length){html+='<div class="hinweis">Keine Konten gefunden.</div>';box.innerHTML=html;return}
  html+='<div id="gruppenliste">';
  gruppen.forEach(([g,info])=>{
    const gesetzt=!!(info.html||'').trim();
    html+='<div class="siggruppe" onclick="signaturEdit(\''+esc(g)+'\')">'+
      '<div style="display:flex;justify-content:space-between;gap:10px">'+
        '<b>'+esc(g)+'</b>'+
        '<span style="font-size:12px;color:'+(gesetzt?'#5fd08a':'#ff7a7a')+'">'+
          (gesetzt?'Signatur gesetzt':'keine Signatur')+'</span>'+
      '</div>'+
      '<div style="font-size:12px;color:var(--muted);margin-top:2px">'+
        info.konten.length+(info.konten.length===1?' Konto: ':' Konten: ')+esc(info.konten.join(', '))+'</div>'+
    '</div>';
  });
  html+='</div><div id="signaturDetail"></div>';
  box.innerHTML=html;
}
async function signaturEdit(gruppe){
  const d=await hole('/api/signaturen');
  const info=(d.gruppen||{})[gruppe]||{konten:[],html:''};
  const detail=document.getElementById('signaturDetail');
  detail.innerHTML='<h2 style="margin-top:24px">Signatur: '+esc(gruppe)+'</h2>'+
    '<div class="hinweis" style="padding:0 0 10px">Gilt für: '+esc(info.konten.join(', '))+
    '. Feld leeren und speichern = keine Signatur für diese Gruppe.</div>'+
    '<div class="toolbar">'+
      '<button onmousedown="event.preventDefault();sigFmt(\'bold\')" title="Fett"><b>B</b></button>'+
      '<button onmousedown="event.preventDefault();sigFmt(\'italic\')" title="Kursiv"><i>I</i></button>'+
      '<button onmousedown="event.preventDefault();sigFmt(\'underline\')" title="Unterstrichen"><u>U</u></button>'+
      '<select onchange="sigFmtWert(\'fontSize\',this.value)"><option value="">Größe</option>'+
        '<option value="1">klein</option><option value="2">normal</option>'+
        '<option value="4">groß</option><option value="5">sehr groß</option></select>'+
      '<select onchange="sigFmtWert(\'fontName\',this.value)"><option value="">Schrift</option>'+
        '<option value="Arial">Arial</option><option value="Georgia">Georgia</option>'+
        '<option value="Courier New">Courier</option><option value="Verdana">Verdana</option></select>'+
      '<input type="color" value="#111111" onchange="sigFmtWert(\'foreColor\',this.value)" title="Schriftfarbe">'+
      '<input type="color" value="#ffff00" onchange="sigFmtWert(\'hiliteColor\',this.value)" title="Textmarker">'+
      '<button onmousedown="event.preventDefault();sigFmt(\'insertUnorderedList\')" title="Aufzählung">•</button>'+
      '<button onmousedown="event.preventDefault();sigFmt(\'removeFormat\')" title="Formatierung entfernen">×</button>'+
    '</div>'+
    '<div id="signaturEditor" contenteditable="true"></div>'+
    '<div class="senden-zeile">'+
      '<button onclick="signaturSpeichern(\''+esc(gruppe)+'\')">Speichern</button>'+
      '<button onclick="signaturVorschau()" style="background:#1c2740;color:var(--text);border:1px solid var(--rand)">Vorschau</button>'+
      '<span class="status" id="sigStatus"></span></div>'+
    '<div id="sigVorschau" style="display:none;margin-top:14px;padding:14px;background:#fff;color:#111;border-radius:5px"></div>';
  const ed=document.getElementById('signaturEditor');
  ed.innerHTML=info.html||(''+(
    gruppe==='dekojuwelen'?'<p><b>Andreas Smarz</b><br><span style="color:#c00000">dekojuwelen.de</span></p>':
    gruppe==='smartystech'?'<p><b>Andreas Smarz</b><br>smartys.tech</p>':
    '<p><b>Dein Name</b><br>deine-domain.de</p>'));
  ed.focus();
  detail.scrollIntoView({behavior:'smooth',block:'start'});
}
function sigFmt(b){document.getElementById('signaturEditor').focus();document.execCommand(b,false,null)}
function sigFmtWert(b,w){document.getElementById('signaturEditor').focus();document.execCommand(b,false,w)}
function signaturVorschau(){
  const v=document.getElementById('sigVorschau');
  v.innerHTML=document.getElementById('signaturEditor').innerHTML;
  v.style.display='block';
}
async function signaturSpeichern(gruppe){
  const st=document.getElementById('sigStatus');
  const html=document.getElementById('signaturEditor').innerHTML;
  st.className='status';st.textContent='speichere…';
  const r=await fetch('/api/signatur',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({gruppe:gruppe,html:html})});
  const d=await r.json();
  if(d.error){st.className='status fehler';st.textContent='Fehler: '+d.error;return}
  signaturCache=null;
  st.className='status ok';st.textContent='Gespeichert — gilt für alle Konten dieser Gruppe.';
}
async function senden(){
  if(!konto)return;
  const st=document.getElementById('sendestatus'),bt=document.getElementById('sendenbtn');
  const an=document.getElementById('fAn').value.trim();
  const cc=document.getElementById('fCc').value.trim();
  const betreff=document.getElementById('fBetreff').value.trim();
  const html=document.getElementById('editor').innerHTML;
  if(!an){st.className='status fehler';st.textContent='Empfänger fehlt';return}
  bt.disabled=true;st.className='status';st.textContent='sende…';
  try{
    const r=await fetch('/api/send',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({account:konto,an:an,cc:cc,betreff:betreff,html:html,
                           antwortAuf:mail,ordner:ordner})});
    const d=await r.json();
    if(d.error){st.className='status fehler';st.textContent='Fehler: '+d.error;bt.disabled=false;return}
    st.className='status ok';st.textContent='Gesendet.';
    setTimeout(()=>{const b=document.getElementById('editorbereich');if(b)b.innerHTML=''},2500);
  }catch(e){st.className='status fehler';st.textContent='Fehler: '+e;bt.disabled=false}
}
async function alsGelesen(){
  if(!mail)return;
  await fetch('/api/flag',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({account:konto,id:mail,mailbox:ordner})});
  ladeListe();
}
async function loeschen(){
  if(!mail)return;
  if(!confirm('Nachricht löschen?'))return;
  const r=await fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({account:konto,id:mail,mailbox:ordner})});
  const d=await r.json();
  if(d.error){alert('Fehler: '+d.error);return}
  document.getElementById('lesen').innerHTML='<div class="hinweis">Gelöscht.</div>';
  ladeListe();
}
let suchTimer=null;
document.getElementById('suche').addEventListener('input',e=>{
  clearTimeout(suchTimer);
  const q=e.target.value.trim();
  suchTimer=setTimeout(async()=>{
    if(!konto)return;
    const box=document.getElementById('liste');
    box.querySelectorAll('.mail,.ladehinweis').forEach(m=>m.remove());
    if(!q){ladeListe();return}
    document.getElementById('listenkopf').textContent=konto+' · Suche';
    const d=await hole('/api/search?account='+encodeURIComponent(konto)+'&q='+encodeURIComponent(q));
    if(d.error){box.insertAdjacentHTML('beforeend',
      '<div class="hinweis ladehinweis">Fehler: '+esc(d.error)+'</div>');return}
    (d.envelopes||[]).forEach(x=>box.appendChild(mailZeile(x)));
    if(!(d.envelopes||[]).length)
      box.insertAdjacentHTML('beforeend','<div class="hinweis ladehinweis">Nichts gefunden</div>');
  },450);
});
ladeKonten();
