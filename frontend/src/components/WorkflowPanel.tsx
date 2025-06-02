import React, { useState, useEffect } from 'react';
import { User, Download, Brain, CheckCircle, Clock, AlertCircle, Play, Settings } from 'lucide-react';
import { apiService, GameStats } from '../services/api';

interface WorkflowPanelProps {
  onStatsUpdate?: () => void;
  username: string;
  onUsernameChange: (username: string) => void;
}

type WorkflowStep = 'input' | 'fetch' | 'analyze' | 'complete';

interface OperationStatus {
  fetching: boolean;
  analyzing: boolean;
  last_operation: {
    type: string;
    completed_at: string;
    result?: string;
    error?: string;
  } | null;
  progress: any;
}

export const WorkflowPanel: React.FC<WorkflowPanelProps> = ({ onStatsUpdate, username, onUsernameChange }) => {
  const [currentStep, setCurrentStep] = useState<WorkflowStep>('input');
  const [batchSize, setBatchSize] = useState(50);
  const [timeLimit, setTimeLimit] = useState(20);
  const [totalTimeLimit, setTotalTimeLimit] = useState<number | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [operationStatus, setOperationStatus] = useState<OperationStatus>({
    fetching: false,
    analyzing: false,
    last_operation: null,
    progress: {}
  });
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');
  const [stats, setStats] = useState<GameStats | null>(null);
  const [countdown, setCountdown] = useState<number | null>(null);
  const [estimatedTimeRemaining, setEstimatedTimeRemaining] = useState<number | null>(null);

  // Poll for operation status and stats
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (currentStep === 'fetch' || currentStep === 'analyze') {
      interval = setInterval(async () => {
        try {
          const newStats = await apiService.getStats(username);
          setStats(newStats);
          setOperationStatus(newStats.operation_status);
          
          // Calculate countdown and time estimates for analysis
          if (currentStep === 'analyze' && newStats.operation_status.analyzing && newStats.operation_status.progress) {
            const progress = newStats.operation_status.progress;
            
            // Calculate time remaining estimates
            if (progress.start_time && progress.current > 0) {
              const startTime = new Date(progress.start_time).getTime();
              const now = Date.now();
              const elapsedSeconds = (now - startTime) / 1000;
              const avgTimePerGame = elapsedSeconds / progress.current;
              const remainingGames = progress.total - progress.current;
              const estimatedRemaining = remainingGames * avgTimePerGame;
              setEstimatedTimeRemaining(Math.round(estimatedRemaining));
            }
            
            // Update countdown for current game (per-game time limit)
            if (progress.time_limit_per_game) {
              setCountdown(progress.time_limit_per_game);
            }
          }
          
          // Check if operations are complete
          if (currentStep === 'fetch' && !newStats.operation_status.fetching) {
            if (newStats.operation_status.last_operation?.type === 'fetch') {
              if (newStats.operation_status.last_operation?.error) {
                setError(newStats.operation_status.last_operation.error);
                setCurrentStep('input');
              } else {
                setStatusMessage('Games fetched successfully! Ready to analyze.');
                setCurrentStep('analyze');
              }
            }
          }
          
          if (currentStep === 'analyze' && !newStats.operation_status.analyzing) {
            if (newStats.operation_status.last_operation?.type === 'analyze') {
              if (newStats.operation_status.last_operation?.error) {
                setError(newStats.operation_status.last_operation.error);
                setCurrentStep('input');
              } else {
                setStatusMessage('Analysis completed successfully!');
                setCurrentStep('complete');
                onStatsUpdate?.();
              }
            }
            // Clear countdown when analysis finishes
            setCountdown(null);
            setEstimatedTimeRemaining(null);
          }
        } catch (error) {
          console.error('Error polling status:', error);
        }
      }, 2000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [currentStep, onStatsUpdate, username]);

  const handleFetchGames = async (fetchOlder: boolean = false) => {
    if (!username.trim()) {
      setError('Please enter a Lichess username');
      return;
    }

    setIsLoading(true);
    setError('');
    setStatusMessage('');

    try {
      await apiService.fetchGames(username.trim(), batchSize, fetchOlder);
      setCurrentStep('fetch');
      const direction = fetchOlder ? 'older' : 'newer';
      setStatusMessage(`Fetching ${direction} games from Lichess...`);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to start fetching games');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeGames = async () => {
    if (!username.trim()) {
      setError('Please enter a Lichess username');
      return;
    }

    setIsLoading(true);
    setError('');
    setStatusMessage('');

    try {
      await apiService.analyzeGames(username.trim(), timeLimit, totalTimeLimit);
      setCurrentStep('analyze');
      setStatusMessage('Analyzing games...');
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to start analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setCurrentStep('input');
    setStatusMessage('');
    setError('');
    setStats(null);
    setCountdown(null);
    setEstimatedTimeRemaining(null);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStepStatus = (step: WorkflowStep) => {
    if (currentStep === step) return 'current';
    const stepOrder = ['input', 'fetch', 'analyze', 'complete'];
    const currentIndex = stepOrder.indexOf(currentStep);
    const stepIndex = stepOrder.indexOf(step);
    return stepIndex < currentIndex ? 'completed' : 'pending';
  };

  const renderStepIndicator = (step: WorkflowStep, icon: React.ReactNode, title: string, description: string) => {
    const status = getStepStatus(step);
    
    return (
      <div className="flex flex-col items-center">
        <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
          status === 'completed' 
            ? 'bg-green-500 border-green-500 text-white'
            : status === 'current'
            ? 'bg-blue-500 border-blue-500 text-white'
            : 'bg-gray-100 border-gray-300 text-gray-400'
        }`}>
          {status === 'completed' ? <CheckCircle className="h-4 w-4" /> : icon}
        </div>
        <div className="mt-1 text-center">
          <div className={`text-xs font-medium ${
            status === 'completed' ? 'text-green-700' 
            : status === 'current' ? 'text-blue-700'
            : 'text-gray-500'
          }`}>
            {title}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Play className="h-5 w-5 text-blue-600" />
          Game Loading
        </h2>
      </div>

      {/* Compact Progress Steps */}
      <div className="mb-4">
        <div className="flex items-center justify-between space-x-2">
          {renderStepIndicator('input', <User className="h-4 w-4" />, 'Input', '')}
          <div className="flex-1 h-0.5 bg-gray-200"></div>
          {renderStepIndicator('fetch', <Download className="h-4 w-4" />, 'Fetch', '')}
          <div className="flex-1 h-0.5 bg-gray-200"></div>
          {renderStepIndicator('analyze', <Brain className="h-4 w-4" />, 'Analyze', '')}
          <div className="flex-1 h-0.5 bg-gray-200"></div>
          {renderStepIndicator('complete', <CheckCircle className="h-4 w-4" />, 'Done', '')}
        </div>
      </div>

      <div>
        {/* Step 1: Input */}
        {currentStep === 'input' && (
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label htmlFor="batchSize" className="block text-xs font-medium text-gray-700 mb-1">
                  Games
                </label>
                <select
                  id="batchSize"
                  value={batchSize}
                  onChange={(e) => setBatchSize(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                </select>
              </div>

              <div>
                <label htmlFor="timeLimit" className="block text-xs font-medium text-gray-700 mb-1">
                  Per Game (s)
                </label>
                <select
                  id="timeLimit"
                  value={timeLimit}
                  onChange={(e) => setTimeLimit(Number(e.target.value))}
                  className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                >
                  <option value={10}>10</option>
                  <option value={20}>20</option>
                  <option value={30}>30</option>
                  <option value={60}>60</option>
                </select>
              </div>

              <div>
                <label htmlFor="totalTimeLimit" className="block text-xs font-medium text-gray-700 mb-1">
                  Total (s)
                </label>
                <select
                  id="totalTimeLimit"
                  value={totalTimeLimit || ''}
                  onChange={(e) => setTotalTimeLimit(e.target.value ? Number(e.target.value) : undefined)}
                  className="w-full border border-gray-300 rounded-md px-2 py-1 text-sm"
                >
                  <option value="">No limit</option>
                  <option value={300}>300</option>
                  <option value={600}>600</option>
                  <option value={1200}>1200</option>
                  <option value={1800}>1800</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => handleFetchGames(false)}
                disabled={isLoading || !username.trim()}
                className="flex-1 bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1 text-sm"
              >
                <Download className="h-3 w-3" />
                Fetch Newer
              </button>
              <button
                onClick={() => handleFetchGames(true)}
                disabled={isLoading || !username.trim()}
                className="flex-1 bg-gray-600 text-white py-2 px-3 rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1 text-sm"
              >
                <Download className="h-3 w-3" />
                Fetch Older
              </button>
            </div>

            <button
              onClick={handleAnalyzeGames}
              disabled={isLoading || !username.trim()}
              className="w-full bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1 text-sm"
            >
              <Brain className="h-3 w-3" />
              Start Analysis
            </button>
          </div>
        )}

        {/* Step 2: Fetch Games */}
        {currentStep === 'fetch' && (
          <div className="flex items-center justify-center p-4">
            <div className="text-center">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
              <p className="text-sm text-gray-600">Fetching {batchSize} games...</p>
              {operationStatus.progress?.stage && (
                <p className="text-xs text-blue-600 mt-1">
                  {operationStatus.progress.current || 0} / {operationStatus.progress.total || 0}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Analyze Games */}
        {currentStep === 'analyze' && (
          <div className="space-y-3">
            <button
              onClick={handleAnalyzeGames}
              disabled={isLoading}
              className="w-full bg-green-600 text-white py-2 px-3 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1 text-sm"
            >
              <Brain className="h-3 w-3" />
              Analyze Games ({timeLimit}s per game{totalTimeLimit ? `, ${totalTimeLimit}s total` : ''})
            </button>

            {operationStatus.analyzing && (
              <div className="space-y-3">
                <div className="flex items-center justify-center p-4">
                  <div className="text-center">
                    <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    <p className="text-sm text-gray-600">Analyzing games...</p>
                    
                    {/* Progress Bar */}
                    {operationStatus.progress?.total > 0 && (
                      <div className="mt-2 w-full">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full transition-all duration-300"
                            style={{ 
                              width: `${((operationStatus.progress.current || 0) / operationStatus.progress.total) * 100}%` 
                            }}
                          ></div>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>{operationStatus.progress.current || 0} / {operationStatus.progress.total}</span>
                          <span>
                            {Math.round(((operationStatus.progress.current || 0) / operationStatus.progress.total) * 100)}%
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Current Game Info */}
                    {operationStatus.progress?.current_game && (
                      <p className="text-xs text-gray-500 mt-1">
                        Current: {operationStatus.progress.current_game}
                      </p>
                    )}

                    {/* Time Estimates */}
                    <div className="mt-2 space-y-1">
                      {countdown && (
                        <div className="text-xs text-blue-600">
                          <Clock className="h-3 w-3 inline mr-1" />
                          Per game limit: {formatTime(countdown)}
                        </div>
                      )}
                      {estimatedTimeRemaining && (
                        <div className="text-xs text-orange-600">
                          Estimated remaining: {formatTime(estimatedTimeRemaining)}
                        </div>
                      )}
                      {operationStatus.progress?.total_time_limit && (
                        <div className="text-xs text-red-600">
                          Session limit: {formatTime(operationStatus.progress.total_time_limit)}
                        </div>
                      )}
                    </div>

                    {/* Analysis Results Summary */}
                    {operationStatus.progress?.games_analyzed !== undefined && (
                      <div className="text-xs text-gray-600 mt-2">
                        Completed: {operationStatus.progress.games_analyzed} | 
                        Skipped: {operationStatus.progress.games_skipped || 0}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {stats && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-600">Games:</span>
                    <span className="ml-1 font-medium">{stats.games.analyzed}/{stats.games.total}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Blunders:</span>
                    <span className="ml-1 font-medium">{stats.moves.blunders}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Step 4: Complete */}
        {currentStep === 'complete' && (
          <div className="space-y-3">
            <div className="text-center p-4">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-2" />
              <h3 className="text-lg font-semibold text-green-900 mb-1">Analysis Complete!</h3>
              <p className="text-sm text-green-700">Check results above</p>
            </div>

            {stats && (
              <div className="bg-green-50 rounded-lg p-3">
                <div className="grid grid-cols-4 gap-3 text-center text-sm">
                  <div>
                    <div className="text-xl font-bold text-green-700">{stats.games.analyzed}</div>
                    <div className="text-xs text-green-600">Games</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-green-700">{stats.moves.total}</div>
                    <div className="text-xs text-green-600">Moves</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-red-700">{stats.moves.blunders}</div>
                    <div className="text-xs text-red-600">Blunders</div>
                  </div>
                  <div>
                    <div className="text-xl font-bold text-yellow-700">{stats.moves.mistakes}</div>
                    <div className="text-xs text-yellow-600">Mistakes</div>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleReset}
              className="w-full bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 flex items-center justify-center gap-1 text-sm"
            >
              <Settings className="h-3 w-3" />
              Analyze More
            </button>
          </div>
        )}
      </div>

      {/* Status Messages */}
      {statusMessage && (
        <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded-md">
          <div className="flex items-center">
            <Clock className="h-3 w-3 text-blue-500 mr-2" />
            <span className="text-blue-700 text-xs">{statusMessage}</span>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-md">
          <div className="flex items-center">
            <AlertCircle className="h-3 w-3 text-red-500 mr-2" />
            <span className="text-red-700 text-xs">{error}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowPanel;
