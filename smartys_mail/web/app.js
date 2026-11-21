let konto=null, ordner='INBOX', mail=null, signaturCache=null;
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
async function hole(u){const r=await fetch(u);return r.json()}

/* Kurze Rueckmeldung unten einblenden — fuer Faelle, in denen kein eigenes
   Statusfeld in der Naehe ist (z. B. Umbenennen in der Kontenleiste). */
function zeigeHinweis(text){
  let box=document.querySelector('.hinweis-toast');
  if(!box){box=document.createElement('div');box.className='hinweis-toast';document.body.appendChild(box)}
  box.textContent=text;
  clearTimeout(zeigeHinweis._t);
  zeigeHinweis._t=setTimeout(()=>{box.remove()},4200);
}
async function verbindungEditor(){
  const box=document.getElementById('lesen');
  const v=await hole('/api/verbindung');
  const ssh=v.modus==='ssh';
  box.innerHTML=ui('<h2>Wo läuft himalaya?</h2>'+
    '<div class="hinweis" style="padding:0 0 14px">Die Oberfläche kann himalaya auf diesem '+
    'Rechner benutzen — oder auf einem anderen, auf dem deine Postfächer eingerichtet sind. '+
    'Im zweiten Fall bleiben die Zugangsdaten dort, und hier wird nur ein SSH-Zugang gebraucht.</div>'+
    '<div class="verfassen" style="border-top:0;padding-top:0;max-width:560px">'+
      '<label style="display:block;margin-bottom:6px;color:#a3b1c2;font-size:12.5px">'+
        '<input type="radio" name="vmodus" value="lokal" '+(ssh?'':'checked')+'> Auf diesem Rechner</label>'+
      '<label style="display:block;margin-bottom:12px;color:#a3b1c2;font-size:12.5px">'+
        '<input type="radio" name="vmodus" value="ssh" '+(ssh?'checked':'')+'> Auf einem anderen Rechner (SSH)</label>'+
      '<div id="sshFelder" style="display:'+(ssh?'block':'none')+'">'+
        '<input id="vZiel" placeholder="benutzer@rechner, z.B. benutzer@192.0.2.10" value="'+esc(v.ssh_ziel||'')+'">'+
        '<input id="vPfad" placeholder="Pfad zu himalaya dort (Standard: himalaya)" value="'+esc(v.himalaya_pfad||'himalaya')+'">'+
        '<div class="hinweis" style="padding:6px 0 10px;font-size:12px">Der öffentliche SSH-Schlüssel '+
          'dieses Rechners muss dort hinterlegt sein — sonst kommt keine Verbindung zustande.</div>'+
      '</div>'+
      '<label style="display:block;margin:14px 0 6px;color:#a3b1c2;font-size:12.5px">'+
        '<input type="checkbox" id="vBilder" '+(v.bilder_laden?'checked':'')+'> '+
        'Bilder aus Mails laden</label>'+
      '<div class="hinweis" style="padding:0 0 12px;font-size:12px">Aus: fremde Bilder bleiben '+
        'gesperrt. Ein eingebundenes Z&auml;hlpixel verr&auml;t dem Absender sonst, dass und wann '+
        'du die Mail ge&ouml;ffnet hast — bei Newslettern passiert genau das.</div>'+
      '<h3 style="margin:22px 0 8px;font-size:14px;color:#e8eef6">Übersetzer</h3>'+
      '<div class="hinweis" style="padding:0 0 8px;font-size:12px">Damit lässt sich eine '+
        'Nachricht auf Knopfdruck übersetzen. Ein lokales Sprachmodell (ollama) behält den '+
        'Text auf dem Rechner; ein LibreTranslate-Dienst schickt ihn an den eingetragenen Server.</div>'+
      '<select id="vUebDienst" style="width:100%;margin-bottom:8px">'+
        '<option value=""'+(v.uebersetzer?'':' selected')+'>— aus —</option>'+
        '<option value="ollama"'+(v.uebersetzer==='ollama'?' selected':'')+'>ollama (lokales Sprachmodell)</option>'+
        '<option value="libretranslate"'+(v.uebersetzer==='libretranslate'?' selected':'')+'>LibreTranslate</option>'+
      '</select>'+
      '<input id="vUebUrl" placeholder="Adresse, z.B. http://127.0.0.1:11434" value="'+esc(v.uebersetzer_url||'')+'">'+
      '<input id="vUebModell" placeholder="Modell (nur ollama), z.B. qwen2.5:7b" value="'+esc(v.uebersetzer_modell||'')+'">'+
      '<select id="vUebZiel" style="width:100%;margin-bottom:8px">'+
        ['Deutsch','Englisch','Französisch','Spanisch','Italienisch','Polnisch','Türkisch','Niederländisch']
          .map(function(s){return '<option value="'+s+'"'+((v.uebersetzer_ziel||'Deutsch')===s?' selected':'')+'>'+s+'</option>'}).join('')+
      '</select>'+
      '<h3 style="margin:22px 0 8px;font-size:14px;color:#e8eef6">'+t('Sprache der Oberfläche')+'</h3>'+
      '<select id="vSprache" style="width:100%;margin-bottom:8px">'+
        '<option value="de"'+(hgIstEnglisch()?'':' selected')+'>Deutsch</option>'+
        '<option value="en"'+(hgIstEnglisch()?' selected':'')+'>English</option>'+
      '</select>'+
      '<div class="senden-zeile"><button id="vSpeichern" onclick="verbindungSpeichern()">Speichern und prüfen</button>'+
        '<span class="status" id="vStatus"></span></div>'+
    '</div>');
  document.querySelectorAll('input[name=vmodus]').forEach(r=>{
    r.onchange=()=>{document.getElementById('sshFelder').style.display=
      (r.value==='ssh'&&r.checked)?'block':'none'};
  });
}
async function verbindungSpeichern(){
  const st=document.getElementById('vStatus'),bt=document.getElementById('vSpeichern');
  const modus=document.querySelector('input[name=vmodus]:checked').value;
  bt.disabled=true;st.className='status';st.textContent=t('prüfe…');
  const r=await fetch('/api/verbindung',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({modus:modus,
      ssh_ziel:document.getElementById('vZiel')?.value.trim()||'',
      bilder_laden: !!document.getElementById('vBilder')?.checked,
      uebersetzer:document.getElementById('vUebDienst')?.value||'',
      uebersetzer_url:document.getElementById('vUebUrl')?.value.trim()||'',
      uebersetzer_modell:document.getElementById('vUebModell')?.value.trim()||'',
      uebersetzer_ziel:document.getElementById('vUebZiel')?.value.trim()||'Deutsch',
      himalaya_pfad:document.getElementById('vPfad')?.value.trim()||'himalaya'})});
  const d=await r.json();
  bt.disabled=false;
  const sprache=document.getElementById('vSprache');
  if(sprache && sprache.value!==hgSprache()){hgSpracheSetzen(sprache.value);return}
  if(d.error){st.className='status fehler';st.textContent=d.error;return}
  if(d.erreichbar){
    st.className='status ok';
    st.textContent=hgIstEnglisch()
      ?('Connected — '+d.konten+' account'+(d.konten===1?'':'s')+' found. Reloading…')
      :('Verbunden — '+d.konten+' Konto'+(d.konten===1?'':'en')+' gefunden. Lade neu…');
    setTimeout(()=>{document.getElementById('kontenliste').innerHTML='lade…';ladeKonten()},1200);
  }else{
    st.className='status fehler';
    st.textContent=t('Gespeichert, aber keine Verbindung: ')+d.meldung;
  }
}
async function ladeKonten(){
  const d=await hole('/api/accounts');
  const el=document.getElementById('kontenliste');
  // "No configuration found" ist kein Defekt, sondern der Normalfall beim
  // ersten Start: dann gehoert der Einrichtungsassistent hin, nicht der
  // rohe Fehlertext von himalaya.
  const keineKonfig = d.error && /no configuration|config.*not found/i.test(d.error);
  if(d.error && !keineKonfig){el.textContent=t('Fehler: ')+d.error;return}
  el.innerHTML='';
  const liste=(d.accounts||[]);
  if(keineKonfig || !liste.length){kontoAssistent();return}

  // Nach Gruppen buendeln. Die Gruppe kommt vom Server aus der Domain, die
  // Reihenfolge bestimmt er ebenfalls — hier wird nur gezeichnet.
  const reihenfolge=[],nachGruppe={};
  liste.forEach(a=>{
    const g=a.gruppe||'';
    if(!nachGruppe[g]){nachGruppe[g]=[];reihenfolge.push(g)}
    nachGruppe[g].push(a);
  });
  // Gespeicherte Reihenfolge gilt; Gruppen, die dort noch nicht stehen,
  // haengen hinten an, statt zu verschwinden.
  const gespeichert=Array.isArray(d.ordnung)?d.ordnung:[];
  const sortiert=gespeichert.filter(g=>nachGruppe[g]);
  reihenfolge.forEach(g=>{if(sortiert.indexOf(g)<0)sortiert.push(g)});

  sortiert.forEach(g=>{
    const block=document.createElement('div');
    block.className='kontogruppe';
    if(g){
      const titel=document.createElement('div');
      titel.className='kontogruppe-titel';
      const pfeile=document.createElement('span');
      pfeile.className='gruppen-pfeile';
      [['▲',-1],['▼',1]].forEach(([zeichen,richtung])=>{
        const b=document.createElement('button');
        b.type='button';b.textContent=zeichen;
        b.title=richtung<0?t('Gruppe nach oben'):t('Gruppe nach unten');
        b.onclick=ev=>{ev.stopPropagation();gruppeVerschieben(g,richtung)};
        pfeile.appendChild(b);
      });
      const name=document.createElement('span');
      name.className='gruppenname';name.textContent=g;
      titel.appendChild(name);titel.appendChild(pfeile);
      titel.draggable=true;
      titel.addEventListener('dragstart',ev=>{
        gezogeneGruppe=g;
        ev.dataTransfer.setData('text/plain',g);
        ev.dataTransfer.effectAllowed='move';
        block.classList.add('wird-gezogen');
      });
      titel.addEventListener('dragend',()=>{
        gezogeneGruppe=null;
        document.querySelectorAll('.kontogruppe').forEach(x=>x.classList.remove('wird-gezogen','zielecke'));
      });
      block.appendChild(titel);
    }
    // Standardkonto nach oben, sonst nach Anzeigename — der Server liefert
    // alphabetisch nach Kontoname, und "dekojuwelen-ashley" vor "Dekojuwelen.de"
    // liest sich unordentlich.
    nachGruppe[g].sort((x,y)=>{
      if(!!y.default!==!!x.default)return y.default?1:-1;
      return String(x.display_name||x.name).localeCompare(String(y.display_name||y.name),'de');
    });
    nachGruppe[g].forEach(a=>block.appendChild(kontoZeile(a)));
    el.appendChild(block);
  });
}

