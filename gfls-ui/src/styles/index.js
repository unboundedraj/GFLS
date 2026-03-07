export const styles = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  :root{
    --bg:#0b0c0f;--surface:#13151a;--card:#1a1d25;--border:#2a2d38;
    --border2:#353848;--accent:#e8c547;--accent2:#f0d97a;
    --text:#e4e6ee;--muted:#7a7f96;--danger:#e05c5c;
    --success:#4ecb8d;--info:#5c9fe0;
    --font-head:'Syne',sans-serif;--font-mono:'DM Mono',monospace;--radius:6px;
  }
  body{background:var(--bg);color:var(--text);font-family:var(--font-mono)}
  .app{min-height:100vh;display:flex;flex-direction:column}
  .header{border-bottom:1px solid var(--border);padding:0 40px;height:64px;display:flex;align-items:center;justify-content:space-between;background:var(--surface);position:sticky;top:0;z-index:100}
  .logo{font-family:var(--font-head);font-weight:800;font-size:20px;letter-spacing:-0.5px;color:var(--accent);display:flex;align-items:center;gap:10px}
  .logo-sub{font-family:var(--font-mono);font-size:11px;font-weight:300;color:var(--muted);text-transform:uppercase;letter-spacing:2px;margin-top:2px}
  .step-nav{display:flex;border-bottom:1px solid var(--border);background:var(--surface);padding:0 40px;overflow-x:auto}
  .step-btn{padding:14px 28px;background:none;border:none;cursor:pointer;font-family:var(--font-mono);font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);border-bottom:2px solid transparent;transition:all .2s;white-space:nowrap;display:flex;align-items:center;gap:8px}
  .step-btn:hover{color:var(--text)}
  .step-btn.active{color:var(--accent);border-bottom-color:var(--accent)}
  .step-btn.done{color:var(--success)}
  .step-num{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:500;background:var(--border);color:var(--muted)}
  .step-btn.active .step-num{background:var(--accent);color:#000}
  .step-btn.done .step-num{background:var(--success);color:#000}
  .main{flex:1;padding:40px;max-width:1200px;margin:0 auto;width:100%}
  .section-title{font-family:var(--font-head);font-size:28px;font-weight:700;letter-spacing:-0.5px;margin-bottom:4px}
  .section-sub{font-size:12px;color:var(--muted);margin-bottom:32px;letter-spacing:0.5px}
  .card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:20px}
  .card-title{font-family:var(--font-head);font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--muted);margin-bottom:16px}
  .card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
  .card-header .card-title{margin-bottom:0}
  .upload-zone{border:1.5px dashed var(--border2);border-radius:var(--radius);padding:40px;text-align:center;cursor:pointer;transition:all .2s;background:var(--surface)}
  .upload-zone:hover,.upload-zone.drag{border-color:var(--accent);background:rgba(232,197,71,0.04)}
  .upload-icon{font-size:32px;margin-bottom:12px}
  .upload-label{font-family:var(--font-head);font-size:16px;font-weight:600;color:var(--text);margin-bottom:6px}
  .upload-hint{font-size:11px;color:var(--muted);letter-spacing:0.5px}
  .upload-success{display:flex;align-items:center;gap:12px;background:rgba(78,203,141,0.08);border:1px solid rgba(78,203,141,0.25);border-radius:var(--radius);padding:14px 18px;margin-top:14px}
  .radio-group{display:flex;gap:10px;margin-bottom:20px}
  .radio-btn{padding:8px 20px;border:1.5px solid var(--border2);border-radius:var(--radius);background:none;cursor:pointer;font-family:var(--font-mono);font-size:12px;letter-spacing:0.5px;color:var(--muted);transition:all .15s}
  .radio-btn:hover{border-color:var(--accent);color:var(--text)}
  .radio-btn.selected{border-color:var(--accent);color:var(--accent);background:rgba(232,197,71,0.07)}
  .input-label{font-size:11px;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}
  .input-field{width:100%;padding:10px 14px;background:var(--surface);border:1.5px solid var(--border2);border-radius:var(--radius);color:var(--text);font-family:var(--font-mono);font-size:13px;outline:none;transition:border-color .15s}
  .input-field:focus{border-color:var(--accent)}
  .input-group{margin-bottom:16px}
  select.input-field{cursor:pointer}
  select.input-field option{background:var(--card)}
  .format-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
  .format-card{border:1.5px solid var(--border);border-radius:var(--radius);padding:16px;cursor:pointer;transition:all .15s;background:var(--surface);text-align:left}
  .format-card:hover{border-color:var(--accent)}
  .format-card.selected{border-color:var(--accent);background:rgba(232,197,71,0.06)}
  .format-card-num{font-family:var(--font-head);font-size:22px;font-weight:800;color:var(--border2);transition:color .15s;line-height:1;margin-bottom:8px}
  .format-card.selected .format-card-num,.format-card:hover .format-card-num{color:var(--accent)}
  .format-card-label{font-size:12px;font-weight:500;color:var(--text);margin-bottom:4px}
  .format-card-desc{font-size:10px;color:var(--muted);letter-spacing:0.3px}
  .mapping-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .btn{padding:10px 22px;border-radius:var(--radius);font-family:var(--font-mono);font-size:12px;letter-spacing:0.8px;text-transform:uppercase;cursor:pointer;border:none;transition:all .15s;font-weight:500;display:inline-flex;align-items:center;gap:8px}
  .btn:disabled{opacity:0.4;cursor:not-allowed}
  .btn-primary{background:var(--accent);color:#000}
  .btn-primary:hover:not(:disabled){background:var(--accent2)}
  .btn-secondary{background:none;color:var(--muted);border:1.5px solid var(--border2)}
  .btn-secondary:hover:not(:disabled){border-color:var(--text);color:var(--text)}
  .btn-success{background:var(--success);color:#000}
  .btn-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:16px}
  .alert{padding:12px 16px;border-radius:var(--radius);font-size:12px;display:flex;align-items:flex-start;gap:10px;margin-bottom:16px}
  .alert-info{background:rgba(92,159,224,0.08);border:1px solid rgba(92,159,224,0.2);color:var(--info)}
  .alert-success{background:rgba(78,203,141,0.08);border:1px solid rgba(78,203,141,0.2);color:var(--success)}
  .alert-warn{background:rgba(232,197,71,0.08);border:1px solid rgba(232,197,71,0.2);color:var(--accent)}
  .alert-error{background:rgba(224,92,92,0.08);border:1px solid rgba(224,92,92,0.2);color:var(--danger)}
  .checkbox-row{display:flex;align-items:center;gap:10px;cursor:pointer;margin-bottom:16px}
  .checkbox-box{width:18px;height:18px;border:1.5px solid var(--border2);border-radius:3px;display:flex;align-items:center;justify-content:center;transition:all .15s;flex-shrink:0}
  .checkbox-box.checked{background:var(--accent);border-color:var(--accent)}
  .method-grid{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
  .method-chip{padding:7px 14px;border:1.5px solid var(--border2);border-radius:20px;font-size:11px;letter-spacing:0.5px;cursor:pointer;color:var(--muted);transition:all .15s;background:none;font-family:var(--font-mono)}
  .method-chip:hover{border-color:var(--accent);color:var(--text)}
  .method-chip.selected{border-color:var(--accent);color:var(--accent);background:rgba(232,197,71,0.07)}
  .slider-row{display:flex;align-items:center;gap:12px}
  .slider{flex:1;-webkit-appearance:none;height:4px;background:var(--border2);border-radius:2px;outline:none}
  .slider::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:var(--accent);cursor:pointer}
  .slider-val{min-width:32px;text-align:center;font-size:14px;font-weight:500;color:var(--accent)}
  .prediction-box{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:var(--radius);padding:20px;margin-top:16px;animation:fadeIn .3s ease}
  .prediction-value{font-family:var(--font-head);font-size:36px;font-weight:800;color:var(--accent);line-height:1}
  .tag-list{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
  .tag{padding:5px 12px;border-radius:3px;font-size:11px;cursor:pointer;transition:all .15s;border:1.5px solid var(--border2);color:var(--muted);background:none;font-family:var(--font-mono)}
  .tag:hover{border-color:var(--info);color:var(--info)}
  .tag.active{border-color:var(--info);color:var(--info);background:rgba(92,159,224,0.07)}
  .divider{height:1px;background:var(--border);margin:28px 0}
  .two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px}
  .stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
  .stat-box{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px}
  .stat-val{font-family:var(--font-head);font-size:22px;font-weight:800}
  .spinner{display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,0.2);border-top-color:currentColor;border-radius:50%;animation:spin .6s linear infinite}
  .tbl-wrap{width:100%;overflow-x:auto;border-radius:var(--radius);border:1px solid var(--border)}
  .tbl{width:100%;border-collapse:collapse;font-family:var(--font-mono);font-size:12px;min-width:max-content}
  .tbl thead tr{background:var(--surface)}
  .tbl th{padding:11px 16px;text-align:left;color:var(--accent);font-weight:500;font-size:11px;white-space:nowrap;border-bottom:2px solid var(--border);letter-spacing:0.3px}
  .tbl td{padding:9px 16px;white-space:nowrap;border-bottom:1px solid var(--border);color:var(--text);font-size:12px}
  .tbl tbody tr:last-child td{border-bottom:none}
  .tbl tbody tr:nth-child(even){background:rgba(255,255,255,0.02)}
  .tbl tbody tr:hover{background:rgba(232,197,71,0.04)}
  .tbl td.null{color:var(--muted)}
  .tbl-meta{font-size:11px;color:var(--muted);margin-top:10px;letter-spacing:0.3px}
  @media(max-width:640px){
    .two-col,.format-grid,.mapping-grid{grid-template-columns:1fr}
    .stat-grid{grid-template-columns:1fr 1fr}
    .main{padding:20px}
  }
  @keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1}}
  @keyframes spin{to{transform:rotate(360deg)}}
`;
