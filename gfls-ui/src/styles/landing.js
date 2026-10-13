export const landingStyles = `
  html{scroll-behavior:smooth}
  .lp{background:var(--bg);color:var(--text);overflow-x:hidden}
  .lp-wrap{max-width:1120px;margin:0 auto;padding:0 24px}
  .lp a{color:inherit;text-decoration:none}

  .lp-nav{position:sticky;top:0;z-index:50;background:rgba(11,12,15,0.72);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid rgba(42,45,56,0.7)}
  .lp-nav-in{height:64px;display:flex;align-items:center;justify-content:space-between;gap:16px}
  .lp-brand{font-family:var(--font-head);font-weight:800;font-size:20px;letter-spacing:-0.5px;color:var(--accent);display:flex;align-items:center;gap:10px}
  .lp-links{display:flex;gap:28px;font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted)}
  .lp-links a{transition:color .15s}
  .lp-links a:hover{color:var(--text)}

  .lp-hero{position:relative;padding:96px 0 72px;isolation:isolate}
  .lp-hero::before{content:"";position:absolute;inset:0;z-index:-2;background:radial-gradient(60% 55% at 50% 0%,rgba(232,197,71,0.16),transparent 70%)}
  .lp-hero::after{content:"";position:absolute;inset:0;z-index:-1;background-image:linear-gradient(rgba(255,255,255,0.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.035) 1px,transparent 1px);background-size:44px 44px;-webkit-mask-image:radial-gradient(70% 70% at 50% 25%,#000,transparent);mask-image:radial-gradient(70% 70% at 50% 25%,#000,transparent)}
  .lp-hero-grid{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center}
  .lp-eyebrow{display:inline-flex;align-items:center;gap:10px;padding:6px 14px;border:1px solid var(--border2);border-radius:999px;background:rgba(19,21,26,0.8);font-size:11px;letter-spacing:1.6px;text-transform:uppercase;color:var(--muted);margin-bottom:28px}
  .lp-dot{width:7px;height:7px;border-radius:50%;background:var(--success);box-shadow:0 0 0 0 rgba(78,203,141,0.6);animation:lpPulse 2.2s infinite}
  .lp-h1{font-family:var(--font-head);font-weight:800;font-size:clamp(36px,5vw,58px);line-height:1.04;letter-spacing:-1.8px;margin-bottom:24px}
  .lp-h1 em{font-style:normal;color:var(--accent);background:linear-gradient(100deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
  .lp-lead{font-size:14px;line-height:1.8;color:var(--muted);max-width:520px;margin-bottom:36px}
  .lp-cta{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:22px}
  .lp-btn{padding:14px 28px;font-size:12px}
  .lp-note{font-size:11px;letter-spacing:0.6px;color:var(--muted)}
  .lp-note b{color:var(--text);font-weight:500}

  .lp-panel{background:linear-gradient(180deg,rgba(26,29,37,0.95),rgba(19,21,26,0.95));border:1px solid var(--border);border-radius:12px;box-shadow:0 30px 80px -30px rgba(0,0,0,0.8),0 0 0 1px rgba(232,197,71,0.04);overflow:hidden}
  .lp-panel-bar{display:flex;align-items:center;gap:7px;padding:12px 16px;border-bottom:1px solid var(--border);background:rgba(11,12,15,0.5)}
  .lp-panel-bar i{width:9px;height:9px;border-radius:50%;background:var(--border2)}
  .lp-panel-bar span{margin-left:10px;font-size:11px;letter-spacing:0.8px;color:var(--muted)}
  .lp-panel-body{padding:18px 18px 12px}
  .lp-svg{width:100%;height:auto;display:block}
  .lp-legend{display:flex;flex-wrap:wrap;gap:16px;padding:0 18px 16px;font-size:10px;letter-spacing:0.8px;text-transform:uppercase;color:var(--muted)}
  .lp-legend span{display:inline-flex;align-items:center;gap:7px}
  .lp-legend i{width:14px;height:0;border-top:2px solid var(--accent)}
  .lp-legend i.dash{border-top-style:dashed}

  .lp-draw{stroke-dasharray:1;stroke-dashoffset:1;animation:lpDraw 2.2s .3s cubic-bezier(.4,0,.2,1) forwards}
  .lp-fade{opacity:0;animation:lpFade .8s 2.1s ease forwards}
  .lp-ping{transform-origin:center;transform-box:fill-box;animation:lpPing 2s 2.6s infinite}

  .lp-stats{border-top:1px solid var(--border);border-bottom:1px solid var(--border);background:var(--surface)}
  .lp-stats-grid{display:grid;grid-template-columns:repeat(4,1fr)}
  .lp-stat{padding:30px 24px;border-right:1px solid var(--border)}
  .lp-stat:last-child{border-right:none}
  .lp-stat b{display:block;font-family:var(--font-head);font-size:40px;font-weight:800;letter-spacing:-1px;color:var(--accent);line-height:1;margin-bottom:8px}
  .lp-stat span{font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted)}

  .lp-sec{padding:104px 0 0}
  .lp-kicker{font-size:11px;letter-spacing:2.2px;text-transform:uppercase;color:var(--accent);margin-bottom:14px}
  .lp-h2{font-family:var(--font-head);font-weight:800;font-size:clamp(28px,4vw,42px);letter-spacing:-1.2px;line-height:1.08;margin-bottom:14px;max-width:640px}
  .lp-sub{font-size:13px;line-height:1.8;color:var(--muted);max-width:560px;margin-bottom:48px}

  .lp-steps{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;position:relative}
  .lp-step{position:relative;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:22px 18px 20px;transition:transform .2s,border-color .2s}
  .lp-step:hover{transform:translateY(-4px);border-color:var(--accent)}
  .lp-step-n{font-family:var(--font-head);font-size:34px;font-weight:800;line-height:1;color:var(--border2);margin-bottom:18px;transition:color .2s}
  .lp-step:hover .lp-step-n{color:var(--accent)}
  .lp-step h3{font-family:var(--font-head);font-size:15px;font-weight:700;margin-bottom:8px}
  .lp-step p{font-size:11px;line-height:1.7;color:var(--muted)}

  .lp-show{display:grid;grid-template-columns:1fr 1fr;gap:20px}
  .lp-cap{padding:16px 18px 18px;border-top:1px solid var(--border)}
  .lp-cap h3{font-family:var(--font-head);font-size:16px;font-weight:700;margin-bottom:6px}
  .lp-cap p{font-size:11px;line-height:1.7;color:var(--muted)}
  .lp-reshape{display:grid;grid-template-columns:1fr;gap:10px;justify-items:stretch;padding:22px 18px}
  .lp-mini{font-size:10px;border:1px solid var(--border);border-radius:4px;overflow:hidden;background:var(--surface)}
  .lp-mini div{display:grid;gap:0;border-bottom:1px solid var(--border)}
  .lp-mini div:last-child{border-bottom:none}
  .lp-mini div>span{padding:7px 8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .lp-mini .h{background:rgba(232,197,71,0.07);color:var(--accent)}
  .lp-mini .c3{grid-template-columns:1.1fr 1fr 1fr}
  .lp-mini .c4{grid-template-columns:1fr .7fr 1.5fr .8fr}
  .lp-mini .mut{color:var(--muted)}
  .lp-arrow{color:var(--accent);font-size:20px;justify-self:center;transform:rotate(90deg)}
  .lp-tag-mini{font-size:9px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px}

  .lp-feats{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
  .lp-feat{padding:26px 22px;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);transition:border-color .2s,background .2s}
  .lp-feat:hover{border-color:var(--border2);background:#1d2029}
  .lp-ico{width:38px;height:38px;border-radius:8px;display:flex;align-items:center;justify-content:center;background:rgba(232,197,71,0.09);border:1px solid rgba(232,197,71,0.22);color:var(--accent);font-size:17px;margin-bottom:18px}
  .lp-feat h3{font-family:var(--font-head);font-size:16px;font-weight:700;margin-bottom:8px}
  .lp-feat p{font-size:11.5px;line-height:1.75;color:var(--muted)}
  .lp-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
  .lp-chip{padding:3px 9px;border:1px solid var(--border2);border-radius:999px;font-size:10px;color:var(--muted)}

  .lp-final{margin-top:112px;padding:84px 0;text-align:center;position:relative;border-top:1px solid var(--border);background:radial-gradient(50% 90% at 50% 100%,rgba(232,197,71,0.12),transparent 70%),var(--surface)}
  .lp-final .lp-h2{margin:0 auto 14px}
  .lp-final .lp-sub{margin:0 auto 32px}
  .lp-foot{padding:22px 0;border-top:1px solid var(--border);font-size:11px;letter-spacing:0.6px;color:var(--muted);display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}

  .lp-rv{opacity:0;transform:translateY(22px);transition:opacity .7s ease,transform .7s ease}
  .lp-rv.in{opacity:1;transform:none}

  @keyframes lpDraw{to{stroke-dashoffset:0}}
  @keyframes lpFade{to{opacity:1}}
  @keyframes lpPing{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}
  @keyframes lpPulse{70%{box-shadow:0 0 0 9px rgba(78,203,141,0)}100%{box-shadow:0 0 0 0 rgba(78,203,141,0)}}

  @media(max-width:960px){
    .lp-hero{padding:64px 0 56px}
    .lp-hero-grid,.lp-show{grid-template-columns:1fr}
    .lp-steps{grid-template-columns:1fr 1fr}
    .lp-feats{grid-template-columns:1fr 1fr}
    .lp-stats-grid{grid-template-columns:1fr 1fr}
    .lp-stat:nth-child(2){border-right:none}
    .lp-stat:nth-child(-n+2){border-bottom:1px solid var(--border)}
  }
  @media(max-width:640px){
    .lp-links{display:none}
    .lp-steps,.lp-feats{grid-template-columns:1fr}
    .lp-sec{padding-top:72px}
    .lp-final{margin-top:80px}
  }
  @media(prefers-reduced-motion:reduce){
    html{scroll-behavior:auto}
    .lp-draw{animation:none;stroke-dashoffset:0}
    .lp-fade{animation:none;opacity:1}
    .lp-ping,.lp-dot{animation:none}
    .lp-rv{opacity:1;transform:none;transition:none}
    .lp-step{transition:none}
  }
`;
