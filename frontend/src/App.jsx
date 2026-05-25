import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PropertyCard from './components/PropertyCard';

export default function App() {
  const [localities, setLocalities] = useState([]);
  const [selectedLocality, setSelectedLocality] = useState(null);
  const [properties, setProperties] = useState([]);

  useEffect(() => {
    fetchLocalities();
    const interval = setInterval(fetchLocalities, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchLocalities = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/localities/');
      setLocalities(res.data);
    } catch (err) {
      console.error("Error fetching localities:", err);
    }
  };

  const handleLocalitySelect = async (loc) => {
    setSelectedLocality(loc);
    try {
      const res = await axios.get(`http://localhost:8000/api/localities/${loc.id}/properties/`);
      setProperties(res.data);
    } catch (err) {
      console.error("Error fetching properties for locality:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 px-8 py-4 shadow-sm">
        <h1 className="text-xl font-bold tracking-tight text-slate-900">Property Broker AI</h1>
        <p className="text-xs text-slate-500 mt-1">Browse and analyze property locations</p>
      </header>

      <main className="flex-1 p-8 grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-7xl mx-auto w-full">
        <div className="lg:col-span-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm h-fit">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">Analyzed Localities</h2>
          {localities.length === 0 ? (
            <p className="text-xs text-slate-400 italic">No locations in database yet. Add via Django Admin.</p>
          ) : (
            <div className="space-y-2">
              {localities.map((loc) => (
                <div 
                  key={loc.id} 
                  onClick={() => handleLocalitySelect(loc)}
                  className={`p-3.5 rounded-lg border cursor-pointer transition text-left ${selectedLocality?.id === loc.id ? 'border-slate-900 bg-slate-50 shadow-sm' : 'border-slate-100 hover:border-slate-300'}`}
                >
                  <h3 className="font-semibold text-sm text-slate-800">{loc.name}</h3>
                  <p className="text-xs text-slate-400">{loc.city}</p>
                  {loc.profile ? (
                    <span className="inline-block mt-1.5 bg-emerald-50 text-emerald-700 border border-emerald-100 px-2 py-0.5 text-[10px] font-semibold rounded">✓ Analyzed</span>
                  ) : (
                    <span className="inline-block mt-1.5 bg-amber-50 text-amber-700 border border-amber-100 px-2 py-0.5 text-[10px] font-semibold rounded animate-pulse">⏳ Processing</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="lg:col-span-8 space-y-6">
          {selectedLocality ? (
            <>
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-5">
                <div>
                  <span className="bg-slate-900 text-white font-semibold text-[10px] tracking-widest uppercase px-2 py-0.5 rounded">Groq LLM Analysis</span>
                  <h2 className="text-xl font-bold text-slate-900 mt-2">{selectedLocality.name} Overview</h2>
                </div>

                {selectedLocality.profile ? (
                  <>
                    <p className="text-sm leading-relaxed text-slate-600 bg-slate-50 p-4 border-l-4 border-slate-400 rounded-r-lg">
                      {selectedLocality.profile.summary}
                    </p>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
                      <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <span className="block text-[10px] uppercase font-bold tracking-wider text-slate-400">Tourism</span>
                        <span className="text-lg font-bold text-slate-800">{selectedLocality.profile.tourist_rating}/5 ★</span>
                      </div>
                      <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <span className="block text-[10px] uppercase font-bold tracking-wider text-slate-400">Commerce</span>
                        <span className="text-lg font-bold text-slate-800">{selectedLocality.profile.commercial_rating}/5 ★</span>
                      </div>
                      <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <span className="block text-[10px] uppercase font-bold tracking-wider text-slate-400">Markets</span>
                        <span className="text-lg font-bold text-slate-800">{selectedLocality.profile.market_dist_km} KM</span>
                      </div>
                      <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                        <span className="block text-[10px] uppercase font-bold tracking-wider text-slate-400">Transit</span>
                        <span className="text-lg font-bold text-slate-800">{selectedLocality.profile.transit_dist_km} KM</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Recommended Usage</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedLocality.profile.best_use_suggestions?.map((item, idx) => (
                          <span key={idx} className="bg-emerald-50 text-emerald-700 border border-emerald-100 px-3 py-1 text-xs font-medium rounded-full">
                            ✓ {item}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Infrastructure Analysis - Google-like display */}
                    {selectedLocality.profile.infrastructure_data && Object.keys(selectedLocality.profile.infrastructure_data).length > 0 && (
                      <div className="bg-gradient-to-br from-slate-50 to-slate-100 p-4 rounded-lg border border-slate-200 space-y-3">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">📍 Infrastructure & Accessibility</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {Object.entries(selectedLocality.profile.infrastructure_data).map(([key, value]) => (
                            <div key={key} className="bg-white p-3 rounded-lg border border-slate-100">
                              <span className="block text-[10px] font-semibold text-slate-500 uppercase">{key.replace(/_/g, ' ')}</span>
                              <span className="block text-sm text-slate-700 mt-1">{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Nearby Places - Google Maps style */}
                    {selectedLocality.profile.nearby_places && Object.keys(selectedLocality.profile.nearby_places).length > 0 && (
                      <div className="space-y-3 border-t border-slate-200 pt-4">
                        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600">🏪 Nearby Places (Google Maps Data)</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {Object.entries(selectedLocality.profile.nearby_places).map(([category, data]) => (
                            <div key={category} className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-bold text-slate-800 capitalize">{category.replace(/_/g, ' ')}</span>
                                <span className="bg-blue-600 text-white text-xs font-bold px-2 py-1 rounded">{data.count}</span>
                              </div>
                              <span className="block text-sm text-slate-600 mb-2">
                                ⭐ Avg Rating: <span className="font-bold">{data.avg_rating}/5</span>
                              </span>
                              {data.places && data.places.length > 0 && (
                                <div className="space-y-1.5 max-h-32 overflow-y-auto">
                                  {data.places.slice(0, 3).map((place, idx) => (
                                    <div key={idx} className="text-xs bg-white p-2 rounded border border-blue-100">
                                      <div className="font-semibold text-slate-800">{place.title}</div>
                                      {place.rating && <div className="text-[10px] text-slate-500">⭐ {place.rating}</div>}
                                      {place.address && <div className="text-[10px] text-slate-500">{place.address.substring(0, 50)}...</div>}
                                    </div>
                                  ))}
                                  {data.places.length > 3 && (
                                    <div className="text-xs text-blue-600 font-semibold pt-1">+{data.places.length - 3} more</div>
                                  )}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="p-4 bg-amber-50 text-amber-700 border border-amber-100 rounded-lg text-xs font-medium animate-pulse">
                    ⏳ Analysis is being generated by the backend. Refresh in a few seconds.
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">Listings in Area</h3>
                {properties.length === 0 ? (
                  <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-slate-400 text-sm">
                    No properties listed in this location yet.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {properties.map((p) => (
                      <PropertyCard key={p.id} property={p} locality={selectedLocality} />
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="bg-white border-2 border-dashed border-slate-200 rounded-xl p-12 text-center text-slate-400 text-sm">
              Select a location to view AI analytics.
            </div>
          )}
        </div>
      </main>

      <footer className="bg-white border-t border-slate-200 px-8 py-4 text-xs text-slate-500 text-center">
        <p>Manage properties and localities via <a href="http://localhost:8000/admin/" target="_blank" rel="noopener noreferrer" className="font-semibold text-slate-700 hover:text-slate-900">Django Admin Portal</a></p>
      </footer>
    </div>
  );
}
