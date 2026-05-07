import re

INFILE  = '/sessions/gallant-eager-thompson/mnt/outputs/cotizador_simple_clima_v14.html'
OUTFILE="/sessions/gallant-eager-thompson/mnt/outputs/cotizador_v14_new.html"

with open(INFILE, 'r', encoding='utf-8') as f:
    src = f.read()

# ─────────────────────────────────────────────
# 1. CSS NUEVAS REGLAS  (insertar antes de </style>)
# ─────────────────────────────────────────────
NEW_CSS = """
/* ===== GESTOR DE PRESUPUESTOS ===== */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.65);z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;}
.modal-box{background:#fff;border-radius:10px;width:100%;max-width:640px;max-height:85vh;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.4);}
.modal-hdr{background:var(--n);padding:14px 20px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;}
.modal-hdr h3{color:#fff;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;margin:0;}
.modal-close{background:none;border:none;color:#777;font-size:22px;cursor:pointer;line-height:1;padding:0 2px;}
.modal-close:hover{color:#fff;}
.modal-body{padding:16px;overflow-y:auto;flex:1;}
.budget-item{display:flex;align-items:center;gap:10px;padding:11px 14px;border:1.5px solid var(--br);border-radius:7px;margin-bottom:8px;background:#fafafa;transition:all .15s;}
.budget-item:hover{border-color:var(--v);background:#f5fbea;}
.budget-info{flex:1;min-width:0;}
.budget-name{font-size:13px;font-weight:700;color:var(--n);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.budget-meta{font-size:10px;color:#aaa;margin-top:3px;}
.budget-actions{display:flex;gap:6px;flex-shrink:0;}
.budget-empty{text-align:center;padding:36px 20px;color:#bbb;font-size:12px;}
.budget-empty .bi{font-size:32px;margin-bottom:8px;}

/* ===== TOAST ===== */
#toast_notif{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(20px);background:var(--n);color:#fff;padding:10px 22px;border-radius:6px;font-size:12px;font-weight:700;z-index:3000;opacity:0;transition:opacity .3s,transform .3s;pointer-events:none;border-left:4px solid var(--v);}
#toast_notif.show{opacity:1;transform:translateX(-50%) translateY(0);}

/* ===== PREVIEW DRAWER ===== */
.preview-toggle{position:fixed;right:0;top:50%;transform:translateY(-50%);background:var(--v);color:var(--n);border:none;border-radius:8px 0 0 8px;padding:12px 7px;cursor:pointer;font-family:var(--f);font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;writing-mode:vertical-rl;text-orientation:mixed;z-index:900;box-shadow:-3px 0 10px rgba(0,0,0,.2);transition:background .2s;}
.preview-toggle:hover{background:#7aaa20;}
.preview-toggle.open-state{background:#555;color:#fff;border-radius:0 8px 8px 0;right:auto;left:0;box-shadow:3px 0 10px rgba(0,0,0,.2);}
.preview-drawer{position:fixed;right:-46%;top:0;width:46%;height:100vh;background:#f7f7f7;border-left:3px solid var(--v);z-index:890;transition:right .3s cubic-bezier(.4,0,.2,1);box-shadow:-4px 0 24px rgba(0,0,0,.15);display:flex;flex-direction:column;}
.preview-drawer.open{right:0;}
.preview-dhdr{background:var(--n);padding:10px 16px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;}
.preview-dhdr h3{color:#fff;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;margin:0;}
.preview-status{font-size:10px;font-weight:700;color:var(--v);}
.preview-scroll{flex:1;overflow-y:auto;padding:14px 10px;background:#f0f0f0;}
.preview-scale-wrap{background:#fff;transform-origin:top left;box-shadow:0 2px 12px rgba(0,0,0,.12);border-radius:4px;overflow:hidden;}
.preview-empty{text-align:center;padding:50px 20px;color:#bbb;font-size:12px;line-height:1.8;}

/* ===== HEADER BUTTONS ===== */
.hdr-actions{display:flex;gap:6px;align-items:center;}
.hdr-btn{font-family:var(--f);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;padding:6px 13px;border-radius:4px;border:1.5px solid #444;background:transparent;color:#aaa;cursor:pointer;transition:all .15s;display:flex;align-items:center;gap:5px;}
.hdr-btn:hover{border-color:var(--v);color:var(--v);}
.hdr-btn.save{border-color:var(--v);color:var(--v);}
.hdr-btn.save:hover{background:var(--v);color:var(--n);}
"""

src = src.replace('</style>', NEW_CSS + '\n</style>', 1)

