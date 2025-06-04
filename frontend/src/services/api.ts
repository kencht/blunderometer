import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? window.location.origin  // Use same domain as frontend in production
  : 'http://localhost:5001'; // Use localhost for development

export interface TimeControlStats {
  games: number;
  moves: number;
  blunders: number;
  mistakes: number;
  blunder_rate: number;
  mistake_rate: number;
}

export interface GameStats {
  games: {
    total: number;
    analyzed: number;
    unanalyzed: number;
    analysis_progress: number;
    latest_date: string | null;
    oldest_date: string | null;
  };
  moves: {
    total: number;
    blunders: number;
    mistakes: number;
    inaccuracies: number;
    blunder_rate: number;
    mistake_rate: number;
    inaccuracy_rate: number;
  };
  operation_status: {
    analyzing: boolean;
    fetching: boolean;
    last_operation: {
      type: string;
      completed_at: string;
      result?: string;
      error?: string;
    } | null;
    progress: Record<string, any>;
  };
  time_controls: Array<{
    name: string;
    count: number;
  }>;
  time_control_stats: {
    bullet: TimeControlStats;
    blitz: TimeControlStats;
    rapid: TimeControlStats;
    classical: TimeControlStats;
  };
}

export interface GameData {
  game_id: string;
  played_at: string;
  time_control: string;
  opponent_rating: number;
  result: string;
  opening_name: string;
  fully_analyzed: boolean;
}

export interface MoveData {
  id: number;
  game_lichess_id: string;
  move_number: number;
  move_san: string;
  centipawn_loss: number;
  is_blunder: boolean;
  is_mistake: boolean;
  is_inaccuracy: boolean;
  played_at: string;
  time_control: string;
  opponent_rating: number;
  opening_name: string;
}

export interface PerformanceData {
  date: string;
  blunder_rate: number;
  mistake_rate: number;
  inaccuracy_rate: number;
  total_moves: number;
  avg_centipawn_loss: number;
  user_rating: number | null;
  opponent_rating: number | null;
  opponent_blunder_rate?: number; // Simulated opponent blunder rate percentage
}

export interface FilterOptions {
  timeControl?: string;
  ratingRange?: [number, number];
  dateRange?: [string, string];
  opening?: string;
  rollingWindow?: number;
}

class ApiService {
  private axios = axios.create({
    baseURL: API_BASE_URL,
    timeout: 90000,  // Increased timeout for cloud deployment (90 seconds)
  });

  async getStats(username: string, timeControl?: string): Promise<GameStats> {
    const params: any = { username };
    if (timeControl) {
      params.time_control = timeControl;
    }
    const response = await this.axios.get<GameStats>('/api/stats', { params });
    return response.data;
  }

  async getGames(): Promise<GameData[]> {
    const response = await this.axios.get<GameData[]>('/api/games');
    return response.data;
  }

  async getMoves(): Promise<MoveData[]> {
    const response = await this.axios.get<MoveData[]>('/api/moves');
    return response.data;
  }

  async getPerformanceData(username: string, filters?: FilterOptions): Promise<PerformanceData[]> {
    const params = { ...filters, username };
    const response = await this.axios.get<PerformanceData[]>('/api/performance', { params });
    return response.data;
  }

  async fetchGames(username: string, count: number = 50, fetchOlder: boolean = false): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.axios.post<{ message: string }>('/api/fetch-games', {
        username,
        batch_size: count,
        fetch_older: fetchOlder
      });
      return { 
        success: true, 
        message: response.data.message || 'Started fetching games' 
      };
    } catch (error: any) {
      // Enhanced error handling for cloud deployment
      let errorMessage = 'Failed to fetch games';
      
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        errorMessage = 'Request timed out. The server may be experiencing high load. Please try again in a moment.';
      } else if (error.response) {
        // Server responded with error
        errorMessage = error.response.data?.error || `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error. Please check your connection and try again.';
      } else {
        // Other error
        errorMessage = error.message || 'Unknown error occurred';
      }
      
      return {
        success: false,
        message: errorMessage
      };
    }
  }

  async analyzeGames(username: string, timeLimitPerGame: number = 20, totalTimeLimit?: number): Promise<{ success: boolean; message: string }> {
    const requestData: any = {
      username,
      time_limit_per_game: timeLimitPerGame
    };
    
    if (totalTimeLimit) {
      requestData.total_time_limit = totalTimeLimit;
    }
    
    try {
      const response = await this.axios.post<{ success: boolean; message: string }>('/api/analyze-games', requestData);
      return { 
        success: true, 
        message: response.data.message || 'Analysis started successfully' 
      };
    } catch (error: any) {
      // Enhanced error handling for cloud deployment
      if (error.response && error.response.status === 429) {
        return {
          success: false,
          message: error.response.data.error || 'Maximum concurrent analyses reached. Please try again later.'
        };
      }
      
      let errorMessage = 'Failed to start analysis';
      
      if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        errorMessage = 'Analysis request timed out. The server may be busy. Please try again.';
      } else if (error.response) {
        errorMessage = error.response.data?.error || `Server error: ${error.response.status}`;
      } else if (error.request) {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else {
        errorMessage = error.message || 'Unknown error occurred';
      }
      
      return {
        success: false,
        message: errorMessage
      };
    }
  }
  
  async ping(username: string): Promise<{
    status: string;
    username: string;
    activeAnalyses: number;
    maxConcurrentAnalyses: number;
  }> {
    try {
      const response = await this.axios.post<{
        status: string;
        username: string;
        activeAnalyses: number;
        maxConcurrentAnalyses: number;
      }>('/api/ping', { username });
      return response.data;
    } catch (error) {
      console.error('Ping failed:', error);
      throw error;
    }
  }
  
  // Start a keep-alive ping interval for a user
  startPingInterval(username: string, intervalMs: number = 30000): { stop: () => void } {
    const intervalId = setInterval(async () => {
      try {
        await this.ping(username);
      } catch (error) {
        console.log('Keep-alive ping failed:', error);
      }
    }, intervalMs);
    
    return {
      stop: () => clearInterval(intervalId)
    };
  }
}

export const apiService = new ApiService();