/* Gruppenreihenfolge aendern — per Pfeil oder durch Ziehen der Ueberschrift.
   Gespeichert wird die Reihenfolge der Ueberschriften, wie sie gerade dastehen. */
let gezogeneGruppe=null;

function gruppenNamen(){
  return [...document.querySelectorAll('.kontogruppe-titel .gruppenname')].map(e=>e.textContent);
}

async function ordnungSpeichern(reihe){
  try{
    const r=await (await fetch('/api/konten/ordnung',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({ordnung:reihe})})).json();
    if(r.error){zeigeHinweis(r.error);return false}
  }catch(e){zeigeHinweis(String(e));return false}
  return true;
}

async function nachUmsortieren(){
  await ladeKonten();
  // Auswahl nicht verlieren: Konto wieder oeffnen, wenn es eines gab.
  if(konto){
    const el=document.querySelector('.konto[data-name="'+konto.replace(/"/g,'')+'"]');
    if(el)waehleKonto(konto,el);
  }
}

async function gruppeVerschieben(gruppe,richtung){
  const reihe=gruppenNamen();
  const i=reihe.indexOf(gruppe),j=i+richtung;
  if(i<0||j<0||j>=reihe.length)return;
  const merk=reihe[i];reihe[i]=reihe[j];reihe[j]=merk;
  if(!await ordnungSpeichern(reihe))return;
  await nachUmsortieren();
}

/* Ablegen auf einer anderen Gruppe: die gezogene Ueberschrift landet dort. */
document.addEventListener('dragover',ev=>{
  const block=ev.target.closest&&ev.target.closest('.kontogruppe');
  if(!block||!gezogeneGruppe)return;
  ev.preventDefault();
  document.querySelectorAll('.kontogruppe').forEach(b=>b.classList.remove('zielecke'));
  if((block.querySelector('.gruppenname')||{}).textContent!==gezogeneGruppe)block.classList.add('zielecke');
});

document.addEventListener('drop',async ev=>{
  const block=ev.target.closest&&ev.target.closest('.kontogruppe');
  if(!block||!gezogeneGruppe)return;
  ev.preventDefault();
  const ziel=(block.querySelector('.gruppenname')||{}).textContent;
  const reihe=gruppenNamen().filter(g=>g!==gezogeneGruppe);
  const pos=reihe.indexOf(ziel);
  reihe.splice(pos<0?reihe.length:pos,0,gezogeneGruppe);
  gezogeneGruppe=null;
  document.querySelectorAll('.kontogruppe').forEach(b=>b.classList.remove('zielecke','wird-gezogen'));
  await ordnungSpeichern(reihe);
  await nachUmsortieren();
});

/* Eine Zeile der Kontenliste: Anzeigename oben, Adresse klein darunter.
   Die Adresse ist wichtiger als der Name — jeder kann sich "Bank" nennen. */
function kontoZeile(a){
  const div=document.createElement('div');
  div.className='konto';div.dataset.name=a.name;
  div.innerHTML='<span class="konto-kopf"><span class="kontoname">'+
      esc(a.display_name||a.name)+'</span>'+
      (a.default?'<span class="standard" title="'+t('Standardkonto')+'">★</span>':'')+
    '</span>'+
    '<span class="kontoadresse">'+esc(a.email||a.name)+'</span>';
  const stift=document.createElement('button');
  stift.type='button';stift.className='umbenennen';
  stift.title=t('Anzeigename ändern');stift.textContent='✎';
  stift.onclick=ev=>{ev.stopPropagation();kontoUmbenennen(a,div)};
  div.appendChild(stift);
  div.onclick=()=>kontoKlick(a,div);
  return div;
}

/* Anzeigename an Ort und Stelle aendern. Der Kontoname (der Schluessel in
   himalaya) bleibt unangetastet, sonst verlieren Signatur-Gruppen und
   Mailbox-Aliase ihren Bezug. */
function kontoUmbenennen(a,div){
  const alt=a.display_name||a.name;
  const feld=document.createElement('input');
  feld.className='konto-feld';feld.type='text';feld.value=alt;
  feld.setAttribute('aria-label',t('Anzeigename'));
  const nameEl=div.querySelector('.kontoname');
  nameEl.replaceWith(feld);
  feld.focus();feld.select();
  let erledigt=false;
  const zurueck=(wert)=>{
    const span=document.createElement('span');
    span.className='kontoname';span.textContent=wert;
    feld.replaceWith(span);
  };
  const beenden=async(speichern)=>{
    if(erledigt)return;erledigt=true;
    const neu=(feld.value||'').trim();
    if(!speichern||!neu||neu===alt){zurueck(alt);return}
    let r={};
    try{
      r=await (await fetch('/api/konto/anzeigename',{method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({account:a.name,anzeigename:neu})})).json();
    }catch(e){r={error:String(e)}}
    if(r.error){zurueck(alt);zeigeHinweis(r.error);return}
    a.display_name=neu;zurueck(neu);
  };
  feld.onkeydown=ev=>{
    if(ev.key==='Enter'){ev.preventDefault();beenden(true)}
    else if(ev.key==='Escape'){ev.preventDefault();beenden(false)}
  };
  feld.onblur=()=>beenden(true);
}

/* ---------------------------------------------------------------- Konten */
async function kontoAssistent(){
  const box=document.getElementById('lesen');
  box.innerHTML=ui('<h2>Konto einrichten</h2>'+
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
    '</div>');
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
    st.className='status fehler';st.textContent=t('E-Mail und Passwort sind nötig.');return;
  }
  bt.disabled=true;st.className='status';st.textContent=t('prüfe Zugangsdaten…');
  const r=await fetch('/api/konto/anlegen',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(daten)});
  const d=await r.json();
  bt.disabled=false;
  if(d.error){st.className='status fehler';st.textContent=d.error;return}
  st.className='status ok';
  st.textContent=hgIstEnglisch()
    ?('Account “'+d.name+'” set up. Reloading…')
    :('Konto „'+d.name+'" eingerichtet. Lade neu…');
  setTimeout(()=>{document.getElementById('kontenliste').innerHTML='lade…';ladeKonten()},1200);
}
/* Ein Klick oeffnet das Konto samt Ordnern, ein zweiter Klick auf dasselbe
   Konto schliesst es wieder — die Liste wird sonst lang und laesst sich nicht
   mehr zuklappen. */
