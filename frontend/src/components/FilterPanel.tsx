import React, { useState, useEffect } from 'react';
import { FilterOptions, apiService, GameStats } from '../services/api';
import { Filter, Calendar, Clock, Target, BarChart3 } from 'lucide-react';

interface FilterPanelProps {
  filters: FilterOptions;
  onFiltersChange: (filters: FilterOptions) => void;
  username: string;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFiltersChange, username }) => {
  const [stats, setStats] = useState<GameStats | null>(null);
  const [localFilters, setLocalFilters] = useState<FilterOptions>(filters);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const gameStats = await apiService.getStats(username);
        setStats(gameStats);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };
    fetchStats();
  }, [username]);

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const timeControls = stats?.time_controls?.map(tc => tc.name) || [];
  const uniqueTimeControls = Array.from(new Set(timeControls));

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Filter className="h-5 w-5 text-blue-600" />
          Filters
        </h3>
        <p className="text-sm text-gray-600 mt-1">Customize your analysis</p>
      </div>
      
      <div className="p-6 space-y-6">
        {/* Rolling Window */}
        <div>
          <label htmlFor="rolling-window" className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-gray-500" />
            Rolling Average Window
          </label>
          <select
            id="rolling-window"
            value={localFilters.rollingWindow || 10}
            onChange={(e) => handleFilterChange('rollingWindow', parseInt(e.target.value))}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value={5}>5 games</option>
            <option value={10}>10 games</option>
            <option value={20}>20 games</option>
            <option value={50}>50 games</option>
          </select>
          <p className="text-xs text-gray-500 mt-2">Smooths performance trends</p>
        </div>

        {/* Time Control */}
        {uniqueTimeControls.length > 1 && (
          <div>
            <label htmlFor="time-control" className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Clock className="h-4 w-4 text-gray-500" />
              Time Control
            </label>
            
            {/* Quick time control buttons */}
            <div className="grid grid-cols-2 gap-2 mb-3">
              {['bullet', 'blitz', 'rapid', 'classical'].map((tc) => (
                <button
                  key={tc}
                  onClick={() => handleFilterChange('timeControl', tc)}
                  className={`px-3 py-2 text-xs font-medium rounded-lg border transition-colors ${
                    localFilters.timeControl === tc
                      ? 'bg-blue-500 text-white border-blue-500'
                      : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  {tc.charAt(0).toUpperCase() + tc.slice(1)}
                </button>
              ))}
            </div>
            
            <select
              id="time-control"
              value={localFilters.timeControl || ''}
              onChange={(e) => handleFilterChange('timeControl', e.target.value || undefined)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            >
              <option value="">Select time control</option>
              {uniqueTimeControls.map(tc => (
                <option key={tc} value={tc}>{tc}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-2">Filter by game speed</p>
          </div>
        )}

        {/* Rating Range */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Target className="h-4 w-4 text-gray-500" />
            Opponent Rating Range
          </label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <input
                type="number"
                placeholder="Min"
                value={localFilters.ratingRange?.[0] || ''}
                onChange={(e) => {
                  const min = e.target.value ? parseInt(e.target.value) : undefined;
                  const max = localFilters.ratingRange?.[1];
                  handleFilterChange('ratingRange', min !== undefined || max !== undefined ? [min || 0, max || 3000] : undefined);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <input
                type="number"
                placeholder="Max"
                value={localFilters.ratingRange?.[1] || ''}
                onChange={(e) => {
                  const max = e.target.value ? parseInt(e.target.value) : undefined;
                  const min = localFilters.ratingRange?.[0];
                  handleFilterChange('ratingRange', min !== undefined || max !== undefined ? [min || 0, max || 3000] : undefined);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Analyze specific skill levels</p>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gray-500" />
            Date Range
          </label>
          <div className="space-y-3">
            <div>
              <input
                type="date"
                value={localFilters.dateRange?.[0] || ''}
                onChange={(e) => {
                  const start = e.target.value || undefined;
                  const end = localFilters.dateRange?.[1];
                  handleFilterChange('dateRange', start || end ? [start || '', end || ''] : undefined);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <input
                type="date"
                value={localFilters.dateRange?.[1] || ''}
                onChange={(e) => {
                  const end = e.target.value || undefined;
                  const start = localFilters.dateRange?.[0];
                  handleFilterChange('dateRange', start || end ? [start || '', end || ''] : undefined);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Focus on specific periods</p>
        </div>

        {/* Quick Stats */}
        {stats && (
          <div className="pt-4 border-t border-gray-100">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Quick Stats</h4>
            <div className="space-y-2 text-xs text-gray-600">
              <div className="flex justify-between">
                <span>Total Games:</span>
                <span className="font-medium">{stats.games.total}</span>
              </div>
              <div className="flex justify-between">
                <span>Analyzed:</span>
                <span className="font-medium text-green-600">{stats.games.analyzed}</span>
              </div>
              <div className="flex justify-between">
                <span>Total Moves:</span>
                <span className="font-medium">{stats.moves.total.toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};