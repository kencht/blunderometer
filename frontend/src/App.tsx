import React, { useState } from 'react';
import { PerformanceChart } from './components/PerformanceChart';
import { FilterPanel } from './components/FilterPanel';
import { StatsPanel } from './components/StatsPanel';
import { TimeControlStatsPanel } from './components/TimeControlStatsPanel';
import { WorkflowPanel } from './components/WorkflowPanel';
import { FilterOptions } from './services/api';
import { Crown, Activity, Settings, BarChart3, Play, Clock } from 'lucide-react';

function App() {
  const [filters, setFilters] = useState<FilterOptions>({
    rollingWindow: 10,
    timeControl: 'blitz',
  });
  const [statsKey, setStatsKey] = useState(0);
  const [username, setUsername] = useState(''); // The submitted/active username
  const [usernameInput, setUsernameInput] = useState(''); // The input field value

  const handleStatsUpdate = () => {
    setStatsKey(prev => prev + 1);
  };

  const handleUsernameSubmit = () => {
    if (usernameInput.trim()) {
      setUsername(usernameInput.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl shadow-lg">
                <Crown className="h-7 w-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Chess Blunder Tracker</h1>
                <p className="text-sm text-gray-600">Performance Analysis Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 bg-green-50 px-4 py-2 rounded-full border border-green-200">
              <Activity className="h-5 w-5 text-green-600" />
              <span className="text-sm font-medium text-green-700">Live Data</span>
            </div>
          </div>
          {/* Username input */}
          <div className="flex items-center gap-4 py-2">
            <label htmlFor="username" className="text-sm font-medium text-gray-700">Lichess Username:</label>
            <div className="flex items-center gap-2">
              <input
                id="username"
                type="text"
                className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={usernameInput}
                onChange={e => setUsernameInput(e.target.value)}
                placeholder="Enter Lichess username"
                style={{ width: 200 }}
                onKeyPress={e => e.key === 'Enter' && handleUsernameSubmit()}
              />
              <button
                onClick={handleUsernameSubmit}
                disabled={!usernameInput.trim()}
                className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Submit
              </button>
              {username && (
                <span className="text-sm text-green-600 font-medium">
                  Active: {username}
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Getting Started and Performance Overview - Side by Side */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Getting Started */}
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <Play className="h-6 w-6 text-blue-600" />
                Getting Started
              </h2>
              <p className="text-gray-600 mt-1">Fetch and analyze your chess games from Lichess</p>
            </div>
            <WorkflowPanel onStatsUpdate={handleStatsUpdate} username={username} onUsernameChange={setUsername} />
          </div>

          {/* Performance Overview */}
          <div>
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <BarChart3 className="h-6 w-6 text-blue-600" />
                Performance Overview
              </h2>
              <p className="text-gray-600 mt-1">Key metrics from your chess games</p>
            </div>
            <StatsPanel key={statsKey} username={username} />
          </div>
        </section>

        {/* Time Control Breakdown */}
        <section>
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Clock className="h-6 w-6 text-blue-600" />
              Time Control Analysis
            </h2>
            <p className="text-gray-600 mt-1">Performance breakdown by game time control</p>
          </div>
          <TimeControlStatsPanel key={statsKey} username={username} />
        </section>

        {/* Main Content */}
        <section className="grid grid-cols-1 xl:grid-cols-6 gap-8">
          {/* Filters Sidebar */}
          <div className="xl:col-span-1">
            <div className="sticky top-8">
              <FilterPanel filters={filters} onFiltersChange={setFilters} username={username} />
            </div>
          </div>

          {/* Chart Area */}
          <div className="xl:col-span-5">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-100">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">
                      Performance Trends
                    </h2>
                    <p className="text-gray-600 mt-1">Track your improvement over time</p>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-500 bg-gray-50 px-3 py-2 rounded-lg">
                    <Settings className="h-4 w-4" />
                    <span>Rolling {filters.rollingWindow || 10}-game average</span>
                  </div>
                </div>
              </div>
              <div className="p-4">
                <PerformanceChart filters={filters} height={560} key={statsKey} username={username} />
              </div>
              
              <div className="p-6 bg-gray-50 border-t border-gray-100">
                <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                  <Activity className="h-4 w-4" />
                  Chart Legend
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-chess-blunder"></div>
                    <span><span className="font-medium">Blunder:</span> ≥300 centipawns</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-chess-mistake"></div>
                    <span><span className="font-medium">Mistake:</span> 100-299 centipawns</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-chess-inaccuracy"></div>
                    <span><span className="font-medium">Inaccuracy:</span> 50-99 centipawns</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    <span><span className="font-medium">Trend:</span> Rolling average</span>
                  </div>
                </div>
                <p className="text-gray-600 mt-3 text-xs">
                  Rolling averages smooth out day-to-day variations to show long-term improvement trends.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Additional Information */}
        <section className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start space-x-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">Performance Insights</h3>
              <p className="text-blue-800 leading-relaxed">
                Track your chess improvement over time with rolling averages that reveal trends in your move accuracy. 
                Use the filters to analyze specific time controls, rating ranges, or date periods to identify patterns 
                in your play and discover areas for focused improvement.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;