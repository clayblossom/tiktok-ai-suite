import { useEffect, useState } from 'react';
import { api } from '../api';

type Tab = 'radar' | 'oneclick' | 'score' | 'ab' | 'calendar';

export function GrowthOS() {
  const [tab, setTab] = useState<Tab>('radar');
  const [topic, setTopic] = useState('AI productivity tools');
  const [niche, setNiche] = useState('tech');
  const [tone, setTone] = useState('casual');
  const [loading, setLoading] = useState(false);
  const [radar, setRadar] = useState<any>(null);
  const [blueprint, setBlueprint] = useState<any>(null);
  const [score, setScore] = useState<any>(null);
  const [ab, setAb] = useState<any>(null);
  const [calendar, setCalendar] = useState<any>(null);

  const run = async (target: Tab = tab) => {
    setLoading(true);
    try {
      if (target === 'radar') setRadar(await api.trendRadar(niche, topic));
      if (target === 'oneclick') setBlueprint(await api.oneClick({ niche, topic, tone, duration: 30 }));
      if (target === 'score') setScore(await api.viralScore({ hook: topic, body: blueprint?.script?.body || `A quick proof-driven TikTok about ${topic}`, cta: 'Comment GUIDE and follow for part 2', duration: 30 }));
      if (target === 'ab') setAb(await api.abTests(topic, niche, 5));
      if (target === 'calendar') setCalendar(await api.strategyCalendar(niche, 30));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { run('radar'); }, []);

  const tabs: { id: Tab; label: string }[] = [
    { id: 'radar', label: '📡 Trend Radar' },
    { id: 'oneclick', label: '⚡ One-click TikTok' },
    { id: 'score', label: '🧪 Viral Score' },
    { id: 'ab', label: '🔀 A/B Lab' },
    { id: 'calendar', label: '🗓️ Strategy Calendar' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">🚀 TikTok Growth OS</h2>
          <p className="page-subtitle">Trend intelligence, one-click video planning, viral scoring, A/B hooks, and strategy calendar.</p>
        </div>
        <button onClick={() => run()} disabled={loading} className="btn-primary">{loading ? 'Working...' : 'Generate'}</button>
      </div>

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><label className="label">Topic / Product / Angle</label><input value={topic} onChange={e => setTopic(e.target.value)} className="input" /></div>
          <div><label className="label">Niche</label><input value={niche} onChange={e => setNiche(e.target.value)} className="input" /></div>
          <div><label className="label">Tone</label><select value={tone} onChange={e => setTone(e.target.value)} className="select"><option>casual</option><option>educational</option><option>dramatic</option><option>funny</option><option>motivational</option></select></div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {tabs.map(t => <button key={t.id} onClick={() => { setTab(t.id); run(t.id); }} className={`btn-sm ${tab === t.id ? 'btn-primary' : 'btn-secondary'}`}>{t.label}</button>)}
      </div>

      {tab === 'radar' && (
        <div className="space-y-4">
          <div className="card"><h3 className="font-semibold text-surface-900">Trend Summary</h3><p className="text-sm text-surface-500 mt-2">{radar?.trend_summary || 'Generate to see trend intelligence.'}</p><p className="text-xs text-surface-400 mt-2">Best window: {radar?.recommended_posting_window}</p></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {(radar?.trends || []).map((t: any) => <div key={t.rank} className="card-hover"><div className="flex justify-between"><h4 className="font-semibold">#{t.rank} {t.name}</h4><span className="badge-primary">{t.opportunity_score}</span></div><p className="text-sm text-surface-500 mt-2">{t.pattern}</p><p className="text-xs mt-2">Signal: {t.niche_signal} · Velocity {t.velocity} · Saturation {t.saturation_score}</p><div className="mt-3 space-y-1">{t.hooks?.slice(0,2).map((h: string, i: number) => <p key={i} className="text-sm bg-surface-50 rounded-lg p-2">🪝 {h}</p>)}</div></div>)}
          </div>
        </div>
      )}

      {tab === 'oneclick' && blueprint && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 card"><h3 className="font-semibold mb-3">Script Blueprint</h3><div className="space-y-3"><p className="p-3 bg-blue-50 rounded-lg">🪝 {blueprint.script.hook}</p><p className="p-3 bg-surface-50 rounded-lg">{blueprint.script.body}</p><p className="p-3 bg-emerald-50 rounded-lg">📢 {blueprint.script.cta}</p></div></div>
          <div className="card"><h3 className="font-semibold mb-3">Viral Score</h3><p className="text-5xl font-bold text-primary-600">{blueprint.viral_score.overall_score}</p><p className="badge-info mt-2">{blueprint.viral_score.verdict}</p></div>
          <div className="lg:col-span-3 card"><h3 className="font-semibold mb-3">Visual Plan</h3><div className="grid grid-cols-1 md:grid-cols-4 gap-3">{blueprint.visual_plan.map((v: any, i: number) => <div key={i} className="bg-surface-50 rounded-xl p-3"><p className="text-xs text-surface-400">{v.time}</p><p className="font-medium">{v.shot}</p><p className="text-sm text-surface-500">{v.overlay}</p></div>)}</div></div>
        </div>
      )}

      {tab === 'score' && score && <div className="card"><h3 className="font-semibold mb-3">Pre-publish Viral Score</h3><p className="text-6xl font-bold text-primary-600">{score.overall_score}</p><div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-5">{Object.entries(score.components).map(([k,v]: any) => <div key={k} className="bg-surface-50 rounded-xl p-3"><p className="text-xs text-surface-400">{k.replaceAll('_',' ')}</p><p className="text-xl font-bold">{v}</p></div>)}</div><div className="mt-5 space-y-2">{score.recommendations.map((r: string, i: number) => <p key={i} className="text-sm bg-amber-50 text-amber-800 rounded-lg p-2">💡 {r}</p>)}</div></div>}

      {tab === 'ab' && ab && <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{ab.variants.map((v: any) => <div key={v.variant} className="card-hover"><div className="flex justify-between"><h4 className="font-semibold">Variant {v.variant}: {v.angle}</h4><span className="badge-info">{v.test_goal}</span></div><p className="text-lg mt-3">{v.hook}</p><p className="text-sm text-surface-500 mt-2">{v.caption}</p><div className="flex flex-wrap gap-1 mt-3">{v.hashtags.map((h: string) => <span key={h} className="badge">{h}</span>)}</div></div>)}</div>}

      {tab === 'calendar' && calendar && <div className="card"><h3 className="font-semibold mb-3">30-Day Strategy Calendar</h3><div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">{calendar.entries.slice(0, 30).map((e: any) => <div key={e.date} className="bg-surface-50 rounded-xl p-3"><p className="text-xs text-surface-400">{e.date} · {e.posting_window}</p><p className="font-medium">{e.title}</p><p className="text-sm text-surface-500">{e.format} · {e.goal}</p></div>)}</div></div>}
    </div>
  );
}