function kontoKlick(a,div){
  if(konto===a.name && div.classList.contains('aktiv')){kontoSchliessen(div);return}
  waehleKonto(a.name,div);
}

function kontoSchliessen(div){
  konto=null;mail=null;
  document.querySelectorAll('.konto').forEach(k=>k.classList.remove('aktiv'));
  if(div)div.classList.remove('aktiv');
  document.querySelectorAll('.ordnerblock').forEach(b=>b.remove());
  document.getElementById('listenkopf').textContent='';
  const liste=document.getElementById('liste');
  liste.querySelectorAll('.mail,.ladehinweis').forEach(m=>m.remove());
  document.getElementById('lesen').innerHTML=ui('<div class="hinweis">'+t('Konto wählen')+'</div>');
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
  if(d.error){box.insertAdjacentHTML('beforeend',ui(
    '<div class="hinweis ladehinweis">Fehler: '+esc(d.error)+'</div>'));return}
  (d.envelopes||[]).forEach(e=>box.appendChild(mailZeile(e)));
  if(!(d.envelopes||[]).length)
    box.insertAdjacentHTML('beforeend',ui('<div class="hinweis ladehinweis">Keine Nachrichten</div>'));
}
const ORDNER_DE={'inbox':'Posteingang','sent':'Gesendet','sent items':'Gesendet',
 'sent messages':'Gesendet','drafts':'Entwürfe','trash':'Papierkorb',
 'deleted items':'Papierkorb','junk':'Spam','junk mail':'Spam','spam':'Spam',
 'archive':'Archiv','archives':'Archiv','outbox':'Postausgang'};
