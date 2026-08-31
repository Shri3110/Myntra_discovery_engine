"use client";

import { useEffect, useState, FormEvent } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { Activity, Users, Target, Search, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface Stats {
  total_feedback: number;
  top_barrier: string;
  high_intent_count: number;
  total_raw_reviews: number;
  last_updated: string;
}

interface Opportunity {
  category: string;
  volume: number;
  opportunity_score: number;
}

interface Intent {
  intent: string;
  count: number;
}

interface Feedback {
  text: string;
  source: string;
  category: string;
  intent_level: string;
}

const COLORS = ['#f72585', '#7209b7', '#4cc9f0', '#4361ee', '#3a0ca3'];

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [intents, setIntents] = useState<Intent[]>([]);
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
        const [statsRes, oppRes, intentRes, feedbackRes] = await Promise.all([
          fetch('http://localhost:8000/api/stats').catch(() => null),
          fetch('http://localhost:8000/api/opportunities').catch(() => null),
          fetch('http://localhost:8000/api/intent-distribution').catch(() => null),
          fetch('http://localhost:8000/api/feedback').catch(() => null)
        ]);

        if (statsRes && statsRes.ok) {
          setStats(await statsRes.json());
          setOpportunities(await oppRes?.json());
          setIntents(await intentRes?.json());
          setFeedback(await feedbackRes?.json());
        } else {
          // Mock fallback
          setStats({ 
            total_feedback: 1245, 
            top_barrier: "Sizing/Fit Uncertainty", 
            high_intent_count: 432,
            total_raw_reviews: 1500,
            last_updated: "2026-08-24 10:00 AM"
          });
          setOpportunities([
            { category: "Sizing/Fit Uncertainty", volume: 450, opportunity_score: 1350 },
            { category: "Comparison Paralysis", volume: 320, opportunity_score: 840 },
            { category: "Waiting for Validation", volume: 210, opportunity_score: 550 },
            { category: "High Friction", volume: 150, opportunity_score: 300 }
          ]);
          setIntents([
            { intent: "High Intent", count: 432 },
            { intent: "Medium Intent", count: 500 },
            { intent: "Low Intent", count: 313 }
          ]);
          setFeedback([
            { text: "I love the dress but I'm not sure if Medium will fit my shoulders. Waiting to see if someone posts a photo review.", source: "Reddit", category: "Sizing/Fit Uncertainty", intent_level: "High Intent" },
            { text: "Wishlisted this because it looks cool, but honestly I'm just comparing it with 3 other similar items on Ajio.", source: "YouTube", category: "Comparison Paralysis", intent_level: "Medium Intent" },
            { text: "Added to wishlist so I don't lose it, but I'll only buy if they restock the pink color.", source: "Google Play", category: "High Friction", intent_level: "High Intent" }
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
      const res = await fetch('http://localhost:8000/api/search', {
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

  if (loading) return <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>Loading Engine Insights...</div>;

  return (
    <main className="dashboard-container">
      <header className="header">
        <h1>Myntra Discovery Engine</h1>
        <p>AI-Powered Wishlist Conversion Analytics</p>
      </header>

      {/* RAG Search Engine */}
      <div className="search-container">
        <form className="search-box" onSubmit={handleSearch}>
          <Search size={20} color="#adb5bd" />
          <input 
            type="text" 
            className="search-input" 
            placeholder="Ask the AI Product Strategist (e.g. 'What are the biggest sizing complaints?')"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="search-button" disabled={isSearching}>
            {isSearching ? 'Thinking...' : 'Synthesize Insights'}
          </button>
        </form>

        {aiResponse && (
          <div className="ai-response-card">
            <div className="ai-response-header">
              <Sparkles size={18} />
              <span>AI Synthesized Insight</span>
            </div>
            <div className="ai-response-content">
              <ReactMarkdown>{aiResponse}</ReactMarkdown>
            </div>

          </div>
        )}
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <Activity size={20} color="#f72585" style={{ marginBottom: '1rem' }} />
          <h3>Total Reviews</h3>
          <div className="value">{stats?.total_raw_reviews?.toLocaleString() || "N/A"}</div>
          <div style={{ fontSize: '0.75rem', color: '#adb5bd', marginTop: '0.5rem' }}>
            Last Updated: {stats?.last_updated || "N/A"}
          </div>
        </div>
        <div className="kpi-card">
          <Target size={20} color="#7209b7" style={{ marginBottom: '1rem' }} />
          <h3>Top Opportunity Area</h3>
          <div className="value" style={{ fontSize: '1.4rem', lineHeight: '2.2rem' }}>{stats?.top_barrier}</div>
        </div>
        <div className="kpi-card">
          <Users size={20} color="#4cc9f0" style={{ marginBottom: '1rem' }} />
          <h3>High Intent Users</h3>
          <div className="value highlight">{stats?.high_intent_count.toLocaleString()}</div>
        </div>
      </div>

      <div className="main-grid">
        {/* Opportunity Score Chart */}
        <div className="chart-card">
          <h2>Opportunity Score by Barrier</h2>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <BarChart data={opportunities} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" stroke="#adb5bd" />
                <YAxis dataKey="category" type="category" width={150} stroke="#adb5bd" style={{ fontSize: '0.8rem' }} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(10,10,15,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Bar dataKey="opportunity_score" fill="url(#colorUv)" radius={[0, 4, 4, 0]} />
                <defs>
                  <linearGradient id="colorUv" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#f72585" />
                    <stop offset="100%" stopColor="#7209b7" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Intent Distribution Chart */}
        <div className="chart-card">
          <h2>Intent Distribution</h2>
          <div style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={intents}
                  cx="50%"
                  cy="50%"
                  innerRadius={80}
                  outerRadius={110}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="intent"
                  stroke="none"
                >
                  {intents.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: 'rgba(10,10,15,0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

    </main>
  );
}
