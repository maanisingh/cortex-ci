interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div
      className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="card">
      <div className="flex items-center">
        <Skeleton className="w-12 h-12 rounded-md" />
        <div className="ml-5 flex-1">
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-6 w-16" />
        </div>
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="overflow-hidden">
      <div className="border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-4 py-3">
        <div className="flex space-x-4">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-16" />
        </div>
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="border-b border-gray-200 dark:border-gray-700 px-4 py-4"
        >
          <div className="flex space-x-4">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="card">
      <Skeleton className="h-6 w-40 mb-4" />
      <div className="h-64 flex items-center justify-center">
        <Skeleton className="w-48 h-48 rounded-full" />
      </div>
    </div>
  );
}

export function PageHeaderSkeleton() {
  return (
    <div className="mb-8">
      <Skeleton className="h-8 w-48 mb-2" />
      <Skeleton className="h-4 w-64" />
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div>
      <PageHeaderSkeleton />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {Array.from({ length: 4 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2 mb-8">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
    </div>
  );
}

export function EntityListSkeleton() {
  return (
    <div>
      <PageHeaderSkeleton />
      <div className="mb-4 flex justify-between">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-10 w-32" />
      </div>
      <TableSkeleton rows={10} />
    </div>
  );
}

export function DetailPageSkeleton() {
  return (
    <div>
      <PageHeaderSkeleton />

      {/* Info Cards */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-3 mb-8">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="card">
            <Skeleton className="h-5 w-24 mb-4" />
            <div className="space-y-3">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="card">
        <Skeleton className="h-6 w-32 mb-4" />
        <TableSkeleton rows={5} />
      </div>
    </div>
  );
}

export default {
  Skeleton,
  CardSkeleton,
  TableSkeleton,
  ChartSkeleton,
  PageHeaderSkeleton,
  DashboardSkeleton,
  EntityListSkeleton,
  DetailPageSkeleton,
};