const ORDNER_EN={'inbox':'Inbox','sent':'Sent','sent items':'Sent',
 'sent messages':'Sent','drafts':'Drafts','trash':'Trash',
 'deleted items':'Trash','junk':'Junk','junk mail':'Junk','spam':'Junk',
 'archive':'Archive','archives':'Archive','outbox':'Outbox'};
function ordnerName(name){
  const k=(name||'').toLowerCase();
  const tabelle=hgIstEnglisch()?ORDNER_EN:ORDNER_DE;
  return tabelle[k]||name;
}
function zeitKurz(iso){
  const d=new Date(iso);
  if(isNaN(d))return (iso||'').slice(11,16);
  const jetzt=new Date();
  const gleichTag=d.toDateString()===jetzt.toDateString();
  const gestern=new Date(jetzt); gestern.setDate(jetzt.getDate()-1);
  const sprache=hgDatumLocale();
  if(gleichTag)return d.toLocaleTimeString(sprache,{hour:'2-digit',minute:'2-digit'});
  if(d.toDateString()===gestern.toDateString())return t('gestern');
  if(jetzt-d<6*86400000)return d.toLocaleDateString(sprache,{weekday:'short'})+'.';
  return d.toLocaleDateString(sprache,{day:'2-digit',month:'2-digit',year:'2-digit'});
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
  const fertig=()=>{const alt=el.textContent;el.textContent=t('kopiert');el.classList.add('kopiert');
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
  const sprache=hgDatumLocale();
  return d.toLocaleDateString(sprache,{day:'2-digit',month:'2-digit',year:'numeric'})+
         ', '+d.toLocaleTimeString(sprache,{hour:'2-digit',minute:'2-digit'})+t(' Uhr');
}
function initialen(name){
  const sauber=(name||'?').replace(/["'<>,]/g,'').trim();
  const teile=sauber.split(/[\s.@_-]+/).filter(Boolean);
  if(!teile.length)return '?';
  if(teile.length===1)return teile[0].slice(0,1).toUpperCase();
  return (teile[0][0]+teile[1][0]).toUpperCase();
}
function istGelesen(e){
  // himalaya liefert flags entweder als Strings ("seen") oder als Objekte
  // ({raw:"\\Seen", iana:"seen"}). Fruher wurde nur auf "flags nicht leer"
  // geprueft — damit galt eine markierte, aber ungelesene Mail ($\Flagged ohne
  // $\Seen) faelschlich als gelesen.
  return (e.flags||[]).some(f=>{
    const n=(typeof f==='string'?f:(f.iana||f.raw||'')).toLowerCase();
    return n.indexOf('seen')>=0;
  });
}
function mailZeile(e){
  const abs=(e.from&&e.from[0])||{};
  const name=(abs.name||'').trim();
  const adresse=(abs.email||'').trim();
  // Zur Spam-Erkennung gehoert die echte Adresse, nicht nur der Anzeigename:
  // jeder kann sich "Sparkasse" nennen. Steht ein Name da, wird die Adresse
  // darunter gezeigt; ohne Namen ist sie selbst die erste Zeile.
  const oben=name||adresse||t('(unbekannt)');
  const div=document.createElement('div');
  div.className='mail'+(istGelesen(e)?'':' ungelesen');
  div.innerHTML='<div class="von"><span title="'+esc(oben)+'">'+esc(oben)+'</span>'+
      '<span>'+esc(zeitKurz(e.date))+'</span></div>'+
    (name&&adresse?'<div class="adresse" title="'+esc(adresse)+'">'+esc(adresse)+'</div>':'')+
    '<div class="betreff">'+esc(e.subject||t('(ohne Betreff)'))+'</div>';
  div.onclick=()=>lese(e.id,div,e);
  return div;
}
async function lese(id,el,env){
  mail=id;
  document.querySelectorAll('.mail').forEach(m=>m.classList.remove('aktiv'));
  if(el)el.classList.add('aktiv');
  const box=document.getElementById('lesen');
  box.innerHTML=ui('<div class="hinweis">lade…</div>');
  const d=await hole('/api/read?account='+encodeURIComponent(konto)+'&id='+encodeURIComponent(id)+
                     '&mailbox='+encodeURIComponent(ordner));
  if(d.error){box.innerHTML=ui('<div class="hinweis">Fehler: '+esc(d.error)+'</div>');return}
  // Betreff/Absender aus der Liste als Rueckfall: die Lese-API liefert sie
  // gelegentlich nicht (anderer Ordnername, exotische Mail).
  const envBetreff=(env&&env.subject)||'';
  const envVon=(env&&env.from&&env.from[0])?(env.from[0].name?env.from[0].name+(env.from[0].email?' <'+env.from[0].email+'>':''):(env.from[0].email||'')):'';
  const betreff=d.subject||envBetreff||'';
  const von=d.from||envVon||'';
  const anhangHtml=anhangListe(konto,id,ordner,d.anhaenge||[],!!d.virenscanner);
  box.innerHTML='<h2>'+esc(betreff||t('(ohne Betreff)'))+'</h2>'+
    '<div class="meta">'+absenderKopf(von)+'  ·  '+esc(zeitLang(d.date))+'</div>'+
    anhangHtml+
    ui('<div class="knopfleiste">'+
      '<button onclick="antworten()" title="Antworten (A)">\u21a9 Antworten</button>'+
      '<button onclick="weiterleiten()" title="Weiterleiten (W)">\u21aa Weiterleiten</button>'+
      '<button onclick="alsGelesen()" title="Als gelesen oder ungelesen markieren">\u25cf Gelesen</button>'+
      '<button onclick="loeschen()" title="In den Papierkorb (Entf)">\u2715 Löschen</button>'+
      '<button onclick="uebersetzen()" title="Nachricht übersetzen">\u21c4 Übersetzen</button>'+
    '</div>')+
    mailansicht(d)+
    '<div id="uebersetzung"></div>'+
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
  return ui('<div class="verfassen">'+
    '<input id="fAn" spellcheck="false" autocapitalize="off" placeholder="An (mehrere mit Komma trennen)">'+
    '<input id="fCc" placeholder="Cc (optional)">'+
    '<input id="fBetreff" spellcheck="true" placeholder="Betreff">'+
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
    '<div id="editor" contenteditable="true" spellcheck="true" lang="de"></div>'+
    '<div class="senden-zeile"><button id="sendenbtn" onclick="senden()">Senden</button>'+
      '<span class="status" id="sendestatus"></span></div></div>');
}
function fmt(b){document.getElementById('editor').focus();document.execCommand(b,false,null)}
function fmtWert(b,w){document.getElementById('editor').focus();document.execCommand(b,false,w)}
function linkEinfuegen(){
  const u=prompt(t('Adresse (https://…):'));if(!u)return;
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
  return '<p><br></p><p style="color:#888">'+t('----- Ursprüngliche Nachricht -----')+'<br>'+
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
  if(!konto){alert(t('Erst ein Konto wählen'));return}
  mail=null;
  document.getElementById('lesen').innerHTML=ui('<h2>Neue Nachricht</h2><div id="editorbereich"></div>');
  oeffneEditor({});
}
async function signaturBearbeiten(){
  const box=document.getElementById('lesen');
  box.innerHTML=ui('<div class="hinweis">lade…</div>');
  const d=await hole('/api/signaturen');
  const gruppen=Object.entries(d.gruppen||{}).sort((a,b)=>b[1].konten.length-a[1].konten.length);
  let html=ui('<h2>Signaturen</h2>'+
    '<div class="hinweis" style="padding:0 0 12px">Eine Signatur gilt für alle Konten einer Gruppe — '+
    'die Gruppen ergeben sich aus dem Namensanfang (dekohuwelen-*, smartystech-* …).</div>');
  if(!gruppen.length){html+='<div class="hinweis">Keine Konten gefunden.</div>';box.innerHTML=html;return}
  html+='<div id="gruppenliste">';
  gruppen.forEach(([g,info])=>{
    const gesetzt=!!(info.html||'').trim();
    html+='<div class="siggruppe" onclick="signaturEdit(\''+esc(g)+'\')">'+
      '<div style="display:flex;justify-content:space-between;gap:10px">'+
        '<b>'+esc(g)+'</b>'+
        '<span style="font-size:12px;color:'+(gesetzt?'#5fd08a':'#ff7a7a')+'">'+
          (gesetzt?t('Signatur gesetzt'):t('keine Signatur'))+'</span>'+
      '</div>'+
      '<div style="font-size:12px;color:var(--muted);margin-top:2px">'+
        info.konten.length+t(info.konten.length===1?' Konto: ':' Konten: ')+esc(info.konten.join(', '))+'</div>'+
    '</div>';
  });
  html+='</div><div id="signaturDetail"></div>';
  box.innerHTML=html;
}
async function signaturEdit(gruppe){
  const d=await hole('/api/signaturen');
  const info=(d.gruppen||{})[gruppe]||{konten:[],html:''};
  const detail=document.getElementById('signaturDetail');
  detail.innerHTML=ui('<h2 style="margin-top:24px">Signatur: '+esc(gruppe)+'</h2>'+
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
    '<div id="sigVorschau" style="display:none;margin-top:14px;padding:14px;background:#fff;color:#111;border-radius:5px"></div>');
  const ed=document.getElementById('signaturEditor');
  ed.innerHTML=info.html||(''+(
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
  st.className='status';st.textContent=t('speichere…');
  const r=await fetch('/api/signatur',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({gruppe:gruppe,html:html})});
  const d=await r.json();
  if(d.error){st.className='status fehler';st.textContent=t('Fehler: ')+d.error;return}
  signaturCache=null;
  st.className='status ok';st.textContent=t('Gespeichert — gilt für alle Konten dieser Gruppe.');
}
async function senden(){
  if(!konto)return;
  const st=document.getElementById('sendestatus'),bt=document.getElementById('sendenbtn');
  const an=document.getElementById('fAn').value.trim();
  const cc=document.getElementById('fCc').value.trim();
  const betreff=document.getElementById('fBetreff').value.trim();
  const html=document.getElementById('editor').innerHTML;
  if(!an){st.className='status fehler';st.textContent=t('Empfänger fehlt');return}
  bt.disabled=true;st.className='status';st.textContent=t('sende…');
  try{
    const r=await fetch('/api/send',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({account:konto,an:an,cc:cc,betreff:betreff,html:html,
                           antwortAuf:mail,ordner:ordner})});
    const d=await r.json();
    if(d.error){st.className='status fehler';st.textContent=t('Fehler: ')+d.error;bt.disabled=false;return}
    st.className='status ok';st.textContent=t('Gesendet.');
    setTimeout(()=>{const b=document.getElementById('editorbereich');if(b)b.innerHTML=''},2500);
  }catch(e){st.className='status fehler';st.textContent=t('Fehler: ')+e;bt.disabled=false}
}
async function alsGelesen(){
  if(!mail)return;
  // Umschalten: Der Knopf soll gelesene Post ungelesen machen und umgekehrt.
  // Frueher wurde ohne "gelesen" gesendet; der Server konnte daraus keinen
  // Zielzustand ableiten und setzte faktisch immer nur "seen" (nie zurueck).
  const zeile=document.querySelector('.mail.aktiv');
  const jetztGelesen=!(zeile&&zeile.classList.contains('ungelesen'));
  const ziel=!jetztGelesen;
  const r=await fetch('/api/flag',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({account:konto,id:mail,mailbox:ordner,gelesen:ziel})});
  const d=await r.json().catch(()=>({}));
  if(d.error){alert(t('Fehler: ')+d.error);return}
  if(zeile){
    if(ziel)zeile.classList.remove('ungelesen');else zeile.classList.add('ungelesen');
  }
  ladeListe();
}
async function loeschen(){
  if(!mail)return;
  if(!confirm(t('Nachricht löschen?')))return;
  const r=await fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({account:konto,id:mail,mailbox:ordner})});
  const d=await r.json();
  if(d.error){alert(t('Fehler: ')+d.error);return}
  document.getElementById('lesen').innerHTML=ui('<div class="hinweis">Gelöscht.</div>');
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
    document.getElementById('listenkopf').textContent=konto+t(' · Suche');
    const d=await hole('/api/search?account='+encodeURIComponent(konto)+'&q='+encodeURIComponent(q));
    if(d.error){box.insertAdjacentHTML('beforeend',ui(
      '<div class="hinweis ladehinweis">Fehler: '+esc(d.error)+'</div>'));return}
    (d.envelopes||[]).forEach(x=>box.appendChild(mailZeile(x)));
    if(!(d.envelopes||[]).length)
      box.insertAdjacentHTML('beforeend',ui('<div class="hinweis ladehinweis">Nichts gefunden</div>'));
  },450);
});
ladeKonten();

