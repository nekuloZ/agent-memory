import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { RefreshCw, Clock, CheckCircle, AlertCircle, Loader2, Server } from 'lucide-react';

interface Task {
  id: string;
  from_agent: string;
  to_agent: string;
  task_type: string;
  title: string;
  description: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'retrying';
  priority: number;
  retry_count: number;
  max_retries: number;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  payload: any;
}

// Supabase 配置
const SUPABASE_URL = 'https://bvaykseswlcysfqgxldz.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ2YXlrc2Vzd2xjeXNmcWd4bGR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkxNDAxOTUsImV4cCI6MjA4NDcxNjE5NX0.UcwduJhBy0kmumv9DCvl-3uUZ7fKCpWY7uLFTbexxww';

function App() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${SUPABASE_URL}/rest/v1/agent_tasks?order=created_at.desc&limit=50`, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setTasks(data);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 30000); // 30秒自动刷新
    return () => clearInterval(interval);
  }, [fetchTasks]);

  const pendingTasks = tasks.filter(t => t.status === 'pending');
  const processingTasks = tasks.filter(t => t.status === 'processing');
  const completedTasks = tasks.filter(t => t.status === 'completed');
  const failedTasks = tasks.filter(t => t.status === 'failed');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500/10 text-yellow-600 border-yellow-500/20';
      case 'processing': return 'bg-blue-500/10 text-blue-600 border-blue-500/20';
      case 'completed': return 'bg-green-500/10 text-green-600 border-green-500/20';
      case 'failed': return 'bg-red-500/10 text-red-600 border-red-500/20';
      case 'retrying': return 'bg-orange-500/10 text-orange-600 border-orange-500/20';
      default: return 'bg-gray-500/10 text-gray-600 border-gray-500/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-3 h-3" />;
      case 'processing': return <Loader2 className="w-3 h-3 animate-spin" />;
      case 'completed': return <CheckCircle className="w-3 h-3" />;
      case 'failed': return <AlertCircle className="w-3 h-3" />;
      default: return null;
    }
  };

  const TaskCard = ({ task }: { task: Task }) => (
    <Card className="mb-3 hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs text-muted-foreground font-mono">{task.id.slice(0, 8)}</span>
              <Badge variant="outline" className={`text-xs ${getStatusColor(task.status)}`}>
                <span className="flex items-center gap-1">
                  {getStatusIcon(task.status)}
                  {task.status}
                </span>
              </Badge>
              <Badge variant="secondary" className="text-xs">P{task.priority}</Badge>
            </div>
            <h4 className="font-medium text-sm truncate">{task.title}</h4>
            {task.description && (
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{task.description}</p>
            )}
            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Server className="w-3 h-3" />
                {task.from_agent} → {task.to_agent}
              </span>
              <span className="capitalize">{task.task_type}</span>
              {task.retry_count > 0 && (
                <span className="text-orange-500">
                  Retry {task.retry_count}/{task.max_retries}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="text-xs text-muted-foreground mt-2 pt-2 border-t">
          Created: {new Date(task.created_at).toLocaleString()}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold flex items-center gap-2">
              <Server className="w-6 h-6" />
              Jarvis Task Dashboard
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              Last update: {lastUpdate.toLocaleTimeString()}
            </p>
          </div>
          <Button onClick={fetchTasks} disabled={loading} size="sm">
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {error && (
          <Card className="mb-4 border-red-500/20 bg-red-500/5">
            <CardContent className="p-4 text-sm text-red-600">
              Error: {error}
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-4 gap-3 mb-6">
          <Card className="bg-yellow-500/5 border-yellow-500/20">
            <CardContent className="p-3 text-center">
              <div className="text-2xl font-bold text-yellow-600">{pendingTasks.length}</div>
              <div className="text-xs text-muted-foreground">Pending</div>
            </CardContent>
          </Card>
          <Card className="bg-blue-500/5 border-blue-500/20">
            <CardContent className="p-3 text-center">
              <div className="text-2xl font-bold text-blue-600">{processingTasks.length}</div>
              <div className="text-xs text-muted-foreground">Processing</div>
            </CardContent>
          </Card>
          <Card className="bg-green-500/5 border-green-500/20">
            <CardContent className="p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{completedTasks.length}</div>
              <div className="text-xs text-muted-foreground">Completed</div>
            </CardContent>
          </Card>
          <Card className="bg-red-500/5 border-red-500/20">
            <CardContent className="p-3 text-center">
              <div className="text-2xl font-bold text-red-600">{failedTasks.length}</div>
              <div className="text-xs text-muted-foreground">Failed</div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="all" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="all">All ({tasks.length})</TabsTrigger>
            <TabsTrigger value="pending">Pending ({pendingTasks.length})</TabsTrigger>
            <TabsTrigger value="processing">Processing ({processingTasks.length})</TabsTrigger>
            <TabsTrigger value="completed">Completed ({completedTasks.length})</TabsTrigger>
            <TabsTrigger value="failed">Failed ({failedTasks.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="all">
            <ScrollArea className="h-[500px] pr-4">
              {tasks.length === 0 ? (
                <div className="text-center text-muted-foreground py-12">No tasks found</div>
              ) : (
                tasks.map(task => <TaskCard key={task.id} task={task} />)
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="pending">
            <ScrollArea className="h-[500px] pr-4">
              {pendingTasks.length === 0 ? (
                <div className="text-center text-muted-foreground py-12">No pending tasks</div>
              ) : (
                pendingTasks.map(task => <TaskCard key={task.id} task={task} />)
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="processing">
            <ScrollArea className="h-[500px] pr-4">
              {processingTasks.length === 0 ? (
                <div className="text-center text-muted-foreground py-12">No processing tasks</div>
              ) : (
                processingTasks.map(task => <TaskCard key={task.id} task={task} />)
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="completed">
            <ScrollArea className="h-[500px] pr-4">
              {completedTasks.length === 0 ? (
                <div className="text-center text-muted-foreground py-12">No completed tasks</div>
              ) : (
                completedTasks.map(task => <TaskCard key={task.id} task={task} />)
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="failed">
            <ScrollArea className="h-[500px] pr-4">
              {failedTasks.length === 0 ? (
                <div className="text-center text-muted-foreground py-12">No failed tasks</div>
              ) : (
                failedTasks.map(task => <TaskCard key={task.id} task={task} />)
              )}
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;