# ─────────────────────────────────────────────
# 2. BOTONES EN EL HEADER
# ─────────────────────────────────────────────
HDR_BUTTONS = """  <div class="hdr-actions">
    <button class="hdr-btn save" onclick="saveCurrentBudget()">💾 Guardar</button>
    <button class="hdr-btn" onclick="openGestor()">📂 Presupuestos</button>
  </div>
"""
# Reemplazar el cierre del .hdr-l y el mode-wrap
src = src.replace(
    '  <div class="mode-wrap">',
    HDR_BUTTONS + '  <div class="mode-wrap">',
    1
)

# ─────────────────────────────────────────────
# 3. HTML MODAL + PREVIEW DRAWER  (antes de </body>)
# ─────────────────────────────────────────────
MODAL_HTML = """
<!-- TOAST NOTIFICATION -->
<div id="toast_notif"></div>

<!-- MODAL GESTOR DE PRESUPUESTOS -->
<div class="modal-overlay" id="modal_gestor" style="display:none;" onclick="if(event.target===this)closeGestor()">
  <div class="modal-box">
    <div class="modal-hdr">
      <h3>📂 Presupuestos Guardados</h3>
      <button class="modal-close" onclick="closeGestor()">✕</button>
    </div>
    <div class="modal-body">
      <button class="btn btn-v" onclick="saveCurrentBudget()" style="width:100%;justify-content:center;margin-bottom:14px;">💾 Guardar Presupuesto Actual</button>
      <div id="budget_list"></div>
    </div>
  </div>
</div>

<!-- PREVIEW DRAWER -->
<button class="preview-toggle" id="preview_toggle_btn" onclick="togglePreview()">Vista&#10;Previa</button>
<div class="preview-drawer" id="preview_drawer">
  <div class="preview-dhdr">
    <h3>👁 Vista Previa</h3>
    <span class="preview-status" id="preview_status">—</span>
  </div>
  <div class="preview-scroll" id="preview_scroll">
    <div class="preview-empty">Completá los datos del proyecto<br>para ver el presupuesto en tiempo real.</div>
  </div>
</div>
"""
src = src.replace('</body>', MODAL_HTML + '\n</body>', 1)

