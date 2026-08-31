"use client";

import { useEffect, useState, FormEvent } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  Legend, Cell
} from 'recharts';
import { Activity, Users, Target, Search, Sparkles, MessageSquare, Tag } from 'lucide-react';
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
            last_updated: "2026-08-31 10:00 AM"
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

  const handleSearch = async (e: FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    setAiResponse("");
    setSearchSources([]);
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/api/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery })
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

  if (loading) return (
    <div className="flex h-screen items-center justify-center bg-[#0D0D0D] text-white">
      Loading Engine Insights...
    </div>
  );

  return (
    <main className="min-h-screen bg-[#0D0D0D] text-[#f8f9fa] p-8 md:p-12 font-sans selection:bg-[#f72585] selection:text-white">
      <header className="mb-12 animate-[fadeInDown_0.8s_ease-out_forwards]">
        <h1 className="text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-br from-[#f72585] to-[#7209b7] bg-clip-text text-transparent inline-block">
          Myntra Discovery Engine
        </h1>
        <p className="text-[#adb5bd] text-lg">AI-Powered Persona & Theme Analytics</p>
      </header>

      {/* RAG Search Engine */}
      <div className="mb-12">
        <form className="flex items-center bg-[rgba(255,255,255,0.03)] border border-gray-800 rounded-full px-6 py-3 shadow-[0_4px_20px_rgba(0,0,0,0.2)] focus-within:border-[#f72585] focus-within:shadow-[0_4px_20px_rgba(247,37,133,0.2)] transition-all duration-300" onSubmit={handleSearch}>
          <Search size={20} className="text-gray-400" />
          <input 
            type="text" 
            className="flex-1 bg-transparent border-none text-white text-base px-4 py-2 outline-none placeholder-gray-500" 
            placeholder="Ask the AI Product Strategist (e.g. 'What do Deal Hunters complain about?')"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="bg-gradient-to-r from-[#f72585] to-[#7209b7] text-white rounded-full px-6 py-2 font-semibold hover:opacity-90 transition-opacity disabled:opacity-50" disabled={isSearching}>
            {isSearching ? 'Synthesizing...' : 'Synthesize Insights'}
          </button>
        </form>
        
        {aiResponse && (
          <div className="mt-6 bg-[rgba(114,9,183,0.05)] border border-[rgba(114,9,183,0.3)] rounded-2xl p-8 animate-[fadeIn_0.5s_ease-out]">
            <div className="flex items-center gap-2 text-[#f72585] font-semibold mb-4">
              <Sparkles size={20} /> AI Synthesis
            </div>
            <div className="text-gray-200 leading-relaxed prose prose-invert max-w-none">
              <ReactMarkdown>{aiResponse}</ReactMarkdown>
            </div>
            {searchSources.length > 0 && (
              <div className="mt-6 pt-4 border-t border-[rgba(255,255,255,0.05)]">
                <span className="text-xs uppercase tracking-wider text-gray-500 font-semibold mb-2 block">Sources Cited:</span>
                <div className="flex flex-wrap gap-2">
                  {searchSources.map((source, i) => (
                    <span key={i} className="text-xs bg-black/40 text-gray-400 px-3 py-1 rounded-full border border-gray-800">{source}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div className="bg-[rgba(255,255,255,0.03)] backdrop-blur-xl border border-gray-800 rounded-2xl p-6 transition-all hover:bg-[rgba(255,255,255,0.05)] hover:-translate-y-1 hover:shadow-2xl hover:border-[#f72585]/30 group">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Total Raw Reviews</h3>
            <MessageSquare size={18} className="text-gray-500 group-hover:text-[#f72585] transition-colors" />
          </div>
          <div className="text-4xl font-extrabold text-white mb-2">{stats?.total_raw_reviews.toLocaleString()}</div>
          <p className="text-xs text-gray-500">Last Updated: {stats?.last_updated}</p>
        </div>

        <div className="bg-[rgba(255,255,255,0.03)] backdrop-blur-xl border border-gray-800 rounded-2xl p-6 transition-all hover:bg-[rgba(255,255,255,0.05)] hover:-translate-y-1 hover:shadow-2xl hover:border-[#7209b7]/30 group">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Reviews Processed</h3>
            <Activity size={18} className="text-gray-500 group-hover:text-[#7209b7] transition-colors" />
          </div>
          <div className="text-4xl font-extrabold text-[#4cc9f0] mb-2">{stats?.reviews_processed.toLocaleString()}</div>
          <p className="text-xs text-gray-500">Successfully embedded via RAG</p>
        </div>

        <div className="bg-[rgba(255,255,255,0.03)] backdrop-blur-xl border border-gray-800 rounded-2xl p-6 transition-all hover:bg-[rgba(255,255,255,0.05)] hover:-translate-y-1 hover:shadow-2xl hover:border-[#4cc9f0]/30 group">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Extracted Themes</h3>
            <Tag size={18} className="text-gray-500 group-hover:text-[#4cc9f0] transition-colors" />
          </div>
          <div className="text-4xl font-extrabold text-white mb-2">{stats?.extracted_themes}</div>
          <p className="text-xs text-gray-500">Unique conversation clusters</p>
        </div>

        <div className="bg-[rgba(255,255,255,0.03)] backdrop-blur-xl border border-gray-800 rounded-2xl p-6 transition-all hover:bg-[rgba(255,255,255,0.05)] hover:-translate-y-1 hover:shadow-2xl hover:border-[#4361ee]/30 group">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Identified Personas</h3>
            <Users size={18} className="text-gray-500 group-hover:text-[#4361ee] transition-colors" />
          </div>
          <div className="text-4xl font-extrabold text-white mb-2">{stats?.identified_personas}</div>
          <p className="text-xs text-gray-500">Distinct user archetypes</p>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        
        {/* Top 5 User Personas Card */}
        <div className="bg-[rgba(255,255,255,0.03)] border border-gray-800 rounded-2xl p-6 md:p-8">
          <h2 className="text-xl font-bold mb-6 text-white flex items-center gap-2">
            <Users className="text-[#f72585]" size={24} /> 
            Top 5 User Personas
          </h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={personas} margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="#adb5bd" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" stroke="#adb5bd" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  contentStyle={{ backgroundColor: '#0a0a0f', border: '1px solid #333', borderRadius: '12px', color: '#fff' }}
                  // @ts-ignore
                  formatter={(value: any, name: any, props: any) => [`${value} users (${props?.payload?.percentage}%)`, name]}
                />
                <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={32}>
                  {personas.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Topic Distribution by Persona Card */}
        <div className="bg-[rgba(255,255,255,0.03)] border border-gray-800 rounded-2xl p-6 md:p-8">
          <h2 className="text-xl font-bold mb-6 text-white flex items-center gap-2">
            <Target className="text-[#4cc9f0]" size={24} /> 
            Topic Distribution by Persona
          </h2>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topicDist} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="persona" stroke="#adb5bd" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#adb5bd" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  contentStyle={{ backgroundColor: '#0a0a0f', border: '1px solid #333', borderRadius: '12px', color: '#fff' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '20px' }} />
                <Bar dataKey="Sizing & Fit" stackId="a" fill="#f72585" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Pricing & Value" stackId="a" fill="#7209b7" radius={[0, 0, 0, 0]} />
                <Bar dataKey="App Experience" stackId="a" fill="#4cc9f0" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Delivery & Logistics" stackId="a" fill="#4361ee" radius={[0, 0, 0, 0]} />
                <Bar dataKey="General Experience" stackId="a" fill="#3a0ca3" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Raw Feedback Stream */}
      <div className="bg-[rgba(255,255,255,0.03)] border border-gray-800 rounded-2xl overflow-hidden animate-[fadeInUp_0.8s_ease-out_both_0.2s]">
        <div className="p-6 border-b border-gray-800">
          <h2 className="text-xl font-bold text-white">Live Feedback Stream</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-black/20">
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">User Verbatim</th>
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Source</th>
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Persona</th>
                <th className="p-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Theme</th>
              </tr>
            </thead>
            <tbody>
              {feedback.map((item, i) => (
                <tr key={i} className="hover:bg-white/5 border-b border-gray-800/50 transition-colors">
                  <td className="p-4 text-sm text-gray-200">{item.text}</td>
                  <td className="p-4 text-sm text-gray-400">{item.source}</td>
                  <td className="p-4">
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-[#7209b7]/10 text-[#a544f8] border border-[#7209b7]/30">
                      {item.persona}
                    </span>
                  </td>
                  <td className="p-4">
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-[#4cc9f0]/10 text-[#4cc9f0] border border-[#4cc9f0]/30">
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
