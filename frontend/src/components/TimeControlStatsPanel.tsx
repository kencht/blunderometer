import React, { useEffect, useState } from 'react';
import { Clock, Zap, TrendingUp, Target, Bolt } from 'lucide-react';
import { apiService, GameStats, TimeControlStats } from '../services/api';

interface TimeControlStatsPanelProps {
  username: string;
}

export const TimeControlStatsPanel: React.FC<TimeControlStatsPanelProps> = ({ username }) => {
  const [stats, setStats] = useState<GameStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiService.getStats(username);
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    if (username) {
      fetchStats();
    }
  }, [username]);

  if (loading || !stats) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-3">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
          <div className="space-y-1">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="border border-gray-100 rounded p-1.5">
                <div className="h-2 bg-gray-200 rounded w-16 mb-1"></div>
                <div className="grid grid-cols-3 gap-1">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const timeControlData = [
    {
      name: 'Bullet',
      icon: Bolt,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      stats: stats.time_control_stats.bullet,
      description: '≤2 min + 1 sec'
    },
    {
      name: 'Blitz',
      icon: Zap,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      stats: stats.time_control_stats.blitz,
      description: '3-5 minute games'
    },
    {
      name: 'Rapid',
      icon: Clock,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      stats: stats.time_control_stats.rapid,
      description: '10-30 minute games'
    },
    {
      name: 'Classical',
      icon: Target,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      stats: stats.time_control_stats.classical,
      description: '30+ minute games'
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-3">
      <div className="mb-3">
        <h3 className="text-sm font-medium text-gray-900 flex items-center gap-1">
          <Clock className="h-4 w-4 text-blue-600" />
          Time Controls
        </h3>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {timeControlData.map((tc) => {
          const Icon = tc.icon;
          const hasData = tc.stats.games > 0;

          if (!hasData) {
            return (
              <div
                key={tc.name}
                className={`border ${tc.borderColor} rounded p-1.5 ${tc.bgColor} opacity-40`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    <Icon className={`h-3 w-3 ${tc.color}`} />
                    <span className="text-xs font-medium text-gray-900">{tc.name}</span>
                  </div>
                  <div className="text-xs text-gray-500">No games</div>
                </div>
              </div>
            );
          }

          return (
            <div
              key={tc.name}
              className={`border ${tc.borderColor} rounded p-1.5 ${tc.bgColor}`}
            >
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-1">
                  <Icon className={`h-3 w-3 ${tc.color}`} />
                  <span className="text-xs font-medium text-gray-900">{tc.name}</span>
                </div>
                <span className="text-xs text-gray-600">{tc.stats.games}</span>
              </div>

              <div className="grid grid-cols-3 gap-1 text-center">
                <div className="bg-white rounded p-1 border border-gray-100">
                  <div className="text-xs font-bold text-red-600">
                    {tc.stats.blunder_rate.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-600">Blunders</div>
                </div>

                <div className="bg-white rounded p-1 border border-gray-100">
                  <div className="text-xs font-bold text-orange-600">
                    {tc.stats.mistake_rate.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-600">Mistakes</div>
                </div>

                <div className="bg-white rounded p-1 border border-gray-100">
                  <div className="text-xs font-bold text-green-600">
                    {(100 - tc.stats.blunder_rate - tc.stats.mistake_rate).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-600">Accuracy</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
