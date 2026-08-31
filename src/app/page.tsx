"use client";

import { useEffect, useState, FormEvent } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  Legend, Cell
} from 'recharts';
import { Users, BarChart2, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Stats {
  total_raw_reviews: number;
  reviews_processed: number;
  extracted_themes: number;
  identified_personas: number;
  last_updated: string;
}

interface Persona {
  name: string;
  value: number;
  percentage: number;
}

interface TopicDistribution {
  persona: string;
  [key: string]: string | number;
}

interface Feedback {
  text: string;
  source: string;
  theme: string;
  persona: string;
}

const COLORS = ['#f72585', '#7209b7', '#4cc9f0', '#4361ee', '#3a0ca3'];

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [topicDist, setTopicDist] = useState<TopicDistribution[]>([]);
  const [feedback, setFeedback] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);

  // Search Engine State
  const [searchQuery, setSearchQuery] = useState("");
  const [aiResponse, setAiResponse] = useState("");
  const [searchSources, setSearchSources] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const [statsRes, personaRes, feedbackRes] = await Promise.all([
          fetch(`${apiUrl}/api/stats`).catch(() => null),
          fetch(`${apiUrl}/api/personas`).catch(() => null),
          fetch(`${apiUrl}/api/feedback`).catch(() => null)
        ]);

        if (statsRes && statsRes.ok) {
          setStats(await statsRes.json());
          const personaData = await personaRes?.json();
          setPersonas(personaData?.top_personas || []);
          setTopicDist(personaData?.topic_distribution || []);
          setFeedback(await feedbackRes?.json());
        } else {
          // Mock fallback
          setStats({ 
            total_raw_reviews: 1500,
            reviews_processed: 1082, 
            extracted_themes: 12,
            identified_personas: 5,
            last_updated: "8/31/2026, 10:00:00 AM"
          });
          setPersonas([
            { name: "Quality Seeker", value: 450, percentage: 41.5 },
            { name: "Deal Hunter", value: 320, percentage: 29.5 },
            { name: "App Skeptic", value: 150, percentage: 13.8 },
            { name: "Brand Loyalist", value: 100, percentage: 9.2 },
            { name: "Trend Setter", value: 62, percentage: 6.0 }
          ]);
          setTopicDist([
            { persona: "Quality Seeker", "Sizing & Fit": 400, "General Experience": 50 },
            { persona: "Deal Hunter", "Pricing & Value": 300, "General Experience": 20 },
            { persona: "App Skeptic", "App Experience": 130, "General Experience": 20 },
            { persona: "Brand Loyalist", "Delivery & Logistics": 30, "General Experience": 70 },
            { persona: "Trend Setter", "Sizing & Fit": 20, "Pricing & Value": 42 }
          ]);
          setFeedback([
            { text: "I love the dress but I'm not sure if Medium will fit my shoulders.", source: "Reddit", theme: "Sizing & Fit", persona: "Quality Seeker" },
            { text: "Waiting for a big discount before I buy this.", source: "YouTube", theme: "Pricing & Value", persona: "Deal Hunter" },
            { text: "App crashes every time I try to add this to cart.", source: "Google Play", theme: "App Experience", persona: "App Skeptic" }
          ]);
        }
      } catch (e) {
        console.error("API error", e);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleSearch = async (e?: FormEvent, presetQuery?: string) => {
    if (e) e.preventDefault();
    const queryToSearch = presetQuery || searchQuery;
    if (!queryToSearch.trim()) return;
    
    if (presetQuery) {
      setSearchQuery(presetQuery);
    }
    
    setIsSearching(true);
    setAiResponse("");
    setSearchSources([]);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryToSearch })
      });
      
      const data = await res.json();
      setAiResponse(data.response || "No response received.");
      setSearchSources(data.sources || []);
    } catch (e) {
      setAiResponse("⚠️ Error connecting to the AI backend. Is it running?");
    } finally {
      setIsSearching(false);
    }
  };

  const sampleQueries = [
    "Why do users abandon their carts?",
    "What do people think about delivery times?",
    "Are there complaints about missing items?"
  ];

  if (loading) return (
    <div className="flex h-screen items-center justify-center bg-[#0a0a0a] text-white">
      Loading Engine Insights...
    </div>
  );

  return (
    <main className="min-h-screen bg-[#0a0a0a] text-gray-200 p-8 md:p-12 font-sans selection:bg-[#f72585] selection:text-white">
      {/* Header aligned left per image */}
      <header className="mb-10">
        <h1 className="text-[32px] font-bold text-white mb-2 tracking-tight">
          Myntra AI Discovery Engine
        </h1>
        <p className="text-gray-400 text-[15px]">
          Product intelligence powered by unstructured user feedback.
        </p>
      </header>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl p-5">
          <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Total Raw Reviews</div>
          <div className="text-[32px] font-bold text-white leading-none">{stats?.total_raw_reviews.toLocaleString()}</div>
          <div className="text-[11px] text-gray-500 mt-3 font-medium">Updated: {stats?.last_updated}</div>
        </div>

        <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl p-5">
          <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Reviews Processed</div>
          <div className="text-[32px] font-bold text-white leading-none">{stats?.reviews_processed.toLocaleString()}</div>
        </div>

        <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl p-5">
          <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Extracted Themes</div>
          <div className="text-[32px] font-bold text-white leading-none">{stats?.extracted_themes}</div>
        </div>

        <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl p-5">
          <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Identified Personas</div>
          <div className="text-[32px] font-bold text-white leading-none">{stats?.identified_personas}</div>
        </div>
      </div>

      {/* Search Engine Container */}
      <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl p-6 mb-8">
        <form className="flex flex-col md:flex-row gap-4 mb-4" onSubmit={(e) => handleSearch(e)}>
          <input 
            type="text" 
            className="flex-1 bg-[#0a0a0a] border border-[#f72585] rounded-lg px-5 py-3.5 text-white text-[15px] outline-none placeholder-gray-500 transition-colors focus:border-[#ff479d]" 
            placeholder="Ask anything about user pain points, feature requests, or delivery..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button 
            type="submit" 
            className="bg-[#f72585]/10 hover:bg-[#f72585]/20 text-[#f72585] border border-[#f72585]/50 rounded-lg px-8 py-3.5 font-medium flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            disabled={isSearching}
          >
            <Sparkles size={18} /> {isSearching ? 'Discovering...' : 'Discover'}
          </button>
        </form>
        
        {/* Sample queries pills */}
        <div className="flex flex-wrap gap-3">
          {sampleQueries.map((query, i) => (
            <button
              key={i}
              type="button"
              onClick={() => handleSearch(undefined, query)}
              className="text-[13px] text-gray-300 border border-[#2a2a2a] bg-[#1a1a1a] rounded-full px-4 py-2 hover:bg-[#2a2a2a] transition-colors"
            >
              "{query}"
            </button>
          ))}
        </div>

        {/* Search Results */}
        {aiResponse && (
          <div className="mt-8 bg-[#0a0a0a] border border-[#7209b7]/30 rounded-xl p-6">
            <div className="text-gray-200 leading-relaxed prose prose-invert max-w-none text-[15px]">
              <ReactMarkdown>{aiResponse}</ReactMarkdown>
            </div>
            {searchSources.length > 0 && (
              <div className="mt-6 pt-4 border-t border-[#2a2a2a]">
                <span className="text-[11px] uppercase tracking-wider text-gray-500 font-semibold mb-3 block">Sources Cited:</span>
                <div className="flex flex-wrap gap-2">
                  {searchSources.map((source, i) => (
                    <span key={i} className="text-xs bg-[#161616] text-gray-400 px-3 py-1.5 rounded border border-[#2a2a2a]">{source}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        
        {/* Top 5 User Personas Card */}
        <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl p-6">
          <h2 className="text-[17px] font-bold mb-6 text-white flex items-center gap-2">
            <Users className="text-blue-500" size={20} /> 
            Top 5 User Personas
          </h2>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={personas} margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#2a2a2a" />
                <XAxis type="number" stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" stroke="#d1d5db" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  contentStyle={{ backgroundColor: '#161616', border: '1px solid #2a2a2a', borderRadius: '8px', color: '#fff' }}
                  // @ts-ignore
                  formatter={(value: any, name: any, props: any) => [`${value} users (${props?.payload?.percentage}%)`, name]}
                />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                  {personas.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Topic Distribution by Persona Card */}
        <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl p-6">
          <h2 className="text-[17px] font-bold mb-6 text-white flex items-center gap-2">
            <BarChart2 className="text-green-500" size={20} /> 
            Topic Distribution by Persona
          </h2>
          <div className="h-[280px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topicDist} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#2a2a2a" />
                <XAxis dataKey="persona" stroke="#d1d5db" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#6b7280" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  contentStyle={{ backgroundColor: '#161616', border: '1px solid #2a2a2a', borderRadius: '8px', color: '#fff' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} iconType="circle" />
                <Bar dataKey="Sizing & Fit" stackId="a" fill="#f72585" radius={[0, 0, 0, 0]} barSize={32} />
                <Bar dataKey="Pricing & Value" stackId="a" fill="#7209b7" radius={[0, 0, 0, 0]} />
                <Bar dataKey="App Experience" stackId="a" fill="#4cc9f0" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Delivery & Logistics" stackId="a" fill="#4361ee" radius={[0, 0, 0, 0]} />
                <Bar dataKey="General Experience" stackId="a" fill="#3a0ca3" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      
      {/* (Optional) Feedback Table */}
      {/* Kept this down below so it doesn't clutter the top view */}
      <div className="bg-[#161616] border border-[#2a2a2a] rounded-xl overflow-hidden mt-8">
        <div className="p-5 border-b border-[#2a2a2a]">
          <h2 className="text-[17px] font-bold text-white">Live Feedback Stream</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#0a0a0a]">
                <th className="p-4 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">User Verbatim</th>
                <th className="p-4 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Source</th>
                <th className="p-4 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Persona</th>
                <th className="p-4 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Theme</th>
              </tr>
            </thead>
            <tbody>
              {feedback.map((item, i) => (
                <tr key={i} className="hover:bg-[#1a1a1a] border-b border-[#2a2a2a] transition-colors">
                  <td className="p-4 text-[13px] text-gray-300">{item.text}</td>
                  <td className="p-4 text-[13px] text-gray-500">{item.source}</td>
                  <td className="p-4">
                    <span className="inline-block px-3 py-1 rounded-md text-[11px] font-semibold bg-[#7209b7]/20 text-[#a544f8]">
                      {item.persona}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="inline-block px-3 py-1 rounded-md text-[11px] font-semibold bg-[#f72585]/20 text-[#ff479d]">
                      {item.theme}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