/* ---------------------------------------------------------------
   Mailinhalt darstellen. Zwei Faelle:

   * HTML-Mail: sandboxed iframe mit srcdoc. Skripte sind im HTML
     bereits entfernt (mime._entschaerfen), hier kommt die zweite
     Sperre: ohne allow-scripts laeuft nichts, ohne allow-same-origin
     kommt das Dokument nicht an die Oberflaeche. Links bleiben
     klickbar und oeffnen im Systembrowser (base target=_blank).
     Bilder sind per CSP gesperrt — ein geladenes Zaehlpixel verraet
     dem Absender sofort, dass und wann die Mail gelesen wurde.

   * Nur Text: <pre>, wie bisher.
   --------------------------------------------------------------- */
function mailansicht(d){
  if(d && d.body_html && d.body_html.length>60){
    return '<iframe class="mailhtml" sandbox="allow-same-origin allow-popups allow-popups-to-escape-sandbox" '+
           'referrerpolicy="no-referrer" srcdoc="'+esc(docMitCsp(d.body_html, d.bilder_laden))+'">'+
           '</iframe>';
  }
  return '<pre class="body">'+esc((d&&d.body)||'')+'</pre>';
}

function docMitCsp(html, bilderLaden){
  // Bilder nur laden, wenn der Nutzer es in den Einstellungen erlaubt hat.
  // Sonst verraet ein Zaehlpixel dem Absender sofort, dass die Mail offen ist.
  const bildQuellen = bilderLaden ? "img-src data: https: http:;"
                                  : "img-src data:;";
  const kopf = '<meta http-equiv="Content-Security-Policy" content="' +
    "default-src 'none'; style-src 'unsafe-inline'; " + bildQuellen +
    ' font-src data: https:">' +
    '<base target="_blank">' +
    '<style>body{font-family:system-ui,-apple-system,sans-serif;font-size:14px;'+
    'line-height:1.55;color:#e8e8ea;background:transparent;margin:0;padding:2px;'+
    'word-wrap:break-word}a{color:#ffc94d}img{max-width:100%;height:auto}'+
    'table{max-width:100%;border-collapse:collapse;font-size:13px}'+
    'td,th{padding:3px 6px}blockquote{border-left:3px solid #444;margin:8px 0;'+
    'padding-left:10px;color:#aaa}</style>';
  if(/<head[^>]*>/i.test(html)){
    return html.replace(/<head([^>]*)>/i,'<head$1>'+kopf);
  }
  if(/<html[^>]*>/i.test(html)){
    return html.replace(/<html([^>]*)>/i,'<html$1><head>'+kopf+'</head>');
  }
  return kopf+html;
}

