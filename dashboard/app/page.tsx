'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

interface Stats {
  revenue: string;
  processed: number;
  pending: number;
  completed: number;
  pending_approval: number;
}

interface Activity {
  type: string;
  file: string;
  timestamp: string;
}

interface ChartData {
  dates: string[];
  completed: number[];
  pending: number[];
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState('');

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, activityRes, chartsRes] = await Promise.all([
        axios.get(`${API_BASE}/stats`),
        axios.get(`${API_BASE}/activity?limit=10`),
        axios.get(`${API_BASE}/charts`),
      ]);

      setStats(statsRes.data.stats);
      setActivity(activityRes.data.activity);
      setChartData(chartsRes.data);
      setLastUpdated(new Date(statsRes.data.last_updated).toLocaleString());
      setLoading(false);
    } catch (error) {
      console.error('Failed to load data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl">Loading...</div>
      </div>
    );
  }

  const pieData = chartData ? [
    { name: 'Completed', value: chartData.completed.reduce((a, b) => a + b, 0) },
    { name: 'Pending', value: chartData.pending.reduce((a, b) => a + b, 0) },
  ] : [];

  const COLORS = ['#10b981', '#f59e0b'];

  return (
    <div className="min-h-screen p-8">
      {/* Header */}
      <header className="mb-8 p-6 bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">
          🤖 AI Employee Dashboard
        </h1>
        <p className="text-gray-400 mb-4">Your 24/7 Digital Employee - Pure Python + Next.js 14</p>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-success rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-400">Online</span>
          <span className="text-sm text-gray-400 ml-auto">Last Updated: {lastUpdated}</span>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon="💰"
          title="Revenue"
          value={`Rs. ${stats?.revenue || '0'}`}
          label="Total Tracked"
          color="success"
        />
        <StatCard
          icon="📊"
          title="Processed"
          value={stats?.processed.toString() || '0'}
          label="Total Items"
          color="primary"
        />
        <StatCard
          icon="⏳"
          title="Pending"
          value={stats?.pending.toString() || '0'}
          label="Awaiting Action"
          color="warning"
        />
        <StatCard
          icon="✅"
          title="Completed"
          value={stats?.completed.toString() || '0'}
          label="Tasks Done"
          color="secondary"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ChartCard title="📈 Activity Trend (Last 7 Days)">
          {chartData && (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData.dates.map((date, i) => ({
                date,
                completed: chartData.completed[i],
                pending: chartData.pending[i],
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="completed" stroke="#10b981" strokeWidth={2} />
                <Line type="monotone" dataKey="pending" stroke="#f59e0b" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard title="📊 Task Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Activity Feed */}
      <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6 mb-8">
        <h3 className="text-xl font-bold mb-4">🕐 Recent Activity</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {activity.length > 0 ? (
            activity.map((item, index) => (
              <ActivityItem key={index} activity={item} />
            ))
          ) : (
            <div className="text-gray-400">No recent activity</div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center text-gray-400 py-6 border-t border-white/10">
        <p>Platinum Tier - Personal AI Employee Hackathon 0</p>
        <p className="text-sm mt-2">Built with Pure Python + FastAPI + Next.js 14</p>
      </footer>
    </div>
  );
}

function StatCard({ icon, title, value, label, color }: {
  icon: string;
  title: string;
  value: string;
  label: string;
  color: string;
}) {
  const colorClasses: { [key: string]: string } = {
    success: 'border-success/30 bg-gradient-to-br from-success/10 to-success/5',
    primary: 'border-primary/30 bg-gradient-to-br from-primary/10 to-primary/5',
    warning: 'border-warning/30 bg-gradient-to-br from-warning/10 to-warning/5',
    secondary: 'border-secondary/30 bg-gradient-to-br from-secondary/10 to-secondary/5',
  };

  return (
    <div className={`p-6 rounded-2xl border backdrop-blur-lg transition-all hover:transform hover:-translate-y-1 ${colorClasses[color] || colorClasses.primary}`}>
      <div className="flex items-center gap-4">
        <div className="text-4xl">{icon}</div>
        <div>
          <h3 className="text-sm text-gray-400 mb-1">{title}</h3>
          <p className="text-3xl font-bold">{value}</p>
          <p className="text-xs text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white/5 backdrop-blur-lg rounded-2xl border border-white/10 p-6">
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      {children}
    </div>
  );
}

function ActivityItem({ activity }: { activity: Activity }) {
  return (
    <div className="flex items-center gap-4 p-4 rounded-xl bg-white/5 hover:bg-white/10 transition-all">
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl ${
        activity.type === 'completed' ? 'bg-success/20' : 'bg-warning/20'
      }`}>
        {activity.type === 'completed' ? '✅' : '⏳'}
      </div>
      <div className="flex-1">
        <div className="font-medium">{activity.file}</div>
        <div className="text-sm text-gray-400">{new Date(activity.timestamp).toLocaleString()}</div>
      </div>
    </div>
  );
}
