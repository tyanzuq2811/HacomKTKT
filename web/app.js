const list = document.querySelector('#bidder-list');
const template = document.querySelector('#bidder-template');
const runButton = document.querySelector('#run');
const statusBox = document.querySelector('#status');
const statusText = document.querySelector('#status-text');
const statusPercent = document.querySelector('#status-percent');
const progressBar = document.querySelector('#progress-bar');
const resultBox = document.querySelector('#result');
const metrics = document.querySelector('#metrics');
const download = document.querySelector('#download');
const errorBox = document.querySelector('#error');

function renumber(){
  [...list.querySelectorAll('.bidder-row')].forEach((row,index)=>{
    row.querySelector('.bidder-number').textContent=index+1;
    row.querySelector('.remove').disabled=list.children.length<=2;
  });
}
function addBidder(name=''){
  const node=template.content.firstElementChild.cloneNode(true);
  node.querySelector('.bidder-name').value=name;
  node.querySelector('.remove').addEventListener('click',()=>{node.remove();renumber();});
  list.appendChild(node);renumber();
}
document.querySelector('#add-bidder').addEventListener('click',()=>addBidder());
addBidder('Nhà thầu A');addBidder('Nhà thầu B');

function setError(message=''){
  errorBox.textContent=message;
  errorBox.classList.toggle('hidden',!message);
}
function setStatus(progress,message){
  statusBox.classList.remove('hidden');
  progressBar.style.width=`${progress}%`;
  statusPercent.textContent=`${progress}%`;
  statusText.textContent=message;
}
function metric(label,value){return `<div class="metric"><b>${value ?? 0}</b><span>${label}</span></div>`;}

async function poll(jobId){
  while(true){
    const response=await fetch(`/api/jobs/${jobId}`);
    const status=await response.json();
    if(!response.ok) throw new Error(status.detail || 'Không đọc được trạng thái tác vụ');
    setStatus(status.progress || 0,status.message || 'Đang xử lý');
    if(status.state==='failed') throw new Error(status.message || 'So sánh thất bại');
    if(status.state==='done') break;
    await new Promise(resolve=>setTimeout(resolve,1200));
  }
  const response=await fetch(`/api/jobs/${jobId}/result`);
  const data=await response.json();
  if(!response.ok) throw new Error(data.detail || 'Không đọc được kết quả');
  const s=data.summary;
  metrics.innerHTML=[
    metric('Nhà thầu',s.bidder_count),
    metric('Nhóm hạng mục',s.total_groups),
    metric('Thiếu ở ít nhất một hồ sơ',s.partial_groups),
    metric('Thông số bị đánh dấu',s.flagged_fields),
    metric('Thông tin',s.groups_info),
    metric('Cần kiểm tra',s.groups_review),
    metric('Cảnh báo',s.groups_warning),
    metric('Bất thường',s.groups_critical),
  ].join('');
  download.href=`/api/jobs/${jobId}/download`;
  resultBox.classList.remove('hidden');
}

runButton.addEventListener('click',async()=>{
  setError('');resultBox.classList.add('hidden');
  const rows=[...list.querySelectorAll('.bidder-row')];
  const names=rows.map(row=>row.querySelector('.bidder-name').value.trim());
  const files=rows.map(row=>row.querySelector('.bidder-file').files[0]);
  if(rows.length<2){setError('Cần ít nhất 2 nhà thầu.');return;}
  if(names.some(name=>!name)){setError('Hãy nhập tên cho tất cả nhà thầu.');return;}
  if(new Set(names).size!==names.length){setError('Tên nhà thầu phải khác nhau.');return;}
  if(files.some(file=>!file)){setError('Hãy chọn file Excel cho tất cả nhà thầu.');return;}

  const form=new FormData();
  rows.forEach((row,index)=>{form.append('files',files[index]);form.append('bidder_names',names[index]);});
  form.append('price_warn_pct',Number(document.querySelector('#price-warn').value)/100);
  form.append('price_critical_pct',Number(document.querySelector('#price-critical').value)/100);
  form.append('quantity_warn_pct',Number(document.querySelector('#qty-warn').value)/100);
  form.append('quantity_critical_pct',Number(document.querySelector('#qty-critical').value)/100);
  runButton.disabled=true;setStatus(2,'Đang tải file lên máy chủ nội bộ…');
  try{
    const response=await fetch('/api/compare-bidders',{method:'POST',body:form});
    const data=await response.json();
    if(!response.ok) throw new Error(data.detail || 'Không thể bắt đầu so sánh');
    await poll(data.job_id);
  }catch(error){setError(error.message || String(error));}
  finally{runButton.disabled=false;}
});