function mailhtmlHoehe(rahmen){
  // Bewusst KEINE automatische Hoehenanpassung: die Messung ueber
  // contentDocument war unzuverlaessig (3829 px fuer 269 Zeichen Text,
  // je nach Layout und Messzeitpunkt). Der Rahmen bekommt stattdessen eine
  // feste Hoehe und einen eigenen Scrollbalken — so verhalten sich
  // Mailprogramme auch, und sehr lange Newsletter bleiben bedienbar.
  rahmen.style.height = "";
}


/* ---- Uebersetzer ------------------------------------------------------ */
async function uebersetzen(){
  const box=document.getElementById('uebersetzung');
  if(!box)return;
  const m=window._letzte||{};
  const text=(m.body||'').trim();
  if(!text){
    box.innerHTML=ui('<div class="uebersetzung fehler">Kein Text zum Übersetzen gefunden.</div>');
    return;
  }
  box.innerHTML=ui('<div class="uebersetzung">übersetze…</div>');
  let d;
  try{
    const r=await fetch('/api/uebersetzen',{method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({text:text})});
    d=await r.json();
  }catch(e){
    box.innerHTML=ui('<div class="uebersetzung fehler">Der Dienst antwortet nicht.</div>');
    return;
  }
  if(d.error){
    box.innerHTML='<div class="uebersetzung fehler">'+esc(d.error)+'</div>';
    return;
  }
  box.innerHTML=ui('<div class="uebersetzung"><div class="ueberkopf">Übersetzung'+
    '<button class="ueberschliessen" onclick="uebersetzungSchliessen()">schließen</button>'+
    '</div>')+'<pre>'+esc(d.uebersetzt||'')+'</pre></div>';
}

