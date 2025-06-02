import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Target, BarChart3 } from 'lucide-react';
import { apiService, GameStats } from '../services/api';

export const StatsPanel: React.FC<{ username: string }> = ({ username }) => {
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

    fetchStats();
    const interval = setInterval(fetchStats, 10000);
    return () => clearInterval(interval);
  }, [username]);

  if (loading) {
    return (
      <div className="grid grid-cols-2 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 animate-pulse">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="h-3 bg-gray-200 rounded w-16 mb-2"></div>
                <div className="h-6 bg-gray-200 rounded w-12 mb-1"></div>
                <div className="h-2 bg-gray-200 rounded w-20"></div>
              </div>
              <div className="h-8 w-8 bg-gray-200 rounded-full"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8">
        <div className="text-center text-gray-500">
          <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p>Failed to load statistics</p>
        </div>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Games',
      value: stats.games.total.toLocaleString(),
      subtitle: `${stats.games.analyzed} analyzed`,
      icon: BarChart3,
      color: 'blue',
      trend: `${stats.games.analysis_progress.toFixed(1)}% complete`,
    },
    {
      title: 'Blunder Rate',
      value: `${stats.moves.blunder_rate.toFixed(2)}%`,
      subtitle: `${stats.moves.blunders.toLocaleString()} blunders`,
      icon: TrendingDown,
      color: 'red',
      trend: `of ${stats.moves.total.toLocaleString()} moves`,
    },
    {
      title: 'Mistake Rate',
      value: `${stats.moves.mistake_rate.toFixed(2)}%`,
      subtitle: `${stats.moves.mistakes.toLocaleString()} mistakes`,
      icon: TrendingUp,
      color: 'orange',
      trend: `Accuracy focus area`,
    },
    {
      title: 'Accuracy',
      value: `${(100 - stats.moves.blunder_rate - stats.moves.mistake_rate - stats.moves.inaccuracy_rate).toFixed(1)}%`,
      subtitle: `${stats.moves.inaccuracies.toLocaleString()} inaccuracies`,
      icon: Target,
      color: 'green',
      trend: `Overall performance`,
    },
  ];

  const getColorClasses = (color: string) => {
    const colors = {
      blue: {
        icon: 'text-blue-600 bg-blue-50 border-blue-100',
        text: 'text-blue-600',
        bg: 'hover:bg-blue-50'
      },
      red: {
        icon: 'text-chess-blunder bg-red-50 border-red-100',
        text: 'text-chess-blunder',
        bg: 'hover:bg-red-50'
      },
      orange: {
        icon: 'text-chess-mistake bg-orange-50 border-orange-100',
        text: 'text-chess-mistake',
        bg: 'hover:bg-orange-50'
      },
      green: {
        icon: 'text-chess-good bg-green-50 border-green-100',
        text: 'text-chess-good',
        bg: 'hover:bg-green-50'
      },
    };
    return colors[color as keyof typeof colors] || colors.blue;
  };

  return (
    <div className="grid grid-cols-2 gap-4">
      {statCards.map((card, index) => {
        const Icon = card.icon;
        const colors = getColorClasses(card.color);
        
        return (
          <div 
            key={index} 
            className={`bg-white rounded-xl shadow-sm border border-gray-100 p-4 transition-all duration-200 ${colors.bg} hover:shadow-md group`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-gray-600 mb-1">{card.title}</p>
                <p className="text-xl font-bold text-gray-900 mb-1 truncate">{card.value}</p>
                <p className="text-xs text-gray-500 mb-1">{card.subtitle}</p>
                <p className={`text-xs font-medium ${colors.text}`}>{card.trend}</p>
              </div>
              <div className={`p-2 rounded-xl border ${colors.icon} group-hover:scale-110 transition-transform duration-200`}>
                <Icon className="h-4 w-4" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};