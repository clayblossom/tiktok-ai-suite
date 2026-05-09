import { useState, useEffect } from 'react';
import { api } from '../api';

export function ShopManager() {
  const [products, setProducts] = useState<any[]>([]);
  const [research, setResearch] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [newProduct, setNewProduct] = useState({ name: '', price: '', category: '', description: '' });
  const [activeTab, setActiveTab] = useState<'products' | 'research' | 'analytics'>('products');

  useEffect(() => { api.listProducts().then(setProducts).catch(() => {}); }, []);

  const handleResearch = async () => {
    try { const resp = await api.researchProducts(); setResearch(resp.products || []); setActiveTab('research'); } catch (err) { console.error(err); }
  };

  const handleAddProduct = async () => {
    if (!newProduct.name.trim()) return;
    try {
      await api.createProduct({ name: newProduct.name, price: Number(newProduct.price) || 0, category: newProduct.category, description: newProduct.description });
      setNewProduct({ name: '', price: '', category: '', description: '' }); setShowAdd(false);
      api.listProducts().then(setProducts);
    } catch (err) { console.error(err); }
  };

  const analytics = [
    { icon: '💰', label: 'Revenue', value: '$0', change: '+0%', color: 'bg-emerald-50 text-emerald-600' },
    { icon: '📦', label: 'Orders', value: '0', change: '+0%', color: 'bg-primary-50 text-primary-600' },
    { icon: '📊', label: 'Conversion', value: '0%', change: '+0%', color: 'bg-violet-50 text-violet-600' },
    { icon: '⭐', label: 'Avg Rating', value: '0.0', change: '+0', color: 'bg-amber-50 text-amber-600' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">🛒 TikTok Shop Manager</h2>
          <p className="page-subtitle">Manage products and track sales performance</p>
        </div>
        <div className="flex gap-2">
          <button onClick={handleResearch} className="btn-secondary">🔍 Research</button>
          <button onClick={() => setShowAdd(!showAdd)} className="btn-primary">{showAdd ? '✕ Cancel' : '+ Add Product'}</button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-surface-100 rounded-xl p-1 w-fit">
        {(['products', 'research', 'analytics'] as const).map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab ? 'bg-white text-primary-700 shadow-sm' : 'text-surface-500 hover:text-surface-700'}`}>
            {tab === 'products' ? '📦 Products' : tab === 'research' ? '🔍 Research' : '📊 Analytics'}
          </button>
        ))}
      </div>

      {/* Add Product */}
      {showAdd && (
        <div className="card border-2 border-primary-200">
          <h3 className="font-semibold text-surface-900 mb-4">➕ Add New Product</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div><label className="label">Product Name</label><input value={newProduct.name} onChange={e => setNewProduct(p => ({ ...p, name: e.target.value }))} placeholder="e.g. LED Strip Lights" className="input" /></div>
            <div><label className="label">Price ($)</label><input value={newProduct.price} onChange={e => setNewProduct(p => ({ ...p, price: e.target.value }))} placeholder="19.99" type="number" className="input" /></div>
          </div>
          <div className="mb-4"><label className="label">Category</label><input value={newProduct.category} onChange={e => setNewProduct(p => ({ ...p, category: e.target.value }))} placeholder="Home, Electronics, Fashion..." className="input" /></div>
          <div className="mb-4"><label className="label">Description</label><textarea value={newProduct.description} onChange={e => setNewProduct(p => ({ ...p, description: e.target.value }))} placeholder="Describe your product..." rows={3} className="textarea" /></div>
          <button onClick={handleAddProduct} className="btn-primary">✅ Add Product</button>
        </div>
      )}

      {/* Products Tab */}
      {activeTab === 'products' && (
        <div className="card">
          {products.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-5xl mb-4">🛒</div>
              <h3 className="text-lg font-semibold text-surface-800 mb-2">No products yet</h3>
              <p className="text-sm text-surface-400">Add your first product to start selling!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {products.map(p => (
                <div key={p.id} className="bg-surface-50 rounded-xl p-4 hover:shadow-card transition-all">
                  <div className="w-full h-32 bg-surface-200 rounded-lg mb-3 flex items-center justify-center text-4xl">📦</div>
                  <h4 className="font-medium text-surface-800">{p.name}</h4>
                  <p className="text-xs text-surface-400 mb-2">{p.category}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-primary-600">${p.price}</span>
                    <span className={`badge ${p.status === 'active' ? 'badge-success' : 'badge-warning'}`}>{p.status}</span>
                  </div>
                  <p className="text-xs text-surface-400 mt-2">Stock: {p.stock}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Research Tab */}
      {activeTab === 'research' && (
        <div className="card">
          <h3 className="font-semibold text-surface-900 mb-4">🔥 Trending Products</h3>
          {research.length === 0 ? (
            <div className="text-center py-8">
              <button onClick={handleResearch} className="btn-primary">🔍 Research Trending Products</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {research.map((p, i) => (
                <div key={i} className="bg-surface-50 rounded-xl p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-medium text-surface-800">{p.name}</h4>
                      <p className="text-xs text-surface-400">{p.category}</p>
                    </div>
                    <span className="text-lg font-bold text-primary-600">${p.avg_price}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-surface-500">Trend:</span>
                      <div className="progress-bar w-24"><div className="progress-fill" style={{width: `${p.trend_score}%`}} /></div>
                      <span className="text-xs font-medium">{p.trend_score}</span>
                    </div>
                    <span className={`badge ${p.competition === 'low' ? 'badge-success' : p.competition === 'medium' ? 'badge-warning' : 'badge-danger'}`}>
                      {p.competition}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-5">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {analytics.map((a, i) => (
              <div key={i} className="card-hover">
                <div className="flex items-center justify-between mb-3">
                  <div className={`w-10 h-10 rounded-xl ${a.color} flex items-center justify-center text-lg`}>{a.icon}</div>
                  <span className="text-xs font-medium text-emerald-600">{a.change}</span>
                </div>
                <p className="text-2xl font-bold text-surface-900">{a.value}</p>
                <p className="text-xs text-surface-500">{a.label}</p>
              </div>
            ))}
          </div>
          <div className="card text-center py-12">
            <p className="text-surface-400">Connect TikTok Shop API for real analytics data</p>
          </div>
        </div>
      )}
    </div>
  );
}