function uebersetzungSchliessen(){
  const b=document.getElementById('uebersetzung');
  if(b)b.innerHTML='';
}

/* ------------------------------------------------------------- Anhänge */
function dateiGroesse(b){
  b=Number(b)||0;
  if(!b)return '';
  if(b<1024)return b+' B';
  if(b<1024*1024)return (b/1024).toFixed(0)+' KB';
  return (b/1048576).toFixed(1).replace('.',',')+' MB';
}

/* Vorschau im Fenster geht fuer PDF, Bilder und Text. Alles andere wird
   heruntergeladen — ein Word-Dokument kann der Browser nicht darstellen. */
function anhangArt(a){
  const mime=(a.mime||'').toLowerCase();
  const name=(a.name||'').toLowerCase();
  if(mime==='application/pdf'||name.endsWith('.pdf'))return 'pdf';
  if(mime.startsWith('image/')||/\.(png|jpe?g|gif|webp|bmp|svg)$/.test(name))return 'bild';
  if(mime.startsWith('text/')||/\.(txt|csv|log|md)$/.test(name))return 'text';
  return 'sonst';
}

function anhangSymbol(art){
  return art==='pdf'?'\ud83d\udcc4':art==='bild'?'\ud83d\uddbc\ufe0f':
         art==='text'?'\ud83d\udcc3':'\ud83d\udcc1';
}