# ─────────────────────────────────────────────
# 4. JAVASCRIPT NUEVO  (antes de init();)
# ─────────────────────────────────────────────
NEW_JS = """
// ================================================================
// GESTOR DE PRESUPUESTOS (localStorage)
// ================================================================
const BUDGET_KEY = 'sc_budgets_v1';

function _getBudgets(){
  try{return JSON.parse(localStorage.getItem(BUDGET_KEY))||{};}
  catch(e){return {};}
}
function _saveBudgets(data){
  localStorage.setItem(BUDGET_KEY,JSON.stringify(data));
}

function _collectForm(){
  const ids=[
    'cl_n','cl_f','cl_l','cl_r','cl_d','cl_o',
    'd_l','d_a','d_at','d_ac','ren',
    'op_intro','op_breve','op_tec','op_acl','op_fich','op_conc','op_eco',
    'op_mo_iny','op_mo_ext','mo_iny_val','mo_ext_val',
    'pct_e','chk_com','pct_com','chk_desc','desc_tipo','desc_val',
    'acl_texto','eco_texto',
    'pt_n','pt_f','pt_l','pt_r',
    'pt_chk','pt_pct','pt_chk_desc','pt_desc_tipo','pt_desc_val'
  ];
  const fd={};
  ids.forEach(id=>{
    const el=document.getElementById(id);
    if(!el)return;
    fd[id]=(el.type==='checkbox')?el.checked:el.value;
  });
  return fd;
}

function _applyForm(fd){
  if(!fd)return;
  Object.entries(fd).forEach(([id,val])=>{
    const el=document.getElementById(id);
    if(!el)return;
    if(el.type==='checkbox')el.checked=!!val;
    else el.value=val;
  });
  // Panels dependientes
  if(document.getElementById('op_acl')&&document.getElementById('op_acl').checked)
    document.getElementById('acl_panel').style.display='block';
  else if(document.getElementById('acl_panel'))
    document.getElementById('acl_panel').style.display='none';
  if(document.getElementById('op_eco')&&document.getElementById('op_eco').checked)
    document.getElementById('eco_panel').style.display='block';
  else if(document.getElementById('eco_panel'))
    document.getElementById('eco_panel').style.display='none';
  if(document.getElementById('chk_com')&&document.getElementById('chk_com').checked)
    document.getElementById('com_box').style.display='flex';
  else if(document.getElementById('com_box'))
    document.getElementById('com_box').style.display='none';
  if(document.getElementById('chk_desc'))togDesc&&togDesc();
  if(document.getElementById('pt_chk'))togComPt&&togComPt();
  if(document.getElementById('pt_chk_desc'))togDescPt&&togDescPt();
}

function saveCurrentBudget(){
  const defaultName=(document.getElementById('cl_n').value||'Sin nombre')+
    ' — '+new Date().toLocaleDateString('es-AR');
  const name=prompt('Nombre del presupuesto:',defaultName);
  if(name===null)return;
  const nm=name.trim()||defaultName;

  const budgets=_getBudgets();
  const id='b'+Date.now();
  const snap={
    id,name:nm,
    clientName:document.getElementById('cl_n').value||'—',
    ref:document.getElementById('cl_r').value||'',
    savedAt:new Date().toISOString(),
    form:_collectForm(),
    state:{
      vol:S.vol,aT:S.aT,aC:S.aC,pE:S.pE,ren:S.ren,
      qi:{...S.qi},qe:{...S.qe},
      com:S.com,pCom:S.pCom,desc:S.desc,
      modo:S.modo,qpt_proj:{...S.qpt_proj}
    },
    prices:JSON.parse(JSON.stringify(PRICES)),
    ptPrices:typeof PROJ_PT_PRICES!=='undefined'?JSON.parse(JSON.stringify(PROJ_PT_PRICES)):{}
  };
  budgets[id]=snap;
  try{
    _saveBudgets(budgets);
    showToast('💾 Presupuesto guardado');
    renderBudgetList();
  }catch(e){
    if(e.name==='QuotaExceededError')alert('Sin espacio en el navegador. Eliminá presupuestos viejos.');
    else alert('Error al guardar: '+e.message);
  }
}

function loadBudget(id){
  const budgets=_getBudgets();
  const b=budgets[id];
  if(!b)return;
  if(!confirm('¿Cargar "'+b.name+'"? Los datos actuales se perderán.'))return;

  // Restaurar estado
  Object.assign(S,b.state);
  if(b.prices)Object.assign(PRICES,b.prices);
  if(b.ptPrices&&typeof PROJ_PT_PRICES!=='undefined')Object.assign(PROJ_PT_PRICES,b.ptPrices);

  // Restaurar formularios
  _applyForm(b.form);

  // Re-render todo
  updExtPct&&updExtPct();
  calcDim&&calcDim();
  calcCaudal&&calcCaudal();
  ['pw','tc','si','po'].forEach(c=>renderTab&&renderTab(c));
  renderExtTab&&renderExtTab();
  renderProjPtGrid&&renderProjPtGrid();
  calcEco&&calcEco();
  updEstados&&updEstados();
  updSugs&&updSugs();
  updSugExt&&updSugExt();
  if(b.state&&b.state.modo)setMode(b.state.modo);

  closeGestor();
  showToast('✅ Presupuesto cargado: '+b.name);
  schedulePreviewUpdate();
}

function renameBudget(id){
  const budgets=_getBudgets();
  const b=budgets[id];
  if(!b)return;
  const name=prompt('Nuevo nombre:',b.name);
  if(!name||!name.trim())return;
  b.name=name.trim();
  _saveBudgets(budgets);
  renderBudgetList();
}

function deleteBudget(id){
  const budgets=_getBudgets();
  if(!budgets[id])return;
  if(!confirm('¿Eliminar "'+budgets[id].name+'"?'))return;
  delete budgets[id];
  _saveBudgets(budgets);
  renderBudgetList();
  showToast('🗑 Presupuesto eliminado');
}

function renderBudgetList(){
  const budgets=_getBudgets();
  const list=document.getElementById('budget_list');
  if(!list)return;
  const entries=Object.values(budgets).sort((a,b)=>b.savedAt.localeCompare(a.savedAt));
  if(entries.length===0){
    list.innerHTML='<div class="budget-empty"><div class="bi">📋</div>No hay presupuestos guardados aún.<br>Usá el botón de arriba para guardar el actual.</div>';
    return;
  }
  list.innerHTML=entries.map(b=>{
    const d=new Date(b.savedAt);
    const ds=d.toLocaleDateString('es-AR')+' '+d.toLocaleTimeString('es-AR',{hour:'2-digit',minute:'2-digit'});
    return `<div class="budget-item">
      <div class="budget-info">
        <div class="budget-name" title="${b.name}">${b.name}</div>
        <div class="budget-meta">Cliente: ${b.clientName}${b.ref?' · Ref: '+b.ref:''} · ${ds}</div>
      </div>
      <div class="budget-actions">
        <button class="btn btn-v" style="padding:5px 11px;font-size:10px;" onclick="loadBudget('${b.id}')">Cargar</button>
        <button class="btn btn-o" style="padding:5px 10px;font-size:10px;" onclick="renameBudget('${b.id}')" title="Renombrar">✏️</button>
        <button class="btn btn-o" style="padding:5px 10px;font-size:10px;color:var(--r);border-color:#f5ccc8;" onclick="deleteBudget('${b.id}')" title="Eliminar">✕</button>
      </div>
    </div>`;
  }).join('');
}

function openGestor(){
  renderBudgetList();
  document.getElementById('modal_gestor').style.display='flex';
}
function closeGestor(){
  document.getElementById('modal_gestor').style.display='none';
}

// ================================================================
// VISTA PREVIA EN TIEMPO REAL
// ================================================================
let _prevOpen=false;
let _prevTimer=null;
let _prevW=0; // ancho del contenedor preview

function togglePreview(){
  _prevOpen=!_prevOpen;
  const drawer=document.getElementById('preview_drawer');
  const btn=document.getElementById('preview_toggle_btn');
  drawer.classList.toggle('open',_prevOpen);
  btn.classList.toggle('open-state',_prevOpen);
  btn.innerHTML=_prevOpen?'✕<br>Cerrar':'Vista<br>Previa';
  if(_prevOpen){
    // Medir ancho real del drawer después de transición
    setTimeout(()=>{
      _prevW=document.getElementById('preview_scroll').clientWidth;
      updatePreview(true);
    },320);
  }
}

function schedulePreviewUpdate(){
  if(!_prevOpen)return;
  clearTimeout(_prevTimer);
  _prevTimer=setTimeout(()=>updatePreview(false),600);
}

function updatePreview(force){
  if(!_prevOpen)return;
  const status=document.getElementById('preview_status');
  const scroll=document.getElementById('preview_scroll');
  if(!status||!scroll)return;
  status.textContent='Actualizando...';
  status.style.color='#888';

  requestAnimationFrame(()=>{
    try{
      if(S.modo!=='p'){
        scroll.innerHTML='<div class="preview-empty">La vista previa muestra el modo Proyecto.<br>Switcheá a modo Proyecto para verla.</div>';
        status.textContent='—';
        return;
      }
      // Renderizar en pp_page (oculto en otro step)
      renderPpto();
      const ppPage=document.getElementById('pp_page');
      if(!ppPage||!ppPage.innerHTML){
        scroll.innerHTML='<div class="preview-empty">Completá los datos del proyecto.</div>';
        status.textContent='—';
        return;
      }
      // Extraer solo el contenido del body-cell
      const tmp=document.createElement('div');
      tmp.innerHTML=ppPage.innerHTML;
      const bodyCell=tmp.querySelector('.pp-print-body-cell');
      const inner=bodyCell?bodyCell.innerHTML:tmp.innerHTML;

      // Calcular escala: A4 ~ 794px, escalar al ancho del preview
      const w=_prevW||document.getElementById('preview_scroll').clientWidth||300;
      const scale=Math.min((w-20)/794,1);

      scroll.innerHTML=`<div class="preview-scale-wrap" style="width:794px;transform:scale(${scale});transform-origin:top left;margin-bottom:${Math.round(794*scale*1.415-794*scale)}px;">${inner}</div>`;
      status.textContent='● En vivo';
      status.style.color='#8BBF2E';
    }catch(e){
      status.textContent='⚠ Error';
      status.style.color='#e74c3c';
      console.warn('Preview error:',e);
    }
  });
}

// ================================================================
// TOAST
// ================================================================
function showToast(msg){
  const t=document.getElementById('toast_notif');
  if(!t)return;
  t.textContent=msg;
  t.classList.add('show');
  clearTimeout(t._tid);
  t._tid=setTimeout(()=>t.classList.remove('show'),2800);
}

// ================================================================
// HOOK: escuchar todos los cambios para actualizar preview
// ================================================================
function _initPreviewHooks(){
  document.addEventListener('input',schedulePreviewUpdate,{passive:true});
  document.addEventListener('change',schedulePreviewUpdate,{passive:true});
}

// Parchar goStep para que al ir al paso 5 también actualice
const _origGoStep=goStep;
function goStep(n){
  _origGoStep(n);
  if(n===5){
    if(_prevOpen)setTimeout(()=>updatePreview(true),100);
  }else{
    schedulePreviewUpdate();
  }
}
"""

src = src.replace('init();', NEW_JS + '\n_initPreviewHooks();\ninit();\n', 1)

with open(OUTFILE="/sessions/gallant-eager-thompson/mnt/outputs/cotizador_v14_new.html"
    f.write(src)

print("✅ Listo. Líneas:", src.count('\\n')+1)
