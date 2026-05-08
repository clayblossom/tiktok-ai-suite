import { useState, useEffect } from 'react';
import { api } from '../api';

export function ShopManager() {
  const [products, setProducts] = useState<any[]>([]);
  const [research, setResearch] = useState<any[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [newProduct, setNewProduct] = useState({ name: '', price: '', category: '', description: '' });

  useEffect(() => {
    api.listProducts().then(setProducts).catch(() => {});
  }, []);

  const handleResearch = async () => {
    try {
      const resp = await api.researchProducts();
      setResearch(resp.products || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddProduct = async () => {
    if (!newProduct.name.trim()) return;
    try {
      await api.createProduct({
        name: newProduct.name,
        price: Number(newProduct.price) || 0,
        category: newProduct.category,
        description: newProduct.description,
      });
      setNewProduct({ name: '', price: '', category: '', description: '' });
      setShowAdd(false);
      api.listProducts().then(setProducts);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">🛒 TikTok Shop Manager</h2>
        <div className="flex gap-2">
          <button onClick={handleResearch} className="btn-secondary text-sm">🔍 Research Products</button>
          <button onClick={() => setShowAdd(!showAdd)} className="btn-primary text-sm">
            {showAdd ? '✕ Cancel' : '+ Add Product'}
          </button>
        </div>
      </div>

      {/* Add Product Form */}
      {showAdd && (
        <div className="card border-tiktok-pink/30 space-y-3">
          <h3 className="font-semibold">➕ Add Product</h3>
          <div className="grid grid-cols-2 gap-3">
            <input value={newProduct.name} onChange={e => setNewProduct(p => ({ ...p, name: e.target.value }))}
              placeholder="Product name" className="input-field" />
            <input value={newProduct.price} onChange={e => setNewProduct(p => ({ ...p, price: e.target.value }))}
              placeholder="Price" type="number" className="input-field" />
          </div>
          <input value={newProduct.category} onChange={e => setNewProduct(p => ({ ...p, category: e.target.value }))}
            placeholder="Category" className="input-field" />
          <textarea value={newProduct.description} onChange={e => setNewProduct(p => ({ ...p, description: e.target.value }))}
            placeholder="Description" rows={3} className="input-field resize-none" />
          <button onClick={handleAddProduct} className="btn-primary">✅ Add Product</button>
        </div>
      )}

      {/* Trending Research */}
      {research.length > 0 && (
        <div className="card">
          <h3 className="font-semibold mb-3">🔥 Trending Products</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {research.map((p, i) => (
              <div key={i} className="bg-tiktok-darker rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{p.name}</p>
                    <p className="text-xs text-gray-500">{p.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-tiktok-pink font-bold">${p.avg_price}</p>
                    <p className="text-xs text-gray-500">Score: {p.trend_score}</p>
                  </div>
                </div>
                <div className="mt-2">
                  <span className={`badge ${p.competition === 'low' ? 'bg-green-900/50 text-green-400' : p.competition === 'medium' ? 'bg-yellow-900/50 text-yellow-400' : 'bg-red-900/50 text-red-400'}`}>
                    {p.competition} competition
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Product List */}
      <div className="card">
        <h3 className="font-semibold mb-3">📦 My Products ({products.length})</h3>
        {products.length === 0 ? (
          <p className="text-gray-500 text-sm text-center py-8">No products yet. Add your first product!</p>
        ) : (
          <div className="space-y-2">
            {products.map(p => (
              <div key={p.id} className="bg-tiktok-darker rounded-lg p-3 flex items-center justify-between">
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-xs text-gray-500">{p.category} • Stock: {p.stock}</p>
                </div>
                <div className="text-right">
                  <p className="text-tiktok-pink font-bold">${p.price}</p>
                  <span className={`badge ${p.status === 'active' ? 'bg-green-900/50 text-green-400' : 'bg-gray-700 text-gray-400'}`}>
                    {p.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