function anhangUrl(konto,id,ordner,teil,namen){
  return '/api/attachment?account='+encodeURIComponent(konto)+
    '&id='+encodeURIComponent(id)+'&mailbox='+encodeURIComponent(ordner)+
    (teil!==undefined&&teil!==null&&teil!==''?'&teil='+encodeURIComponent(teil):'')+
    (namen?'&vorschau=1':'');
}

function anhangListe(konto,id,ordner,liste,scanner){
  if(!liste.length)return '';
  const zeilen=liste.map(a=>{
    const art=anhangArt(a);
    const name=a.name||(t('Anhang'));
    const vorschau=(art!=='sonst');
    return '<div class="anhang">'+
      '<span class="anhang-symbol" aria-hidden="true">'+anhangSymbol(art)+'</span>'+
      '<span class="anhang-text"><span class="anhang-name">'+esc(name)+'</span>'+
        '<span class="anhang-groesse">'+esc(dateiGroesse(a.size))+'</span></span>'+
      (vorschau
        ? '<button type="button" class="anhang-knopf" '+
          'onclick="anhangVorschau(\''+esc(konto)+'\',\''+esc(id)+'\',\''+esc(ordner)+
          '\',\''+esc(a.id)+'\',\''+esc(name).replace(/'/g,'')+'\')">Vorschau</button>'
        : '')+
      '<a class="anhang-knopf" href="'+anhangUrl(konto,id,ordner,a.id,false)+'">Herunterladen</a>'+
    '</div>';
  }).join('');
  return '<div class="anhaenge"><b>'+t('Anhänge')+' ('+liste.length+')</b>'+zeilen+
    (scanner?'':'<div class="anhang-warnung">Kein Virenscanner installiert — '+
      'Anhänge werden beim Öffnen nicht geprüft.</div>')+'</div>';
}

/* Eigenes Vorschaufenster: laedt den Anhang einmal, zeigt den Pruefstand aus
   dem Kopf der Antwort und stellt die Daten als Blob dar. So laeuft jede
   Vorschau durch dieselbe Virenpruefung wie der Download — und ein Fund wird
   als Meldung gezeigt statt als leeres Fenster. */
async function anhangVorschau(konto,id,ordner,teil,name){
  const url=anhangUrl(konto,id,ordner,teil,true);
  let antwort;
  try{
    antwort=await fetch(url);
  }catch(e){zeigeHinweis('Anhang nicht abrufbar: '+e);return}
  if(!antwort.ok){
    let meldung='Anhang nicht abrufbar ('+antwort.status+')';
    try{const j=await antwort.json();if(j&&j.error)meldung=j.error}catch(e){}
    zeigeHinweis(meldung);return
  }
  const stand=(antwort.headers.get('X-Virenscan')||'').toLowerCase();
  const blob=await antwort.blob();
  const quelle=URL.createObjectURL(blob);
  const art=anhangArt({name:name});
  const rahmen=art==='pdf'
    ? '<iframe class="vorschau-rahmen" src="'+quelle+'" title="'+esc(name)+'"></iframe>'
    : '<img class="vorschau-bild" src="'+quelle+'" alt="'+esc(name)+'">';
  const hinweis=stand==='sauber'?'<span class="vorschau-scan gut">virengeprüft</span>'
    :stand==='infiziert'?'<span class="vorschau-scan schlecht">Fund gemeldet</span>'
    :'<span class="vorschau-scan offen">nicht geprüft</span>';
  const box=document.createElement('div');
  box.className='vorschau-overlay';
  box.innerHTML='<div class="vorschau-fenster" role="dialog" aria-label="'+esc(name)+'">'+
      '<div class="vorschau-kopf"><span class="vorschau-name">'+esc(name)+'</span>'+hinweis+
        '<a class="vorschau-knopf" href="'+url+'" target="_blank" rel="noopener">Im Browser öffnen</a>'+
        '<a class="vorschau-knopf" href="'+anhangUrl(konto,id,ordner,teil,false)+'">Herunterladen</a>'+
        '<button type="button" class="vorschau-schliessen" title="Schließen (Esc)">\u2715</button>'+
      '</div>'+rahmen+
    '</div>';
  const schliessen=()=>{
    box.remove();URL.revokeObjectURL(quelle);document.removeEventListener('keydown',taste);
  };
  const taste=ev=>{if(ev.key==='Escape')schliessen()};
  box.addEventListener('click',ev=>{if(ev.target===box)schliessen()});
  box.querySelector('.vorschau-schliessen').onclick=schliessen;
  document.addEventListener('keydown',taste);
  document.body.appendChild(box);
}
